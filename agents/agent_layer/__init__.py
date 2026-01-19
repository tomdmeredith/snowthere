"""Agent Layer - True agents with think→act→observe loops.

This layer transforms the primitive-based system into true Agent Native
architecture with reasoning loops, memory, and coordination.

Components:
- BaseAgent: Foundation class with think→act→observe pattern
- AgentMemory: Three-tier memory (working, episodic, semantic)
- AgentTracer: Observability and distributed tracing
- AgentCoordinator: Message passing between agents
- Hooks: Human intervention points

Agents:
- ResearchAgent: Gather comprehensive resort data
- ContentAgent: Generate family-friendly content
- QualityAgent: Continuous quality audit and improvement
- DiscoveryAgent: Find new content opportunities
- OrchestratorAgent: Coordinate daily pipeline execution

Design Principle: All agents CAN access all primitives (capability parity),
but behavior is guided by system prompts and controlled by approval gates.
"""

from .base import BaseAgent, AgentPlan, AgentResult, Observation
from .memory import AgentMemory
from .tracer import AgentTracer, Span
from .coordinator import AgentCoordinator, AgentMessage
from .hooks import HookRegistry, HookResult

__all__ = [
    # Base
    "BaseAgent",
    "AgentPlan",
    "AgentResult",
    "Observation",
    # Memory
    "AgentMemory",
    # Tracer
    "AgentTracer",
    "Span",
    # Coordinator
    "AgentCoordinator",
    "AgentMessage",
    # Hooks
    "HookRegistry",
    "HookResult",
]
