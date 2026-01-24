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
from dataclasses import dataclass, asdict
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
            "type": "neural",
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
        "search_lang": "en",
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


async def extract_coordinates(
    resort_name: str,
    country: str,
) -> tuple[float, float] | None:
    """Extract coordinates for a ski resort using Nominatim (OpenStreetMap).

    This is free and requires no API key. Used to improve Google Places
    search accuracy and trail map lookups.

    Uses a fallback strategy with multiple query formats since "ski resort"
    in the query often returns no results.

    Args:
        resort_name: Name of the ski resort
        country: Country where resort is located

    Returns:
        Tuple of (latitude, longitude) or None if not found
    """
    # Try multiple query formats (more specific to less specific)
    queries = [
        f"{resort_name}, {country}",           # Most reliable
        f"{resort_name} {country}",            # No comma
        resort_name,                            # Just the name
        f"{resort_name} ski resort, {country}", # Original (sometimes works)
    ]

    async with httpx.AsyncClient(timeout=30) as client:
        for query in queries:
            # Respect Nominatim rate limit (1 request/second)
            await asyncio.sleep(1.1)

            try:
                response = await client.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={
                        "q": query,
                        "format": "json",
                        "limit": 1,
                    },
                    headers={"User-Agent": "Snowthere/1.0 (family-ski-directory)"},
                )
                response.raise_for_status()
                data = response.json()

                if data:
                    return (float(data[0]["lat"]), float(data[0]["lon"]))

            except (httpx.HTTPError, KeyError, IndexError, ValueError):
                continue

    return None
