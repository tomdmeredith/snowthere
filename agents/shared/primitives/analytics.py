"""Analytics primitives for SEO performance tracking.

These primitives handle fetching and storing Google Search Console data
for SEO optimization. Following Agent Native principles, these enable
data-driven decisions about content improvement.
"""

import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any

from ..config import settings
from ..supabase_client import get_supabase_client


# =============================================================================
# DATA CLASSES
# =============================================================================


@dataclass
class GSCFetchResult:
    """Result of fetching GSC performance data."""

    success: bool
    rows_fetched: int
    rows_stored: int
    date_range: tuple[str, str]
    error: str | None = None


@dataclass
class UnderperformingPage:
    """A page with high impressions but low CTR."""

    page_url: str
    impressions: int
    clicks: int
    ctr: float
    position: float
    date: str
    improvement_potential: str  # "high", "medium", "low"


# =============================================================================
# GOOGLE SEARCH CONSOLE API
# =============================================================================


async def fetch_gsc_performance(days: int = 7) -> GSCFetchResult:
    """Fetch Google Search Console performance data and store in database.

    Uses the Search Console API to get page-level and query-level metrics.
    Data is stored in the gsc_performance table for analysis.

    Args:
        days: Number of days of data to fetch (max 16 months back)

    Returns:
        GSCFetchResult with fetch status and counts
    """
    # Check if credentials are configured
    if not settings.gsc_credentials_json or not settings.gsc_property_url:
        return GSCFetchResult(
            success=False,
            rows_fetched=0,
            rows_stored=0,
            date_range=("", ""),
            error="GSC credentials not configured (GSC_CREDENTIALS_JSON and GSC_PROPERTY_URL required)",
        )

    try:
        # Import Google API client
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except ImportError:
        return GSCFetchResult(
            success=False,
            rows_fetched=0,
            rows_stored=0,
            date_range=("", ""),
            error="Google API client not installed. Run: pip install google-api-python-client google-auth",
        )

    try:
        # Parse credentials from JSON string
        credentials_info = json.loads(settings.gsc_credentials_json)
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=["https://www.googleapis.com/auth/webmasters.readonly"],
        )

        # Build the Search Console service
        service = build("searchconsole", "v1", credentials=credentials)

        # Calculate date range
        end_date = date.today() - timedelta(days=3)  # GSC data is ~3 days delayed
        start_date = end_date - timedelta(days=days)

        # Fetch page-level data
        request = {
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
            "dimensions": ["page", "query", "date"],
            "rowLimit": 25000,  # Max allowed
            "dataState": "all",
        }

        response = (
            service.searchanalytics()
            .query(siteUrl=settings.gsc_property_url, body=request)
            .execute()
        )

        rows = response.get("rows", [])

        if not rows:
            return GSCFetchResult(
                success=True,
                rows_fetched=0,
                rows_stored=0,
                date_range=(start_date.isoformat(), end_date.isoformat()),
                error="No data returned from GSC (this may be normal for new sites)",
            )

        # Store in database
        rows_stored = await _store_gsc_data(rows)

        return GSCFetchResult(
            success=True,
            rows_fetched=len(rows),
            rows_stored=rows_stored,
            date_range=(start_date.isoformat(), end_date.isoformat()),
        )

    except json.JSONDecodeError as e:
        return GSCFetchResult(
            success=False,
            rows_fetched=0,
            rows_stored=0,
            date_range=("", ""),
            error=f"Invalid GSC_CREDENTIALS_JSON format: {e}",
        )
    except Exception as e:
        return GSCFetchResult(
            success=False,
            rows_fetched=0,
            rows_stored=0,
            date_range=("", ""),
            error=f"GSC API error: {e}",
        )


async def _store_gsc_data(rows: list[dict]) -> int:
    """Store GSC API response rows in database.

    Args:
        rows: List of row dicts from GSC API response

    Returns:
        Number of rows stored
    """
    client = get_supabase_client()
    stored = 0

    # Transform and batch insert
    batch = []
    for row in rows:
        keys = row.get("keys", [])
        if len(keys) < 3:
            continue

        page_url = keys[0]
        query = keys[1]
        date_str = keys[2]

        record = {
            "page_url": page_url,
            "query": query,
            "date": date_str,
            "impressions": row.get("impressions", 0),
            "clicks": row.get("clicks", 0),
            "ctr": row.get("ctr", 0),
            "position": row.get("position", 0),
            "fetched_at": datetime.utcnow().isoformat(),
        }
        batch.append(record)

        # Insert in batches of 500
        if len(batch) >= 500:
            try:
                client.table("gsc_performance").upsert(
                    batch,
                    on_conflict="page_url,query,date",
                ).execute()
                stored += len(batch)
                batch = []
            except Exception as e:
                print(f"Error storing GSC batch: {e}")

    # Insert remaining
    if batch:
        try:
            client.table("gsc_performance").upsert(
                batch,
                on_conflict="page_url,query,date",
            ).execute()
            stored += len(batch)
        except Exception as e:
            print(f"Error storing final GSC batch: {e}")

    return stored


# =============================================================================
# ANALYSIS QUERIES
# =============================================================================


def get_underperforming_pages(
    min_impressions: int = 100,
    max_ctr: float = 0.02,
    limit: int = 20,
) -> list[UnderperformingPage]:
    """Find pages with high impressions but low CTR.

    These are prime candidates for title/description optimization.

    Args:
        min_impressions: Minimum impressions to consider (filters noise)
        max_ctr: Maximum CTR to consider "underperforming" (0.02 = 2%)
        limit: Maximum results to return

    Returns:
        List of underperforming pages sorted by improvement potential
    """
    client = get_supabase_client()

    # Get recent data (last 7 days aggregated)
    week_ago = (date.today() - timedelta(days=7)).isoformat()

    response = (
        client.table("gsc_performance")
        .select("page_url, impressions, clicks, ctr, position, date")
        .gte("date", week_ago)
        .gte("impressions", min_impressions)
        .lte("ctr", max_ctr)
        .is_("query", "null")  # Page-level aggregates only
        .order("impressions", desc=True)
        .limit(limit)
        .execute()
    )

    results = []
    for row in response.data or []:
        # Calculate improvement potential
        impressions = row.get("impressions", 0)
        ctr = row.get("ctr", 0)
        position = row.get("position", 50)

        # High impressions + low CTR + decent position = high potential
        if impressions > 500 and position < 10:
            potential = "high"
        elif impressions > 200 and position < 20:
            potential = "medium"
        else:
            potential = "low"

        results.append(
            UnderperformingPage(
                page_url=row.get("page_url", ""),
                impressions=impressions,
                clicks=row.get("clicks", 0),
                ctr=ctr,
                position=position,
                date=row.get("date", ""),
                improvement_potential=potential,
            )
        )

    return results


def get_top_performing_pages(limit: int = 10) -> list[dict]:
    """Get pages with highest traffic for the past week.

    Useful for understanding what content is working.

    Args:
        limit: Maximum results to return

    Returns:
        List of top performing pages with metrics
    """
    client = get_supabase_client()

    week_ago = (date.today() - timedelta(days=7)).isoformat()

    response = (
        client.table("gsc_performance")
        .select("page_url, impressions, clicks, ctr, position")
        .gte("date", week_ago)
        .is_("query", "null")  # Page-level aggregates
        .order("clicks", desc=True)
        .limit(limit)
        .execute()
    )

    return response.data or []


def get_top_queries(limit: int = 20) -> list[dict]:
    """Get top search queries driving traffic.

    Useful for understanding user search intent.

    Args:
        limit: Maximum results to return

    Returns:
        List of top queries with metrics
    """
    client = get_supabase_client()

    week_ago = (date.today() - timedelta(days=7)).isoformat()

    response = (
        client.table("gsc_performance")
        .select("query, impressions, clicks, ctr, position")
        .gte("date", week_ago)
        .not_.is_("query", "null")
        .order("impressions", desc=True)
        .limit(limit)
        .execute()
    )

    return response.data or []


def get_page_performance_trend(page_url: str, days: int = 30) -> list[dict]:
    """Get daily performance trend for a specific page.

    Args:
        page_url: The page URL to analyze
        days: Number of days of history

    Returns:
        List of daily metrics ordered by date
    """
    client = get_supabase_client()

    start_date = (date.today() - timedelta(days=days)).isoformat()

    response = (
        client.table("gsc_performance")
        .select("date, impressions, clicks, ctr, position")
        .eq("page_url", page_url)
        .is_("query", "null")  # Page-level data
        .gte("date", start_date)
        .order("date", desc=False)
        .execute()
    )

    return response.data or []


def get_gsc_summary(days: int = 7) -> dict[str, Any]:
    """Get a summary of GSC performance for logging/alerts.

    Args:
        days: Number of days to summarize

    Returns:
        Summary dict with totals and averages
    """
    client = get_supabase_client()

    start_date = (date.today() - timedelta(days=days)).isoformat()

    # Get page-level totals
    response = (
        client.table("gsc_performance")
        .select("impressions, clicks, ctr, position")
        .gte("date", start_date)
        .is_("query", "null")
        .execute()
    )

    rows = response.data or []

    if not rows:
        return {
            "period_days": days,
            "total_impressions": 0,
            "total_clicks": 0,
            "avg_ctr": 0,
            "avg_position": 0,
            "pages_tracked": 0,
        }

    total_impressions = sum(r.get("impressions", 0) for r in rows)
    total_clicks = sum(r.get("clicks", 0) for r in rows)
    avg_ctr = total_clicks / total_impressions if total_impressions > 0 else 0
    avg_position = sum(r.get("position", 0) for r in rows) / len(rows) if rows else 0

    return {
        "period_days": days,
        "total_impressions": total_impressions,
        "total_clicks": total_clicks,
        "avg_ctr": round(avg_ctr, 4),
        "avg_position": round(avg_position, 1),
        "pages_tracked": len(set(r.get("page_url") for r in rows)),
    }
