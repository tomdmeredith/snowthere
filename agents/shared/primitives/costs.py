"""Cost acquisition primitives for ski resort pricing data.

Multi-strategy approach to acquire pricing data:
1. Cache (free, instant)
2. Exa: Discover official pricing page URL (~$0.006)
3. Scrape + Claude Haiku: Read the pricing page (~$0.003)
4. Tavily: Corroborate via cross-validation (~$0.007)
5. Claude Extraction from research snippets (last resort, ~$0.01)

Round 24: Complete redesign. Previous system used regex on Tavily AI text,
which grabbed wrong numbers ($23 for Mount Bachelor, $29 for Sunday River).
New approach: find the official pricing page, have Claude read it, validate
against country-specific ranges.

Design Decision: Price data is critical for family trip planning.
Without costs, families can't compare resorts or budget their trips.
"""

import asyncio
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
import anthropic

from ..config import settings
from ..supabase_client import get_supabase_client
from .system import log_cost

logger = logging.getLogger(__name__)


# =============================================================================
# Country-Specific Validation Ranges (local currency)
# =============================================================================

LIFT_TICKET_RANGES: dict[str, tuple[float, float]] = {
    "united states": (60, 300),
    "usa": (60, 300),
    "canada": (70, 250),
    "austria": (30, 80),
    "france": (30, 75),
    "switzerland": (45, 100),
    "italy": (25, 70),
    "germany": (25, 65),
    "andorra": (25, 60),
    "spain": (25, 60),
    "japan": (3000, 8000),
    "norway": (300, 800),
    "sweden": (300, 700),
    "finland": (25, 65),
    "australia": (80, 200),
    "new zealand": (80, 180),
    "chile": (20000, 60000),
    "argentina": (10000, 50000),
}

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
    "EUR": 1.08,
    "CHF": 1.12,
    "CAD": 0.74,
    "JPY": 0.0067,
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


# =============================================================================
# Data Structures
# =============================================================================


@dataclass
class PriceValidation:
    """Result of price validation against country ranges."""
    valid: bool
    field: str
    value: float
    country: str
    expected_range: tuple[float, float] | None = None
    severity: str = "ok"  # "ok", "warning", "hard_reject"
    message: str = ""


@dataclass
class CostResult:
    """Result from cost acquisition attempt."""
    success: bool
    costs: dict[str, Any] = field(default_factory=dict)
    currency: str | None = None
    source: str | None = None
    confidence: float = 0.0
    official_website_url: str | None = None
    source_urls: list[str] = field(default_factory=list)
    validation_notes: list[str] = field(default_factory=list)
    error: str | None = None


# =============================================================================
# Validation
# =============================================================================


def validate_price(
    field_name: str,
    value: float,
    country: str,
) -> PriceValidation:
    """Validate a price against country-specific ranges.

    Hard reject: below 50% of min or above 150% of max.
    Warning: outside normal range but not absurd.
    """
    country_lower = country.lower()
    expected = LIFT_TICKET_RANGES.get(country_lower)

    if not expected:
        return PriceValidation(
            valid=True, field=field_name, value=value, country=country,
            message=f"No range data for {country}, accepting price",
        )

    range_min, range_max = expected

    # Hard reject: clearly wrong
    if value < range_min * 0.5:
        return PriceValidation(
            valid=False, field=field_name, value=value, country=country,
            expected_range=expected, severity="hard_reject",
            message=f"{field_name}={value} far below minimum {range_min} for {country}",
        )
    if value > range_max * 1.5:
        return PriceValidation(
            valid=False, field=field_name, value=value, country=country,
            expected_range=expected, severity="hard_reject",
            message=f"{field_name}={value} far above maximum {range_max} for {country}",
        )

    # Warning: borderline
    if value < range_min or value > range_max:
        return PriceValidation(
            valid=True, field=field_name, value=value, country=country,
            expected_range=expected, severity="warning",
            message=f"{field_name}={value} outside typical range {range_min}-{range_max} for {country}",
        )

    return PriceValidation(
        valid=True, field=field_name, value=value, country=country,
        expected_range=expected,
    )


def validate_costs(costs: dict[str, Any], country: str) -> tuple[dict[str, Any], list[str]]:
    """Validate all prices in a costs dict. Returns (validated_costs, notes)."""
    validated = {}
    notes = []

    for field_name, value in costs.items():
        if not isinstance(value, (int, float)) or value <= 0:
            continue

        if field_name.startswith("lift_"):
            result = validate_price(field_name, value, country)
        elif field_name.startswith("lodging_"):
            # Lodging has wider ranges, skip country validation
            validated[field_name] = value
            continue
        else:
            validated[field_name] = value
            continue

        if result.severity == "hard_reject":
            notes.append(f"REJECTED: {result.message}")
            logger.warning(f"[costs] {result.message}")
        else:
            validated[field_name] = value
            if result.severity == "warning":
                notes.append(f"WARNING: {result.message}")

    return validated, notes


# =============================================================================
# Utility Functions
# =============================================================================


def get_currency_for_country(country: str) -> str:
    """Get default currency for a country."""
    return COUNTRY_CURRENCIES.get(country.lower(), "EUR")


def convert_to_usd(amount: float | None, currency: str) -> float | None:
    """Convert amount to USD using approximate rates."""
    if amount is None:
        return None
    rate = USD_RATES.get(currency.upper(), 1.0)
    return round(amount * rate, 2)


# =============================================================================
# Strategy 1: Cache
# =============================================================================


async def get_cached_pricing(resort_name: str, country: str) -> CostResult | None:
    """Check pricing cache for existing valid data. Free, instant."""
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
        source_urls=cached.get("source_urls") or [],
        validation_notes=cached.get("validation_notes") or [],
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

    # Include provenance columns if migration 044 has been applied
    try:
        data["source_urls"] = result.source_urls
        data["validation_notes"] = result.validation_notes
        client.table("pricing_cache").upsert(
            data,
            on_conflict="resort_name,country"
        ).execute()
    except Exception:
        # Fall back without provenance columns
        data.pop("source_urls", None)
        data.pop("validation_notes", None)
        client.table("pricing_cache").upsert(
            data,
            on_conflict="resort_name,country"
        ).execute()

    logger.info(f"[costs] Cached pricing for {resort_name} (source: {result.source})")


# =============================================================================
# Strategy 2: Exa Official Page Discovery
# =============================================================================


def _score_pricing_url(url: str, resort_name: str) -> int:
    """Score a URL for likelihood of being the official pricing page."""
    score = 0
    url_lower = url.lower()
    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    # Resort name in domain (strong signal)
    resort_words = resort_name.lower().replace("-", " ").replace("'", "").split()
    domain_matches = sum(1 for w in resort_words if w in domain and len(w) > 3)
    score += domain_matches * 3

    # Pricing-related paths
    pricing_paths = ["/tickets", "/prices", "/rates", "/lift-tickets", "/pricing",
                     "/tarife", "/preise", "/tarifs", "/prezzi", "/ski-pass",
                     "/passes", "/lift-pass"]
    if any(p in url_lower for p in pricing_paths):
        score += 2

    # Penalize aggregators
    aggregators = ["tripadvisor", "expedia", "booking.com", "kayak", "skyscanner",
                   "liftopia", "epic", "ikonpass", "onthesnow", "skiresort.info",
                   "snow-forecast", "j2ski", "wikipedia"]
    if any(a in domain for a in aggregators):
        score -= 5

    return score


async def discover_official_pricing_url(
    resort_name: str,
    country: str,
) -> tuple[str | None, str | None]:
    """Use Exa to find the resort's official pricing page.

    Returns (pricing_page_url, official_domain) or (None, None).
    """
    if not settings.exa_api_key:
        return None, None

    try:
        from exa_py import Exa
        exa = Exa(api_key=settings.exa_api_key)

        results = exa.search(
            f"{resort_name} {country} lift ticket prices",
            num_results=5,
        )

        log_cost("exa", 0.006, None, {
            "stage": "pricing_discovery",
            "resort": resort_name,
        })

        if not results.results:
            return None, None

        # Score and rank URLs
        scored = []
        for r in results.results:
            url = r.url
            score = _score_pricing_url(url, resort_name)
            scored.append((score, url))

        scored.sort(reverse=True)

        # Pick best URL
        best_score, best_url = scored[0]

        if best_score < 0:
            # All results are aggregators, return None
            logger.info(f"[costs] Exa found no official pricing URLs for {resort_name}")
            return None, None

        parsed = urlparse(best_url)
        official_domain = f"{parsed.scheme}://{parsed.netloc}"

        logger.info(f"[costs] Exa discovered pricing URL: {best_url} (score: {best_score})")
        return best_url, official_domain

    except Exception as e:
        logger.error(f"[costs] Exa pricing discovery failed: {e}")
        return None, None


# =============================================================================
# Strategy 3: Scrape + Claude Interpretation
# =============================================================================


def _clean_html_for_pricing(html: str) -> str:
    """Strip navigation, scripts, footers — keep pricing-relevant text."""
    soup = BeautifulSoup(html, "html.parser")

    # Remove noise
    for tag in soup.find_all(["script", "style", "nav", "footer", "header", "iframe"]):
        tag.decompose()

    # Check JSON-LD first (highest reliability)
    json_ld_prices = []
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "{}")
            if "offers" in data:
                json_ld_prices.append(json.dumps(data["offers"], indent=2))
        except Exception:
            pass

    if json_ld_prices:
        return "JSON-LD STRUCTURED DATA:\n" + "\n".join(json_ld_prices)

    # Get text content, limited to reasonable size
    text = soup.get_text(separator="\n", strip=True)
    # Limit to first 4000 chars (pricing is usually near top)
    return text[:4000]


async def scrape_and_interpret_pricing(
    url: str,
    resort_name: str,
    country: str,
) -> CostResult:
    """Scrape a pricing page and have Claude Haiku interpret it.

    Strategy 3: ~$0.003, high accuracy when URL is correct.
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                url,
                follow_redirects=True,
                headers={"User-Agent": "Mozilla/5.0 (compatible; SnowthereBot/1.0)"},
            )
            response.raise_for_status()
            html = response.text

        cleaned_text = _clean_html_for_pricing(html)
        is_json_ld = cleaned_text.startswith("JSON-LD")

        if not cleaned_text.strip():
            return CostResult(success=False, error="Empty page content", official_website_url=url)

    except Exception as e:
        logger.error(f"[costs] Scrape failed for {url}: {e}")
        return CostResult(success=False, error=f"Scrape failed: {e}", official_website_url=url)

    # Claude Haiku interprets the page content
    if not settings.anthropic_api_key:
        return CostResult(success=False, error="Anthropic API key not configured")

    try:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        currency = get_currency_for_country(country)

        prompt = f"""Extract lift ticket pricing from this {resort_name} ({country}) page content.

I need the STANDARD ADULT 1-DAY WINDOW PRICE (walk-up rate, not multi-day, not promo, not online-only discounts).
Also extract the standard child 1-day price if available.

Page content:
{cleaned_text}

Return ONLY a JSON object:
{{
    "lift_adult_daily": <number or null>,
    "lift_child_daily": <number or null>,
    "lodging_mid_nightly": <number or null>,
    "currency": "{currency}",
    "confidence": <0.0-1.0>,
    "source_description": "<what you found, e.g. '2025/26 season rates table'>"
}}

Be conservative. Only extract prices you're confident about. If the page shows ranges, use the high-season price."""

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )

        log_cost("anthropic", 0.003, None, {"stage": "pricing_interpretation", "resort": resort_name})

        response_text = response.content[0].text
        json_match = re.search(r"\{[^{}]+\}", response_text, re.DOTALL)
        if not json_match:
            return CostResult(success=False, error="No JSON in Claude response", official_website_url=url)

        data = json.loads(json_match.group())

        costs = {}
        if data.get("lift_adult_daily"):
            costs["lift_adult_daily"] = float(data["lift_adult_daily"])
        if data.get("lift_child_daily"):
            costs["lift_child_daily"] = float(data["lift_child_daily"])
        if data.get("lodging_mid_nightly"):
            costs["lodging_mid_nightly"] = float(data["lodging_mid_nightly"])

        if not costs:
            return CostResult(success=False, error="No prices extracted", official_website_url=url)

        # Validate against country ranges
        validated_costs, notes = validate_costs(costs, country)
        if not validated_costs:
            return CostResult(
                success=False,
                error=f"All prices failed validation: {'; '.join(notes)}",
                official_website_url=url,
                validation_notes=notes,
            )

        confidence = 0.95 if is_json_ld else float(data.get("confidence", 0.85))

        return CostResult(
            success=True,
            costs=validated_costs,
            currency=data.get("currency", currency),
            source="exa_scrape",
            confidence=confidence,
            official_website_url=url,
            source_urls=[url],
            validation_notes=notes,
        )

    except Exception as e:
        logger.error(f"[costs] Claude interpretation failed: {e}")
        return CostResult(success=False, error=str(e), official_website_url=url)


# =============================================================================
# Strategy 4: Tavily Corroboration
# =============================================================================


async def corroborate_pricing(
    resort_name: str,
    country: str,
    known_price: float | None = None,
) -> CostResult:
    """Single Tavily search + Claude Haiku interpretation for corroboration.

    If known_price provided: confirms or rejects it.
    If standalone: extracts and validates.
    """
    if not settings.tavily_api_key:
        return CostResult(success=False, error="Tavily API key not configured")

    try:
        from tavily import TavilyClient
        tavily = TavilyClient(api_key=settings.tavily_api_key)

        response = tavily.search(
            query=f"{resort_name} {country} adult lift ticket price 2025 2026 season",
            search_depth="advanced",
            max_results=5,
            include_answer=True,
        )

        log_cost("tavily", 0.007, None, {"stage": "pricing_corroboration", "resort": resort_name})

        # Collect all text
        snippets = []
        source_urls = []
        if response.get("answer"):
            snippets.append(f"AI Summary: {response['answer']}")
        for r in response.get("results", []):
            if r.get("content"):
                snippets.append(r["content"][:500])
            if r.get("url"):
                source_urls.append(r["url"])

        combined = "\n\n".join(snippets[:8])

        if not combined.strip():
            return CostResult(success=False, error="No Tavily results")

        # Claude Haiku interprets
        if not settings.anthropic_api_key:
            return CostResult(success=False, error="Anthropic API key not configured")

        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        currency = get_currency_for_country(country)

        corroboration_note = ""
        if known_price:
            corroboration_note = f"\nI already have a price of {currency} {known_price} from the official website. Does this search data confirm or contradict it?"

        prompt = f"""Extract lift ticket pricing for {resort_name} ({country}) from these search results.
{corroboration_note}

Search results:
{combined}

Return ONLY a JSON object:
{{
    "lift_adult_daily": <number or null>,
    "lift_child_daily": <number or null>,
    "currency": "{currency}",
    "confidence": <0.0-1.0>,
    "confirms_known_price": <true/false/null if no known price>
}}

Extract the STANDARD ADULT 1-DAY WINDOW PRICE. Not multi-day, not promo, not online-only."""

        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )

        log_cost("anthropic", 0.002, None, {"stage": "pricing_corroboration_llm"})

        response_text = resp.content[0].text
        json_match = re.search(r"\{[^{}]+\}", response_text, re.DOTALL)
        if not json_match:
            return CostResult(success=False, error="No JSON in corroboration response")

        data = json.loads(json_match.group())

        costs = {}
        if data.get("lift_adult_daily"):
            costs["lift_adult_daily"] = float(data["lift_adult_daily"])
        if data.get("lift_child_daily"):
            costs["lift_child_daily"] = float(data["lift_child_daily"])

        if not costs:
            return CostResult(success=False, error="No prices from corroboration")

        validated_costs, notes = validate_costs(costs, country)
        if not validated_costs:
            return CostResult(
                success=False, error=f"Corroboration prices failed validation: {'; '.join(notes)}",
                validation_notes=notes,
            )

        return CostResult(
            success=True,
            costs=validated_costs,
            currency=data.get("currency", currency),
            source="tavily_corroboration",
            confidence=float(data.get("confidence", 0.7)),
            source_urls=source_urls[:3],
            validation_notes=notes,
        )

    except Exception as e:
        logger.error(f"[costs] Corroboration failed: {e}")
        return CostResult(success=False, error=str(e))


# =============================================================================
# Strategy 5: Claude Extraction from Research Snippets (last resort)
# =============================================================================


async def extract_pricing_with_claude(
    resort_name: str,
    country: str,
    research_snippets: list[str],
) -> CostResult:
    """Use Claude to extract pricing from research snippets. Last resort."""
    if not settings.anthropic_api_key:
        return CostResult(success=False, error="Anthropic API key not configured")

    try:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        combined_text = "\n\n".join(research_snippets[:10])
        currency = get_currency_for_country(country)

        prompt = f"""Extract ski resort pricing data from the following text about {resort_name}, {country}.

Text:
{combined_text}

Return ONLY a JSON object with these fields (use null if not found):
{{
    "lift_adult_daily": <number or null>,
    "lift_child_daily": <number or null>,
    "lodging_mid_nightly": <number or null>,
    "currency": "{currency}",
    "confidence": <0.0-1.0 based on how clear the data was>
}}

Extract the STANDARD ADULT 1-DAY WINDOW PRICE. Not multi-day, not promo, not online-only.
Be conservative - only extract prices you're confident about."""

        response = client.messages.create(
            model=settings.default_model,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )

        log_cost("anthropic", 0.01, None, {"stage": "pricing_extraction"})

        response_text = response.content[0].text
        json_match = re.search(r"\{[^{}]+\}", response_text, re.DOTALL)
        if not json_match:
            return CostResult(success=False, error="No JSON in Claude response")

        data = json.loads(json_match.group())

        costs = {}
        if data.get("lift_adult_daily"):
            costs["lift_adult_daily"] = float(data["lift_adult_daily"])
        if data.get("lift_child_daily"):
            costs["lift_child_daily"] = float(data["lift_child_daily"])
        if data.get("lodging_mid_nightly"):
            costs["lodging_mid_nightly"] = float(data["lodging_mid_nightly"])

        if not costs:
            return CostResult(success=False, error="No prices extracted by Claude")

        validated_costs, notes = validate_costs(costs, country)
        if not validated_costs:
            return CostResult(
                success=False, error=f"Claude prices failed validation: {'; '.join(notes)}",
                validation_notes=notes,
            )

        return CostResult(
            success=True,
            costs=validated_costs,
            currency=data.get("currency", currency),
            source="claude",
            confidence=float(data.get("confidence", 0.6)),
            validation_notes=notes,
        )

    except Exception as e:
        logger.error(f"[costs] Claude extraction failed: {e}")
        return CostResult(success=False, error=str(e))


# =============================================================================
# Pass Network Check (kept for context, not pricing)
# =============================================================================


async def get_pass_network_pricing(
    resort_name: str,
    country: str,
) -> CostResult:
    """Check if resort is on Epic/Ikon. Currently can't provide pricing."""
    client = get_supabase_client()

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

    pass_response = (
        client.table("resort_passes")
        .select("access_type, ski_passes(name, type)")
        .eq("resort_id", resort_id)
        .execute()
    )

    if not pass_response.data:
        return CostResult(success=False, error="Not on any pass network")

    pass_names = []
    for pass_entry in pass_response.data:
        pass_info = pass_entry.get("ski_passes", {})
        if pass_info.get("name"):
            pass_names.append(pass_info["name"])

    return CostResult(
        success=False,
        error=f"On pass network ({', '.join(pass_names)}) but pass prices not in DB",
    )


# =============================================================================
# Main Orchestrator
# =============================================================================


async def acquire_resort_costs(
    resort_name: str,
    country: str,
    official_website: str | None = None,
    research_snippets: list[str] | None = None,
) -> CostResult:
    """Orchestrate multi-strategy cost acquisition.

    New strategy order (Round 24):
    1. Cache (free, instant)
    2. Exa: Find official pricing page URL
    3. Scrape + Claude Haiku: Read the page
    4. Tavily: Corroborate (cross-validate, not primary)
    5. Claude extraction from research snippets (last resort)

    Returns first successful result, caches for future use.
    """
    logger.info(f"[costs] Acquiring costs for {resort_name}, {country}")

    # Strategy 1: Check cache
    cached = await get_cached_pricing(resort_name, country)
    if cached and cached.success:
        return cached

    # Strategy 2+3: Exa discover → Scrape + Claude interpret
    pricing_url, official_domain = await discover_official_pricing_url(resort_name, country)
    if pricing_url:
        scrape_result = await scrape_and_interpret_pricing(pricing_url, resort_name, country)
        if scrape_result.success:
            # Optional: corroborate the price we found
            known_adult = scrape_result.costs.get("lift_adult_daily")
            if known_adult:
                corr = await corroborate_pricing(resort_name, country, known_price=known_adult)
                if corr.success and corr.costs.get("lift_adult_daily"):
                    corr_price = corr.costs["lift_adult_daily"]
                    # If corroboration differs by >30%, flag but keep official
                    diff_pct = abs(corr_price - known_adult) / known_adult
                    if diff_pct > 0.3:
                        scrape_result.validation_notes.append(
                            f"Corroboration price ({corr_price}) differs {diff_pct:.0%} from official ({known_adult})"
                        )
                        scrape_result.confidence = min(scrape_result.confidence, 0.7)
                    else:
                        scrape_result.confidence = min(scrape_result.confidence + 0.05, 1.0)
                        scrape_result.validation_notes.append("Corroborated by Tavily search")
                    scrape_result.source_urls.extend(corr.source_urls)

            await cache_pricing_result(resort_name, country, scrape_result)
            return scrape_result

    # Strategy 4: Tavily standalone (if Exa didn't find anything)
    tavily_result = await corroborate_pricing(resort_name, country)
    if tavily_result.success:
        tavily_result.source = "tavily"
        await cache_pricing_result(resort_name, country, tavily_result)
        return tavily_result

    # Strategy 5: Claude extraction from research snippets
    if research_snippets:
        claude_result = await extract_pricing_with_claude(
            resort_name, country, research_snippets
        )
        if claude_result.success:
            await cache_pricing_result(resort_name, country, claude_result)
            return claude_result

    logger.warning(f"[costs] All strategies failed for {resort_name}")
    return CostResult(
        success=False,
        error="All cost acquisition strategies failed",
    )


# =============================================================================
# USD Column Updates
# =============================================================================


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


# =============================================================================
# Legacy Compatibility (kept for existing callers)
# =============================================================================

# These are still imported by __init__.py — keep the names but they now
# delegate to the new system or are kept for backward compatibility.

def parse_prices_from_text(text: str, default_currency: str = "EUR") -> dict[str, Any]:
    """Legacy regex price extraction. Kept for backward compatibility but
    no longer used in the primary acquisition flow."""
    costs = {}
    text_lower = text.lower()

    lift_patterns = [
        r"adult.*?(?:lift|ticket|pass).*?(\d+(?:\.\d{2})?)",
        r"(?:lift|ticket|pass).*?adult.*?(\d+(?:\.\d{2})?)",
        r"adult\s*:?\s*[$€]?(\d+(?:\.\d{2})?)",
    ]

    for pattern in lift_patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            price = float(match)
            if 20 < price < 500:
                if "lift_adult_daily" not in costs:
                    costs["lift_adult_daily"] = price
                break

    return costs


def extract_pricing_from_html(html: str) -> dict[str, Any]:
    """Legacy HTML extraction. Kept for backward compatibility."""
    soup = BeautifulSoup(html, "html.parser")
    costs = {}

    scripts = soup.find_all("script", type="application/ld+json")
    for script in scripts:
        try:
            data = json.loads(script.string or "{}")
            if "offers" in data:
                offer = data["offers"]
                if isinstance(offer, list):
                    offer = offer[0] if offer else {}
                if "price" in offer:
                    costs["lift_adult_daily"] = float(offer["price"])
        except Exception:
            pass

    if not costs:
        text = soup.get_text()
        costs = parse_prices_from_text(text, "EUR")

    return costs


async def search_targeted_pricing(resort_name: str, country: str) -> CostResult:
    """Legacy Tavily search. Now delegates to corroborate_pricing."""
    return await corroborate_pricing(resort_name, country)


async def find_pricing_page(
    resort_name: str,
    country: str,
    official_website: str | None = None,
) -> str | None:
    """Legacy pricing page finder. Now delegates to Exa discovery."""
    url, _ = await discover_official_pricing_url(resort_name, country)
    return url


async def scrape_resort_pricing_page(url: str) -> CostResult:
    """Legacy scrape. Kept for backward compatibility."""
    return await scrape_and_interpret_pricing(url, "Unknown", "Unknown")
