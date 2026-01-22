"""
Discovery Primitives - Finding new resort opportunities.

Identifies high-value content opportunities through:
- Search demand analysis (what are people searching for?)
- Competitive gap analysis (what's poorly covered elsewhere?)
- Coverage completeness (what passes/regions are we missing?)
- Seasonal/trending opportunities (what's hot right now?)

Uses DataForSEO for keyword data and Exa for semantic trending.
"""

import asyncio
import base64
import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

import httpx

from shared.config import settings
from shared.supabase_client import get_supabase_client


class DiscoverySource(str, Enum):
    """Source of the discovery signal."""
    KEYWORD_RESEARCH = "keyword_research"
    COVERAGE_GAP = "coverage_gap"
    TRENDING = "trending"
    PASS_NETWORK = "pass_network"
    MANUAL = "manual"
    EXPLORATION = "exploration"  # Random discovery for diversity


class CompetitiveGap(str, Enum):
    """How well competitors cover this resort."""
    NONE = "none"  # No competitors have content
    WEAK = "weak"  # Competitors have thin content
    MODERATE = "moderate"  # Competitors have decent content
    STRONG = "strong"  # Competitors have comprehensive content


class CandidateStatus(str, Enum):
    """Status of a discovery candidate."""
    PENDING = "pending"  # Awaiting processing
    QUEUED = "queued"  # Added to content queue
    RESEARCHED = "researched"  # Research complete
    REJECTED = "rejected"  # Not worth pursuing
    PUBLISHED = "published"  # Content live


@dataclass
class DiscoverySignal:
    """A signal indicating potential content opportunity."""
    source: DiscoverySource
    strength: float  # 0-1
    data: dict = field(default_factory=dict)
    reasoning: str = ""


@dataclass
class DiscoveryCandidate:
    """A potential resort to research and create content for."""
    resort_name: str
    country: str
    region: Optional[str] = None
    opportunity_score: float = 0.0
    search_volume_monthly: Optional[int] = None
    competitive_gap: CompetitiveGap = CompetitiveGap.MODERATE
    pass_networks: list[str] = field(default_factory=list)
    signals: list[DiscoverySignal] = field(default_factory=list)
    reasoning: str = ""
    status: CandidateStatus = CandidateStatus.PENDING
    discovered_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def total_signal_strength(self) -> float:
        """Sum of all signal strengths."""
        return sum(s.strength for s in self.signals)


@dataclass
class DiscoveryResult:
    """Result of a discovery run."""
    success: bool
    candidates: list[DiscoveryCandidate] = field(default_factory=list)
    mode: str = ""
    cost: float = 0.0
    error: Optional[str] = None
    metadata: dict = field(default_factory=dict)


# =============================================================================
# DataForSEO Integration
# =============================================================================

async def get_keyword_data(
    keywords: list[str],
    location_code: int = 2840,  # USA
    language_code: str = "en",
) -> list[dict]:
    """
    Get search volume and competition data from DataForSEO.

    Args:
        keywords: List of keywords to analyze
        location_code: DataForSEO location code (2840=USA, 2826=UK, etc.)
        language_code: Language code

    Returns:
        List of keyword data dicts with volume, competition, etc.
    """
    if not settings.dataforseo_login or not settings.dataforseo_password:
        return []

    try:
        auth = base64.b64encode(
            f"{settings.dataforseo_login}:{settings.dataforseo_password}".encode()
        ).decode()

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.dataforseo.com/v3/keywords_data/google_ads/search_volume/live",
                headers={
                    "Authorization": f"Basic {auth}",
                    "Content-Type": "application/json",
                },
                json=[{
                    "keywords": keywords,
                    "location_code": location_code,
                    "language_code": language_code,
                }],
            )

            if response.status_code != 200:
                return []

            data = response.json()

            if data.get("status_code") != 20000:
                return []

            results = []
            tasks = data.get("tasks", [])
            for task in tasks:
                task_result = task.get("result", [])
                for item in task_result:
                    results.append({
                        "keyword": item.get("keyword"),
                        "search_volume": item.get("search_volume"),
                        "competition": item.get("competition"),
                        "competition_index": item.get("competition_index"),
                        "cpc": item.get("cpc"),
                        "monthly_searches": item.get("monthly_searches", []),
                    })

            return results

    except Exception as e:
        print(f"DataForSEO error: {e}")
        return []


async def get_keyword_suggestions(
    seed_keyword: str,
    location_code: int = 2840,
    limit: int = 50,
) -> list[dict]:
    """
    Get keyword suggestions/related keywords from DataForSEO.

    Args:
        seed_keyword: Starting keyword
        location_code: DataForSEO location code
        limit: Max suggestions to return

    Returns:
        List of related keyword data
    """
    if not settings.dataforseo_login or not settings.dataforseo_password:
        return []

    try:
        auth = base64.b64encode(
            f"{settings.dataforseo_login}:{settings.dataforseo_password}".encode()
        ).decode()

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.dataforseo.com/v3/keywords_data/google_ads/keywords_for_keywords/live",
                headers={
                    "Authorization": f"Basic {auth}",
                    "Content-Type": "application/json",
                },
                json=[{
                    "keywords": [seed_keyword],
                    "location_code": location_code,
                    "language_code": "en",
                }],
            )

            if response.status_code != 200:
                return []

            data = response.json()

            if data.get("status_code") != 20000:
                return []

            results = []
            tasks = data.get("tasks", [])
            for task in tasks:
                task_result = task.get("result", [])
                for item in task_result[:limit]:
                    results.append({
                        "keyword": item.get("keyword"),
                        "search_volume": item.get("search_volume"),
                        "competition": item.get("competition"),
                    })

            return results

    except Exception as e:
        print(f"DataForSEO suggestions error: {e}")
        return []


# =============================================================================
# Exa Trending Integration
# =============================================================================

async def search_trending_ski_topics(
    days_back: int = 7,
    num_results: int = 20,
) -> list[dict]:
    """
    Search Exa for trending ski and family travel topics.

    Args:
        days_back: How many days back to search
        num_results: Number of results

    Returns:
        List of trending topic data
    """
    if not settings.exa_api_key:
        return []

    try:
        from exa_py import Exa

        exa = Exa(api_key=settings.exa_api_key)

        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)

        # Search for family ski content
        response = exa.search(
            query="family ski resort vacation tips kids",
            num_results=num_results,
            start_published_date=start_date.strftime("%Y-%m-%d"),
            end_published_date=end_date.strftime("%Y-%m-%d"),
            use_autoprompt=True,
        )

        results = []
        for r in response.results:
            results.append({
                "title": r.title,
                "url": r.url,
                "published_date": r.published_date,
                "score": r.score,
            })

        return results

    except Exception as e:
        print(f"Exa trending error: {e}")
        return []


async def extract_resort_mentions(
    content_results: list[dict],
) -> list[str]:
    """
    Extract ski resort names mentioned in trending content.

    Uses Claude to identify resort names from titles/URLs.

    Args:
        content_results: Results from Exa search

    Returns:
        List of resort names mentioned
    """
    if not content_results:
        return []

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

        # Build content summary
        content_text = "\n".join([
            f"- {r.get('title', '')} ({r.get('url', '')})"
            for r in content_results[:20]
        ])

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": f"""Extract any ski resort names mentioned in these article titles/URLs.

Content:
{content_text}

Return a JSON array of resort names only. If no resorts are mentioned, return empty array.
Example: ["Vail", "Park City", "Zermatt"]"""
            }],
        )

        import json
        text = response.content[0].text.strip()
        if text.startswith("["):
            return json.loads(text)
        return []

    except Exception as e:
        print(f"Resort extraction error: {e}")
        return []


# =============================================================================
# Coverage Gap Analysis
# =============================================================================

async def get_covered_resorts() -> set[str]:
    """
    Get set of resorts we already have content for.

    Returns:
        Set of (resort_name, country) tuples
    """
    try:
        supabase = get_supabase_client()
        result = supabase.table("resorts").select("name, country").execute()

        covered = set()
        for r in result.data:
            covered.add((r["name"].lower(), r["country"].lower()))

        return covered

    except Exception as e:
        print(f"Error getting covered resorts: {e}")
        return set()


async def get_pass_network_resorts(pass_name: str) -> list[dict]:
    """
    Get all resorts on a specific ski pass network.

    Args:
        pass_name: Name of the pass (e.g., "Epic", "Ikon")

    Returns:
        List of resort info dicts
    """
    # Known pass networks (could be moved to database)
    PASS_NETWORKS = {
        "epic": [
            {"name": "Vail", "country": "USA", "region": "Colorado"},
            {"name": "Park City", "country": "USA", "region": "Utah"},
            {"name": "Whistler Blackcomb", "country": "Canada", "region": "British Columbia"},
            {"name": "Verbier", "country": "Switzerland", "region": "Valais"},
            {"name": "Les 3 Vallées", "country": "France", "region": "Savoie"},
            {"name": "Hakuba Valley", "country": "Japan", "region": "Nagano"},
            {"name": "Perisher", "country": "Australia", "region": "NSW"},
            {"name": "Breckenridge", "country": "USA", "region": "Colorado"},
            {"name": "Keystone", "country": "USA", "region": "Colorado"},
            {"name": "Heavenly", "country": "USA", "region": "California"},
            {"name": "Northstar", "country": "USA", "region": "California"},
            {"name": "Kirkwood", "country": "USA", "region": "California"},
        ],
        "ikon": [
            {"name": "Aspen Snowmass", "country": "USA", "region": "Colorado"},
            {"name": "Steamboat", "country": "USA", "region": "Colorado"},
            {"name": "Winter Park", "country": "USA", "region": "Colorado"},
            {"name": "Big Sky", "country": "USA", "region": "Montana"},
            {"name": "Jackson Hole", "country": "USA", "region": "Wyoming"},
            {"name": "Deer Valley", "country": "USA", "region": "Utah"},
            {"name": "Alta", "country": "USA", "region": "Utah"},
            {"name": "Snowbird", "country": "USA", "region": "Utah"},
            {"name": "Mammoth Mountain", "country": "USA", "region": "California"},
            {"name": "Squaw Valley", "country": "USA", "region": "California"},
            {"name": "Chamonix", "country": "France", "region": "Haute-Savoie"},
            {"name": "Zermatt", "country": "Switzerland", "region": "Valais"},
            {"name": "St. Moritz", "country": "Switzerland", "region": "Graubünden"},
            {"name": "Niseko", "country": "Japan", "region": "Hokkaido"},
        ],
    }

    return PASS_NETWORKS.get(pass_name.lower(), [])


async def find_pass_coverage_gaps() -> list[DiscoveryCandidate]:
    """
    Find resorts on major pass networks that we don't have content for.

    Returns:
        List of discovery candidates from pass gaps
    """
    covered = await get_covered_resorts()
    candidates = []

    for pass_name in ["epic", "ikon"]:
        resorts = await get_pass_network_resorts(pass_name)

        for resort in resorts:
            key = (resort["name"].lower(), resort["country"].lower())
            if key not in covered:
                candidate = DiscoveryCandidate(
                    resort_name=resort["name"],
                    country=resort["country"],
                    region=resort.get("region"),
                    pass_networks=[pass_name.title()],
                    competitive_gap=CompetitiveGap.MODERATE,
                    signals=[
                        DiscoverySignal(
                            source=DiscoverySource.PASS_NETWORK,
                            strength=0.7,
                            data={"pass": pass_name},
                            reasoning=f"Part of {pass_name.title()} Pass network",
                        )
                    ],
                    reasoning=f"Gap in {pass_name.title()} Pass coverage",
                )
                candidates.append(candidate)

    return candidates


async def find_region_coverage_gaps(
    country: str,
    min_resorts_expected: int = 5,
) -> list[DiscoveryCandidate]:
    """
    Find popular ski regions where we have limited coverage.

    Args:
        country: Country to analyze
        min_resorts_expected: Expected minimum resorts per popular region

    Returns:
        List of candidates from region gaps
    """
    # Known popular ski regions
    POPULAR_REGIONS = {
        "austria": ["Tyrol", "Salzburg", "Vorarlberg", "Styria"],
        "switzerland": ["Valais", "Graubünden", "Bern", "Central Switzerland"],
        "france": ["Savoie", "Haute-Savoie", "Isère", "Hautes-Alpes"],
        "italy": ["South Tyrol", "Trentino", "Aosta Valley", "Lombardy"],
        "usa": ["Colorado", "Utah", "California", "Vermont", "Wyoming", "Montana"],
        "canada": ["British Columbia", "Alberta", "Quebec"],
        "japan": ["Hokkaido", "Nagano", "Niigata"],
    }

    regions = POPULAR_REGIONS.get(country.lower(), [])
    if not regions:
        return []

    try:
        supabase = get_supabase_client()
        result = supabase.table("resorts")\
            .select("region")\
            .ilike("country", country)\
            .execute()

        # Count resorts per region
        region_counts = {}
        for r in result.data:
            region = r.get("region", "Unknown")
            region_counts[region] = region_counts.get(region, 0) + 1

        candidates = []
        for region in regions:
            count = region_counts.get(region, 0)
            if count < min_resorts_expected:
                candidates.append(DiscoveryCandidate(
                    resort_name=f"{region} region resorts",
                    country=country,
                    region=region,
                    competitive_gap=CompetitiveGap.WEAK,
                    signals=[
                        DiscoverySignal(
                            source=DiscoverySource.COVERAGE_GAP,
                            strength=0.6,
                            data={"current_count": count, "expected": min_resorts_expected},
                            reasoning=f"Only {count}/{min_resorts_expected} resorts covered in {region}",
                        )
                    ],
                    reasoning=f"Coverage gap in {region}, {country}",
                ))

        return candidates

    except Exception as e:
        print(f"Region gap analysis error: {e}")
        return []


# =============================================================================
# Opportunity Scoring
# =============================================================================

def calculate_opportunity_score(candidate: DiscoveryCandidate) -> float:
    """
    Calculate overall opportunity score for a candidate.

    Weights:
    - search_demand: 0.25 (search volume exists)
    - competitive_gap: 0.30 (others don't cover well)
    - value_potential: 0.20 (fits "value skiing" angle)
    - coverage_completeness: 0.15 (fills gap in our DB)
    - exploration_bonus: 0.10 (random discovery factor)

    Returns:
        Score from 0.0 to 1.0
    """
    weights = {
        "search_demand": 0.25,
        "competitive_gap": 0.30,
        "value_potential": 0.20,
        "coverage_completeness": 0.15,
        "exploration_bonus": 0.10,
    }

    scores = {}

    # Search demand score
    if candidate.search_volume_monthly:
        if candidate.search_volume_monthly > 10000:
            scores["search_demand"] = 1.0
        elif candidate.search_volume_monthly > 1000:
            scores["search_demand"] = 0.7
        elif candidate.search_volume_monthly > 100:
            scores["search_demand"] = 0.4
        else:
            scores["search_demand"] = 0.2
    else:
        scores["search_demand"] = 0.3  # Unknown = moderate

    # Competitive gap score
    gap_scores = {
        CompetitiveGap.NONE: 1.0,
        CompetitiveGap.WEAK: 0.8,
        CompetitiveGap.MODERATE: 0.5,
        CompetitiveGap.STRONG: 0.2,
    }
    scores["competitive_gap"] = gap_scores.get(candidate.competitive_gap, 0.5)

    # Value potential (European resorts score higher for "value skiing" angle)
    value_countries = ["austria", "switzerland", "france", "italy", "japan", "canada"]
    if candidate.country.lower() in value_countries:
        scores["value_potential"] = 0.8
    else:
        scores["value_potential"] = 0.5

    # Coverage completeness (pass networks score higher)
    if candidate.pass_networks:
        scores["coverage_completeness"] = 0.9
    elif any(s.source == DiscoverySource.COVERAGE_GAP for s in candidate.signals):
        scores["coverage_completeness"] = 0.7
    else:
        scores["coverage_completeness"] = 0.4

    # Exploration bonus (add randomness to prevent echo chamber)
    if any(s.source == DiscoverySource.EXPLORATION for s in candidate.signals):
        scores["exploration_bonus"] = 1.0
    else:
        scores["exploration_bonus"] = random.uniform(0.3, 0.7)

    # Calculate weighted score
    total = sum(scores[k] * weights[k] for k in weights)

    return min(total, 1.0)


# =============================================================================
# Database Operations
# =============================================================================

async def save_discovery_candidate(candidate: DiscoveryCandidate) -> Optional[str]:
    """
    Save a discovery candidate to the database.

    Args:
        candidate: Candidate to save

    Returns:
        Candidate ID or None
    """
    try:
        supabase = get_supabase_client()

        result = supabase.table("discovery_candidates").insert({
            "resort_name": candidate.resort_name,
            "country": candidate.country,
            "region": candidate.region,
            "opportunity_score": candidate.opportunity_score,
            "search_volume_monthly": candidate.search_volume_monthly,
            "competitive_gap": candidate.competitive_gap.value,
            "pass_networks": candidate.pass_networks,
            "signals": [
                {
                    "source": s.source.value,
                    "strength": s.strength,
                    "data": s.data,
                    "reasoning": s.reasoning,
                }
                for s in candidate.signals
            ],
            "reasoning": candidate.reasoning,
            "status": candidate.status.value,
            "discovered_at": candidate.discovered_at.isoformat(),
        }).execute()

        if result.data:
            return result.data[0].get("id")
        return None

    except Exception as e:
        print(f"Error saving candidate: {e}")
        return None


async def get_pending_candidates(limit: int = 10) -> list[dict]:
    """
    Get pending discovery candidates ordered by opportunity score.

    Args:
        limit: Max candidates to return

    Returns:
        List of candidate dicts
    """
    try:
        supabase = get_supabase_client()

        result = supabase.table("discovery_candidates")\
            .select("*")\
            .eq("status", "pending")\
            .order("opportunity_score", desc=True)\
            .limit(limit)\
            .execute()

        return result.data

    except Exception as e:
        print(f"Error getting candidates: {e}")
        return []


async def update_candidate_status(
    candidate_id: str,
    status: CandidateStatus,
) -> bool:
    """
    Update the status of a discovery candidate.

    Args:
        candidate_id: Candidate UUID
        status: New status

    Returns:
        Success boolean
    """
    try:
        supabase = get_supabase_client()

        result = supabase.table("discovery_candidates")\
            .update({"status": status.value})\
            .eq("id", candidate_id)\
            .execute()

        return bool(result.data)

    except Exception as e:
        print(f"Error updating candidate: {e}")
        return False


def check_discovery_candidate_exists(
    resort_name: str,
    country: str,
) -> dict[str, Any] | None:
    """
    Check if a resort is already in discovery_candidates queue.

    This is the agent-native way to check if a resort is already
    being processed, avoiding duplicate work.

    The UNIQUE(resort_name, country) constraint is our gatekeeper.

    Args:
        resort_name: Resort name
        country: Country name

    Returns:
        Candidate dict if exists, None otherwise
    """
    try:
        supabase = get_supabase_client()

        result = supabase.table("discovery_candidates")\
            .select("*")\
            .ilike("resort_name", resort_name)\
            .ilike("country", country)\
            .limit(1)\
            .execute()

        return result.data[0] if result.data else None

    except Exception as e:
        print(f"Error checking discovery candidate: {e}")
        return None


# =============================================================================
# Main Discovery Functions
# =============================================================================

async def run_keyword_discovery(
    seed_keywords: list[str] | None = None,
    limit: int = 20,
) -> DiscoveryResult:
    """
    Run keyword-based discovery to find resort opportunities.

    Args:
        seed_keywords: Starting keywords (default: family ski related)
        limit: Max candidates to return

    Returns:
        DiscoveryResult with candidates
    """
    cost = 0.0

    if seed_keywords is None:
        seed_keywords = [
            "best family ski resorts",
            "ski resorts for kids",
            "family friendly skiing",
            "ski vacation with toddlers",
            "beginner ski resorts",
        ]

    try:
        # Get keyword suggestions
        all_suggestions = []
        for seed in seed_keywords[:3]:  # Limit API calls
            suggestions = await get_keyword_suggestions(seed, limit=30)
            all_suggestions.extend(suggestions)
            cost += 0.05  # DataForSEO cost per call

        # Extract resort names from suggestions
        resort_keywords = [
            s for s in all_suggestions
            if any(term in s.get("keyword", "").lower()
                   for term in ["resort", "ski", "mountain", "valley"])
        ]

        # Get our current coverage
        covered = await get_covered_resorts()

        # Build candidates from keyword data
        candidates = []
        seen = set()

        for kw_data in resort_keywords:
            keyword = kw_data.get("keyword", "")

            # Skip if already seen or covered
            if keyword.lower() in seen:
                continue

            # Try to extract resort name (simple heuristic)
            # Keywords like "vail ski resort" -> "Vail"
            parts = keyword.lower().replace("ski resort", "").replace("resort", "").strip().split()
            if not parts:
                continue

            resort_name = " ".join(parts).title()
            seen.add(keyword.lower())

            # Check if we cover this
            for country in ["USA", "Canada", "Austria", "Switzerland", "France", "Italy", "Japan"]:
                if (resort_name.lower(), country.lower()) in covered:
                    continue

            candidate = DiscoveryCandidate(
                resort_name=resort_name,
                country="Unknown",  # Would need further research
                search_volume_monthly=kw_data.get("search_volume"),
                signals=[
                    DiscoverySignal(
                        source=DiscoverySource.KEYWORD_RESEARCH,
                        strength=0.6 if kw_data.get("search_volume", 0) > 500 else 0.3,
                        data=kw_data,
                        reasoning=f"Found in keyword research with volume {kw_data.get('search_volume', 'unknown')}",
                    )
                ],
            )
            candidate.opportunity_score = calculate_opportunity_score(candidate)
            candidates.append(candidate)

        # Sort by opportunity score
        candidates.sort(key=lambda c: c.opportunity_score, reverse=True)

        return DiscoveryResult(
            success=True,
            candidates=candidates[:limit],
            mode="keyword_research",
            cost=cost,
            metadata={"seed_keywords": seed_keywords, "suggestions_found": len(all_suggestions)},
        )

    except Exception as e:
        return DiscoveryResult(
            success=False,
            error=str(e),
            mode="keyword_research",
            cost=cost,
        )


async def run_gap_discovery() -> DiscoveryResult:
    """
    Run coverage gap discovery to find missing resorts.

    Returns:
        DiscoveryResult with candidates from pass and region gaps
    """
    try:
        # Find pass network gaps
        pass_candidates = await find_pass_coverage_gaps()

        # Find region gaps for major ski countries
        region_candidates = []
        for country in ["austria", "switzerland", "france", "italy", "usa", "canada", "japan"]:
            gaps = await find_region_coverage_gaps(country)
            region_candidates.extend(gaps)

        # Combine and score
        all_candidates = pass_candidates + region_candidates
        for candidate in all_candidates:
            candidate.opportunity_score = calculate_opportunity_score(candidate)

        # Sort by score
        all_candidates.sort(key=lambda c: c.opportunity_score, reverse=True)

        return DiscoveryResult(
            success=True,
            candidates=all_candidates,
            mode="gap_discovery",
            cost=0.0,  # Database-only, no API costs
            metadata={
                "pass_gaps": len(pass_candidates),
                "region_gaps": len(region_candidates),
            },
        )

    except Exception as e:
        return DiscoveryResult(
            success=False,
            error=str(e),
            mode="gap_discovery",
        )


async def run_trending_discovery(days_back: int = 7) -> DiscoveryResult:
    """
    Run trending topic discovery to find hot opportunities.

    Args:
        days_back: How many days of content to analyze

    Returns:
        DiscoveryResult with candidates from trending content
    """
    cost = 0.0

    try:
        # Get trending content from Exa
        trending_content = await search_trending_ski_topics(days_back=days_back)
        cost += 0.10  # Exa API cost

        if not trending_content:
            return DiscoveryResult(
                success=True,
                candidates=[],
                mode="trending",
                cost=cost,
                metadata={"message": "No trending content found"},
            )

        # Extract resort mentions
        resort_names = await extract_resort_mentions(trending_content)
        cost += 0.01  # Claude Haiku cost

        # Get our coverage
        covered = await get_covered_resorts()

        # Build candidates
        candidates = []
        for name in set(resort_names):
            # Check all likely countries
            is_covered = False
            for country in ["USA", "Canada", "Austria", "Switzerland", "France", "Italy", "Japan"]:
                if (name.lower(), country.lower()) in covered:
                    is_covered = True
                    break

            if is_covered:
                continue

            candidate = DiscoveryCandidate(
                resort_name=name,
                country="Unknown",
                competitive_gap=CompetitiveGap.WEAK,
                signals=[
                    DiscoverySignal(
                        source=DiscoverySource.TRENDING,
                        strength=0.8,
                        reasoning=f"Mentioned in {len([c for c in trending_content if name.lower() in c.get('title', '').lower()])} trending articles",
                    )
                ],
                reasoning=f"Trending in recent ski content",
            )
            candidate.opportunity_score = calculate_opportunity_score(candidate)
            candidates.append(candidate)

        candidates.sort(key=lambda c: c.opportunity_score, reverse=True)

        return DiscoveryResult(
            success=True,
            candidates=candidates,
            mode="trending",
            cost=cost,
            metadata={
                "articles_analyzed": len(trending_content),
                "resorts_mentioned": len(resort_names),
            },
        )

    except Exception as e:
        return DiscoveryResult(
            success=False,
            error=str(e),
            mode="trending",
            cost=cost,
        )


async def run_exploration_discovery(count: int = 5) -> DiscoveryResult:
    """
    Run exploration discovery with random seed for diversity.

    Prevents echo chamber by adding random resort discoveries
    that might not surface through demand/gap analysis.

    Args:
        count: Number of random candidates to generate

    Returns:
        DiscoveryResult with random exploration candidates
    """
    # Lesser-known ski regions to explore
    EXPLORATION_POOL = [
        {"name": "Bansko", "country": "Bulgaria", "region": "Pirin"},
        {"name": "Borovets", "country": "Bulgaria", "region": "Rila"},
        {"name": "Jasná", "country": "Slovakia", "region": "Low Tatras"},
        {"name": "Kopaonik", "country": "Serbia", "region": "Central Serbia"},
        {"name": "Gudauri", "country": "Georgia", "region": "Greater Caucasus"},
        {"name": "Grandvalira", "country": "Andorra", "region": "Pyrenees"},
        {"name": "Sierra Nevada", "country": "Spain", "region": "Andalusia"},
        {"name": "Gulmarg", "country": "India", "region": "Kashmir"},
        {"name": "Yongpyong", "country": "South Korea", "region": "Gangwon"},
        {"name": "Thredbo", "country": "Australia", "region": "NSW"},
        {"name": "Ruapehu", "country": "New Zealand", "region": "North Island"},
        {"name": "Cerro Catedral", "country": "Argentina", "region": "Patagonia"},
        {"name": "Valle Nevado", "country": "Chile", "region": "Santiago Region"},
        {"name": "Shymbulak", "country": "Kazakhstan", "region": "Almaty"},
        {"name": "Dizin", "country": "Iran", "region": "Alborz"},
    ]

    try:
        # Get our coverage
        covered = await get_covered_resorts()

        # Filter to uncovered
        uncovered = [
            r for r in EXPLORATION_POOL
            if (r["name"].lower(), r["country"].lower()) not in covered
        ]

        # Random sample
        selected = random.sample(uncovered, min(count, len(uncovered)))

        candidates = []
        for resort in selected:
            candidate = DiscoveryCandidate(
                resort_name=resort["name"],
                country=resort["country"],
                region=resort.get("region"),
                competitive_gap=CompetitiveGap.WEAK,
                signals=[
                    DiscoverySignal(
                        source=DiscoverySource.EXPLORATION,
                        strength=0.5,
                        reasoning="Random exploration for content diversity",
                    )
                ],
                reasoning="Exploration discovery for underrepresented region",
            )
            candidate.opportunity_score = calculate_opportunity_score(candidate)
            candidates.append(candidate)

        return DiscoveryResult(
            success=True,
            candidates=candidates,
            mode="exploration",
            cost=0.0,
            metadata={"pool_size": len(EXPLORATION_POOL), "uncovered": len(uncovered)},
        )

    except Exception as e:
        return DiscoveryResult(
            success=False,
            error=str(e),
            mode="exploration",
        )


async def run_full_discovery(
    include_keywords: bool = True,
    include_gaps: bool = True,
    include_trending: bool = True,
    include_exploration: bool = True,
    max_candidates: int = 20,
) -> DiscoveryResult:
    """
    Run all discovery modes and merge results.

    Args:
        include_keywords: Include keyword research
        include_gaps: Include coverage gap analysis
        include_trending: Include trending analysis
        include_exploration: Include random exploration
        max_candidates: Maximum candidates to return

    Returns:
        Merged DiscoveryResult
    """
    all_candidates = []
    total_cost = 0.0
    metadata = {}

    # Run enabled discovery modes
    if include_keywords:
        result = await run_keyword_discovery()
        all_candidates.extend(result.candidates)
        total_cost += result.cost
        metadata["keyword"] = {"count": len(result.candidates), "cost": result.cost}

    if include_gaps:
        result = await run_gap_discovery()
        all_candidates.extend(result.candidates)
        total_cost += result.cost
        metadata["gaps"] = {"count": len(result.candidates)}

    if include_trending:
        result = await run_trending_discovery()
        all_candidates.extend(result.candidates)
        total_cost += result.cost
        metadata["trending"] = {"count": len(result.candidates), "cost": result.cost}

    if include_exploration:
        result = await run_exploration_discovery(count=3)
        all_candidates.extend(result.candidates)
        metadata["exploration"] = {"count": len(result.candidates)}

    # Deduplicate by resort name
    seen = set()
    unique_candidates = []
    for c in all_candidates:
        key = c.resort_name.lower()
        if key not in seen:
            seen.add(key)
            unique_candidates.append(c)

    # Sort by opportunity score
    unique_candidates.sort(key=lambda c: c.opportunity_score, reverse=True)

    return DiscoveryResult(
        success=True,
        candidates=unique_candidates[:max_candidates],
        mode="full",
        cost=total_cost,
        metadata=metadata,
    )
