"""BaseAgent - Foundation class with think→act→observe reasoning loops.

Inspired by Claude Agent SDK patterns, this provides the core structure
for agents that can reason about their actions, learn from outcomes,
and coordinate with other agents.

Design Principles:
1. All agents have access to all primitives (capability parity)
2. Behavior is guided by system prompts, not code restrictions
3. Destructive operations go through approval gates
4. All reasoning is logged for observability
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable
from uuid import uuid4

from shared.primitives import log_reasoning, handle_error_intelligently


@dataclass
class AgentPlan:
    """The output of an agent's think phase."""

    steps: list[str]
    reasoning: str
    estimated_cost: float = 0.0
    confidence: float = 0.7
    primitives_needed: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)  # Other agents to coordinate with


@dataclass
class Observation:
    """The output of an agent's observe phase."""

    success: bool
    outcome_summary: str
    metrics: dict[str, Any] = field(default_factory=dict)
    lessons: list[str] = field(default_factory=list)
    follow_up_needed: bool = False
    follow_up_context: dict[str, Any] | None = None


@dataclass
class AgentResult:
    """The complete result of an agent run."""

    run_id: str
    agent_name: str
    success: bool
    output: Any
    reasoning: str
    plan: AgentPlan | None = None
    observation: Observation | None = None
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    cost_incurred: float = 0.0
    error: str | None = None


class BaseAgent(ABC):
    """Base class for all agents with think→act→observe loops.

    Subclasses must implement:
    - _think(objective): Analyze and plan
    - _act(plan): Execute using primitives
    - _observe(result, objective): Evaluate and learn

    Example usage:
        class ResearchAgent(BaseAgent):
            async def _think(self, objective):
                # Analyze what research is needed
                return AgentPlan(steps=[...], reasoning="...")

            async def _act(self, plan):
                # Execute research using primitives
                return {"data": ...}

            async def _observe(self, result, objective):
                # Evaluate research quality
                return Observation(success=True, ...)

        agent = ResearchAgent(name="research")
        result = await agent.run({"resort_name": "Zermatt", "country": "Switzerland"})
    """

    def __init__(
        self,
        name: str,
        primitives: dict[str, Callable] | None = None,
        memory: "AgentMemory | None" = None,
        tracer: "AgentTracer | None" = None,
    ):
        """Initialize the agent.

        Args:
            name: Unique name for this agent (e.g., "research", "content")
            primitives: Dict of primitive_name → function. If None, all primitives are available.
            memory: AgentMemory instance. If None, a new one is created.
            tracer: AgentTracer instance. If None, a new one is created.
        """
        self.name = name
        self.primitives = primitives or self._get_all_primitives()
        # Memory and tracer initialized lazily to avoid circular imports
        self._memory = memory
        self._tracer = tracer

    @property
    def memory(self) -> "AgentMemory":
        """Get or create memory instance."""
        if self._memory is None:
            from .memory import AgentMemory

            self._memory = AgentMemory(agent_name=self.name)
        return self._memory

    @property
    def tracer(self) -> "AgentTracer":
        """Get or create tracer instance."""
        if self._tracer is None:
            from .tracer import AgentTracer

            self._tracer = AgentTracer(agent_name=self.name)
        return self._tracer

    def _get_all_primitives(self) -> dict[str, Callable]:
        """Get all available primitives - capability parity."""
        from shared import primitives as p

        # Return all primitives as a dict
        return {
            name: getattr(p, name)
            for name in dir(p)
            if not name.startswith("_") and callable(getattr(p, name, None))
        }

    async def run(self, objective: dict[str, Any]) -> AgentResult:
        """Main execution loop with think→act→observe pattern.

        Args:
            objective: Dict describing what the agent should accomplish

        Returns:
            AgentResult with outcome, reasoning, and lessons learned
        """
        run_id = str(uuid4())
        started_at = datetime.utcnow()

        # Initialize result
        result = AgentResult(
            run_id=run_id,
            agent_name=self.name,
            success=False,
            output=None,
            reasoning="",
            started_at=started_at,
        )

        # Start tracing
        self.tracer.start_run(run_id, objective)

        try:
            # THINK: Analyze objective and plan approach
            log_reasoning(
                task_id=None,
                agent_name=self.name,
                action="think_start",
                reasoning=f"Starting think phase for objective: {list(objective.keys())}",
                metadata={"run_id": run_id, "objective": objective},
            )

            plan = await self._think(objective)
            self.tracer.log_thinking(plan)
            result.plan = plan

            log_reasoning(
                task_id=None,
                agent_name=self.name,
                action="think_complete",
                reasoning=plan.reasoning,
                metadata={"run_id": run_id, "steps": plan.steps, "confidence": plan.confidence},
            )

            # ACT: Execute plan using primitives
            log_reasoning(
                task_id=None,
                agent_name=self.name,
                action="act_start",
                reasoning=f"Executing {len(plan.steps)} planned steps",
                metadata={"run_id": run_id},
            )

            action_result = await self._act(plan)
            self.tracer.log_action(action_result)
            result.output = action_result

            log_reasoning(
                task_id=None,
                agent_name=self.name,
                action="act_complete",
                reasoning="Action phase completed",
                metadata={"run_id": run_id, "output_type": type(action_result).__name__},
            )

            # OBSERVE: Evaluate outcome and learn
            log_reasoning(
                task_id=None,
                agent_name=self.name,
                action="observe_start",
                reasoning="Evaluating outcome and extracting lessons",
                metadata={"run_id": run_id},
            )

            observation = await self._observe(action_result, objective)
            self.tracer.log_observation(observation)
            result.observation = observation
            result.success = observation.success
            result.reasoning = f"Plan: {plan.reasoning}\nOutcome: {observation.outcome_summary}"

            log_reasoning(
                task_id=None,
                agent_name=self.name,
                action="observe_complete",
                reasoning=observation.outcome_summary,
                metadata={
                    "run_id": run_id,
                    "success": observation.success,
                    "lessons": observation.lessons,
                },
            )

            # Store episode in memory for future learning
            await self.memory.store_episode(
                run_id=run_id,
                objective=objective,
                plan=plan,
                result=action_result,
                observation=observation,
            )

        except Exception as e:
            # Intelligent error handling
            error_context = {
                "agent": self.name,
                "objective": objective,
                "run_id": run_id,
                "stage": self.tracer.current_stage,
            }

            error_handling = await handle_error_intelligently(e, error_context)
            self.tracer.log_error(e, error_handling)

            result.success = False
            result.error = str(e)
            result.reasoning = f"Error during {error_context.get('stage', 'execution')}: {e}"

            log_reasoning(
                task_id=None,
                agent_name=self.name,
                action="error",
                reasoning=f"Agent error: {e}. Action: {error_handling.action}",
                metadata={
                    "run_id": run_id,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "handling": error_handling.action,
                },
            )

            # Re-raise if escalation needed
            if error_handling.action == "escalate":
                raise

        finally:
            result.completed_at = datetime.utcnow()
            self.tracer.end_run(result)

        return result

    @abstractmethod
    async def _think(self, objective: dict[str, Any]) -> AgentPlan:
        """Analyze the objective and create an execution plan.

        This is where the agent reasons about:
        - What information is needed?
        - What steps should be taken?
        - What primitives will be used?
        - What could go wrong?

        Args:
            objective: Dict describing what to accomplish

        Returns:
            AgentPlan with steps, reasoning, and metadata
        """
        pass

    @abstractmethod
    async def _act(self, plan: AgentPlan) -> Any:
        """Execute the plan using available primitives.

        This is where the agent actually does the work:
        - Call primitives in sequence or parallel
        - Handle intermediate results
        - Adapt if things don't go as planned

        Args:
            plan: The AgentPlan from _think()

        Returns:
            The output of the action (structure depends on agent type)
        """
        pass

    @abstractmethod
    async def _observe(self, result: Any, objective: dict[str, Any]) -> Observation:
        """Evaluate the outcome and extract lessons.

        This is where the agent reflects:
        - Did we achieve the objective?
        - What worked well?
        - What could be improved?
        - Should we follow up with another action?

        Args:
            result: The output from _act()
            objective: The original objective for comparison

        Returns:
            Observation with success status, summary, and lessons
        """
        pass

    async def resume(self, run_id: str) -> AgentResult:
        """Resume a previous run using stored memory.

        Useful when an agent was interrupted or needs to continue
        where it left off.

        Args:
            run_id: The run_id to resume

        Returns:
            AgentResult continuing from the previous state
        """
        episode = await self.memory.recall_episode(run_id)
        if not episode:
            raise ValueError(f"No episode found for run_id: {run_id}")

        # Create follow-up objective based on previous observation
        if episode.get("observation", {}).get("follow_up_needed"):
            follow_up_objective = {
                **episode["objective"],
                **episode["observation"].get("follow_up_context", {}),
                "_resumed_from": run_id,
            }
            return await self.run(follow_up_objective)

        # If no follow-up needed, just return the stored result
        return AgentResult(
            run_id=run_id,
            agent_name=self.name,
            success=episode.get("observation", {}).get("success", False),
            output=episode.get("result"),
            reasoning="Resumed from stored episode - no follow-up needed",
        )
