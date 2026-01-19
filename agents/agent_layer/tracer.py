"""AgentTracer - Observability and distributed tracing for agent execution.

Provides visibility into agent behavior for debugging and improvement.
All spans are persisted to the agent_audit_log table.

Design Principle: Every agent action should be traceable back to its
reasoning, enabling post-hoc analysis and continuous improvement.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from shared.primitives import log_reasoning


@dataclass
class Span:
    """A single traceable unit of work."""

    name: str
    agent_name: str
    run_id: str
    parent_span_id: str | None = None
    span_id: str = ""
    started_at: datetime = field(default_factory=datetime.utcnow)
    ended_at: datetime | None = None
    attributes: dict[str, Any] = field(default_factory=dict)
    events: list[dict[str, Any]] = field(default_factory=list)
    status: str = "running"  # running, completed, error

    @property
    def duration_ms(self) -> float | None:
        """Duration in milliseconds if span has ended."""
        if self.ended_at:
            delta = self.ended_at - self.started_at
            return delta.total_seconds() * 1000
        return None


class AgentTracer:
    """Traces agent execution for observability.

    Creates a tree of spans tracking:
    - Run start/end
    - Think/act/observe phases
    - Primitive calls
    - Errors and recovery

    Usage:
        tracer = AgentTracer(agent_name="research")

        tracer.start_run(run_id, objective)

        tracer.log_thinking(plan)
        tracer.log_action(result)
        tracer.log_observation(observation)

        tracer.end_run(final_result)

        # All spans automatically persisted to agent_audit_log
    """

    def __init__(self, agent_name: str):
        """Initialize tracer for an agent.

        Args:
            agent_name: Unique identifier for this agent
        """
        self.agent_name = agent_name
        self.current_run_id: str | None = None
        self.current_stage: str = "init"
        self.spans: list[Span] = []
        self._span_counter = 0

    def _generate_span_id(self) -> str:
        """Generate a unique span ID."""
        self._span_counter += 1
        return f"{self.current_run_id}:{self._span_counter}"

    def _create_span(
        self,
        name: str,
        parent_span_id: str | None = None,
        attributes: dict[str, Any] | None = None,
    ) -> Span:
        """Create and register a new span."""
        span = Span(
            name=name,
            agent_name=self.agent_name,
            run_id=self.current_run_id or "unknown",
            parent_span_id=parent_span_id,
            span_id=self._generate_span_id(),
            attributes=attributes or {},
        )
        self.spans.append(span)
        return span

    def start_run(self, run_id: str, objective: dict[str, Any]) -> Span:
        """Start tracing a new agent run.

        Args:
            run_id: Unique identifier for this run
            objective: The objective being executed

        Returns:
            The root span for this run
        """
        self.current_run_id = run_id
        self.current_stage = "started"
        self.spans = []
        self._span_counter = 0

        root_span = self._create_span(
            name="agent_run",
            attributes={
                "objective": objective,
                "agent_name": self.agent_name,
            },
        )

        return root_span

    def log_thinking(self, plan: Any) -> Span:
        """Log the think phase.

        Args:
            plan: The AgentPlan produced

        Returns:
            The thinking span
        """
        self.current_stage = "thinking"

        plan_dict = plan.__dict__ if hasattr(plan, "__dict__") else plan

        span = self._create_span(
            name="think",
            parent_span_id=self.spans[0].span_id if self.spans else None,
            attributes={
                "steps": plan_dict.get("steps", []),
                "reasoning": plan_dict.get("reasoning", ""),
                "confidence": plan_dict.get("confidence", 0),
                "primitives_needed": plan_dict.get("primitives_needed", []),
            },
        )
        span.ended_at = datetime.utcnow()
        span.status = "completed"

        return span

    def log_action(self, result: Any) -> Span:
        """Log the act phase.

        Args:
            result: The result of the action

        Returns:
            The action span
        """
        self.current_stage = "acting"

        # Summarize result to avoid huge logs
        result_summary = self._summarize_result(result)

        span = self._create_span(
            name="act",
            parent_span_id=self.spans[0].span_id if self.spans else None,
            attributes={
                "result_type": type(result).__name__,
                "result_summary": result_summary,
            },
        )
        span.ended_at = datetime.utcnow()
        span.status = "completed"

        return span

    def log_observation(self, observation: Any) -> Span:
        """Log the observe phase.

        Args:
            observation: The Observation produced

        Returns:
            The observation span
        """
        self.current_stage = "observing"

        obs_dict = observation.__dict__ if hasattr(observation, "__dict__") else observation

        span = self._create_span(
            name="observe",
            parent_span_id=self.spans[0].span_id if self.spans else None,
            attributes={
                "success": obs_dict.get("success", False),
                "outcome_summary": obs_dict.get("outcome_summary", ""),
                "lessons": obs_dict.get("lessons", []),
                "follow_up_needed": obs_dict.get("follow_up_needed", False),
            },
        )
        span.ended_at = datetime.utcnow()
        span.status = "completed"

        return span

    def log_primitive_call(
        self,
        primitive_name: str,
        inputs: dict[str, Any],
        output: Any,
        duration_ms: float,
    ) -> Span:
        """Log a primitive call within an action.

        Args:
            primitive_name: Name of the primitive called
            inputs: Input arguments
            output: Return value
            duration_ms: How long the call took

        Returns:
            The primitive span
        """
        # Find the act span to parent under
        act_span_id = None
        for span in reversed(self.spans):
            if span.name == "act":
                act_span_id = span.span_id
                break

        span = self._create_span(
            name=f"primitive:{primitive_name}",
            parent_span_id=act_span_id,
            attributes={
                "primitive": primitive_name,
                "inputs": self._summarize_result(inputs),
                "output": self._summarize_result(output),
            },
        )
        span.ended_at = span.started_at  # Immediate for primitive calls
        span.status = "completed"
        span.attributes["duration_ms"] = duration_ms

        return span

    def log_event(self, name: str, attributes: dict[str, Any] | None = None) -> None:
        """Log a point-in-time event within the current stage.

        Args:
            name: Event name (e.g., "retry", "cache_hit", "validation_failed")
            attributes: Event attributes
        """
        if self.spans:
            self.spans[-1].events.append({
                "name": name,
                "timestamp": datetime.utcnow().isoformat(),
                "attributes": attributes or {},
            })

    def log_error(self, error: Exception, handling: Any) -> Span:
        """Log an error and its handling decision.

        Args:
            error: The exception that occurred
            handling: The ErrorHandling decision

        Returns:
            The error span
        """
        self.current_stage = "error"

        handling_dict = handling.__dict__ if hasattr(handling, "__dict__") else handling

        span = self._create_span(
            name="error",
            parent_span_id=self.spans[0].span_id if self.spans else None,
            attributes={
                "error_type": type(error).__name__,
                "error_message": str(error),
                "handling_action": handling_dict.get("action", "unknown"),
                "handling_reasoning": handling_dict.get("reasoning", ""),
                "should_alert": handling_dict.get("should_alert", False),
            },
        )
        span.ended_at = datetime.utcnow()
        span.status = "error"

        return span

    def end_run(self, result: Any) -> None:
        """End the run and persist all spans.

        Args:
            result: The final AgentResult
        """
        self.current_stage = "completed"

        # Close the root span
        if self.spans:
            self.spans[0].ended_at = datetime.utcnow()
            result_dict = result.__dict__ if hasattr(result, "__dict__") else result
            self.spans[0].status = "completed" if result_dict.get("success", False) else "error"
            self.spans[0].attributes["final_success"] = result_dict.get("success", False)

        # Persist all spans to audit log
        self._flush()

    def _flush(self) -> None:
        """Persist all spans to the agent_audit_log table."""
        for span in self.spans:
            try:
                log_reasoning(
                    task_id=None,
                    agent_name=self.agent_name,
                    action=f"trace:{span.name}",
                    reasoning=json.dumps(span.attributes, default=str)[:2000],
                    metadata={
                        "run_id": span.run_id,
                        "span_id": span.span_id,
                        "parent_span_id": span.parent_span_id,
                        "duration_ms": span.duration_ms,
                        "status": span.status,
                        "events": span.events,
                    },
                )
            except Exception as e:
                # Don't let tracing failures break agent execution
                print(f"Warning: Failed to persist span {span.name}: {e}")

    def _summarize_result(self, result: Any, max_length: int = 500) -> str:
        """Create a summary of a result for logging.

        Args:
            result: Any value to summarize
            max_length: Maximum characters in summary

        Returns:
            String summary
        """
        if result is None:
            return "None"

        if isinstance(result, (str, int, float, bool)):
            summary = str(result)
        elif isinstance(result, (list, tuple)):
            summary = f"[{len(result)} items]"
            if result and len(str(result[0])) < 100:
                summary = f"[{len(result)} items, first: {result[0]}]"
        elif isinstance(result, dict):
            keys = list(result.keys())[:5]
            summary = f"{{keys: {keys}{'...' if len(result) > 5 else ''}}}"
        else:
            summary = f"{type(result).__name__}"

        return summary[:max_length]

    def get_trace_summary(self) -> dict[str, Any]:
        """Get a summary of the current trace for debugging.

        Returns:
            Dict with trace overview
        """
        return {
            "run_id": self.current_run_id,
            "agent_name": self.agent_name,
            "current_stage": self.current_stage,
            "span_count": len(self.spans),
            "spans": [
                {
                    "name": s.name,
                    "status": s.status,
                    "duration_ms": s.duration_ms,
                }
                for s in self.spans
            ],
        }
