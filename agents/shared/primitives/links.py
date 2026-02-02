"""Outbound links primitives with UTM tracking."""

from urllib.parse import urlencode, urlparse, urlunparse, parse_qs
from typing import Any

from ..supabase_client import get_supabase_client


def add_utm_params(url: str, resort_slug: str, category: str, campaign: str = "resort_page") -> str:
    """
    Add UTM tracking parameters to an outbound URL.

    Args:
        url: The original URL
        resort_slug: Resort identifier for utm_campaign
        category: Link category for utm_content
        campaign: UTM medium/campaign context (default: resort_page, use "in_content" for entity links)

    Returns:
        URL with UTM parameters appended
    """
    utm_params = {
        "utm_source": "snowthere",
        "utm_medium": campaign,
        "utm_campaign": resort_slug,
        "utm_content": category,
    }

    # Parse the URL
    parsed = urlparse(url)

    # Get existing query params
    existing_params = parse_qs(parsed.query)

    # Merge with UTM params (don't overwrite existing UTM params)
    for key, value in utm_params.items():
        if key not in existing_params:
            existing_params[key] = [value]

    # Flatten the params dict
    flat_params = {k: v[0] if len(v) == 1 else v for k, v in existing_params.items()}

    # Rebuild the URL
    new_query = urlencode(flat_params, doseq=True)
    new_url = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment
    ))

    return new_url


async def get_resort_links(resort_id: str) -> list[dict[str, Any]]:
    """
    Get all outbound links for a resort.

    Args:
        resort_id: UUID of the resort

    Returns:
        List of link dictionaries
    """
    supabase = get_supabase_client()

    result = supabase.table("resort_links").select("*").eq(
        "resort_id", resort_id
    ).order("display_order").execute()

    return result.data or []


async def add_resort_link(
    resort_id: str,
    title: str,
    url: str,
    category: str,
    description: str | None = None,
    is_affiliate: bool = False,
    affiliate_url: str | None = None,
    display_order: int = 0,
) -> dict[str, Any]:
    """
    Add an outbound link for a resort.

    Args:
        resort_id: UUID of the resort
        title: Display title for the link
        url: Target URL
        category: Link category (official, lodging, dining, activity, transport, rental)
        description: Optional description
        is_affiliate: Whether this is an affiliate link
        affiliate_url: Optional affiliate URL to use instead
        display_order: Order for display (lower = first)

    Returns:
        Created link record
    """
    supabase = get_supabase_client()

    link_data = {
        "resort_id": resort_id,
        "title": title,
        "url": url,
        "category": category,
        "description": description,
        "is_affiliate": is_affiliate,
        "affiliate_url": affiliate_url,
        "display_order": display_order,
    }

    result = supabase.table("resort_links").insert(link_data).execute()

    return result.data[0] if result.data else {}


async def update_resort_link(link_id: str, **updates) -> dict[str, Any]:
    """
    Update an existing resort link.

    Args:
        link_id: UUID of the link to update
        **updates: Fields to update

    Returns:
        Updated link record
    """
    supabase = get_supabase_client()

    result = supabase.table("resort_links").update(updates).eq(
        "id", link_id
    ).execute()

    return result.data[0] if result.data else {}


async def delete_resort_link(link_id: str) -> bool:
    """
    Delete a resort link.

    Args:
        link_id: UUID of the link to delete

    Returns:
        True if deleted successfully
    """
    supabase = get_supabase_client()

    result = supabase.table("resort_links").delete().eq(
        "id", link_id
    ).execute()

    return len(result.data) > 0 if result.data else False


async def get_links_by_category(resort_id: str, category: str) -> list[dict[str, Any]]:
    """
    Get links for a resort filtered by category.

    Args:
        resort_id: UUID of the resort
        category: Category to filter by

    Returns:
        List of matching links
    """
    supabase = get_supabase_client()

    result = supabase.table("resort_links").select("*").eq(
        "resort_id", resort_id
    ).eq(
        "category", category
    ).order("display_order").execute()

    return result.data or []


# Category display configuration
LINK_CATEGORIES = {
    "official": {"label": "Official Website", "emoji": "🌐"},
    "lodging": {"label": "Where to Stay", "emoji": "🏨"},
    "dining": {"label": "Restaurants", "emoji": "🍽️"},
    "activity": {"label": "Activities", "emoji": "🎿"},
    "transport": {"label": "Getting There", "emoji": "✈️"},
    "rental": {"label": "Equipment Rental", "emoji": "🎿"},
    "ski_school": {"label": "Ski School", "emoji": "👨‍🏫"},
    "childcare": {"label": "Childcare", "emoji": "👶"},
}


def get_category_config(category: str) -> dict[str, str]:
    """Get display configuration for a link category."""
    return LINK_CATEGORIES.get(category, {"label": category.title(), "emoji": "🔗"})
