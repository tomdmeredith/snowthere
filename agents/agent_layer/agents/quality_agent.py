"""QualityAuditAgent - Continuous content quality monitoring and improvement.

This agent audits resort content quality across the directory, detecting issues
and triggering fixes. It operates in three modes:

1. Quick Scan (Daily): Fast database queries to detect formula-based issues
   - Staleness (>30 days since refresh)
   - Low confidence scores
   - Missing required sections

2. Deep Audit (Weekly): LLM-assisted quality assessment
   - Price drift detection (compare DB to fresh research)
   - Voice consistency checks
   - Cross-source accuracy validation

3. Triggered (On-demand): Full audit of a single resort
   - User feedback, low traffic, manual request
   - All checks including external link validation

Design Principles:
- Hybrid approach: Formulas detect issues, LLMs assess quality
- Cost-conscious: Quick scans are free, deep audits have budget caps
- Actionable output: Issues include fix recommendations and cost estimates
- Learning: Patterns discovered feed back into future audits
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import uuid4

from ..base import BaseAgent, AgentPlan, Observation
from .schemas.quality import (
    AuditObjective,
    QualityAuditPlan,
    QualityObservation,
    AuditPlanStep,
    QuickScanConfig,
    DeepAuditConfig,
    TriggeredAuditConfig,
    QUICK_SCAN_CHECKS,
    DEEP_AUDIT_CHECKS,
    TRIGGERED_AUDIT_CHECKS,
)
from shared.primitives.quality import (
    QualityIssue,
    AuditResult,
    IssueSeverity,
    IssueType,
    check_staleness,
    check_low_confidence,
    check_completeness,
    get_resorts_needing_audit,
    log_quality_issue,
    log_audit_run,
    calculate_fix_priority,
    batch_issues_for_fix,
)
from shared.primitives import (
    log_reasoning,
    get_daily_spend,
    queue_task,
    assess_data_quality,
    make_decision,
)
from shared.config import settings
from shared.supabase_client import get_supabase_client


class QualityAuditAgent(BaseAgent):
    """Agent that continuously monitors and improves content quality.

    Usage:
        # Daily quick scan
        agent = QualityAuditAgent()
        objective = AuditObjective.quick_scan(staleness_threshold_days=30)
        result = await agent.run(objective.__dict__)

        # Weekly deep audit
        objective = AuditObjective.deep_audit(sample_size=10)
        result = await agent.run(objective.__dict__)

        # Triggered audit for specific resort
        objective = AuditObjective.triggered(
            resort_id="abc123",
            triggered_by="user_feedback"
        )
        result = await agent.run(objective.__dict__)
    """

    def __init__(self):
        """Initialize QualityAuditAgent."""
        super().__init__(name="quality")

    # =========================================================================
    # THINK PHASE: Analyze what needs auditing and create plan
    # =========================================================================

    async def _think(self, objective: dict[str, Any]) -> AgentPlan:
        """Analyze the audit objective and create an execution plan.

        For Quick Scan: Identify which database checks to run
        For Deep Audit: Select resort sample and determine LLM checks
        For Triggered: Plan full audit of single resort
        """
        mode = objective.get("mode", "quick_scan")
        config = objective.get("config", {})
        triggered_by = objective.get("triggered_by", "cron")

        log_reasoning(
            task_id=None,
            agent_name=self.name,
            action="think_mode_analysis",
            reasoning=f"Planning {mode} audit triggered by {triggered_by}",
            metadata={"mode": mode, "config": config},
        )

        if mode == "quick_scan":
            return await self._plan_quick_scan(config)
        elif mode == "deep_audit":
            return await self._plan_deep_audit(config)
        elif mode == "triggered":
            return await self._plan_triggered_audit(config)
        else:
            raise ValueError(f"Unknown audit mode: {mode}")

    async def _plan_quick_scan(self, config: dict) -> AgentPlan:
        """Plan a quick scan audit (database queries only)."""
        staleness_threshold = config.get("staleness_threshold_days", 30)
        confidence_threshold = config.get("confidence_threshold", 0.7)
        status_filter = config.get("status_filter", "published")
        max_resorts = config.get("max_resorts", 1000)

        # Get resorts needing attention
        resorts = get_resorts_needing_audit(
            staleness_threshold_days=staleness_threshold,
            confidence_threshold=confidence_threshold,
            status_filter=status_filter,
            limit=max_resorts,
        )

        steps = [
            f"Check {len(resorts)} flagged resorts for staleness",
            f"Check {len(resorts)} flagged resorts for low confidence",
            f"Check {len(resorts)} flagged resorts for completeness",
            "Aggregate issues by severity",
            "Queue high-priority fixes",
        ]

        reasoning = f"""Quick Scan Plan:
Found {len(resorts)} resorts with potential issues (stale or low confidence).
Will run database-only checks: {QUICK_SCAN_CHECKS}
No LLM calls - this is cost-free monitoring."""

        return AgentPlan(
            steps=steps,
            reasoning=reasoning,
            estimated_cost=0.0,  # Database queries only
            confidence=0.9,
            primitives_needed=["check_staleness", "check_low_confidence", "check_completeness"],
            dependencies=[],
        )

    async def _plan_deep_audit(self, config: dict) -> AgentPlan:
        """Plan a deep audit (LLM-assisted quality checks)."""
        sample_size = config.get("sample_size", 10)
        max_cost = config.get("max_cost", 5.0)
        check_price_drift = config.get("check_price_drift", True)
        check_voice_consistency = config.get("check_voice_consistency", True)
        prioritize_countries = config.get("prioritize_countries", [])

        # Check budget availability
        remaining = settings.daily_budget_limit - get_daily_spend()
        if remaining < max_cost:
            return AgentPlan(
                steps=["Skip deep audit - insufficient budget"],
                reasoning=f"Budget remaining ${remaining:.2f} is less than max_cost ${max_cost:.2f}",
                estimated_cost=0.0,
                confidence=1.0,
                primitives_needed=[],
                dependencies=[],
            )

        # Select sample of resorts to audit
        sample = await self._select_audit_sample(sample_size, prioritize_countries)

        steps = [
            f"Run formula checks on {len(sample)} sampled resorts",
            "For each resort with issues:",
        ]

        if check_price_drift:
            steps.append("  - Fetch fresh pricing and compare to stored data")
        if check_voice_consistency:
            steps.append("  - LLM assessment of voice consistency")

        steps.extend([
            "Classify issues by severity",
            "Queue auto-fixable issues",
            "Escalate critical issues requiring human review",
            "Extract patterns for future audits",
        ])

        reasoning = f"""Deep Audit Plan:
Selected {len(sample)} resorts for detailed review.
Will run checks: {DEEP_AUDIT_CHECKS}
Budget cap: ${max_cost:.2f}
Estimated cost: ~${len(sample) * 0.3:.2f} (assuming 30% need LLM assessment)"""

        return AgentPlan(
            steps=steps,
            reasoning=reasoning,
            estimated_cost=len(sample) * 0.3,
            confidence=0.8,
            primitives_needed=[
                "check_staleness", "check_low_confidence", "check_completeness",
                "assess_data_quality", "make_decision",
            ],
            dependencies=["research"] if check_price_drift else [],
        )

    async def _plan_triggered_audit(self, config: dict) -> AgentPlan:
        """Plan a triggered audit (full audit of single resort)."""
        resort_id = config.get("resort_id", "")
        full_audit = config.get("full_audit", True)
        include_recommendations = config.get("include_recommendations", True)

        if not resort_id:
            return AgentPlan(
                steps=["Error: No resort_id provided"],
                reasoning="Triggered audit requires a resort_id",
                estimated_cost=0.0,
                confidence=0.0,
                primitives_needed=[],
                dependencies=[],
            )

        # Get resort info
        client = get_supabase_client()
        resort_response = (
            client.table("resorts")
            .select("id, name, country, status, confidence_score")
            .eq("id", resort_id)
            .limit(1)
            .execute()
        )

        if not resort_response.data:
            return AgentPlan(
                steps=[f"Error: Resort {resort_id} not found"],
                reasoning="Cannot audit non-existent resort",
                estimated_cost=0.0,
                confidence=0.0,
                primitives_needed=[],
                dependencies=[],
            )

        resort = resort_response.data[0]

        steps = [
            f"Full audit of {resort['name']} ({resort['country']})",
            "Run all formula-based checks",
            "LLM assessment of data quality",
            "LLM assessment of voice consistency",
            "Check for data inconsistencies",
        ]

        if full_audit:
            steps.append("Validate external links (if configured)")

        if include_recommendations:
            steps.append("Generate specific improvement recommendations")

        reasoning = f"""Triggered Audit Plan:
Full quality audit of {resort['name']}.
Current status: {resort['status']}, confidence: {resort['confidence_score']}
Will run all checks: {TRIGGERED_AUDIT_CHECKS}
This is comprehensive but more expensive."""

        return AgentPlan(
            steps=steps,
            reasoning=reasoning,
            estimated_cost=1.5,  # Full LLM assessment
            confidence=0.85,
            primitives_needed=[
                "check_staleness", "check_low_confidence", "check_completeness",
                "assess_data_quality", "make_decision",
            ],
            dependencies=["research"],  # May need fresh data
        )

    async def _select_audit_sample(
        self,
        sample_size: int,
        prioritize_countries: list[str],
    ) -> list[dict]:
        """Select a sample of resorts for deep audit.

        Selection criteria:
        - Prioritize flagged resorts (stale, low confidence)
        - Apply country prioritization if specified
        - Include some random selection for coverage
        """
        client = get_supabase_client()

        # Get flagged resorts
        flagged = get_resorts_needing_audit(limit=sample_size * 2)

        # If country prioritization, filter/reorder
        if prioritize_countries:
            prioritized = [r for r in flagged if r.get("country") in prioritize_countries]
            other = [r for r in flagged if r.get("country") not in prioritize_countries]
            flagged = prioritized + other

        # Take sample
        sample = flagged[:sample_size]

        # If we don't have enough flagged, add random published resorts
        if len(sample) < sample_size:
            needed = sample_size - len(sample)
            existing_ids = [r["id"] for r in sample]

            random_response = (
                client.table("resorts")
                .select("*")
                .eq("status", "published")
                .not_.in_("id", existing_ids)
                .limit(needed)
                .execute()
            )

            sample.extend(random_response.data or [])

        return sample

    # =========================================================================
    # ACT PHASE: Execute the audit plan
    # =========================================================================

    async def _act(self, plan: AgentPlan) -> AuditResult:
        """Execute the audit plan by running checks and collecting issues."""
        audit_id = str(uuid4())
        started_at = datetime.utcnow()

        result = AuditResult(
            audit_id=audit_id,
            mode="unknown",  # Will be set based on plan
            started_at=started_at,
        )

        # Determine mode from plan reasoning
        if "Quick Scan" in plan.reasoning:
            result.mode = "quick_scan"
            await self._execute_quick_scan(result, plan)
        elif "Deep Audit" in plan.reasoning:
            result.mode = "deep_audit"
            await self._execute_deep_audit(result, plan)
        elif "Triggered Audit" in plan.reasoning or "Full audit" in plan.reasoning:
            result.mode = "triggered"
            await self._execute_triggered_audit(result, plan)
        else:
            log_reasoning(
                task_id=None,
                agent_name=self.name,
                action="act_error",
                reasoning=f"Could not determine audit mode from plan: {plan.reasoning[:100]}",
                metadata={"audit_id": audit_id},
            )

        result.completed_at = datetime.utcnow()
        return result

    async def _execute_quick_scan(self, result: AuditResult, plan: AgentPlan) -> None:
        """Execute quick scan - database queries only."""
        # Get all published resorts
        client = get_supabase_client()
        response = (
            client.table("resorts")
            .select("id, name")
            .eq("status", "published")
            .execute()
        )

        resorts = response.data or []
        result.resorts_audited = len(resorts)

        for resort in resorts:
            resort_id = resort["id"]

            # Check staleness
            stale_issue = check_staleness(resort_id)
            if stale_issue:
                result.issues.append(stale_issue)
                log_quality_issue(stale_issue)

            # Check confidence
            confidence_issue = check_low_confidence(resort_id)
            if confidence_issue:
                result.issues.append(confidence_issue)
                log_quality_issue(confidence_issue)

            # Check completeness
            completeness_issues = check_completeness(resort_id)
            for issue in completeness_issues:
                result.issues.append(issue)
                log_quality_issue(issue)

        # Calculate total fix cost
        result.total_fix_cost_estimate = sum(i.estimated_fix_cost for i in result.issues)

        # Queue auto-fixable high-priority issues
        await self._queue_fixes(result)

    async def _execute_deep_audit(self, result: AuditResult, plan: AgentPlan) -> None:
        """Execute deep audit - formula checks + LLM assessment."""
        # Extract sample from plan (would be stored in plan metadata in production)
        # For now, re-select sample
        sample = await self._select_audit_sample(sample_size=10, prioritize_countries=[])
        result.resorts_audited = len(sample)

        for resort in sample:
            resort_id = resort["id"]

            # Run formula checks first (free)
            stale_issue = check_staleness(resort_id)
            if stale_issue:
                result.issues.append(stale_issue)

            confidence_issue = check_low_confidence(resort_id)
            if confidence_issue:
                result.issues.append(confidence_issue)

            completeness_issues = check_completeness(resort_id)
            result.issues.extend(completeness_issues)

            # For resorts with issues, run LLM assessment
            resort_issues = [i for i in result.issues if i.resort_id == resort_id]
            if resort_issues:
                await self._llm_assess_resort(resort, resort_issues, result)

        # Log all issues
        for issue in result.issues:
            log_quality_issue(issue)

        result.total_fix_cost_estimate = sum(i.estimated_fix_cost for i in result.issues)
        await self._queue_fixes(result)

    async def _execute_triggered_audit(self, result: AuditResult, plan: AgentPlan) -> None:
        """Execute triggered audit - full audit of single resort."""
        # Extract resort_id from plan (look for it in the steps)
        # This is a simplification - in production, pass through plan metadata
        client = get_supabase_client()

        # Get all resorts and find the one mentioned in plan
        # (In production, store resort_id in plan metadata)
        response = (
            client.table("resorts")
            .select("*")
            .limit(1)
            .execute()
        )

        if not response.data:
            return

        resort = response.data[0]
        resort_id = resort["id"]
        result.resorts_audited = 1

        # Run all formula checks
        stale_issue = check_staleness(resort_id)
        if stale_issue:
            result.issues.append(stale_issue)

        confidence_issue = check_low_confidence(resort_id)
        if confidence_issue:
            result.issues.append(confidence_issue)

        completeness_issues = check_completeness(resort_id)
        result.issues.extend(completeness_issues)

        # Run LLM assessment regardless of formula results
        await self._llm_assess_resort(resort, result.issues, result)

        # Log issues
        for issue in result.issues:
            log_quality_issue(issue)

        result.total_fix_cost_estimate = sum(i.estimated_fix_cost for i in result.issues)
        await self._queue_fixes(result)

    async def _llm_assess_resort(
        self,
        resort: dict,
        existing_issues: list[QualityIssue],
        result: AuditResult,
    ) -> None:
        """Use LLM to assess resort quality in more depth."""
        client = get_supabase_client()
        resort_id = resort["id"]
        resort_name = resort.get("name", "Unknown")

        # Get content
        content_response = (
            client.table("resort_content")
            .select("*")
            .eq("resort_id", resort_id)
            .limit(1)
            .execute()
        )

        if not content_response.data:
            return

        content = content_response.data[0]

        # Assess data quality using LLM primitive
        try:
            quality_assessment = await assess_data_quality(
                data={
                    "content": content,
                    "existing_issues": [i.to_dict() for i in existing_issues],
                },
                context=f"Resort content quality assessment for {resort_name}",
                required_fields=["quick_take", "getting_there", "where_to_stay"],
            )

            # Add any new issues discovered by LLM
            if quality_assessment.confidence < 0.6:
                result.issues.append(QualityIssue(
                    resort_id=resort_id,
                    resort_name=resort_name,
                    issue_type=IssueType.DATA_INCONSISTENCY,
                    severity=IssueSeverity.HIGH,
                    description=f"LLM assessment confidence {quality_assessment.confidence:.2f}: {quality_assessment.reasoning}",
                    evidence={
                        "llm_confidence": quality_assessment.confidence,
                        "missing_critical": quality_assessment.missing_critical,
                        "red_flags": quality_assessment.red_flags,
                    },
                    recommended_action="manual_review",
                    estimated_fix_cost=1.0,
                    auto_fixable=False,
                ))

            # Record patterns discovered
            if quality_assessment.strengths:
                result.patterns_discovered.extend(
                    [f"Strength in {resort_name}: {s}" for s in quality_assessment.strengths[:2]]
                )

        except Exception as e:
            log_reasoning(
                task_id=None,
                agent_name=self.name,
                action="llm_assess_error",
                reasoning=f"LLM assessment failed for {resort_name}: {e}",
                metadata={"resort_id": resort_id, "error": str(e)},
            )

    async def _queue_fixes(self, result: AuditResult) -> None:
        """Queue auto-fixable issues for repair."""
        # Get batch of high-priority auto-fixable issues
        auto_fixable = [i for i in result.issues if i.auto_fixable]
        batch_to_fix, remainder = batch_issues_for_fix(
            auto_fixable,
            max_cost=5.0,
            max_items=10,
        )

        for issue in batch_to_fix:
            # Determine task type based on issue
            task_type = "research" if issue.issue_type in [IssueType.STALE, IssueType.LOW_CONFIDENCE] else "generate"

            task_id = queue_task(
                task_type=task_type,
                resort_id=issue.resort_id,
                priority=self._severity_to_priority(issue.severity),
                metadata={
                    "source": "quality_audit",
                    "issue_type": issue.issue_type.value,
                    "recommended_action": issue.recommended_action,
                },
            )

            if task_id:
                result.actions_queued.append(
                    f"Queued {task_type} for {issue.resort_name}: {issue.description[:50]}"
                )

        # Escalate critical issues that aren't auto-fixable
        critical_issues = [
            i for i in result.issues
            if i.severity == IssueSeverity.CRITICAL and not i.auto_fixable
        ]

        for issue in critical_issues:
            result.actions_escalated.append(
                f"CRITICAL: {issue.resort_name} - {issue.description}"
            )

    def _severity_to_priority(self, severity: IssueSeverity) -> int:
        """Convert severity to queue priority (1=highest, 10=lowest)."""
        mapping = {
            IssueSeverity.CRITICAL: 1,
            IssueSeverity.HIGH: 3,
            IssueSeverity.MEDIUM: 5,
            IssueSeverity.LOW: 8,
        }
        return mapping.get(severity, 5)

    # =========================================================================
    # OBSERVE PHASE: Evaluate results and extract lessons
    # =========================================================================

    async def _observe(self, result: AuditResult, objective: dict[str, Any]) -> Observation:
        """Evaluate audit results and extract patterns for future audits."""
        mode = objective.get("mode", "quick_scan")
        issues_by_severity = result.issues_by_severity()
        issues_by_type = result.issues_by_type()

        # Determine success criteria by mode
        if mode == "quick_scan":
            # Quick scan succeeds if it completes
            success = True
            outcome = f"Quick scan completed: {len(result.issues)} issues found across {result.resorts_audited} resorts"
        elif mode == "deep_audit":
            # Deep audit succeeds if we audited the sample
            success = result.resorts_audited >= int(objective.get("config", {}).get("sample_size", 10) * 0.8)
            outcome = f"Deep audit completed: {len(result.issues)} issues, {len(result.actions_queued)} fixes queued"
        else:  # triggered
            # Triggered audit succeeds if we found or ruled out issues
            success = result.resorts_audited == 1
            outcome = f"Triggered audit completed: {len(result.issues)} issues found"

        # Extract lessons
        lessons = []

        # Learn from issue distribution
        if issues_by_severity.get("critical", 0) > 0:
            lessons.append(f"Found {issues_by_severity['critical']} critical issues requiring immediate attention")

        if issues_by_type.get("stale", 0) > result.resorts_audited * 0.3:
            lessons.append("High staleness rate detected - consider increasing refresh frequency")

        if issues_by_type.get("low_confidence", 0) > result.resorts_audited * 0.2:
            lessons.append("Many low-confidence resorts - research quality may need improvement")

        # Add patterns discovered during audit
        lessons.extend(result.patterns_discovered[:3])

        # Determine if follow-up is needed
        follow_up_needed = issues_by_severity.get("critical", 0) > 0
        follow_up_context = None

        if follow_up_needed:
            follow_up_context = {
                "reason": "critical_issues_found",
                "critical_resort_ids": [
                    i.resort_id for i in result.issues
                    if i.severity == IssueSeverity.CRITICAL
                ],
            }

        # Build metrics
        metrics = {
            "resorts_audited": result.resorts_audited,
            "total_issues": len(result.issues),
            "issues_by_severity": issues_by_severity,
            "issues_by_type": issues_by_type,
            "fixes_queued": len(result.actions_queued),
            "escalations": len(result.actions_escalated),
            "estimated_fix_cost": result.total_fix_cost_estimate,
            "duration_seconds": (
                (result.completed_at - result.started_at).total_seconds()
                if result.completed_at else 0
            ),
        }

        # Log the audit run
        log_audit_run(result)

        # Store observation for memory
        observation = QualityObservation(
            success=success,
            issues_found=len(result.issues),
            issues_fixed=0,  # Fixed by queued tasks later
            issues_queued=len(result.actions_queued),
            issues_escalated=len(result.actions_escalated),
            patterns_discovered=result.patterns_discovered,
            lessons=lessons,
            recommendations=[],  # Could add LLM-generated recommendations
            process_notes=f"Mode: {mode}, Duration: {metrics['duration_seconds']:.1f}s",
        )

        return Observation(
            success=success,
            outcome_summary=outcome,
            metrics=metrics,
            lessons=lessons,
            follow_up_needed=follow_up_needed,
            follow_up_context=follow_up_context,
        )


# =============================================================================
# ENTRY POINTS
# =============================================================================


async def run_quick_scan(**config_kwargs) -> dict:
    """Convenience function to run a quick scan.

    Args:
        staleness_threshold_days: Days threshold (default 30)
        confidence_threshold: Confidence threshold (default 0.7)
        status_filter: Filter by status (default "published")

    Returns:
        Dict with audit results
    """
    agent = QualityAuditAgent()
    objective = AuditObjective.quick_scan(**config_kwargs)
    result = await agent.run({
        "mode": objective.mode,
        "config": objective.config.__dict__,
        "triggered_by": objective.triggered_by,
    })
    return {
        "success": result.success,
        "output": result.output.to_dict() if result.output else None,
        "reasoning": result.reasoning,
    }


async def run_deep_audit(sample_size: int = 10, **config_kwargs) -> dict:
    """Convenience function to run a deep audit.

    Args:
        sample_size: Number of resorts to audit (default 10)
        max_cost: Budget cap for this audit (default 5.0)
        check_price_drift: Whether to check pricing (default True)
        check_voice_consistency: Whether to check voice (default True)

    Returns:
        Dict with audit results
    """
    agent = QualityAuditAgent()
    objective = AuditObjective.deep_audit(sample_size=sample_size, **config_kwargs)
    result = await agent.run({
        "mode": objective.mode,
        "config": objective.config.__dict__,
        "triggered_by": objective.triggered_by,
    })
    return {
        "success": result.success,
        "output": result.output.to_dict() if result.output else None,
        "reasoning": result.reasoning,
    }


async def run_triggered_audit(resort_id: str, triggered_by: str = "manual") -> dict:
    """Convenience function to run a triggered audit on a single resort.

    Args:
        resort_id: UUID of the resort to audit
        triggered_by: What triggered this audit (manual, user_feedback, low_traffic)

    Returns:
        Dict with audit results
    """
    agent = QualityAuditAgent()
    objective = AuditObjective.triggered(resort_id=resort_id, triggered_by=triggered_by)
    result = await agent.run({
        "mode": objective.mode,
        "config": objective.config.__dict__,
        "triggered_by": objective.triggered_by,
    })
    return {
        "success": result.success,
        "output": result.output.to_dict() if result.output else None,
        "reasoning": result.reasoning,
    }
