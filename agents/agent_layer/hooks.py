"""AgentHooks - Human intervention points for agent execution.

Provides controllable pause points where humans can review, approve,
or redirect agent behavior. Hooks can be triggered automatically based
on conditions or manually by operators.

Design Principle: Agents should be autonomous but not opaque. Hooks
enable human oversight without blocking normal operation.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable
from uuid import uuid4

from shared.supabase_client import get_supabase_client


class HookType(Enum):
    """Types of intervention hooks."""

    PRE_RESEARCH = "pre_research"  # Review search plan before executing
    POST_RESEARCH = "post_research"  # Review gathered data before content generation
    POST_CONTENT = "post_content"  # Review generated content before storage
    PRE_PUBLISH = "pre_publish"  # Final approval before going live
    ON_LOW_CONFIDENCE = "on_low_confidence"  # Agent is uncertain, requesting guidance
    ON_ERROR = "on_error"  # Something failed, human decision needed
    ON_QUALITY_ISSUE = "on_quality_issue"  # Quality agent found a problem
    ON_HIGH_COST = "on_high_cost"  # Operation exceeds cost threshold


class HookAction(Enum):
    """Actions that can be taken at a hook."""

    CONTINUE = "continue"  # Proceed with normal flow
    PAUSE = "pause"  # Wait for human input
    ABORT = "abort"  # Stop execution
    MODIFY = "modify"  # Use modified data provided by human
    SKIP = "skip"  # Skip this step and continue
    RETRY = "retry"  # Retry the previous operation


@dataclass
class HookResult:
    """Result of a hook check."""

    hook_type: HookType
    action: HookAction
    should_pause: bool = False
    human_input: dict[str, Any] | None = None
    modified_data: dict[str, Any] | None = None
    message: str = ""
    wait_id: str | None = None  # ID for async waiting


@dataclass
class HookConfig:
    """Configuration for a hook."""

    hook_type: HookType
    enabled: bool = True
    auto_approve: bool = False  # Skip if confidence > threshold
    confidence_threshold: float = 0.8
    cost_threshold: float = 1.0  # In dollars
    timeout_minutes: int = 60  # How long to wait for human
    notification_channels: list[str] = field(default_factory=list)  # slack, email


@dataclass
class PendingApproval:
    """A hook waiting for human approval."""

    id: str
    hook_type: HookType
    agent_name: str
    run_id: str
    context: dict[str, Any]
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime | None = None
    status: str = "pending"  # pending, approved, rejected, expired
    resolved_by: str | None = None
    resolved_at: datetime | None = None
    resolution_notes: str | None = None


class HookRegistry:
    """Manages intervention hooks for agent execution.

    Usage:
        registry = HookRegistry(agent_name="research")

        # Check if hook should pause
        result = await registry.check_hook(
            HookType.PRE_RESEARCH,
            context={"resort": "Zermatt", "search_plan": [...]}
        )

        if result.should_pause:
            # Wait for human or continue based on config
            result = await registry.wait_for_approval(result.wait_id)

        if result.action == HookAction.CONTINUE:
            # Proceed with execution
            pass
        elif result.action == HookAction.MODIFY:
            # Use modified data
            search_plan = result.modified_data["search_plan"]
    """

    # Default hook configurations
    DEFAULT_CONFIGS = {
        HookType.PRE_RESEARCH: HookConfig(
            hook_type=HookType.PRE_RESEARCH,
            enabled=False,  # Usually auto-approve
            auto_approve=True,
        ),
        HookType.POST_RESEARCH: HookConfig(
            hook_type=HookType.POST_RESEARCH,
            enabled=True,
            auto_approve=True,
            confidence_threshold=0.7,
        ),
        HookType.POST_CONTENT: HookConfig(
            hook_type=HookType.POST_CONTENT,
            enabled=True,
            auto_approve=True,
            confidence_threshold=0.8,
        ),
        HookType.PRE_PUBLISH: HookConfig(
            hook_type=HookType.PRE_PUBLISH,
            enabled=True,
            auto_approve=True,
            confidence_threshold=0.8,
        ),
        HookType.ON_LOW_CONFIDENCE: HookConfig(
            hook_type=HookType.ON_LOW_CONFIDENCE,
            enabled=True,
            auto_approve=False,  # Always pause for low confidence
        ),
        HookType.ON_ERROR: HookConfig(
            hook_type=HookType.ON_ERROR,
            enabled=True,
            auto_approve=False,  # Always pause on errors
        ),
        HookType.ON_QUALITY_ISSUE: HookConfig(
            hook_type=HookType.ON_QUALITY_ISSUE,
            enabled=True,
            auto_approve=False,
        ),
        HookType.ON_HIGH_COST: HookConfig(
            hook_type=HookType.ON_HIGH_COST,
            enabled=True,
            auto_approve=False,
            cost_threshold=5.0,  # $5 threshold
        ),
    }

    def __init__(
        self,
        agent_name: str,
        configs: dict[HookType, HookConfig] | None = None,
        notifiers: dict[str, Callable] | None = None,
    ):
        """Initialize hook registry for an agent.

        Args:
            agent_name: Name of the agent using this registry
            configs: Custom hook configurations (merged with defaults)
            notifiers: Dict of channel_name → notification function
        """
        self.agent_name = agent_name
        self.configs = {**self.DEFAULT_CONFIGS, **(configs or {})}
        self.notifiers = notifiers or {}
        self._client = None

    @property
    def client(self):
        """Lazy-load Supabase client."""
        if self._client is None:
            self._client = get_supabase_client()
        return self._client

    async def check_hook(
        self,
        hook_type: HookType,
        context: dict[str, Any],
        confidence: float | None = None,
        cost: float | None = None,
    ) -> HookResult:
        """Check if a hook should pause execution.

        Args:
            hook_type: Type of hook to check
            context: Relevant context for the hook
            confidence: Current confidence score (if applicable)
            cost: Current/estimated cost (if applicable)

        Returns:
            HookResult indicating what action to take
        """
        config = self.configs.get(hook_type, HookConfig(hook_type=hook_type))

        # Hook disabled
        if not config.enabled:
            return HookResult(
                hook_type=hook_type,
                action=HookAction.CONTINUE,
                should_pause=False,
                message="Hook disabled",
            )

        # Auto-approve based on confidence
        if config.auto_approve and confidence is not None:
            if confidence >= config.confidence_threshold:
                return HookResult(
                    hook_type=hook_type,
                    action=HookAction.CONTINUE,
                    should_pause=False,
                    message=f"Auto-approved: confidence {confidence:.2f} >= threshold {config.confidence_threshold}",
                )

        # Check cost threshold
        if hook_type == HookType.ON_HIGH_COST and cost is not None:
            if cost < config.cost_threshold:
                return HookResult(
                    hook_type=hook_type,
                    action=HookAction.CONTINUE,
                    should_pause=False,
                    message=f"Cost ${cost:.2f} below threshold ${config.cost_threshold:.2f}",
                )

        # Need human approval - create pending approval
        approval = await self._create_pending_approval(hook_type, context, config)

        # Send notifications
        await self._notify(hook_type, approval, context)

        return HookResult(
            hook_type=hook_type,
            action=HookAction.PAUSE,
            should_pause=True,
            wait_id=approval.id,
            message=f"Waiting for human approval: {hook_type.value}",
        )

    async def _create_pending_approval(
        self,
        hook_type: HookType,
        context: dict[str, Any],
        config: HookConfig,
    ) -> PendingApproval:
        """Create a pending approval record."""
        approval = PendingApproval(
            id=str(uuid4()),
            hook_type=hook_type,
            agent_name=self.agent_name,
            run_id=context.get("run_id", "unknown"),
            context=context,
            expires_at=datetime.utcnow() + timedelta(minutes=config.timeout_minutes) if config.timeout_minutes else None,
        )

        try:
            self.client.table("agent_pending_approvals").insert({
                "id": approval.id,
                "hook_type": hook_type.value,
                "agent_name": self.agent_name,
                "run_id": approval.run_id,
                "context": json.dumps(context, default=str),
                "status": "pending",
                "expires_at": approval.expires_at.isoformat() if approval.expires_at else None,
            }).execute()
        except Exception as e:
            print(f"Warning: Failed to persist pending approval: {e}")

        return approval

    async def _notify(
        self,
        hook_type: HookType,
        approval: PendingApproval,
        context: dict[str, Any],
    ) -> None:
        """Send notifications for a pending approval."""
        config = self.configs.get(hook_type)
        if not config:
            return

        for channel in config.notification_channels:
            notifier = self.notifiers.get(channel)
            if notifier:
                try:
                    await notifier({
                        "hook_type": hook_type.value,
                        "approval_id": approval.id,
                        "agent_name": self.agent_name,
                        "context": context,
                        "expires_at": approval.expires_at.isoformat() if approval.expires_at else None,
                    })
                except Exception as e:
                    print(f"Warning: Failed to notify via {channel}: {e}")

    async def wait_for_approval(
        self,
        approval_id: str,
        timeout_seconds: int = 300,
        poll_interval: float = 5.0,
    ) -> HookResult:
        """Wait for human approval with polling.

        Args:
            approval_id: ID of the pending approval
            timeout_seconds: How long to wait before timeout
            poll_interval: Seconds between polls

        Returns:
            HookResult with the human's decision
        """
        import asyncio

        elapsed = 0.0

        while elapsed < timeout_seconds:
            try:
                result = (
                    self.client.table("agent_pending_approvals")
                    .select("*")
                    .eq("id", approval_id)
                    .single()
                    .execute()
                )

                if result.data:
                    status = result.data.get("status", "pending")

                    if status == "approved":
                        modified = result.data.get("modified_data")
                        return HookResult(
                            hook_type=HookType(result.data["hook_type"]),
                            action=HookAction.CONTINUE if not modified else HookAction.MODIFY,
                            should_pause=False,
                            modified_data=json.loads(modified) if modified else None,
                            message=result.data.get("resolution_notes", "Approved"),
                        )
                    elif status == "rejected":
                        return HookResult(
                            hook_type=HookType(result.data["hook_type"]),
                            action=HookAction.ABORT,
                            should_pause=False,
                            message=result.data.get("resolution_notes", "Rejected by human"),
                        )
                    elif status == "skip":
                        return HookResult(
                            hook_type=HookType(result.data["hook_type"]),
                            action=HookAction.SKIP,
                            should_pause=False,
                            message=result.data.get("resolution_notes", "Skipped by human"),
                        )
                    elif status == "expired":
                        return HookResult(
                            hook_type=HookType(result.data["hook_type"]),
                            action=HookAction.CONTINUE,
                            should_pause=False,
                            message="Approval expired, continuing with default behavior",
                        )

            except Exception:
                pass

            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

        # Timeout - mark as expired and continue
        await self._expire_approval(approval_id)

        return HookResult(
            hook_type=HookType.PRE_RESEARCH,  # Generic
            action=HookAction.CONTINUE,
            should_pause=False,
            message="Approval timeout, continuing with default behavior",
        )

    async def _expire_approval(self, approval_id: str) -> None:
        """Mark an approval as expired."""
        try:
            self.client.table("agent_pending_approvals").update({
                "status": "expired",
                "resolved_at": datetime.utcnow().isoformat(),
            }).eq("id", approval_id).execute()
        except Exception as e:
            print(f"Warning: Failed to expire approval: {e}")

    async def approve(
        self,
        approval_id: str,
        approved_by: str,
        notes: str = "",
        modified_data: dict[str, Any] | None = None,
    ) -> bool:
        """Approve a pending approval.

        Args:
            approval_id: ID of the pending approval
            approved_by: Who approved (user ID or name)
            notes: Optional notes
            modified_data: Optional modified data to use instead

        Returns:
            True if update succeeded
        """
        try:
            update_data = {
                "status": "approved",
                "resolved_by": approved_by,
                "resolved_at": datetime.utcnow().isoformat(),
                "resolution_notes": notes,
            }
            if modified_data:
                update_data["modified_data"] = json.dumps(modified_data, default=str)

            self.client.table("agent_pending_approvals").update(update_data).eq("id", approval_id).execute()
            return True
        except Exception as e:
            print(f"Warning: Failed to approve: {e}")
            return False

    async def reject(
        self,
        approval_id: str,
        rejected_by: str,
        reason: str = "",
    ) -> bool:
        """Reject a pending approval.

        Args:
            approval_id: ID of the pending approval
            rejected_by: Who rejected
            reason: Why rejected

        Returns:
            True if update succeeded
        """
        try:
            self.client.table("agent_pending_approvals").update({
                "status": "rejected",
                "resolved_by": rejected_by,
                "resolved_at": datetime.utcnow().isoformat(),
                "resolution_notes": reason,
            }).eq("id", approval_id).execute()
            return True
        except Exception as e:
            print(f"Warning: Failed to reject: {e}")
            return False

    async def list_pending(self, include_expired: bool = False) -> list[PendingApproval]:
        """List pending approvals for this agent.

        Args:
            include_expired: Whether to include expired approvals

        Returns:
            List of pending approvals
        """
        try:
            query = (
                self.client.table("agent_pending_approvals")
                .select("*")
                .eq("agent_name", self.agent_name)
            )

            if not include_expired:
                query = query.eq("status", "pending")

            result = query.order("created_at", desc=True).execute()

            return [
                PendingApproval(
                    id=row["id"],
                    hook_type=HookType(row["hook_type"]),
                    agent_name=row["agent_name"],
                    run_id=row["run_id"],
                    context=json.loads(row["context"]) if row.get("context") else {},
                    created_at=datetime.fromisoformat(row["created_at"]) if row.get("created_at") else datetime.utcnow(),
                    expires_at=datetime.fromisoformat(row["expires_at"]) if row.get("expires_at") else None,
                    status=row.get("status", "pending"),
                    resolved_by=row.get("resolved_by"),
                    resolved_at=datetime.fromisoformat(row["resolved_at"]) if row.get("resolved_at") else None,
                    resolution_notes=row.get("resolution_notes"),
                )
                for row in (result.data or [])
            ]
        except Exception as e:
            print(f"Warning: Failed to list pending approvals: {e}")
            return []


# Import timedelta at module level
from datetime import timedelta


# =========================================================================
# Convenience Functions for Common Hook Patterns
# =========================================================================


async def require_human_approval(
    agent_name: str,
    hook_type: HookType,
    context: dict[str, Any],
    timeout_minutes: int = 60,
) -> HookResult:
    """Convenience function to require human approval.

    Args:
        agent_name: Name of the agent
        hook_type: Type of hook
        context: Context for the approval
        timeout_minutes: How long to wait

    Returns:
        HookResult with the decision
    """
    registry = HookRegistry(agent_name)

    # Override config to always require approval
    registry.configs[hook_type] = HookConfig(
        hook_type=hook_type,
        enabled=True,
        auto_approve=False,
        timeout_minutes=timeout_minutes,
    )

    result = await registry.check_hook(hook_type, context)

    if result.should_pause and result.wait_id:
        result = await registry.wait_for_approval(
            result.wait_id,
            timeout_seconds=timeout_minutes * 60,
        )

    return result


async def check_publish_approval(
    agent_name: str,
    resort_id: str,
    content_preview: dict[str, Any],
    confidence: float,
) -> HookResult:
    """Check if content can be published.

    Args:
        agent_name: Agent requesting publish
        resort_id: Resort being published
        content_preview: Preview of content to publish
        confidence: Confidence score

    Returns:
        HookResult with publish decision
    """
    registry = HookRegistry(agent_name)

    return await registry.check_hook(
        HookType.PRE_PUBLISH,
        context={
            "resort_id": resort_id,
            "content_preview": content_preview,
        },
        confidence=confidence,
    )
