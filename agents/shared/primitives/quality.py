"""Quality audit primitives for content monitoring and improvement.

These primitives support the QualityAuditAgent's three operating modes:
- Quick Scan: Fast database queries for formula-based checks
- Deep Audit: LLM-assisted quality assessment
- Triggered: On-demand full audit of single resort

Following Agent Native principles, these primitives can detect issues
using formulas (fast, cheap) and assess quality using LLMs (flexible, intelligent).
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any
from enum import Enum

from ..supabase_client import get_supabase_client


class IssueSeverity(Enum):
    """Severity levels for quality issues."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IssueType(Enum):
    """Types of quality issues."""
    STALE = "stale"
    LOW_CONFIDENCE = "low_confidence"
    INCOMPLETE = "incomplete"
    PRICE_DRIFT = "price_drift"
    VOICE_DRIFT = "voice_drift"
    MISSING_SECTION = "missing_section"
    BROKEN_LINK = "broken_link"
    DATA_INCONSISTENCY = "data_inconsistency"


@dataclass
class QualityIssue:
    """Represents a single quality issue found during audit."""

    resort_id: str
    resort_name: str
    issue_type: IssueType
    severity: IssueSeverity
    description: str
    evidence: dict[str, Any] = field(default_factory=dict)
    recommended_action: str = ""
    estimated_fix_cost: float = 0.0
    auto_fixable: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage/transmission."""
        return {
            "resort_id": self.resort_id,
            "resort_name": self.resort_name,
            "issue_type": self.issue_type.value,
            "severity": self.severity.value,
            "description": self.description,
            "evidence": self.evidence,
            "recommended_action": self.recommended_action,
            "estimated_fix_cost": self.estimated_fix_cost,
            "auto_fixable": self.auto_fixable,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class AuditResult:
    """Result of a quality audit run."""

    audit_id: str
    mode: str  # quick_scan, deep_audit, triggered
    started_at: datetime
    completed_at: datetime | None = None

    resorts_audited: int = 0
    issues: list[QualityIssue] = field(default_factory=list)

    actions_taken: list[str] = field(default_factory=list)
    actions_queued: list[str] = field(default_factory=list)
    actions_escalated: list[str] = field(default_factory=list)

    patterns_discovered: list[str] = field(default_factory=list)
    total_fix_cost_estimate: float = 0.0

    def issues_by_severity(self) -> dict[str, int]:
        """Count issues by severity."""
        counts = {s.value: 0 for s in IssueSeverity}
        for issue in self.issues:
            counts[issue.severity.value] += 1
        return counts

    def issues_by_type(self) -> dict[str, int]:
        """Count issues by type."""
        counts = {t.value: 0 for t in IssueType}
        for issue in self.issues:
            counts[issue.issue_type.value] += 1
        return counts

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "audit_id": self.audit_id,
            "mode": self.mode,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "resorts_audited": self.resorts_audited,
            "issues": [i.to_dict() for i in self.issues],
            "issues_by_severity": self.issues_by_severity(),
            "issues_by_type": self.issues_by_type(),
            "actions_taken": self.actions_taken,
            "actions_queued": self.actions_queued,
            "actions_escalated": self.actions_escalated,
            "patterns_discovered": self.patterns_discovered,
            "total_fix_cost_estimate": self.total_fix_cost_estimate,
        }

    def to_summary(self) -> str:
        """Generate human-readable summary."""
        severity_counts = self.issues_by_severity()
        duration = (self.completed_at - self.started_at).total_seconds() if self.completed_at else 0

        return f"""
Quality Audit Summary ({self.mode})
================================
Resorts audited: {self.resorts_audited}
Duration: {duration:.1f}s
Total issues: {len(self.issues)}

By Severity:
  Critical: {severity_counts['critical']}
  High: {severity_counts['high']}
  Medium: {severity_counts['medium']}
  Low: {severity_counts['low']}

Actions:
  Taken: {len(self.actions_taken)}
  Queued: {len(self.actions_queued)}
  Escalated: {len(self.actions_escalated)}

Estimated fix cost: ${self.total_fix_cost_estimate:.2f}
""".strip()


# =============================================================================
# FORMULA-BASED CHECKS (Fast, cheap - for Quick Scan mode)
# =============================================================================


REQUIRED_CONTENT_SECTIONS = [
    "quick_take",
    "getting_there",
    "where_to_stay",
    "lift_tickets",
    "on_mountain",
]

OPTIONAL_CONTENT_SECTIONS = [
    "off_mountain",
    "parent_reviews_summary",
    "faqs",
]


def check_staleness(
    resort_id: str,
    threshold_days: int = 30,
) -> QualityIssue | None:
    """
    Check if a resort's content is stale (not refreshed recently).

    Args:
        resort_id: UUID of the resort
        threshold_days: Days after which content is considered stale

    Returns:
        QualityIssue if stale, None otherwise
    """
    client = get_supabase_client()

    response = (
        client.table("resorts")
        .select("id, name, last_refreshed, updated_at")
        .eq("id", resort_id)
        .single()
        .execute()
    )

    if not response.data:
        return None

    resort = response.data
    last_refreshed = resort.get("last_refreshed") or resort.get("updated_at")

    if not last_refreshed:
        return QualityIssue(
            resort_id=resort_id,
            resort_name=resort["name"],
            issue_type=IssueType.STALE,
            severity=IssueSeverity.HIGH,
            description="Resort has never been refreshed",
            evidence={"last_refreshed": None},
            recommended_action="re_research",
            estimated_fix_cost=1.0,
            auto_fixable=True,
        )

    last_date = datetime.fromisoformat(last_refreshed.replace("Z", "+00:00"))
    days_since = (datetime.now(last_date.tzinfo) - last_date).days

    if days_since > threshold_days:
        severity = IssueSeverity.CRITICAL if days_since > 60 else IssueSeverity.HIGH if days_since > 45 else IssueSeverity.MEDIUM

        return QualityIssue(
            resort_id=resort_id,
            resort_name=resort["name"],
            issue_type=IssueType.STALE,
            severity=severity,
            description=f"Content is {days_since} days old (threshold: {threshold_days})",
            evidence={"days_since_refresh": days_since, "last_refreshed": last_refreshed},
            recommended_action="re_research",
            estimated_fix_cost=1.0,
            auto_fixable=True,
        )

    return None


def check_low_confidence(
    resort_id: str,
    threshold: float = 0.7,
) -> QualityIssue | None:
    """
    Check if a resort has low confidence score.

    Args:
        resort_id: UUID of the resort
        threshold: Confidence score below which is considered low

    Returns:
        QualityIssue if low confidence, None otherwise
    """
    client = get_supabase_client()

    response = (
        client.table("resorts")
        .select("id, name, confidence_score, status")
        .eq("id", resort_id)
        .single()
        .execute()
    )

    if not response.data:
        return None

    resort = response.data
    confidence = resort.get("confidence_score", 0.0) or 0.0
    status = resort.get("status", "draft")

    if confidence < threshold:
        # Critical if published with very low confidence
        if status == "published" and confidence < 0.5:
            severity = IssueSeverity.CRITICAL
        elif status == "published":
            severity = IssueSeverity.HIGH
        else:
            severity = IssueSeverity.MEDIUM

        return QualityIssue(
            resort_id=resort_id,
            resort_name=resort["name"],
            issue_type=IssueType.LOW_CONFIDENCE,
            severity=severity,
            description=f"Confidence score {confidence:.2f} is below threshold {threshold}",
            evidence={"confidence_score": confidence, "threshold": threshold, "status": status},
            recommended_action="re_research" if confidence < 0.5 else "review",
            estimated_fix_cost=1.0 if confidence < 0.5 else 0.5,
            auto_fixable=confidence < 0.5,
        )

    return None


def check_completeness(
    resort_id: str,
) -> list[QualityIssue]:
    """
    Check if a resort has all required content sections.

    Args:
        resort_id: UUID of the resort

    Returns:
        List of QualityIssue for missing sections
    """
    client = get_supabase_client()

    # Get resort name
    resort_response = (
        client.table("resorts")
        .select("id, name")
        .eq("id", resort_id)
        .single()
        .execute()
    )

    if not resort_response.data:
        return []

    resort_name = resort_response.data["name"]

    # Get content
    content_response = (
        client.table("resort_content")
        .select("*")
        .eq("resort_id", resort_id)
        .single()
        .execute()
    )

    issues = []

    if not content_response.data:
        issues.append(QualityIssue(
            resort_id=resort_id,
            resort_name=resort_name,
            issue_type=IssueType.INCOMPLETE,
            severity=IssueSeverity.CRITICAL,
            description="No content record exists",
            evidence={"missing": "entire content record"},
            recommended_action="generate_content",
            estimated_fix_cost=2.0,
            auto_fixable=True,
        ))
        return issues

    content = content_response.data

    # Check required sections
    for section in REQUIRED_CONTENT_SECTIONS:
        value = content.get(section)
        if not value or (isinstance(value, str) and len(value.strip()) < 50):
            issues.append(QualityIssue(
                resort_id=resort_id,
                resort_name=resort_name,
                issue_type=IssueType.MISSING_SECTION,
                severity=IssueSeverity.HIGH,
                description=f"Required section '{section}' is missing or too short",
                evidence={"section": section, "current_length": len(value) if value else 0},
                recommended_action="regenerate_section",
                estimated_fix_cost=0.3,
                auto_fixable=True,
            ))

    # Check optional sections (lower severity)
    for section in OPTIONAL_CONTENT_SECTIONS:
        value = content.get(section)
        if not value or (isinstance(value, str) and len(value.strip()) < 20):
            issues.append(QualityIssue(
                resort_id=resort_id,
                resort_name=resort_name,
                issue_type=IssueType.MISSING_SECTION,
                severity=IssueSeverity.LOW,
                description=f"Optional section '{section}' is missing",
                evidence={"section": section},
                recommended_action="regenerate_section",
                estimated_fix_cost=0.2,
                auto_fixable=True,
            ))

    return issues


def get_resorts_needing_audit(
    staleness_threshold_days: int = 30,
    confidence_threshold: float = 0.7,
    status_filter: str | None = "published",
    limit: int = 100,
) -> list[dict]:
    """
    Get list of resorts that need quality audit.

    Combines multiple quick checks to identify resorts needing attention.

    Args:
        staleness_threshold_days: Days after which content is stale
        confidence_threshold: Low confidence threshold
        status_filter: Filter by status (None for all)
        limit: Maximum results

    Returns:
        List of resort records with audit flags
    """
    client = get_supabase_client()

    cutoff_date = (datetime.utcnow() - timedelta(days=staleness_threshold_days)).isoformat() + "+00:00"

    query = client.table("resorts").select("*")

    if status_filter:
        query = query.eq("status", status_filter)

    response = query.limit(limit).execute()

    results = []
    for resort in (response.data or []):
        flags = []

        # Check staleness
        last_refreshed = resort.get("last_refreshed") or resort.get("updated_at")
        if last_refreshed and last_refreshed < cutoff_date:
            flags.append("stale")
        elif not last_refreshed:
            flags.append("never_refreshed")

        # Check confidence
        confidence = resort.get("confidence_score", 0.0) or 0.0
        if confidence < confidence_threshold:
            flags.append("low_confidence")

        if flags:
            results.append({**resort, "audit_flags": flags})

    return results


def get_stale_resorts_count(
    threshold_days: int = 30,
    status: str = "published",
) -> int:
    """
    Count resorts with stale content.

    Args:
        threshold_days: Days threshold for staleness
        status: Filter by status

    Returns:
        Count of stale resorts
    """
    client = get_supabase_client()

    cutoff_date = (datetime.utcnow() - timedelta(days=threshold_days)).isoformat() + "+00:00"

    response = (
        client.table("resorts")
        .select("id", count="exact")
        .eq("status", status)
        .lt("last_refreshed", cutoff_date)
        .execute()
    )

    return response.count or 0


# =============================================================================
# AUDIT LOGGING
# =============================================================================


def log_quality_issue(issue: QualityIssue) -> str | None:
    """
    Log a quality issue to the database for tracking.

    Args:
        issue: QualityIssue to log

    Returns:
        ID of created record, or None on failure
    """
    client = get_supabase_client()

    from uuid import uuid4
    issue_id = str(uuid4())

    try:
        client.table("agent_audit_log").insert({
            "id": issue_id,
            "task_id": f"quality_issue_{issue.resort_id}",
            "agent_name": "quality",
            "action": f"issue_detected:{issue.issue_type.value}",
            "reasoning": issue.description,
            "metadata": issue.to_dict(),
        }).execute()
        return issue_id
    except Exception as e:
        print(f"Warning: Failed to log quality issue: {e}")
        return None


def log_audit_run(result: AuditResult) -> str | None:
    """
    Log an audit run to the database.

    Args:
        result: AuditResult to log

    Returns:
        ID of created record, or None on failure
    """
    client = get_supabase_client()

    try:
        client.table("agent_audit_log").insert({
            "id": result.audit_id,
            "task_id": f"audit_{result.mode}_{result.started_at.strftime('%Y%m%d_%H%M%S')}",
            "agent_name": "quality",
            "action": f"audit_complete:{result.mode}",
            "reasoning": result.to_summary(),
            "metadata": result.to_dict(),
        }).execute()
        return result.audit_id
    except Exception as e:
        print(f"Warning: Failed to log audit run: {e}")
        return None


def get_recent_quality_issues(
    resort_id: str | None = None,
    severity: str | None = None,
    limit: int = 50,
) -> list[dict]:
    """
    Get recent quality issues from audit log.

    Args:
        resort_id: Filter by specific resort
        severity: Filter by severity level
        limit: Maximum results

    Returns:
        List of quality issue records
    """
    client = get_supabase_client()

    query = (
        client.table("agent_audit_log")
        .select("*")
        .eq("agent_name", "quality")
        .like("action", "issue_detected:%")
        .order("created_at", desc=True)
        .limit(limit)
    )

    response = query.execute()

    issues = []
    for record in (response.data or []):
        metadata = record.get("metadata", {})
        if resort_id and metadata.get("resort_id") != resort_id:
            continue
        if severity and metadata.get("severity") != severity:
            continue
        issues.append(record)

    return issues


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def calculate_fix_priority(issues: list[QualityIssue]) -> list[tuple[QualityIssue, float]]:
    """
    Calculate fix priority for a list of issues.

    Priority considers:
    - Severity weight
    - Whether auto-fixable
    - Estimated cost

    Args:
        issues: List of quality issues

    Returns:
        List of (issue, priority_score) sorted by priority
    """
    severity_weights = {
        IssueSeverity.CRITICAL: 1.0,
        IssueSeverity.HIGH: 0.7,
        IssueSeverity.MEDIUM: 0.4,
        IssueSeverity.LOW: 0.1,
    }

    priorities = []
    for issue in issues:
        score = severity_weights[issue.severity]

        # Boost auto-fixable issues
        if issue.auto_fixable:
            score *= 1.2

        # Lower priority for expensive fixes
        if issue.estimated_fix_cost > 2.0:
            score *= 0.8

        priorities.append((issue, score))

    return sorted(priorities, key=lambda x: x[1], reverse=True)


def batch_issues_for_fix(
    issues: list[QualityIssue],
    max_cost: float = 5.0,
    max_items: int = 10,
) -> tuple[list[QualityIssue], list[QualityIssue]]:
    """
    Split issues into a batch to fix now and a remainder.

    Args:
        issues: List of quality issues
        max_cost: Maximum total cost for this batch
        max_items: Maximum items in batch

    Returns:
        Tuple of (batch_to_fix, remainder)
    """
    prioritized = calculate_fix_priority(issues)

    batch = []
    remainder = []
    total_cost = 0.0

    for issue, _ in prioritized:
        if len(batch) < max_items and total_cost + issue.estimated_fix_cost <= max_cost:
            batch.append(issue)
            total_cost += issue.estimated_fix_cost
        else:
            remainder.append(issue)

    return batch, remainder


# =============================================================================
# PERFECT PAGE CHECKLIST
# =============================================================================
# Agent-native quality system for resort page excellence.
# Each check returns pass/fail and feeds into approval panel decisions.


PERFECT_PAGE_CHECKLIST = {
    "content": [
        ("quick_take_length", "50-95 words", "Quick Take is optimal length for scanning"),
        ("tagline_exists", "Has unique tagline", "Resort has a distinctive 8-12 word tagline"),
        ("no_em_dashes", "No em/en-dashes", "Uses commas/periods instead of dashes"),
        ("no_llm_markers", "No LLM markers", "No 'Additionally', 'Furthermore', 'It's worth noting'"),
        ("has_pro_tips", "Has pro tips", "Content includes actionable 'Pro tip:' items"),
    ],
    "media": [
        ("has_hero_image", "Has hero image", "Resort has a hero or atmosphere image"),
        ("has_trail_map", "Has trail map", "Has trail map data OR official URL fallback"),
        ("has_terrain_data", "Has terrain %s", "Has beginner/intermediate/advanced percentages"),
    ],
    "data": [
        ("has_lift_prices", "Has lift prices", "Has adult and child daily lift ticket prices"),
        ("has_family_score", "Has family score", "Has overall family friendliness score"),
        ("has_best_age_range", "Has age range", "Has best_age_min and best_age_max for family planning"),
        ("has_lodging_prices", "Has lodging prices", "Has at least mid-range lodging price"),
        ("has_perfect_if", "Has Perfect If", "Has 3+ 'Perfect if' items"),
        ("has_skip_if", "Has Skip If", "Has 1+ 'Skip if' items"),
    ],
    "links": [
        ("has_official_link", "Has official link", "Has official resort website link"),
        ("has_outbound_links", "Has useful links", "Has curated outbound links for families"),
    ],
}


# LLM markers to detect in content
LLM_MARKERS = [
    "additionally",
    "furthermore",
    "moreover",
    "it's worth noting",
    "it is worth noting",
    "it's important to note",
    "subsequently",
]


@dataclass
class CheckResult:
    """Result of a single checklist item check."""
    check_id: str
    label: str
    description: str
    passed: bool
    details: str = ""


@dataclass
class PageQualityScore:
    """Overall quality score for a resort page."""
    resort_id: str
    resort_name: str
    total_checks: int
    passed_checks: int
    score_pct: float
    results_by_category: dict[str, list[CheckResult]]
    failing_checks: list[CheckResult]
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "resort_id": self.resort_id,
            "resort_name": self.resort_name,
            "total_checks": self.total_checks,
            "passed_checks": self.passed_checks,
            "score_pct": self.score_pct,
            "results_by_category": {
                cat: [{"check_id": r.check_id, "passed": r.passed, "details": r.details}
                      for r in results]
                for cat, results in self.results_by_category.items()
            },
            "failing_checks": [r.check_id for r in self.failing_checks],
            "timestamp": self.timestamp.isoformat(),
        }


def _count_words(text: str | None) -> int:
    """Count words in text, handling None and HTML."""
    if not text:
        return 0
    # Strip HTML tags for word count
    import re
    clean = re.sub(r'<[^>]+>', ' ', text)
    return len(clean.split())


def _check_content_for_markers(text: str | None, markers: list[str]) -> list[str]:
    """Check if text contains any of the given markers (case-insensitive)."""
    if not text:
        return []
    text_lower = text.lower()
    found = []
    for marker in markers:
        if marker.lower() in text_lower:
            found.append(marker)
    return found


def _check_for_dashes(text: str | None) -> bool:
    """Check if text contains em-dashes or en-dashes."""
    if not text:
        return False
    # Em-dash: — (U+2014), En-dash: – (U+2013)
    return "—" in text or "–" in text


def score_resort_page(resort_id: str) -> PageQualityScore | None:
    """
    Score a resort page against the Perfect Page Checklist.

    Runs all checks and returns a comprehensive quality score.

    Args:
        resort_id: UUID of the resort to score

    Returns:
        PageQualityScore with all check results, or None if resort not found
    """
    client = get_supabase_client()

    # Fetch all data needed for checks
    resort_response = (
        client.table("resorts")
        .select("id, name, slug, trail_map_data")
        .eq("id", resort_id)
        .single()
        .execute()
    )

    if not resort_response.data:
        return None

    resort = resort_response.data
    resort_name = resort["name"]
    trail_map = resort.get("trail_map_data") or {}

    # Get content (use limit(1) and handle empty results - safer than maybe_single)
    content_response = (
        client.table("resort_content")
        .select("*")
        .eq("resort_id", resort_id)
        .limit(1)
        .execute()
    )
    content = content_response.data[0] if content_response.data else {}

    # Get family metrics
    metrics_response = (
        client.table("resort_family_metrics")
        .select("*")
        .eq("resort_id", resort_id)
        .limit(1)
        .execute()
    )
    metrics = metrics_response.data[0] if metrics_response.data else {}

    # Get costs
    costs_response = (
        client.table("resort_costs")
        .select("*")
        .eq("resort_id", resort_id)
        .limit(1)
        .execute()
    )
    costs = costs_response.data[0] if costs_response.data else {}

    # trail_map already fetched from resorts table above

    # Get images
    images_response = (
        client.table("resort_images")
        .select("*")
        .eq("resort_id", resort_id)
        .execute()
    )
    images = images_response.data or []

    # Get links
    links_response = (
        client.table("resort_links")
        .select("*")
        .eq("resort_id", resort_id)
        .execute()
    )
    links = links_response.data or []

    # Run all checks
    results_by_category: dict[str, list[CheckResult]] = {}

    # CONTENT CHECKS
    content_results = []

    # quick_take_length
    quick_take = content.get("quick_take", "")
    word_count = _count_words(quick_take)
    passed = 50 <= word_count <= 95
    content_results.append(CheckResult(
        check_id="quick_take_length",
        label="50-95 words",
        description="Quick Take is optimal length for scanning",
        passed=passed,
        details=f"{word_count} words" + (" (too short)" if word_count < 50 else " (too long)" if word_count > 95 else ""),
    ))

    # tagline_exists
    tagline = content.get("tagline") or ""
    passed = bool(tagline and len(tagline.strip()) >= 20)
    tagline_display = tagline[:50] + "..." if tagline and len(tagline) > 50 else (tagline or "No tagline")
    content_results.append(CheckResult(
        check_id="tagline_exists",
        label="Has unique tagline",
        description="Resort has a distinctive 8-12 word tagline",
        passed=passed,
        details=tagline_display,
    ))

    # no_em_dashes - check all content fields
    all_content = " ".join([
        content.get("quick_take", ""),
        content.get("getting_there", ""),
        content.get("where_to_stay", ""),
        content.get("on_mountain", ""),
        content.get("off_mountain", ""),
    ])
    has_dashes = _check_for_dashes(all_content)
    content_results.append(CheckResult(
        check_id="no_em_dashes",
        label="No em/en-dashes",
        description="Uses commas/periods instead of dashes",
        passed=not has_dashes,
        details="Contains em/en-dashes" if has_dashes else "Clean",
    ))

    # no_llm_markers
    found_markers = _check_content_for_markers(all_content, LLM_MARKERS)
    content_results.append(CheckResult(
        check_id="no_llm_markers",
        label="No LLM markers",
        description="No 'Additionally', 'Furthermore', 'It's worth noting'",
        passed=len(found_markers) == 0,
        details=f"Found: {', '.join(found_markers)}" if found_markers else "Clean",
    ))

    # has_pro_tips
    has_tips = "pro tip" in all_content.lower() or "pro-tip" in all_content.lower()
    content_results.append(CheckResult(
        check_id="has_pro_tips",
        label="Has pro tips",
        description="Content includes actionable 'Pro tip:' items",
        passed=has_tips,
        details="Has pro tips" if has_tips else "No pro tips found",
    ))

    results_by_category["content"] = content_results

    # MEDIA CHECKS
    media_results = []

    # has_hero_image
    hero_images = [img for img in images if img.get("image_type") in ("hero", "atmosphere")]
    media_results.append(CheckResult(
        check_id="has_hero_image",
        label="Has hero image",
        description="Resort has a hero or atmosphere image",
        passed=len(hero_images) > 0,
        details=f"{len(hero_images)} hero/atmosphere images" if hero_images else "No hero image",
    ))

    # has_trail_map (check for piste_count/lift_count or official URL)
    has_map = bool(trail_map.get("piste_count")) or bool(trail_map.get("official_map_url"))
    map_details = ""
    if trail_map.get("piste_count"):
        map_details = f"{trail_map.get('piste_count')} runs, {trail_map.get('lift_count', 0)} lifts"
    elif trail_map.get("official_map_url"):
        map_details = "Official map URL"
    else:
        map_details = "No trail map data"
    media_results.append(CheckResult(
        check_id="has_trail_map",
        label="Has trail map",
        description="Has trail map data OR official URL fallback",
        passed=has_map,
        details=map_details,
    ))

    # has_terrain_data (difficulty breakdown from trail_map_data)
    difficulty = trail_map.get("difficulty_breakdown", {})
    has_terrain = bool(difficulty.get("easy") or difficulty.get("intermediate") or difficulty.get("advanced"))
    terrain_details = ""
    if has_terrain:
        terrain_details = f"Easy: {difficulty.get('easy', 0)}, Int: {difficulty.get('intermediate', 0)}, Adv: {difficulty.get('advanced', 0)}"
    else:
        terrain_details = "Missing terrain data"
    media_results.append(CheckResult(
        check_id="has_terrain_data",
        label="Has terrain %s",
        description="Has beginner/intermediate/advanced percentages",
        passed=has_terrain,
        details=terrain_details,
    ))

    results_by_category["media"] = media_results

    # DATA CHECKS
    data_results = []

    # has_lift_prices (use 'is not None' to allow 0 values like free child tickets)
    has_prices = costs.get("lift_adult_daily") is not None and costs.get("lift_child_daily") is not None
    price_details = ""
    if has_prices:
        adult = costs.get("lift_adult_daily", 0)
        child = costs.get("lift_child_daily", 0)
        price_details = f"Adult: ${adult}, Child: ${child}" + (" (free)" if child == 0 else "")
    else:
        price_details = "Missing lift prices"
    data_results.append(CheckResult(
        check_id="has_lift_prices",
        label="Has lift prices",
        description="Has adult and child daily lift ticket prices",
        passed=has_prices,
        details=price_details,
    ))

    # has_family_score
    has_score = metrics.get("family_overall_score") is not None
    data_results.append(CheckResult(
        check_id="has_family_score",
        label="Has family score",
        description="Has overall family friendliness score",
        passed=has_score,
        details=f"Score: {metrics.get('family_overall_score')}/10" if has_score else "No family score",
    ))

    # has_best_age_range
    has_age_range = metrics.get("best_age_min") is not None and metrics.get("best_age_max") is not None
    data_results.append(CheckResult(
        check_id="has_best_age_range",
        label="Has age range",
        description="Has best_age_min and best_age_max for family planning",
        passed=has_age_range,
        details=f"Ages {metrics.get('best_age_min')}-{metrics.get('best_age_max')}" if has_age_range else "No age range",
    ))

    # has_lodging_prices (use 'is not None' to allow 0 values)
    has_lodging = costs.get("lodging_mid_nightly") is not None
    lodging_details = f"${costs.get('lodging_mid_nightly')}/night" if has_lodging else "No lodging prices"
    data_results.append(CheckResult(
        check_id="has_lodging_prices",
        label="Has lodging prices",
        description="Has at least mid-range lodging price",
        passed=has_lodging,
        details=lodging_details,
    ))

    # has_perfect_if
    perfect_if = metrics.get("perfect_if") or []
    if isinstance(perfect_if, str):
        import json
        try:
            perfect_if = json.loads(perfect_if)
        except (json.JSONDecodeError, TypeError, ValueError):
            perfect_if = []
    has_perfect = len(perfect_if) >= 3
    data_results.append(CheckResult(
        check_id="has_perfect_if",
        label="Has Perfect If",
        description="Has 3+ 'Perfect if' items",
        passed=has_perfect,
        details=f"{len(perfect_if)} items" if perfect_if else "No Perfect If items",
    ))

    # has_skip_if
    skip_if = metrics.get("skip_if") or []
    if isinstance(skip_if, str):
        import json
        try:
            skip_if = json.loads(skip_if)
        except (json.JSONDecodeError, TypeError, ValueError):
            skip_if = []
    has_skip = len(skip_if) >= 1
    data_results.append(CheckResult(
        check_id="has_skip_if",
        label="Has Skip If",
        description="Has 1+ 'Skip if' items",
        passed=has_skip,
        details=f"{len(skip_if)} items" if skip_if else "No Skip If items",
    ))

    results_by_category["data"] = data_results

    # LINKS CHECKS
    links_results = []

    # has_official_link
    official_links = [l for l in links if l.get("category") == "official"]
    links_results.append(CheckResult(
        check_id="has_official_link",
        label="Has official link",
        description="Has official resort website link",
        passed=len(official_links) > 0,
        details="Has official website" if official_links else "No official link",
    ))

    # has_outbound_links
    links_results.append(CheckResult(
        check_id="has_outbound_links",
        label="Has useful links",
        description="Has curated outbound links for families",
        passed=len(links) >= 3,
        details=f"{len(links)} links" if links else "No outbound links",
    ))

    results_by_category["links"] = links_results

    # Calculate totals
    all_results = [r for results in results_by_category.values() for r in results]
    total_checks = len(all_results)
    passed_checks = sum(1 for r in all_results if r.passed)
    score_pct = (passed_checks / total_checks * 100) if total_checks > 0 else 0
    failing_checks = [r for r in all_results if not r.passed]

    return PageQualityScore(
        resort_id=resort_id,
        resort_name=resort_name,
        total_checks=total_checks,
        passed_checks=passed_checks,
        score_pct=score_pct,
        results_by_category=results_by_category,
        failing_checks=failing_checks,
    )


def get_resorts_below_quality_threshold(
    threshold_pct: float = 80.0,
    status: str = "published",
    limit: int = 50,
) -> list[dict]:
    """
    Get resorts that score below the quality threshold.

    Args:
        threshold_pct: Minimum acceptable quality percentage
        status: Filter by resort status
        limit: Maximum results

    Returns:
        List of resort dicts with quality scores
    """
    client = get_supabase_client()

    # Get all resorts
    response = (
        client.table("resorts")
        .select("id, name, slug, status")
        .eq("status", status)
        .limit(limit)
        .execute()
    )

    results = []
    for resort in (response.data or []):
        score = score_resort_page(resort["id"])
        if score and score.score_pct < threshold_pct:
            results.append({
                **resort,
                "quality_score": score.score_pct,
                "failing_checks": [r.check_id for r in score.failing_checks],
                "passed": score.passed_checks,
                "total": score.total_checks,
            })

    # Sort by quality score (worst first)
    results.sort(key=lambda x: x["quality_score"])

    return results


async def queue_quality_improvements(
    resort_id: str,
    score: PageQualityScore,
    priority: str = "normal",
) -> list[str]:
    """
    Queue improvement tasks for failing quality checks.

    Args:
        resort_id: UUID of the resort
        score: Quality score with failing checks
        priority: Task priority

    Returns:
        List of queued task IDs
    """
    from .system import queue_task

    task_ids = []

    for check in score.failing_checks:
        # Map check_id to appropriate task type
        task_type_map = {
            "quick_take_length": "regenerate_quick_take",
            "tagline_exists": "generate_tagline",
            "no_em_dashes": "clean_content_dashes",
            "no_llm_markers": "clean_content_markers",
            "has_pro_tips": "add_pro_tips",
            "has_hero_image": "find_hero_image",
            "has_trail_map": "fetch_trail_map",
            "has_terrain_data": "research_terrain",
            "has_lift_prices": "research_prices",
            "has_family_score": "calculate_family_score",
            "has_best_age_range": "research_age_range",
            "has_lodging_prices": "research_lodging_prices",
            "has_perfect_if": "generate_perfect_if",
            "has_skip_if": "generate_skip_if",
            "has_official_link": "find_official_link",
            "has_outbound_links": "curate_links",
        }

        task_type = task_type_map.get(check.check_id, "review")

        task_id = await queue_task(
            resort_id=resort_id,
            task_type=task_type,
            priority=priority,
            metadata={
                "check_id": check.check_id,
                "check_label": check.label,
                "details": check.details,
                "from_quality_audit": True,
            },
        )

        if task_id:
            task_ids.append(task_id)

    return task_ids
