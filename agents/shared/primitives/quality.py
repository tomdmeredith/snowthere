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

    cutoff_date = (datetime.utcnow() - timedelta(days=staleness_threshold_days)).isoformat()

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

    cutoff_date = (datetime.utcnow() - timedelta(days=threshold_days)).isoformat()

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
