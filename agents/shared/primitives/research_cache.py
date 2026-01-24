"""Research cache primitives for storing and retrieving search results.

Enables:
- Avoiding redundant API calls (cost savings)
- Tracking which sources were used per resort
- Foundation for citation tracking
"""

import json
import logging
from dataclasses import asdict
from datetime import datetime, timedelta
from typing import Any

from ..supabase_client import get_supabase_client

logger = logging.getLogger(__name__)


# Default TTL for different query types (days)
CACHE_TTL = {
    "lift_prices": 30,      # Prices change seasonally
    "lodging_rates": 30,    # Prices change seasonally
    "ski_school_cost": 30,  # Prices change seasonally
    "official_info": 90,    # Official sites update less frequently
    "family_reviews": 180,  # Reviews stay relevant longer
    "ski_school": 90,
    "lodging": 90,
    "default": 60,
}


def get_cache_ttl(query_type: str) -> int:
    """Get TTL in days for a query type."""
    return CACHE_TTL.get(query_type, CACHE_TTL["default"])


def get_cached_results(
    resort_name: str,
    country: str,
    query_type: str,
    api_source: str,
) -> dict[str, Any] | None:
    """Get cached search results if valid.

    Args:
        resort_name: Name of the resort
        country: Country of the resort
        query_type: Type of query (family_reviews, lift_prices, etc.)
        api_source: API that produced results (exa, brave, tavily)

    Returns:
        Cached entry dict if valid, None if not found or expired
    """
    try:
        supabase = get_supabase_client()

        result = supabase.table("research_cache")\
            .select("*")\
            .eq("resort_name", resort_name)\
            .eq("country", country)\
            .eq("query_type", query_type)\
            .eq("api_source", api_source)\
            .gt("expires_at", datetime.utcnow().isoformat())\
            .single()\
            .execute()

        if result.data:
            # Update use count
            supabase.table("research_cache")\
                .update({
                    "use_count": result.data["use_count"] + 1,
                    "last_used_at": datetime.utcnow().isoformat(),
                })\
                .eq("id", result.data["id"])\
                .execute()

            logger.info(f"Cache HIT: {resort_name} {query_type} {api_source}")
            return result.data

    except Exception as e:
        # Log but don't fail - cache misses are fine
        logger.debug(f"Cache lookup failed (will fetch fresh): {e}")

    return None


def cache_results(
    resort_name: str,
    country: str,
    query_type: str,
    query_text: str,
    api_source: str,
    results: list[dict[str, Any]],
    latency_ms: int | None = None,
    ai_answer: str | None = None,
    error: str | None = None,
) -> bool:
    """Store search results in cache.

    Args:
        resort_name: Name of the resort
        country: Country of the resort
        query_type: Type of query
        query_text: Actual query string
        api_source: API that produced results
        results: List of search result dicts
        latency_ms: API latency in milliseconds
        ai_answer: Tavily's AI-generated answer (if applicable)
        error: Error message if fetch failed

    Returns:
        True if cached successfully
    """
    try:
        supabase = get_supabase_client()

        ttl_days = get_cache_ttl(query_type)
        expires_at = datetime.utcnow() + timedelta(days=ttl_days)

        data = {
            "resort_name": resort_name,
            "country": country,
            "query_type": query_type,
            "query_text": query_text,
            "api_source": api_source,
            "results": results,
            "result_count": len(results),
            "latency_ms": latency_ms,
            "ai_answer": ai_answer,
            "error": error,
            "fetched_at": datetime.utcnow().isoformat(),
            "expires_at": expires_at.isoformat(),
            "use_count": 0,
        }

        # Upsert (update if exists, insert if not)
        supabase.table("research_cache")\
            .upsert(data, on_conflict="resort_name,country,query_type,api_source")\
            .execute()

        logger.info(f"Cached: {resort_name} {query_type} {api_source} ({len(results)} results, expires {expires_at.date()})")
        return True

    except Exception as e:
        logger.warning(f"Failed to cache results: {e}")
        return False


def store_resort_sources(
    resort_id: str,
    sources: list[dict[str, Any]],
) -> int:
    """Store research sources for a resort.

    Called after content generation to record which sources were used.

    Args:
        resort_id: UUID of the resort
        sources: List of source dicts with url, title, snippet, api_source, query_type

    Returns:
        Number of sources stored
    """
    try:
        supabase = get_supabase_client()

        stored = 0
        for source in sources:
            try:
                data = {
                    "resort_id": resort_id,
                    "url": source.get("url"),
                    "title": source.get("title"),
                    "snippet": source.get("snippet", "")[:1000],  # Limit snippet size
                    "api_source": source.get("source") or source.get("api_source"),
                    "query_type": source.get("category") or source.get("query_type"),
                    "relevance_score": source.get("score"),
                }

                supabase.table("resort_research_sources")\
                    .upsert(data, on_conflict="resort_id,url")\
                    .execute()
                stored += 1

            except Exception as e:
                logger.debug(f"Skipped source {source.get('url')}: {e}")

        logger.info(f"Stored {stored}/{len(sources)} sources for resort {resort_id}")
        return stored

    except Exception as e:
        logger.warning(f"Failed to store resort sources: {e}")
        return 0


def mark_sources_cited(
    resort_id: str,
    cited_urls: list[str],
    section: str,
) -> int:
    """Mark sources as cited in content generation.

    Args:
        resort_id: UUID of the resort
        cited_urls: List of URLs that were cited
        section: Which section cited them (e.g., "quick_take", "lift_tickets")

    Returns:
        Number of sources marked
    """
    try:
        supabase = get_supabase_client()

        marked = 0
        for url in cited_urls:
            try:
                # Get current cited_in_sections
                result = supabase.table("resort_research_sources")\
                    .select("cited_in_sections")\
                    .eq("resort_id", resort_id)\
                    .eq("url", url)\
                    .single()\
                    .execute()

                if result.data:
                    current_sections = result.data.get("cited_in_sections") or []
                    if section not in current_sections:
                        current_sections.append(section)

                    supabase.table("resort_research_sources")\
                        .update({
                            "was_cited": True,
                            "cited_in_sections": current_sections,
                        })\
                        .eq("resort_id", resort_id)\
                        .eq("url", url)\
                        .execute()
                    marked += 1

            except Exception:
                pass

        return marked

    except Exception as e:
        logger.warning(f"Failed to mark cited sources: {e}")
        return 0


def get_cache_stats() -> dict[str, Any]:
    """Get cache statistics.

    Returns:
        Dict with cache stats by API and query type
    """
    try:
        supabase = get_supabase_client()

        # Total entries
        total_result = supabase.table("research_cache")\
            .select("id", count="exact")\
            .execute()

        # Valid (non-expired) entries
        valid_result = supabase.table("research_cache")\
            .select("id", count="exact")\
            .gt("expires_at", datetime.utcnow().isoformat())\
            .execute()

        # By API
        by_api = {}
        for api in ["exa", "brave", "tavily"]:
            api_result = supabase.table("research_cache")\
                .select("id", count="exact")\
                .eq("api_source", api)\
                .execute()
            by_api[api] = api_result.count or 0

        return {
            "total_entries": total_result.count or 0,
            "valid_entries": valid_result.count or 0,
            "by_api": by_api,
        }

    except Exception as e:
        logger.warning(f"Failed to get cache stats: {e}")
        return {"error": str(e)}


def clear_expired_cache() -> int:
    """Clear expired cache entries.

    Returns:
        Number of entries deleted
    """
    try:
        supabase = get_supabase_client()

        result = supabase.table("research_cache")\
            .delete()\
            .lt("expires_at", datetime.utcnow().isoformat())\
            .execute()

        deleted = len(result.data) if result.data else 0
        logger.info(f"Cleared {deleted} expired cache entries")
        return deleted

    except Exception as e:
        logger.warning(f"Failed to clear expired cache: {e}")
        return 0
