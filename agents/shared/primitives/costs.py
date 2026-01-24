"""Cost acquisition primitives for ski resort pricing data.

Multi-strategy approach to acquire pricing data:
1. Cache (free, instant)
2. Pass Network (free, ~100ms) - if resort is on Epic/Ikon
3. Tavily Search (paid, ~2s) - enhanced queries for pricing
4. Website Scrape (free, ~5s) - if official URL known
5. Claude Extraction (paid, ~3s) - last resort

Design Decision: Price data is critical for family trip planning.
Without costs, families can't compare resorts or budget their trips.
We use multiple strategies to maximize coverage.

Round 5.9.2: Created to address 25.7% price discovery rate from Tavily alone.
"""

import asyncio
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx
from bs4 import BeautifulSoup
from tavily import TavilyClient
import anthropic

from ..config import settings
from ..supabase_client import get_supabase_client
from .system import log_cost

logger = logging.getLogger(__name__)


# Currency mappings by country
COUNTRY_CURRENCIES: dict[str, str] = {
    "austria": "EUR",
    "france": "EUR",
    "italy": "EUR",
    "germany": "EUR",
    "switzerland": "CHF",
    "united states": "USD",
    "usa": "USD",
    "canada": "CAD",
    "japan": "JPY",
    "andorra": "EUR",
    "spain": "EUR",
    "norway": "NOK",
    "sweden": "SEK",
    "finland": "EUR",
    "australia": "AUD",
    "new zealand": "NZD",
    "chile": "CLP",
    "argentina": "ARS",
}

# Approximate USD conversion rates (updated periodically)
USD_RATES: dict[str, float] = {
    "USD": 1.0,
    "EUR": 1.08,  # 1 EUR = 1.08 USD
    "CHF": 1.12,  # 1 CHF = 1.12 USD
    "CAD": 0.74,  # 1 CAD = 0.74 USD
    "JPY": 0.0067,  # 1 JPY = 0.0067 USD
    "NOK": 0.092,
    "SEK": 0.095,
    "AUD": 0.65,
    "NZD": 0.60,
    "CLP": 0.00106,
    "ARS": 0.00115,
    "GBP": 1.27,
}

# Cache TTL
CACHE_TTL_DAYS = 30


@dataclass
class CostResult:
    """Result from cost acquisition attempt."""
    success: bool
    costs: dict[str, Any] = field(default_factory=dict)
    currency: str | None = None
    source: str | None = None  # cache, pass_network, tavily, scrape, claude
    confidence: float = 0.0
    official_website_url: str | None = None
    error: str | None = None


def get_currency_for_country(country: str) -> str:
    """Get default currency for a country."""
    return COUNTRY_CURRENCIES.get(country.lower(), "EUR")


def convert_to_usd(amount: float | None, currency: str) -> float | None:
    """Convert amount to USD using approximate rates."""
    if amount is None:
        return None
    rate = USD_RATES.get(currency.upper(), 1.0)
    return round(amount * rate, 2)


async def get_cached_pricing(resort_name: str, country: str) -> CostResult | None:
    """Check pricing cache for existing valid data.

    Strategy 1: Free, instant, high reliability if cached.
    """
    client = get_supabase_client()

    response = (
        client.table("pricing_cache")
        .select("*")
        .eq("resort_name", resort_name)
        .eq("country", country)
        .limit(1)
        .execute()
    )

    if not response.data:
        return None

    cached = response.data[0]

    # Check if expired
    if cached.get("expires_at"):
        expires = datetime.fromisoformat(cached["expires_at"].replace("Z", "+00:00"))
        if expires < datetime.now(timezone.utc):
            logger.info(f"[costs] Cache expired for {resort_name}")
            return None

    logger.info(f"[costs] Cache HIT for {resort_name}")
    return CostResult(
        success=True,
        costs=cached.get("costs", {}),
        currency=cached.get("currency"),
        source="cache",
        confidence=cached.get("confidence", 0.8),
        official_website_url=cached.get("official_website_url"),
    )


async def cache_pricing_result(
    resort_name: str,
    country: str,
    result: CostResult,
) -> None:
    """Store pricing result in cache."""
    if not result.success or not result.costs:
        return

    client = get_supabase_client()
    expires_at = datetime.now(timezone.utc) + timedelta(days=CACHE_TTL_DAYS)

    data = {
        "resort_name": resort_name,
        "country": country,
        "costs": result.costs,
        "currency": result.currency,
        "source": result.source,
        "confidence": result.confidence,
        "official_website_url": result.official_website_url,
        "expires_at": expires_at.isoformat(),
    }

    # Upsert (insert or update)
    client.table("pricing_cache").upsert(
        data,
        on_conflict="resort_name,country"
    ).execute()

    logger.info(f"[costs] Cached pricing for {resort_name} (source: {result.source})")


async def get_pass_network_pricing(
    resort_name: str,
    country: str,
) -> CostResult:
    """Check if resort is on Epic/Ikon and get network pricing.

    Strategy 2: Free, reliable for pass resorts.
    """
    client = get_supabase_client()

    # Find resort
    resort_response = (
        client.table("resorts")
        .select("id")
        .ilike("name", f"%{resort_name}%")
        .eq("country", country)
        .limit(1)
        .execute()
    )

    if not resort_response.data:
        return CostResult(success=False, error="Resort not found")

    resort_id = resort_response.data[0]["id"]

    # Check for pass associations
    # Note: ski_passes table only has name, type, website_url, purchase_url
    # No adult_price/child_price columns - pass pricing not stored in DB
    pass_response = (
        client.table("resort_passes")
        .select("access_type, ski_passes(name, type)")
        .eq("resort_id", resort_id)
        .execute()
    )

    if not pass_response.data:
        return CostResult(success=False, error="Not on any pass network")

    # We can confirm the resort is on a pass network, but we don't have pass prices
    # in the database. Return pass info for context but no pricing.
    pass_names = []
    for pass_entry in pass_response.data:
        pass_info = pass_entry.get("ski_passes", {})
        if pass_info.get("name"):
            pass_names.append(pass_info["name"])

    # Pass network strategy can't provide pricing since we don't store pass prices
    # Return failure so we fall through to other strategies
    return CostResult(
        success=False,
        error=f"On pass network ({', '.join(pass_names)}) but pass prices not in DB",
    )


async def search_targeted_pricing(
    resort_name: str,
    country: str,
) -> CostResult:
    """Enhanced Tavily search with price-specific queries.

    Strategy 3: Paid (~$0.02), ~2s, 25-40% success rate.
    """
    if not settings.tavily_api_key:
        return CostResult(success=False, error="Tavily API key not configured")

    try:
        client = TavilyClient(api_key=settings.tavily_api_key)

        # Price-focused queries
        queries = [
            f"{resort_name} {country} lift ticket prices 2025 2026",
            f"{resort_name} ski pass daily rates adult child",
            f"{resort_name} accommodation hotels prices per night",
        ]

        all_results = []
        for query in queries:
            response = client.search(
                query=query,
                search_depth="advanced",
                max_results=5,
                include_answer=True,
            )
            all_results.append(response)

            # Log cost
            log_cost("tavily", 0.005, None, {"query": query, "stage": "pricing_search"})

        # Parse results for pricing data
        costs = {}
        currency = get_currency_for_country(country)

        for response in all_results:
            # Check AI answer for prices
            answer = response.get("answer", "")
            if answer:
                prices = parse_prices_from_text(answer, currency)
                costs.update(prices)

            # Check result snippets
            for result in response.get("results", []):
                snippet = result.get("content", "")
                prices = parse_prices_from_text(snippet, currency)
                costs.update(prices)

        if not costs:
            return CostResult(
                success=False,
                error="No prices found in Tavily results",
            )

        return CostResult(
            success=True,
            costs=costs,
            currency=currency,
            source="tavily",
            confidence=0.7,
        )

    except Exception as e:
        logger.error(f"[costs] Tavily search failed: {e}")
        return CostResult(success=False, error=str(e))


def parse_prices_from_text(text: str, default_currency: str = "EUR") -> dict[str, Any]:
    """Extract pricing data from text using regex patterns."""
    costs = {}
    text_lower = text.lower()

    # Currency symbol patterns
    currency_patterns = {
        "USD": [r"\$(\d+(?:\.\d{2})?)", r"(\d+(?:\.\d{2})?)\s*(?:usd|dollars?)"],
        "EUR": [r"€(\d+(?:\.\d{2})?)", r"(\d+(?:\.\d{2})?)\s*(?:eur|euros?)"],
        "CHF": [r"CHF\s*(\d+(?:\.\d{2})?)", r"(\d+(?:\.\d{2})?)\s*(?:chf|francs?)"],
    }

    # Lift ticket patterns
    lift_patterns = [
        r"adult.*?(?:lift|ticket|pass).*?(\d+(?:\.\d{2})?)",
        r"(?:lift|ticket|pass).*?adult.*?(\d+(?:\.\d{2})?)",
        r"adult\s*:?\s*[$€]?(\d+(?:\.\d{2})?)",
        r"(\d+(?:\.\d{2})?)\s*(?:per day|daily|/day).*?adult",
    ]

    child_patterns = [
        r"child.*?(?:lift|ticket|pass).*?(\d+(?:\.\d{2})?)",
        r"(?:lift|ticket|pass).*?child.*?(\d+(?:\.\d{2})?)",
        r"(?:kids?|children?).*?(\d+(?:\.\d{2})?)",
    ]

    # Lodging patterns
    lodging_patterns = [
        r"(?:hotel|accommodation|lodging).*?(\d+(?:\.\d{2})?)\s*(?:per night|/night|nightly)",
        r"(\d+(?:\.\d{2})?)\s*(?:per night|/night).*?(?:hotel|room|stay)",
        r"from\s*[$€CHF]*\s*(\d+(?:\.\d{2})?)\s*(?:per night|/night)",
    ]

    # Try to find lift prices
    for pattern in lift_patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            price = float(match)
            if 20 < price < 500:  # Sanity check for lift tickets
                if "lift_adult_daily" not in costs:
                    costs["lift_adult_daily"] = price
                break

    for pattern in child_patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            price = float(match)
            if price < 300:  # Child tickets should be cheaper
                if "lift_child_daily" not in costs:
                    costs["lift_child_daily"] = price
                break

    # Try to find lodging prices
    for pattern in lodging_patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            price = float(match)
            if 30 < price < 2000:  # Sanity check for lodging
                if "lodging_mid_nightly" not in costs:
                    costs["lodging_mid_nightly"] = price
                break

    return costs


async def find_pricing_page(
    resort_name: str,
    country: str,
    official_website: str | None = None,
) -> str | None:
    """Find the pricing/tickets page URL for a resort."""
    if not official_website:
        # Try to discover official website
        if settings.tavily_api_key:
            try:
                client = TavilyClient(api_key=settings.tavily_api_key)
                response = client.search(
                    query=f"{resort_name} {country} official website ski resort",
                    search_depth="basic",
                    max_results=3,
                )
                log_cost("tavily", 0.003, None, {"stage": "find_website"})

                for result in response.get("results", []):
                    url = result.get("url", "")
                    # Look for likely official domains
                    if any(term in url.lower() for term in ["ski", "resort", "lift", "mountain"]):
                        official_website = url.split("/")[0] + "//" + url.split("/")[2]
                        break
            except Exception as e:
                logger.warning(f"[costs] Failed to find official website: {e}")
                return None

    if not official_website:
        return None

    # Common pricing page paths
    pricing_paths = [
        "/tickets",
        "/prices",
        "/rates",
        "/lift-tickets",
        "/ski-pass",
        "/tarife",  # German
        "/preise",  # German
        "/tarifs",  # French
        "/prezzi",  # Italian
    ]

    async with httpx.AsyncClient(timeout=10.0) as client:
        for path in pricing_paths:
            url = official_website.rstrip("/") + path
            try:
                response = await client.head(url, follow_redirects=True)
                if response.status_code == 200:
                    return url
            except Exception:
                continue

    return official_website  # Fall back to homepage


async def scrape_resort_pricing_page(url: str) -> CostResult:
    """Scrape pricing data from a resort website.

    Strategy 4: Free, ~5s, 60-70% success rate when URL is valid.
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                url,
                follow_redirects=True,
                headers={"User-Agent": "Mozilla/5.0 (compatible; SnowthereBot/1.0)"}
            )
            response.raise_for_status()
            html = response.text

        costs = extract_pricing_from_html(html)

        if not costs:
            return CostResult(
                success=False,
                error="No pricing data found in HTML",
                official_website_url=url,
            )

        # Try to detect currency from page
        currency = "EUR"  # Default
        if "$" in html and "USD" in html.upper():
            currency = "USD"
        elif "CHF" in html or "Franken" in html:
            currency = "CHF"

        return CostResult(
            success=True,
            costs=costs,
            currency=currency,
            source="scrape",
            confidence=0.85,
            official_website_url=url,
        )

    except Exception as e:
        logger.error(f"[costs] Scrape failed for {url}: {e}")
        return CostResult(
            success=False,
            error=str(e),
            official_website_url=url,
        )


def extract_pricing_from_html(html: str) -> dict[str, Any]:
    """Parse pricing tables and structured data from HTML."""
    soup = BeautifulSoup(html, "html.parser")
    costs = {}

    # Look for price tables
    tables = soup.find_all("table")
    for table in tables:
        text = table.get_text().lower()
        if any(term in text for term in ["adult", "erwachsene", "adulte", "price", "preis", "tarif"]):
            # Parse table for prices
            prices = parse_prices_from_text(table.get_text(), "EUR")
            costs.update(prices)

    # Look for JSON-LD structured data
    scripts = soup.find_all("script", type="application/ld+json")
    for script in scripts:
        try:
            import json
            data = json.loads(script.string or "{}")
            if "offers" in data:
                offer = data["offers"]
                if isinstance(offer, list):
                    offer = offer[0] if offer else {}
                if "price" in offer:
                    costs["lift_adult_daily"] = float(offer["price"])
        except Exception:
            pass

    # Look for common price patterns in the HTML
    if not costs:
        text = soup.get_text()
        costs = parse_prices_from_text(text, "EUR")

    return costs


async def extract_pricing_with_claude(
    resort_name: str,
    country: str,
    research_snippets: list[str],
) -> CostResult:
    """Use Claude to extract pricing from research snippets.

    Strategy 5: Paid (~$0.01), ~3s, high accuracy when data exists.
    """
    if not settings.anthropic_api_key:
        return CostResult(success=False, error="Anthropic API key not configured")

    try:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

        # Combine snippets
        combined_text = "\n\n".join(research_snippets[:10])  # Limit to avoid token issues

        prompt = f"""Extract ski resort pricing data from the following text about {resort_name}, {country}.

Text:
{combined_text}

Return ONLY a JSON object with these fields (use null if not found):
{{
    "lift_adult_daily": <number or null>,
    "lift_child_daily": <number or null>,
    "lodging_mid_nightly": <number or null>,
    "currency": "<3-letter currency code>",
    "confidence": <0.0-1.0 based on how clear the data was>
}}

Be conservative - only extract prices you're confident about. Include the currency code (USD, EUR, CHF, etc.)."""

        response = client.messages.create(
            model=settings.default_model,  # Use fast model
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )

        # Log cost
        log_cost("anthropic", 0.01, None, {"stage": "pricing_extraction"})

        # Parse response
        import json
        response_text = response.content[0].text

        # Extract JSON from response
        json_match = re.search(r"\{[^{}]+\}", response_text, re.DOTALL)
        if not json_match:
            return CostResult(success=False, error="No JSON in Claude response")

        data = json.loads(json_match.group())

        costs = {}
        if data.get("lift_adult_daily"):
            costs["lift_adult_daily"] = data["lift_adult_daily"]
        if data.get("lift_child_daily"):
            costs["lift_child_daily"] = data["lift_child_daily"]
        if data.get("lodging_mid_nightly"):
            costs["lodging_mid_nightly"] = data["lodging_mid_nightly"]

        if not costs:
            return CostResult(success=False, error="No prices extracted by Claude")

        return CostResult(
            success=True,
            costs=costs,
            currency=data.get("currency", get_currency_for_country(country)),
            source="claude",
            confidence=data.get("confidence", 0.6),
        )

    except Exception as e:
        logger.error(f"[costs] Claude extraction failed: {e}")
        return CostResult(success=False, error=str(e))


async def acquire_resort_costs(
    resort_name: str,
    country: str,
    official_website: str | None = None,
    research_snippets: list[str] | None = None,
) -> CostResult:
    """Orchestrate multi-strategy cost acquisition.

    Tries strategies in order of cost-effectiveness:
    1. Cache (free, instant)
    2. Pass Network (free, ~100ms)
    3. Tavily Search (paid, ~2s)
    4. Website Scrape (free, ~5s)
    5. Claude Extraction (paid, ~3s)

    Returns first successful result, caches for future use.
    """
    logger.info(f"[costs] Acquiring costs for {resort_name}, {country}")

    # Strategy 1: Check cache
    cached = await get_cached_pricing(resort_name, country)
    if cached and cached.success:
        return cached

    # Strategy 2: Pass network
    pass_result = await get_pass_network_pricing(resort_name, country)
    if pass_result.success:
        await cache_pricing_result(resort_name, country, pass_result)
        return pass_result

    # Strategy 3: Tavily search
    tavily_result = await search_targeted_pricing(resort_name, country)
    if tavily_result.success:
        await cache_pricing_result(resort_name, country, tavily_result)
        return tavily_result

    # Strategy 4: Website scrape
    pricing_url = await find_pricing_page(resort_name, country, official_website)
    if pricing_url:
        scrape_result = await scrape_resort_pricing_page(pricing_url)
        if scrape_result.success:
            await cache_pricing_result(resort_name, country, scrape_result)
            return scrape_result

    # Strategy 5: Claude extraction (if we have snippets)
    if research_snippets:
        claude_result = await extract_pricing_with_claude(
            resort_name, country, research_snippets
        )
        if claude_result.success:
            await cache_pricing_result(resort_name, country, claude_result)
            return claude_result

    # All strategies failed
    logger.warning(f"[costs] All strategies failed for {resort_name}")
    return CostResult(
        success=False,
        error="All cost acquisition strategies failed",
    )


def update_usd_columns(resort_id: str, costs: dict[str, Any], currency: str) -> None:
    """Update USD comparison columns in resort_costs."""
    client = get_supabase_client()

    usd_updates = {}

    if costs.get("lift_adult_daily"):
        usd_updates["lift_adult_daily_usd"] = convert_to_usd(
            costs["lift_adult_daily"], currency
        )

    if costs.get("lodging_mid_nightly"):
        usd_updates["lodging_mid_nightly_usd"] = convert_to_usd(
            costs["lodging_mid_nightly"], currency
        )

    if usd_updates:
        client.table("resort_costs").update(usd_updates).eq("resort_id", resort_id).execute()
        logger.info(f"[costs] Updated USD columns for resort {resort_id}")
