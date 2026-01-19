"""AgentMemory - Three-tier memory system for agent learning and context.

Memory Tiers:
1. Working Memory: Current run context (ephemeral, in-memory)
2. Episodic Memory: Past runs with objectives, plans, results (Supabase)
3. Semantic Memory: Learned patterns extracted from episodes (Supabase)

Design Principle: Memory enables agents to learn from experience and
maintain context across runs without explicit programming.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from shared.supabase_client import get_supabase_client
from shared.primitives import learn_from_outcome, LearningOutcome


@dataclass
class Episode:
    """A single agent run stored in episodic memory."""

    run_id: str
    agent_name: str
    objective: dict[str, Any]
    plan: dict[str, Any]
    result: Any
    observation: dict[str, Any]
    success: bool
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Pattern:
    """A learned pattern stored in semantic memory."""

    pattern_id: str
    agent_name: str
    pattern_type: str  # "success", "failure", "optimization"
    description: str
    evidence: list[str]  # run_ids that support this pattern
    confidence: float
    applicable_contexts: list[str]
    recommendation: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_validated: datetime | None = None


class AgentMemory:
    """Three-tier memory system for agents.

    Working Memory: Dict stored in-memory for current run context
    Episodic Memory: Supabase table storing past runs
    Semantic Memory: Supabase table storing learned patterns

    Usage:
        memory = AgentMemory(agent_name="research")

        # Working memory (current run)
        await memory.set_working("current_resort", "Zermatt")
        resort = await memory.get_working("current_resort")

        # Store completed episode
        await memory.store_episode(run_id, objective, plan, result, observation)

        # Recall relevant past episodes
        episodes = await memory.recall_similar({"resort_name": "Zermatt"})

        # Extract patterns periodically
        await memory.extract_patterns()
    """

    def __init__(self, agent_name: str):
        """Initialize memory for an agent.

        Args:
            agent_name: Unique identifier for this agent
        """
        self.agent_name = agent_name
        self._working: dict[str, Any] = {}
        self._client = None

    @property
    def client(self):
        """Lazy-load Supabase client."""
        if self._client is None:
            self._client = get_supabase_client()
        return self._client

    # =========================================================================
    # Working Memory (In-Memory, Current Run)
    # =========================================================================

    async def set_working(self, key: str, value: Any) -> None:
        """Store a value in working memory for current run."""
        self._working[key] = value

    async def get_working(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from working memory."""
        return self._working.get(key, default)

    async def clear_working(self) -> None:
        """Clear all working memory (call at end of run)."""
        self._working.clear()

    # =========================================================================
    # Episodic Memory (Supabase - Past Runs)
    # =========================================================================

    async def store_episode(
        self,
        run_id: str,
        objective: dict[str, Any],
        plan: Any,
        result: Any,
        observation: Any,
    ) -> None:
        """Store a completed run in episodic memory.

        Args:
            run_id: Unique identifier for this run
            objective: The original objective
            plan: The AgentPlan (converted to dict)
            result: The action result
            observation: The Observation (converted to dict)
        """
        # Convert dataclasses to dicts if needed
        plan_dict = plan.__dict__ if hasattr(plan, "__dict__") else plan
        obs_dict = observation.__dict__ if hasattr(observation, "__dict__") else observation

        episode_data = {
            "run_id": run_id,
            "agent_name": self.agent_name,
            "objective": json.dumps(objective, default=str),
            "plan": json.dumps(plan_dict, default=str),
            "result": json.dumps(result, default=str),
            "observation": json.dumps(obs_dict, default=str),
            "success": obs_dict.get("success", False) if isinstance(obs_dict, dict) else False,
        }

        try:
            self.client.table("agent_episodes").insert(episode_data).execute()
        except Exception as e:
            # Log but don't fail - memory is enhancement, not critical path
            print(f"Warning: Failed to store episode: {e}")

    async def recall_episode(self, run_id: str) -> dict[str, Any] | None:
        """Retrieve a specific episode by run_id."""
        try:
            result = (
                self.client.table("agent_episodes")
                .select("*")
                .eq("run_id", run_id)
                .single()
                .execute()
            )
            if result.data:
                return {
                    "run_id": result.data["run_id"],
                    "objective": json.loads(result.data["objective"]),
                    "plan": json.loads(result.data["plan"]),
                    "result": json.loads(result.data["result"]),
                    "observation": json.loads(result.data["observation"]),
                    "success": result.data["success"],
                }
        except Exception:
            pass
        return None

    async def recall_similar(
        self,
        context: dict[str, Any],
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """Recall episodes similar to the given context.

        Uses simple keyword matching for now. Could be enhanced with
        embeddings for semantic similarity.

        Args:
            context: Dict with keys to match (e.g., {"resort_name": "Zermatt"})
            limit: Maximum episodes to return

        Returns:
            List of relevant episodes, most recent first
        """
        try:
            # Get recent episodes for this agent
            result = (
                self.client.table("agent_episodes")
                .select("*")
                .eq("agent_name", self.agent_name)
                .order("created_at", desc=True)
                .limit(50)
                .execute()
            )

            episodes = []
            search_terms = set(str(v).lower() for v in context.values() if v)

            for row in result.data or []:
                # Check if any search terms appear in objective
                objective_str = row.get("objective", "").lower()
                if any(term in objective_str for term in search_terms):
                    episodes.append({
                        "run_id": row["run_id"],
                        "objective": json.loads(row["objective"]),
                        "plan": json.loads(row["plan"]),
                        "result": json.loads(row["result"]),
                        "observation": json.loads(row["observation"]),
                        "success": row["success"],
                    })
                    if len(episodes) >= limit:
                        break

            return episodes

        except Exception:
            return []

    async def recall_successful(self, limit: int = 10) -> list[dict[str, Any]]:
        """Recall recent successful episodes for pattern extraction."""
        try:
            result = (
                self.client.table("agent_episodes")
                .select("*")
                .eq("agent_name", self.agent_name)
                .eq("success", True)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )

            return [
                {
                    "run_id": row["run_id"],
                    "objective": json.loads(row["objective"]),
                    "plan": json.loads(row["plan"]),
                    "result": json.loads(row["result"]),
                    "observation": json.loads(row["observation"]),
                    "success": True,
                }
                for row in (result.data or [])
            ]
        except Exception:
            return []

    # =========================================================================
    # Semantic Memory (Supabase - Learned Patterns)
    # =========================================================================

    async def store_pattern(self, pattern: LearningOutcome, evidence_run_ids: list[str]) -> None:
        """Store a learned pattern in semantic memory.

        Args:
            pattern: LearningOutcome from the learn_from_outcome primitive
            evidence_run_ids: Run IDs that support this pattern
        """
        pattern_data = {
            "agent_name": self.agent_name,
            "pattern_type": pattern.pattern_type,
            "description": pattern.description,
            "evidence": json.dumps(evidence_run_ids),
            "confidence": pattern.confidence,
            "applicable_contexts": json.dumps(pattern.applicable_contexts),
            "recommendation": pattern.recommendation,
        }

        try:
            self.client.table("agent_patterns").insert(pattern_data).execute()
        except Exception as e:
            print(f"Warning: Failed to store pattern: {e}")

    async def recall_patterns(
        self,
        context: str | None = None,
        min_confidence: float = 0.5,
    ) -> list[Pattern]:
        """Recall learned patterns, optionally filtered by context.

        Args:
            context: Optional context to filter applicable patterns
            min_confidence: Minimum confidence threshold

        Returns:
            List of relevant patterns
        """
        try:
            query = (
                self.client.table("agent_patterns")
                .select("*")
                .eq("agent_name", self.agent_name)
                .gte("confidence", min_confidence)
                .order("confidence", desc=True)
            )

            result = query.execute()

            patterns = []
            for row in result.data or []:
                applicable = json.loads(row.get("applicable_contexts", "[]"))
                # Filter by context if provided
                if context and applicable and context.lower() not in [c.lower() for c in applicable]:
                    continue

                patterns.append(Pattern(
                    pattern_id=row["id"],
                    agent_name=row["agent_name"],
                    pattern_type=row["pattern_type"],
                    description=row["description"],
                    evidence=json.loads(row.get("evidence", "[]")),
                    confidence=row["confidence"],
                    applicable_contexts=applicable,
                    recommendation=row.get("recommendation", ""),
                    created_at=datetime.fromisoformat(row["created_at"]) if row.get("created_at") else datetime.utcnow(),
                    last_validated=datetime.fromisoformat(row["last_validated"]) if row.get("last_validated") else None,
                ))

            return patterns

        except Exception:
            return []

    async def extract_patterns(self, min_episodes: int = 5) -> list[LearningOutcome]:
        """Analyze recent episodes to extract new patterns.

        This is called periodically to learn from accumulated experience.

        Args:
            min_episodes: Minimum episodes needed before extraction

        Returns:
            List of newly discovered patterns
        """
        # Get recent successful and failed episodes
        successful = await self.recall_successful(limit=20)
        failed = await self._recall_failed(limit=20)

        if len(successful) + len(failed) < min_episodes:
            return []

        new_patterns = []

        # Learn from successes
        for episode in successful[:5]:  # Analyze top 5
            pattern = await learn_from_outcome(
                action=f"{self.agent_name}_run",
                inputs=episode["objective"],
                result=episode["result"],
                success=True,
            )
            if pattern.confidence >= 0.6:
                new_patterns.append(pattern)
                await self.store_pattern(pattern, [episode["run_id"]])

        # Learn from failures
        for episode in failed[:5]:
            pattern = await learn_from_outcome(
                action=f"{self.agent_name}_run",
                inputs=episode["objective"],
                result=episode["result"],
                success=False,
            )
            if pattern.confidence >= 0.6:
                new_patterns.append(pattern)
                await self.store_pattern(pattern, [episode["run_id"]])

        return new_patterns

    async def _recall_failed(self, limit: int = 10) -> list[dict[str, Any]]:
        """Recall recent failed episodes for pattern extraction."""
        try:
            result = (
                self.client.table("agent_episodes")
                .select("*")
                .eq("agent_name", self.agent_name)
                .eq("success", False)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )

            return [
                {
                    "run_id": row["run_id"],
                    "objective": json.loads(row["objective"]),
                    "plan": json.loads(row["plan"]),
                    "result": json.loads(row["result"]),
                    "observation": json.loads(row["observation"]),
                    "success": False,
                }
                for row in (result.data or [])
            ]
        except Exception:
            return []

    # =========================================================================
    # Convenience Methods
    # =========================================================================

    async def get_context_for_objective(self, objective: dict[str, Any]) -> dict[str, Any]:
        """Get relevant context from memory for a new objective.

        Combines:
        - Similar past episodes
        - Applicable learned patterns
        - Current working memory

        This is called at the start of _think() to inform planning.

        Args:
            objective: The new objective to contextualize

        Returns:
            Dict with relevant memory context
        """
        similar_episodes = await self.recall_similar(objective, limit=3)
        patterns = await self.recall_patterns(min_confidence=0.6)

        return {
            "working_memory": dict(self._working),
            "similar_episodes": similar_episodes,
            "learned_patterns": [
                {
                    "description": p.description,
                    "recommendation": p.recommendation,
                    "confidence": p.confidence,
                }
                for p in patterns[:5]
            ],
        }
