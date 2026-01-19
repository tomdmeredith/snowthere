"""Concrete agent implementations.

Each agent inherits from BaseAgent and implements the think→act→observe pattern
with access to all primitives (capability parity) but guided behavior via
system prompts and approval gates (permission guardrails).

Agents:
- ResearchAgent: Comprehensive data gathering from multiple sources
- ContentAgent: Family-friendly content generation with voice consistency
- QualityAgent: Continuous audit and improvement (quick scan, deep audit, triggered)
- DiscoveryAgent: Content opportunity identification via search demand analysis
- OrchestratorAgent: Daily pipeline coordination and prioritization
"""

# Implemented agents
from .quality_agent import (
    QualityAuditAgent,
    run_quick_scan,
    run_deep_audit,
    run_triggered_audit,
)

# Agents to be implemented
# from .research_agent import ResearchAgent
# from .content_agent import ContentAgent
# from .discovery_agent import DiscoveryAgent
# from .orchestrator_agent import OrchestratorAgent

__all__ = [
    # Quality Audit Agent (implemented)
    "QualityAuditAgent",
    "run_quick_scan",
    "run_deep_audit",
    "run_triggered_audit",
    # Other agents (pending)
    # "ResearchAgent",
    # "ContentAgent",
    # "DiscoveryAgent",
    # "OrchestratorAgent",
]
