"""AgentCoordinator - Message passing and coordination between agents.

Enables agents to communicate through a message bus stored in Supabase.
Messages can be requests, responses, or notifications.

Design Principle: Agents should be loosely coupled - they communicate
through messages rather than direct function calls, enabling flexible
orchestration and easy addition of new agents.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from shared.supabase_client import get_supabase_client


class MessageType(Enum):
    """Types of agent-to-agent messages."""

    REQUEST = "request"  # Agent asking another to do something
    RESPONSE = "response"  # Reply to a request
    NOTIFICATION = "notification"  # One-way broadcast (no response expected)
    HANDOFF = "handoff"  # Passing work to another agent


class MessagePriority(Enum):
    """Priority levels for messages."""

    LOW = 1
    NORMAL = 5
    HIGH = 8
    URGENT = 10


@dataclass
class AgentMessage:
    """A message between agents."""

    id: str
    from_agent: str
    to_agent: str
    message_type: MessageType
    payload: dict[str, Any]
    priority: MessagePriority = MessagePriority.NORMAL
    status: str = "pending"  # pending, processing, completed, failed
    correlation_id: str | None = None  # Links request/response pairs
    created_at: datetime = field(default_factory=datetime.utcnow)
    processed_at: datetime | None = None
    response: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict for storage."""
        return {
            "id": self.id,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "message_type": self.message_type.value,
            "payload": json.dumps(self.payload, default=str),
            "priority": self.priority.value,
            "status": self.status,
            "correlation_id": self.correlation_id,
            "response": json.dumps(self.response, default=str) if self.response else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentMessage":
        """Create from storage dict."""
        return cls(
            id=data["id"],
            from_agent=data["from_agent"],
            to_agent=data["to_agent"],
            message_type=MessageType(data["message_type"]),
            payload=json.loads(data["payload"]) if isinstance(data["payload"], str) else data["payload"],
            priority=MessagePriority(data.get("priority", 5)),
            status=data.get("status", "pending"),
            correlation_id=data.get("correlation_id"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.utcnow(),
            processed_at=datetime.fromisoformat(data["processed_at"]) if data.get("processed_at") else None,
            response=json.loads(data["response"]) if data.get("response") else None,
        )


class AgentCoordinator:
    """Coordinates message passing between agents.

    Usage:
        coordinator = AgentCoordinator()

        # Send a request from research to content agent
        msg = await coordinator.send_message(
            from_agent="research",
            to_agent="content",
            message_type=MessageType.HANDOFF,
            payload={"resort_id": "123", "research_data": {...}}
        )

        # Content agent polls for messages
        messages = await coordinator.get_pending_messages("content")
        for msg in messages:
            # Process message
            await coordinator.acknowledge_message(msg.id, response={"status": "completed"})

        # Research agent can check if handoff was processed
        response = await coordinator.get_response(msg.id)
    """

    def __init__(self):
        """Initialize the coordinator."""
        self._client = None

    @property
    def client(self):
        """Lazy-load Supabase client."""
        if self._client is None:
            self._client = get_supabase_client()
        return self._client

    async def send_message(
        self,
        from_agent: str,
        to_agent: str,
        message_type: MessageType,
        payload: dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
        correlation_id: str | None = None,
    ) -> AgentMessage:
        """Send a message to another agent.

        Args:
            from_agent: Sending agent name
            to_agent: Receiving agent name
            message_type: Type of message
            payload: Message content
            priority: Message priority
            correlation_id: Optional ID linking related messages

        Returns:
            The created AgentMessage
        """
        message = AgentMessage(
            id=str(uuid4()),
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=message_type,
            payload=payload,
            priority=priority,
            correlation_id=correlation_id or str(uuid4()),
        )

        try:
            self.client.table("agent_messages").insert(message.to_dict()).execute()
        except Exception as e:
            print(f"Warning: Failed to send message: {e}")
            # Continue anyway - message sending shouldn't block execution
            message.status = "failed"

        return message

    async def get_pending_messages(
        self,
        agent_name: str,
        limit: int = 10,
    ) -> list[AgentMessage]:
        """Get pending messages for an agent.

        Args:
            agent_name: Agent to get messages for
            limit: Maximum messages to return

        Returns:
            List of pending messages, highest priority first
        """
        try:
            result = (
                self.client.table("agent_messages")
                .select("*")
                .eq("to_agent", agent_name)
                .eq("status", "pending")
                .order("priority", desc=True)
                .order("created_at", desc=False)
                .limit(limit)
                .execute()
            )

            return [AgentMessage.from_dict(row) for row in (result.data or [])]
        except Exception as e:
            print(f"Warning: Failed to get messages: {e}")
            return []

    async def acknowledge_message(
        self,
        message_id: str,
        response: dict[str, Any] | None = None,
        status: str = "completed",
    ) -> bool:
        """Acknowledge processing of a message.

        Args:
            message_id: ID of the message
            response: Optional response data
            status: New status (completed, failed)

        Returns:
            True if update succeeded
        """
        try:
            update_data = {
                "status": status,
                "processed_at": datetime.utcnow().isoformat(),
            }
            if response:
                update_data["response"] = json.dumps(response, default=str)

            self.client.table("agent_messages").update(update_data).eq("id", message_id).execute()
            return True
        except Exception as e:
            print(f"Warning: Failed to acknowledge message: {e}")
            return False

    async def get_response(
        self,
        message_id: str,
        timeout_seconds: int = 30,
    ) -> dict[str, Any] | None:
        """Wait for a response to a message.

        Args:
            message_id: ID of the message to get response for
            timeout_seconds: How long to wait (polling)

        Returns:
            Response payload or None if timeout/not found
        """
        import asyncio

        poll_interval = 1.0  # seconds
        elapsed = 0.0

        while elapsed < timeout_seconds:
            try:
                result = (
                    self.client.table("agent_messages")
                    .select("status, response")
                    .eq("id", message_id)
                    .single()
                    .execute()
                )

                if result.data and result.data.get("status") in ("completed", "failed"):
                    response = result.data.get("response")
                    if response and isinstance(response, str):
                        return json.loads(response)
                    return response

            except Exception:
                pass

            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

        return None

    async def broadcast(
        self,
        from_agent: str,
        payload: dict[str, Any],
        exclude_agents: list[str] | None = None,
    ) -> list[AgentMessage]:
        """Broadcast a notification to all agents.

        Args:
            from_agent: Sending agent name
            payload: Message content
            exclude_agents: Agents to exclude from broadcast

        Returns:
            List of created messages
        """
        # Get all known agents (could be from a registry in the future)
        known_agents = ["research", "content", "quality", "discovery", "orchestrator"]
        exclude = set(exclude_agents or [])
        exclude.add(from_agent)  # Don't send to self

        messages = []
        for agent in known_agents:
            if agent not in exclude:
                msg = await self.send_message(
                    from_agent=from_agent,
                    to_agent=agent,
                    message_type=MessageType.NOTIFICATION,
                    payload=payload,
                    priority=MessagePriority.LOW,
                )
                messages.append(msg)

        return messages

    # =========================================================================
    # Common Message Patterns
    # =========================================================================

    async def request_research(
        self,
        from_agent: str,
        resort_name: str,
        country: str,
        priority: MessagePriority = MessagePriority.NORMAL,
    ) -> AgentMessage:
        """Request research for a resort.

        Args:
            from_agent: Requesting agent
            resort_name: Name of resort to research
            country: Country the resort is in
            priority: Request priority

        Returns:
            The request message
        """
        return await self.send_message(
            from_agent=from_agent,
            to_agent="research",
            message_type=MessageType.REQUEST,
            payload={
                "action": "research_resort",
                "resort_name": resort_name,
                "country": country,
            },
            priority=priority,
        )

    async def handoff_to_content(
        self,
        from_agent: str,
        resort_id: str,
        research_data: dict[str, Any],
        confidence: float,
    ) -> AgentMessage:
        """Hand off research data to content agent.

        Args:
            from_agent: Handing off agent (usually research)
            resort_id: Resort ID in database
            research_data: Compiled research
            confidence: Research confidence score

        Returns:
            The handoff message
        """
        return await self.send_message(
            from_agent=from_agent,
            to_agent="content",
            message_type=MessageType.HANDOFF,
            payload={
                "action": "generate_content",
                "resort_id": resort_id,
                "research_data": research_data,
                "confidence": confidence,
            },
            priority=MessagePriority.HIGH,
        )

    async def report_quality_issue(
        self,
        from_agent: str,
        resort_id: str,
        issue_type: str,
        severity: str,
        details: str,
    ) -> AgentMessage:
        """Report a quality issue to the orchestrator.

        Args:
            from_agent: Reporting agent (usually quality)
            resort_id: Affected resort
            issue_type: Type of issue (stale, incomplete, etc.)
            severity: Issue severity (low, medium, high, critical)
            details: Description of the issue

        Returns:
            The notification message
        """
        return await self.send_message(
            from_agent=from_agent,
            to_agent="orchestrator",
            message_type=MessageType.NOTIFICATION,
            payload={
                "type": "quality_issue",
                "resort_id": resort_id,
                "issue_type": issue_type,
                "severity": severity,
                "details": details,
                "action_requested": "re_research" if severity in ("high", "critical") else "review",
            },
            priority=MessagePriority.HIGH if severity in ("high", "critical") else MessagePriority.NORMAL,
        )

    async def suggest_new_content(
        self,
        from_agent: str,
        content_type: str,
        target: dict[str, Any],
        reasoning: str,
        priority_score: float,
    ) -> AgentMessage:
        """Suggest new content to the orchestrator.

        Args:
            from_agent: Suggesting agent (usually discovery)
            content_type: Type of content (resort, comparison, guide)
            target: What to create (resort info, comparison subjects, etc.)
            reasoning: Why this should be created
            priority_score: How important (0-1)

        Returns:
            The notification message
        """
        priority = MessagePriority.HIGH if priority_score > 0.8 else MessagePriority.NORMAL

        return await self.send_message(
            from_agent=from_agent,
            to_agent="orchestrator",
            message_type=MessageType.NOTIFICATION,
            payload={
                "type": "new_opportunity",
                "content_type": content_type,
                "target": target,
                "reasoning": reasoning,
                "priority_score": priority_score,
            },
            priority=priority,
        )
