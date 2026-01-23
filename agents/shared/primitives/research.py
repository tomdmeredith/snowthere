"""Research primitives for gathering ski resort information.

Uses three complementary search APIs:
- Exa: Semantic search (finding content by meaning)
- Brave: Traditional web search (specific queries, official sites)
- Tavily: AI-powered research synthesis

Design Decision: We use Brave instead of SerpAPI because:
1. User already has BRAVE_API_KEY
2. Simpler API with direct HTTP calls
3. Combined with Exa + Tavily provides comprehensive coverage
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Any

import httpx
from exa_py import Exa
from tavily import TavilyClient

from ..config import settings

logger = logging.getLogger(__name__)


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
) -> list[SearchResult]:
    """
    Semantic search via Exa API.

    Best for: Finding trip reports, blog posts, family ski reviews.
    """
    if not settings.exa_api_key:
        return []

    exa = Exa(api_key=settings.exa_api_key)

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

    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, _search)

    results = []
    for r in response.results:
        results.append(
            SearchResult(
                title=r.title or "",
                url=r.url,
                snippet=r.text[:1500] if r.text else "",  # Increased from 500 for better price extraction
                source="exa",
                score=r.score if hasattr(r, "score") else None,
                published_date=r.published_date if hasattr(r, "published_date") else None,
            )
        )

    return results


async def brave_search(
    query: str,
    num_results: int = 10,
    country: str = "US",
    max_retries: int = 3,
) -> list[SearchResult]:
    """
    Web search via Brave Search API with exponential backoff.

    Best for: Official resort sites, current pricing, news.
    Replaces SerpAPI with a simpler, direct HTTP implementation.

    Rate limiting: Implements exponential backoff on 429 errors.
    """
    if not settings.brave_api_key:
        return []

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
                        logger.error(f"Brave API rate limit exceeded after {max_retries} retries for query: {query[:50]}")
                        return []
                else:
                    logger.error(f"Brave search HTTP error: {e}")
                    return []
            except httpx.HTTPError as e:
                logger.error(f"Brave search error: {e}")
                return []
        else:
            # All retries exhausted
            return []

    results = []
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

    return results


# Alias for backwards compatibility
serp_search = brave_search


async def tavily_search(
    query: str,
    search_depth: str = "advanced",
    max_results: int = 10,
    include_answer: bool = True,
) -> dict[str, Any]:
    """
    Web research via Tavily API.

    Best for: General info, news, comprehensive overviews.
    Returns both search results and an AI-generated answer.
    """
    if not settings.tavily_api_key:
        return {"results": [], "answer": None}

    client = TavilyClient(api_key=settings.tavily_api_key)

    def _search():
        return client.search(
            query,
            search_depth=search_depth,
            max_results=max_results,
            include_answer=include_answer,
        )

    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, _search)

    results = []
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

    return {
        "results": results,
        "answer": response.get("answer"),
    }


async def search_resort_info(
    resort_name: str,
    country: str,
    focus: str = "family",
) -> dict[str, Any]:
    """
    Comprehensive resort search across all providers.

    Combines results from Exa (semantic), Brave (web search), and Tavily (AI research).
    Each tool has different strengths:
    - Exa: Finding relevant content by meaning (trip reports, reviews)
    - Brave: Traditional search for official sites, specific queries
    - Tavily: AI-synthesized research with answer generation

    CRITICAL: Includes dedicated pricing queries to find cost data families need.
    """
    from datetime import datetime
    current_year = datetime.now().year

    queries = {
        "family_reviews": f"{resort_name} {country} family ski trip review kids",
        "official_info": f"{resort_name} ski resort official site lift tickets",
        "ski_school": f"{resort_name} ski school children lessons childcare",
        "lodging": f"{resort_name} family lodging ski-in ski-out hotels",
        # NEW: Dedicated pricing queries
        "lift_prices": f"{resort_name} lift ticket prices {current_year} {current_year + 1}",
        "lodging_rates": f"{resort_name} hotel prices per night winter ski season",
        "ski_school_cost": f"{resort_name} ski school lesson prices children cost",
    }

    # Run all searches in parallel
    tasks = []

    # Exa for family reviews (semantic search excels here)
    tasks.append(exa_search(queries["family_reviews"], num_results=5))

    # Brave for official info (traditional web search)
    tasks.append(brave_search(queries["official_info"], num_results=5))

    # Tavily for ski school info
    tasks.append(tavily_search(queries["ski_school"], max_results=5))

    # Additional Exa for lodging
    tasks.append(exa_search(queries["lodging"], num_results=5))

    # NEW: Pricing-specific searches (CRITICAL for family value)
    tasks.append(brave_search(queries["lift_prices"], num_results=5))
    tasks.append(brave_search(queries["lodging_rates"], num_results=5))
    tasks.append(tavily_search(queries["ski_school_cost"], max_results=3))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Organize results
    organized = {
        "family_reviews": results[0] if not isinstance(results[0], Exception) else [],
        "official_info": results[1] if not isinstance(results[1], Exception) else [],
        "ski_school": results[2] if not isinstance(results[2], Exception) else {"results": []},
        "lodging": results[3] if not isinstance(results[3], Exception) else [],
        # NEW: Pricing categories
        "lift_prices": results[4] if not isinstance(results[4], Exception) else [],
        "lodging_rates": results[5] if not isinstance(results[5], Exception) else [],
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

    # Standard list categories (including new pricing categories)
    list_categories = [
        "family_reviews", "official_info", "lodging",
        "lift_prices", "lodging_rates",  # New pricing categories
    ]
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

    # Handle dict categories (from Tavily - ski_school and ski_school_cost)
    dict_categories = ["ski_school", "ski_school_cost"]
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
