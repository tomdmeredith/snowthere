"""Ski quality calendar generation primitive.

Generates monthly snow quality, crowd level, and family recommendation
data for ski resorts. Uses Claude Haiku for cost-effective generation
(~$0.003 per resort).

The frontend displays this as:
- SnowConditionsChart: animated bar chart with crowd dots
- SkiCalendar: month cards (mobile) + table (desktop)

Schema: ski_quality_calendar table with per-month rows.
"""

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any

import anthropic

from ..config import settings
from .database import update_resort_calendar
from .system import log_cost

logger = logging.getLogger(__name__)


# Ski season months by hemisphere
NORTHERN_MONTHS = [12, 1, 2, 3, 4]
SOUTHERN_MONTHS = [6, 7, 8, 9, 10]

# Countries in the southern hemisphere
SOUTHERN_COUNTRIES = {"chile", "argentina", "australia", "new zealand"}


@dataclass
class CalendarMonth:
    """Generated data for one month."""
    month: int
    snow_quality_score: int  # 1-5
    crowd_level: str  # low, medium, high
    family_recommendation: int  # 1-10
    notes: str


@dataclass
class CalendarResult:
    """Result of calendar generation."""
    success: bool
    months: list[CalendarMonth] = field(default_factory=list)
    error: str | None = None


def _get_season_months(country: str) -> list[int]:
    """Get ski season months for a country."""
    if country.lower() in SOUTHERN_COUNTRIES:
        return SOUTHERN_MONTHS
    return NORTHERN_MONTHS


async def generate_ski_calendar(
    resort_name: str,
    country: str,
    research_data: dict[str, Any] | None = None,
) -> CalendarResult:
    """Generate monthly ski quality calendar for a resort.

    Uses Claude Haiku to assess snow conditions, crowd patterns, and
    family suitability for each month of the ski season based on
    resort characteristics and general knowledge.

    Args:
        resort_name: Name of the ski resort
        country: Country where resort is located
        research_data: Optional research data for context

    Returns:
        CalendarResult with monthly data

    Cost: ~$0.003 per call (Claude Haiku)
    """
    if not settings.anthropic_api_key:
        return CalendarResult(success=False, error="Anthropic API key not configured")

    season_months = _get_season_months(country)
    month_names = {
        1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December",
    }

    # Build context from research if available
    context_parts = []
    if research_data:
        if research_data.get("family_metrics"):
            fm = research_data["family_metrics"]
            if fm.get("kid_friendly_terrain_pct"):
                context_parts.append(f"Kid-friendly terrain: {fm['kid_friendly_terrain_pct']}%")
            if fm.get("best_age_min") and fm.get("best_age_max"):
                context_parts.append(f"Best for ages {fm['best_age_min']}-{fm['best_age_max']}")
        if research_data.get("region"):
            context_parts.append(f"Region: {research_data['region']}")

    context_str = "\n".join(context_parts) if context_parts else "No additional context."
    months_str = ", ".join(month_names[m] for m in season_months)

    try:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

        prompt = f"""Generate ski quality calendar data for {resort_name}, {country}.

Months to cover: {months_str}

Additional context:
{context_str}

For each month, provide:
1. snow_quality_score (1-5): Based on typical snowfall, base depth, and conditions
   - 5: Deep powder, excellent base, reliable coverage
   - 4: Good snow, solid base
   - 3: Adequate, may need snowmaking support
   - 2: Thin cover, limited terrain
   - 1: Season start/end, minimal snow

2. crowd_level: "low", "medium", or "high"
   - Consider: school holidays (Christmas, February half-term, Easter), weekends, local holidays
   - Christmas/New Year weeks are always "high"
   - February is often "high" (European school holidays)
   - January (post-holidays) and late March/April are often "low" to "medium"

3. family_recommendation (1-10): Composite score weighing snow, crowds, value, and weather
   - 9-10: Perfect conditions + low crowds + good value
   - 7-8: Great conditions or great value
   - 5-6: Decent but compromised (great snow but packed, or quiet but thin)
   - 3-4: Below average for families

4. notes: One sentence of practical advice for that month (max 20 words)

Return ONLY a JSON array:
[
  {{"month": {season_months[0]}, "snow_quality_score": 3, "crowd_level": "high", "family_recommendation": 6, "notes": "Holiday crowds peak but early season snow can be thin."}},
  ...
]"""

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}],
        )

        log_cost("anthropic", 0.003, None, {
            "stage": "calendar_generation",
            "resort": resort_name,
        })

        response_text = response.content[0].text.strip()

        # Extract JSON array
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if not json_match:
            return CalendarResult(success=False, error="No JSON array in response")

        data = json.loads(json_match.group())

        # Validate and build CalendarMonth objects
        months = []
        for item in data:
            month = item.get("month")
            if month not in season_months:
                continue

            snow = item.get("snow_quality_score", 3)
            snow = max(1, min(5, int(snow)))

            crowd = item.get("crowd_level", "medium")
            if crowd not in ("low", "medium", "high"):
                crowd = "medium"

            family = item.get("family_recommendation", 5)
            family = max(1, min(10, int(family)))

            notes = str(item.get("notes", ""))[:200]

            months.append(CalendarMonth(
                month=month,
                snow_quality_score=snow,
                crowd_level=crowd,
                family_recommendation=family,
                notes=notes,
            ))

        if not months:
            return CalendarResult(success=False, error="No valid months in response")

        logger.info(f"[calendar] Generated {len(months)} months for {resort_name}")
        return CalendarResult(success=True, months=months)

    except Exception as e:
        logger.error(f"[calendar] Generation failed for {resort_name}: {e}")
        return CalendarResult(success=False, error=str(e))


async def generate_and_store_calendar(
    resort_id: str,
    resort_name: str,
    country: str,
    research_data: dict[str, Any] | None = None,
) -> CalendarResult:
    """Generate calendar data and store it in the database.

    Convenience function that combines generation + storage.

    Args:
        resort_id: UUID of the resort
        resort_name: Name of the ski resort
        country: Country where resort is located
        research_data: Optional research data for context

    Returns:
        CalendarResult with generated data
    """
    result = await generate_ski_calendar(resort_name, country, research_data)

    if not result.success:
        return result

    for month_data in result.months:
        update_resort_calendar(resort_id, month_data.month, {
            "snow_quality_score": month_data.snow_quality_score,
            "crowd_level": month_data.crowd_level,
            "family_recommendation": month_data.family_recommendation,
            "notes": month_data.notes,
        })

    logger.info(f"[calendar] Stored {len(result.months)} months for {resort_name} ({resort_id[:8]})")
    return result
