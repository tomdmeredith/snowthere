"""Research primitives for gathering ski resort information.

Uses three complementary search APIs:
- Exa: Semantic search (finding content by meaning)
- Brave: Traditional web search (specific queries, official sites)
- Tavily: AI-powered research synthesis

Design Decision (Round 5.7 - validated 2026-01-23):
Empirical testing of 70 queries across 10 resorts showed:
- Tavily wins ALL 7 query types (3.85 composite score)
- Tavily has 2x better price discovery (25.7% vs ~13%)
- Each API provides ~25% unique URLs (low overlap = keep all 3)
- Cost-effectiveness: Tavily $0.0013/point, Brave $0.0014/point, Exa $0.0031/point

Recommendation: Prioritize Tavily for quality, keep Exa/Brave for URL diversity.

Design Decision: We use Brave instead of SerpAPI because:
1. User already has BRAVE_API_KEY
2. Simpler API with direct HTTP calls
3. Combined with Exa + Tavily provides comprehensive coverage
"""

import asyncio
import logging
import time
from dataclasses import dataclass, asdict, field
from typing import Any

import httpx
from exa_py import Exa
from tavily import TavilyClient

from ..config import settings
from .system import log_cost
from .research_cache import get_cached_results, cache_results

logger = logging.getLogger(__name__)


# Cost constants per API (validated pricing as of 2026-01)
API_COSTS = {
    "exa": 0.001 + 0.001 * 5,  # $0.001/search + $0.001/result with text (assuming 5 results)
    "brave": 0.005,  # $5/1000 queries
    "tavily": 0.005,  # $5/1000 (advanced mode)
}


# Brave Search API base URL
BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"


@dataclass
class SearchLanguageConfig:
    """Language configuration for a country's search queries."""
    code: str           # ISO 639-1 (e.g., "de", "fr")
    name: str           # Human-readable (e.g., "German")
    has_local_queries: bool  # Whether to run local-language queries
    local_domains: list[str] = field(default_factory=list)


COUNTRY_LANGUAGE_MAP: dict[str, SearchLanguageConfig] = {
    "austria": SearchLanguageConfig("de", "German", True, [".at"]),
    "germany": SearchLanguageConfig("de", "German", True, [".de"]),
    "switzerland": SearchLanguageConfig("de", "German", True, [".ch"]),
    "france": SearchLanguageConfig("fr", "French", True, [".fr"]),
    "italy": SearchLanguageConfig("it", "Italian", True, [".it"]),
    "spain": SearchLanguageConfig("es", "Spanish", True, [".es"]),
    "andorra": SearchLanguageConfig("es", "Spanish", True, [".ad"]),
    "japan": SearchLanguageConfig("ja", "Japanese", True, [".jp"]),
    "norway": SearchLanguageConfig("no", "Norwegian", True, [".no"]),
    "sweden": SearchLanguageConfig("sv", "Swedish", True, [".se"]),
    "finland": SearchLanguageConfig("fi", "Finnish", True, [".fi"]),
    "argentina": SearchLanguageConfig("es", "Spanish", True, [".ar"]),
    "chile": SearchLanguageConfig("es", "Spanish", True, [".cl"]),
    # English-primary countries — no local queries needed
    "united states": SearchLanguageConfig("en", "English", False),
    "canada": SearchLanguageConfig("en", "English", False),
    "united kingdom": SearchLanguageConfig("en", "English", False),
    "australia": SearchLanguageConfig("en", "English", False),
    "new zealand": SearchLanguageConfig("en", "English", False),
}


def resolve_search_languages(country: str) -> SearchLanguageConfig:
    """Resolve country to search language config. Deterministic, $0."""
    return COUNTRY_LANGUAGE_MAP.get(
        country.lower(),
        SearchLanguageConfig("en", "English", False),
    )


async def generate_local_queries(
    resort_name: str,
    country: str,
    language: str,
) -> dict[str, str]:
    """Generate local-language search queries using Claude Haiku. ~$0.001/call.

    Agent-native approach: Claude knows ski terminology in all languages natively.
    No static dictionary needed. Handles dialects, regional terms, and edge cases.

    Args:
        resort_name: Resort name (kept as-is, already local)
        country: Country for regional context
        language: Target language name (e.g., "German", "French")

    Returns:
        Dict with query_type -> local-language query string
    """
    import json
    import anthropic

    start_time = time.time()
    valid_keys = {"official", "ski_school", "lodging"}

    def _call_haiku() -> str:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            system="You generate search queries in the specified language for ski resort research. Return ONLY valid JSON, no markdown.",
            messages=[{
                "role": "user",
                "content": f"""Generate 3 search queries in {language} to find family ski information about {resort_name} in {country}.

The queries should find:
1. Official resort info, lift ticket prices, and ski pass costs
2. Ski school for children, childcare facilities, and lesson prices
3. Family-friendly hotels, lodging prices, and accommodation options

Return as JSON:
{{"official": "query in {language}", "ski_school": "query in {language}", "lodging": "query in {language}"}}"""
            }],
        )
        return message.content[0].text

    try:
        response_text = await asyncio.to_thread(_call_haiku)

        if "```" in response_text:
            response_text = response_text.split("```json")[-1].split("```")[0] if "```json" in response_text else response_text.split("```")[1].split("```")[0]

        queries = json.loads(response_text.strip())

        # Validate: only accept expected keys with string values
        queries = {k: v for k, v in queries.items() if k in valid_keys and isinstance(v, str)}
        if not queries:
            logger.warning(f"No valid query keys in Haiku response for {resort_name}")
            return {}

        return queries
    except Exception as e:
        logger.warning(f"Failed to generate local queries for {resort_name} in {language}: {e}")
        return {}
    finally:
        latency_ms = int((time.time() - start_time) * 1000)
        log_cost("anthropic_haiku", 0.001, None, {
            "purpose": "local_query_generation",
            "resort": resort_name,
            "language": language,
            "latency_ms": latency_ms,
        })


def merge_multilingual_results(
    english_results: list["SearchResult"],
    local_results: list["SearchResult"],
) -> list["SearchResult"]:
    """Merge English and local-language results, deduplicating by URL. $0 cost."""
    seen_urls: set[str] = set()
    merged = []
    # English results first (higher baseline quality for extraction)
    for r in english_results:
        if r.url not in seen_urls:
            seen_urls.add(r.url)
            merged.append(r)
    # Then local results (unique URLs only)
    for r in local_results:
        if r.url not in seen_urls:
            seen_urls.add(r.url)
            merged.append(r)
    return merged


@dataclass
class SearchResult:
    """Standardized search result across providers."""

    title: str
    url: str
    snippet: str
    source: str  # 'exa', 'serp', 'tavily'
    score: float | None = None
    published_date: str | None = None


async def exa_search(
    query: str,
    num_results: int = 10,
    include_domains: list[str] | None = None,
    resort_name: str | None = None,
    country: str | None = None,
    query_type: str | None = None,
) -> list[SearchResult]:
    """
    Semantic search via Exa API.

    Best for: Finding trip reports, blog posts, family ski reviews.
    Note: Tavily generally outperforms Exa for all query types (Round 5.7 testing),
    but Exa provides ~28% unique URLs so we keep it for diversity.

    Args:
        query: Search query
        num_results: Number of results to return
        include_domains: Optional list of domains to restrict search to
        resort_name: Optional resort name for caching
        country: Optional country for caching
        query_type: Optional query type for caching (family_reviews, lodging, etc.)
    """
    if not settings.exa_api_key:
        return []

    # Check cache if resort context provided
    if resort_name and country and query_type:
        cached = get_cached_results(resort_name, country, query_type, "exa")
        if cached:
            logger.info(f"[exa] Cache HIT for {resort_name} {query_type}")
            return [
                SearchResult(
                    title=r.get("title", ""),
                    url=r.get("url", ""),
                    snippet=r.get("snippet", ""),
                    source="exa",
                    score=r.get("score"),
                    published_date=r.get("published_date"),
                )
                for r in cached.get("results", [])
            ]

    exa = Exa(api_key=settings.exa_api_key)
    start_time = time.time()
    error_msg = None

    # Run in thread pool since exa-py is sync
    def _search():
        kwargs = {
            "type": "auto",  # Changed from 'neural' (deprecated) - API now uses 'auto', 'fast', 'deep'
            "num_results": num_results,
            "text": {"max_characters": 1500},
        }
        if include_domains:
            kwargs["include_domains"] = include_domains
        return exa.search_and_contents(query, **kwargs)

    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, _search)
    except Exception as e:
        error_msg = str(e)
        logger.error(f"[exa] Search error: {e}")
        response = None

    latency_ms = int((time.time() - start_time) * 1000)

    results = []
    if response:
        for r in response.results:
            results.append(
                SearchResult(
                    title=r.title or "",
                    url=r.url,
                    snippet=r.text[:1500] if r.text else "",
                    source="exa",
                    score=r.score if hasattr(r, "score") else None,
                    published_date=r.published_date if hasattr(r, "published_date") else None,
                )
            )

    # Log cost (per-API tracking)
    cost = API_COSTS["exa"]
    log_cost("exa", cost, None, {
        "query": query[:100],
        "results_count": len(results),
        "latency_ms": latency_ms,
        "query_type": query_type,
    })

    # Cache results if resort context provided
    if resort_name and country and query_type:
        cache_results(
            resort_name=resort_name,
            country=country,
            query_type=query_type,
            query_text=query,
            api_source="exa",
            results=[asdict(r) for r in results],
            latency_ms=latency_ms,
            error=error_msg,
        )

    return results


async def brave_search(
    query: str,
    num_results: int = 10,
    country: str = "US",
    search_lang: str = "en",
    max_retries: int = 3,
    resort_name: str | None = None,
    resort_country: str | None = None,
    query_type: str | None = None,
) -> list[SearchResult]:
    """
    Web search via Brave Search API with exponential backoff.

    Best for: Official resort sites, current pricing, news.
    Replaces SerpAPI with a simpler, direct HTTP implementation.
    Note: Similar quality to Exa (3.53 vs 3.55) but cheaper ($0.005 vs $0.011).

    Rate limiting: Implements exponential backoff on 429 errors.

    Args:
        query: Search query
        num_results: Number of results to return
        country: Country code for search localization
        search_lang: ISO 639-1 language code for search results (default "en")
        max_retries: Number of retries on rate limit
        resort_name: Optional resort name for caching
        resort_country: Optional resort country for caching
        query_type: Optional query type for caching
    """
    if not settings.brave_api_key:
        return []

    # Check cache if resort context provided
    if resort_name and resort_country and query_type:
        cached = get_cached_results(resort_name, resort_country, query_type, "brave")
        if cached:
            logger.info(f"[brave] Cache HIT for {resort_name} {query_type}")
            return [
                SearchResult(
                    title=r.get("title", ""),
                    url=r.get("url", ""),
                    snippet=r.get("snippet", ""),
                    source="brave",
                    score=r.get("score"),
                )
                for r in cached.get("results", [])
            ]

    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": settings.brave_api_key,
    }

    params = {
        "q": query,
        "count": num_results,
        "country": country,
        "search_lang": search_lang,
        "safesearch": "moderate",
    }

    start_time = time.time()
    error_msg = None
    data = None

    async with httpx.AsyncClient() as client:
        for attempt in range(max_retries):
            try:
                response = await client.get(
                    BRAVE_SEARCH_URL,
                    headers=headers,
                    params=params,
                    timeout=30,
                )
                response.raise_for_status()
                data = response.json()
                break  # Success, exit retry loop
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    # Rate limited - exponential backoff
                    wait_time = 2 ** attempt  # 1s, 2s, 4s
                    logger.warning(f"Brave API rate limited (429), waiting {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                    if attempt == max_retries - 1:
                        error_msg = f"Rate limit exceeded after {max_retries} retries"
                        logger.error(f"Brave API rate limit exceeded after {max_retries} retries for query: {query[:50]}")
                else:
                    error_msg = str(e)
                    logger.error(f"Brave search HTTP error: {e}")
            except httpx.HTTPError as e:
                error_msg = str(e)
                logger.error(f"Brave search error: {e}")

    latency_ms = int((time.time() - start_time) * 1000)

    results = []
    if data:
        web_results = data.get("web", {}).get("results", [])
        for i, r in enumerate(web_results[:num_results]):
            results.append(
                SearchResult(
                    title=r.get("title", ""),
                    url=r.get("url", ""),
                    snippet=r.get("description", ""),
                    source="brave",
                    score=1.0 - (i / num_results),  # Higher rank = higher score
                )
            )

    # Log cost (per-API tracking)
    cost = API_COSTS["brave"]
    log_cost("brave", cost, None, {
        "query": query[:100],
        "results_count": len(results),
        "latency_ms": latency_ms,
        "query_type": query_type,
    })

    # Cache results if resort context provided
    if resort_name and resort_country and query_type:
        cache_results(
            resort_name=resort_name,
            country=resort_country,
            query_type=query_type,
            query_text=query,
            api_source="brave",
            results=[asdict(r) for r in results],
            latency_ms=latency_ms,
            error=error_msg,
        )

    return results


# Alias for backwards compatibility
serp_search = brave_search


async def tavily_search(
    query: str,
    search_depth: str = "advanced",
    max_results: int = 10,
    include_answer: bool = True,
    resort_name: str | None = None,
    country: str | None = None,
    query_type: str | None = None,
) -> dict[str, Any]:
    """
    Web research via Tavily API.

    Best for: ALL query types - Round 5.7 testing showed Tavily wins all 7 categories.
    Particularly strong for pricing queries (25.7% have current prices vs ~13% for others).
    Returns both search results and an AI-generated answer.

    Args:
        query: Search query
        search_depth: "basic" or "advanced" (advanced provides better results)
        max_results: Number of results to return
        include_answer: Whether to include AI-generated answer
        resort_name: Optional resort name for caching
        country: Optional country for caching
        query_type: Optional query type for caching
    """
    if not settings.tavily_api_key:
        return {"results": [], "answer": None}

    # Check cache if resort context provided
    if resort_name and country and query_type:
        cached = get_cached_results(resort_name, country, query_type, "tavily")
        if cached:
            logger.info(f"[tavily] Cache HIT for {resort_name} {query_type}")
            return {
                "results": [
                    SearchResult(
                        title=r.get("title", ""),
                        url=r.get("url", ""),
                        snippet=r.get("snippet", ""),
                        source="tavily",
                        score=r.get("score"),
                    )
                    for r in cached.get("results", [])
                ],
                "answer": cached.get("ai_answer"),
            }

    client = TavilyClient(api_key=settings.tavily_api_key)
    start_time = time.time()
    error_msg = None
    response = None

    def _search():
        return client.search(
            query,
            search_depth=search_depth,
            max_results=max_results,
            include_answer=include_answer,
        )

    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, _search)
    except Exception as e:
        error_msg = str(e)
        logger.error(f"[tavily] Search error: {e}")

    latency_ms = int((time.time() - start_time) * 1000)

    results = []
    ai_answer = None
    if response:
        ai_answer = response.get("answer")
        for r in response.get("results", []):
            results.append(
                SearchResult(
                    title=r.get("title", ""),
                    url=r.get("url", ""),
                    snippet=r.get("content", ""),
                    source="tavily",
                    score=r.get("score"),
                )
            )

    # Log cost (per-API tracking)
    cost = API_COSTS["tavily"]
    log_cost("tavily", cost, None, {
        "query": query[:100],
        "results_count": len(results),
        "latency_ms": latency_ms,
        "query_type": query_type,
        "has_answer": ai_answer is not None,
    })

    # Cache results if resort context provided
    if resort_name and country and query_type:
        cache_results(
            resort_name=resort_name,
            country=country,
            query_type=query_type,
            query_text=query,
            api_source="tavily",
            results=[asdict(r) for r in results],
            latency_ms=latency_ms,
            ai_answer=ai_answer,
            error=error_msg,
        )

    return {
        "results": results,
        "answer": ai_answer,
    }


async def search_resort_info(
    resort_name: str,
    country: str,
    focus: str = "family",
) -> dict[str, Any]:
    """
    Comprehensive resort search across all providers with caching.

    Combines results from Exa (semantic), Brave (web search), and Tavily (AI research).

    Round 5.7 Testing Results (2026-01-23):
    - Tavily wins ALL 7 query types with 3.85 composite score
    - Tavily has 2x better price discovery (25.7% vs ~13%)
    - URL overlap only 25.9% - each API provides unique sources
    - Recommendation: Prioritize Tavily, keep others for diversity

    CRITICAL: Includes dedicated pricing queries to find cost data families need.
    Caching: Results are cached per resort/query_type/api for 30-180 days.
    """
    from datetime import datetime
    current_year = datetime.now().year

    queries = {
        "family_reviews": f"{resort_name} {country} family ski trip review kids",
        "official_info": f"{resort_name} ski resort official site lift tickets",
        "ski_school": f"{resort_name} ski school children lessons childcare",
        "lodging": f"{resort_name} family lodging ski-in ski-out hotels",
        # Dedicated pricing queries (CRITICAL for family value)
        "lift_prices": f"{resort_name} lift ticket prices {current_year} {current_year + 1}",
        "lodging_rates": f"{resort_name} hotel prices per night winter ski season",
        "ski_school_cost": f"{resort_name} ski school lesson prices children cost",
    }

    # Run all searches in parallel with resort context for caching
    # API routing optimized based on Round 5.7 comparison (2026-01-23):
    # - Tavily for ALL pricing queries (2x better at finding prices, +0.76 margin on lift_prices)
    # - Exa for semantic content (family reviews, lodging - unique URLs)
    # - Brave for official info (finds official sites well)
    tasks = []

    # Exa for family reviews (semantic search finds unique trip reports)
    tasks.append(exa_search(
        queries["family_reviews"], num_results=5,
        resort_name=resort_name, country=country, query_type="family_reviews"
    ))

    # Brave for official info (traditional web search finds official sites)
    tasks.append(brave_search(
        queries["official_info"], num_results=5,
        resort_name=resort_name, resort_country=country, query_type="official_info"
    ))

    # Tavily for ski school info (AI synthesis - best for this, +0.21 margin)
    tasks.append(tavily_search(
        queries["ski_school"], max_results=5,
        resort_name=resort_name, country=country, query_type="ski_school"
    ))

    # Exa for lodging (semantic search finds unique family lodging content)
    tasks.append(exa_search(
        queries["lodging"], num_results=5,
        resort_name=resort_name, country=country, query_type="lodging"
    ))

    # PRICING QUERIES - ALL routed to Tavily (50.9% price discovery vs 25-30% for others)
    # lift_prices: Tavily wins by +0.76 margin (biggest gain in entire test)
    tasks.append(tavily_search(
        queries["lift_prices"], max_results=5,
        resort_name=resort_name, country=country, query_type="lift_prices"
    ))
    # lodging_rates: Tavily has 2x better price discovery
    tasks.append(tavily_search(
        queries["lodging_rates"], max_results=5,
        resort_name=resort_name, country=country, query_type="lodging_rates"
    ))
    # ski_school_cost: Tavily wins by +0.46 margin
    tasks.append(tavily_search(
        queries["ski_school_cost"], max_results=3,
        resort_name=resort_name, country=country, query_type="ski_school_cost"
    ))

    # --- Multilingual enrichment ---
    lang_config = resolve_search_languages(country)
    local_query_map = {}
    if lang_config.has_local_queries:
        # LLM generates queries natively in the target language (~$0.001)
        local_query_map = await generate_local_queries(resort_name, country, lang_config.name)

    if local_query_map:
        local_country_code = lang_config.local_domains[0].replace(".", "").upper() if lang_config.local_domains else "US"

        # Route: Brave for official (supports search_lang), Tavily for ski school + lodging
        if "official" in local_query_map:
            tasks.append(brave_search(
                local_query_map["official"], num_results=5,
                country=local_country_code,
                search_lang=lang_config.code,
                resort_name=resort_name, resort_country=country,
                query_type="local_official",
            ))
        if "ski_school" in local_query_map:
            tasks.append(tavily_search(
                local_query_map["ski_school"], max_results=5,
                resort_name=resort_name, country=country,
                query_type="local_ski_school",
            ))
        if "lodging" in local_query_map:
            tasks.append(tavily_search(
                local_query_map["lodging"], max_results=5,
                resort_name=resort_name, country=country,
                query_type="local_lodging",
            ))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Organize results
    # Note: Exa/Brave return list[SearchResult], Tavily returns {"results": list, "answer": str}
    organized = {
        "family_reviews": results[0] if not isinstance(results[0], Exception) else [],
        "official_info": results[1] if not isinstance(results[1], Exception) else [],
        "ski_school": results[2] if not isinstance(results[2], Exception) else {"results": []},
        "lodging": results[3] if not isinstance(results[3], Exception) else [],
        # Pricing categories (all Tavily now - dict format)
        "lift_prices": results[4] if not isinstance(results[4], Exception) else {"results": []},
        "lodging_rates": results[5] if not isinstance(results[5], Exception) else {"results": []},
        "ski_school_cost": results[6] if not isinstance(results[6], Exception) else {"results": []},
        "errors": [str(r) for r in results if isinstance(r, Exception)],
    }

    # Merge local-language results into existing categories
    num_english_tasks = 7  # Fixed English queries
    local_task_types = []  # Track which local queries were added, in order
    if local_query_map:
        if "official" in local_query_map:
            local_task_types.append("official_info")
        if "ski_school" in local_query_map:
            local_task_types.append("ski_school")
        if "lodging" in local_query_map:
            local_task_types.append("lodging")

    for i, category in enumerate(local_task_types):
        idx = num_english_tasks + i
        if idx < len(results) and not isinstance(results[idx], Exception):
            local_result = results[idx]
            # Brave returns list[SearchResult], Tavily returns dict with "results" key
            local_items = local_result.get("results", []) if isinstance(local_result, dict) else local_result
            existing = organized.get(category, [])
            existing_items = existing.get("results", []) if isinstance(existing, dict) else existing
            merged = merge_multilingual_results(existing_items, local_items)
            # Preserve original structure (dict for Tavily, list for Brave/Exa)
            if isinstance(existing, dict):
                organized[category] = {**existing, "results": merged}
            else:
                organized[category] = merged

    # Flatten sources for approval panel
    organized["sources"] = flatten_sources(organized)

    return organized


def flatten_sources(research_data: dict[str, Any]) -> list[dict[str, Any]]:
    """Flatten SearchResult objects from categorized research into unified sources list.

    The approval panel needs a flat list of sources to verify facts.
    This extracts SearchResult objects from all categories into a unified format.

    Args:
        research_data: Organized research data from search_resort_info()

    Returns:
        List of source dicts with title, url, snippet, source, category
    """
    sources = []
    seen_urls: set[str] = set()

    # List categories (Exa and Brave return lists directly)
    list_categories = ["family_reviews", "official_info", "lodging"]
    for category in list_categories:
        for result in research_data.get(category, []):
            if isinstance(result, SearchResult) and result.url not in seen_urls:
                sources.append({
                    "title": result.title,
                    "url": result.url,
                    "snippet": result.snippet,
                    "source": result.source,
                    "category": category,
                })
                seen_urls.add(result.url)

    # Dict categories (Tavily returns {"results": list, "answer": str})
    # All pricing queries now use Tavily for 2x better price discovery
    dict_categories = ["ski_school", "lift_prices", "lodging_rates", "ski_school_cost"]
    for category in dict_categories:
        data = research_data.get(category, {})
        if isinstance(data, dict):
            for result in data.get("results", []):
                if isinstance(result, SearchResult) and result.url not in seen_urls:
                    sources.append({
                        "title": result.title,
                        "url": result.url,
                        "snippet": result.snippet,
                        "source": result.source,
                        "category": category,
                    })
                    seen_urls.add(result.url)

    return sources


async def scrape_url(url: str, timeout: int = 30) -> str | None:
    """
    Fetch and clean webpage content.

    Returns raw text content, stripped of HTML.
    """
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.get(
                url,
                follow_redirects=True,
                headers={
                    "User-Agent": "Mozilla/5.0 (compatible; SnowthereBot/1.0)"
                },
            )
            response.raise_for_status()

            # Basic HTML stripping (for more complex needs, use BeautifulSoup)
            import re

            text = response.text
            text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.DOTALL)
            text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
            text = re.sub(r"<[^>]+>", " ", text)
            text = re.sub(r"\s+", " ", text)
            return text.strip()[:10000]  # Limit to 10k chars

        except httpx.HTTPError:
            return None


# Country code mapping for Nominatim disambiguation
COUNTRY_CODES: dict[str, str] = {
    "austria": "at", "france": "fr", "italy": "it", "germany": "de",
    "switzerland": "ch", "united states": "us", "usa": "us", "canada": "ca",
    "japan": "jp", "andorra": "ad", "spain": "es", "norway": "no",
    "sweden": "se", "finland": "fi", "australia": "au", "new zealand": "nz",
    "chile": "cl", "argentina": "ar", "united kingdom": "gb",
}

# Approximate country bounding boxes (lat_min, lat_max, lon_min, lon_max)
COUNTRY_BOUNDS: dict[str, tuple[float, float, float, float]] = {
    "us": (24.0, 72.0, -180.0, -66.0),
    "ca": (41.0, 84.0, -141.0, -52.0),
    "at": (46.3, 49.0, 9.5, 17.2),
    "fr": (41.3, 51.1, -5.1, 9.6),
    "ch": (45.8, 47.8, 5.9, 10.5),
    "it": (35.5, 47.1, 6.6, 18.5),
    "de": (47.3, 55.1, 5.9, 15.0),
    "jp": (24.0, 46.0, 122.9, 153.9),
    "no": (57.9, 71.2, 4.6, 31.1),
    "se": (55.3, 69.1, 11.1, 24.2),
    "fi": (59.8, 70.1, 20.5, 31.6),
    "es": (36.0, 43.8, -9.3, 3.3),
    "ad": (42.4, 42.7, 1.4, 1.8),
    "au": (-44.0, -10.0, 113.0, 154.0),
    "nz": (-47.3, -34.4, 166.4, 178.6),
    "cl": (-56.0, -17.5, -75.6, -66.9),
    "ar": (-55.0, -21.8, -73.6, -53.6),
}


def _coords_in_country(lat: float, lon: float, country_code: str) -> bool:
    """Check if coordinates fall within a country's bounding box."""
    bounds = COUNTRY_BOUNDS.get(country_code)
    if not bounds:
        return True  # No bounds data, accept
    lat_min, lat_max, lon_min, lon_max = bounds
    return lat_min <= lat <= lat_max and lon_min <= lon <= lon_max


async def extract_coordinates(
    resort_name: str,
    country: str,
) -> tuple[float, float] | None:
    """Extract coordinates for a ski resort using Nominatim + Google Geocoding fallback.

    Round 24: Added countrycodes parameter to Nominatim for disambiguation
    (fixes "Alta" returning Iowa/Norway instead of Utah), plus country bounding
    box validation, plus Google Geocoding API fallback.

    Args:
        resort_name: Name of the ski resort
        country: Country where resort is located

    Returns:
        Tuple of (latitude, longitude) or None if not found
    """
    country_code = COUNTRY_CODES.get(country.lower())

    # ---- Nominatim (free, primary) ----
    queries = [
        f"{resort_name} ski area, {country}",
        f"{resort_name} ski resort, {country}",
        f"{resort_name}, {country}",
        f"{resort_name} {country}",
    ]

    async with httpx.AsyncClient(timeout=30) as client:
        for query in queries:
            await asyncio.sleep(1.1)  # Nominatim rate limit

            try:
                params: dict[str, Any] = {
                    "q": query,
                    "format": "json",
                    "limit": 3,  # Get multiple results for validation
                }
                if country_code:
                    params["countrycodes"] = country_code

                response = await client.get(
                    "https://nominatim.openstreetmap.org/search",
                    params=params,
                    headers={"User-Agent": "Snowthere/1.0 (family-ski-directory)"},
                )
                response.raise_for_status()
                data = response.json()

                if data:
                    # Check each result against country bounds
                    for result in data:
                        lat = float(result["lat"])
                        lon = float(result["lon"])
                        if country_code and _coords_in_country(lat, lon, country_code):
                            logger.info(f"[research] Nominatim coords for {resort_name}: ({lat}, {lon})")
                            return (lat, lon)
                    # If no result passed bounds check, use first result anyway
                    lat = float(data[0]["lat"])
                    lon = float(data[0]["lon"])
                    logger.info(f"[research] Nominatim coords for {resort_name} (no bounds match): ({lat}, {lon})")
                    return (lat, lon)

            except (httpx.HTTPError, KeyError, IndexError, ValueError):
                continue

    # ---- Google Geocoding API (fallback) ----
    from ..config import settings
    if settings.google_api_key:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                params = {
                    "address": f"{resort_name}, {country}",
                    "key": settings.google_api_key,
                }
                response = await client.get(
                    "https://maps.googleapis.com/maps/api/geocode/json",
                    params=params,
                )
                response.raise_for_status()
                data = response.json()

                if data.get("status") == "OK" and data.get("results"):
                    location = data["results"][0]["geometry"]["location"]
                    lat = float(location["lat"])
                    lon = float(location["lng"])

                    # Validate against bounds
                    if country_code and not _coords_in_country(lat, lon, country_code):
                        logger.warning(f"[research] Google coords for {resort_name} outside {country} bounds")
                        return None

                    logger.info(f"[research] Google Geocoding coords for {resort_name}: ({lat}, {lon})")
                    return (lat, lon)

        except Exception as e:
            logger.warning(f"[research] Google Geocoding failed for {resort_name}: {e}")

    return None
