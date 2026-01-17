"""Autonomous content generation pipeline.

This pipeline runs daily via cron to:
1. Check budget
2. Generate context (what exists, what's needed)
3. Ask Claude to pick resorts to research
4. Run full pipeline for each resort
5. Auto-publish high-confidence content
6. Send daily digest

No MCP overhead - direct Python + Claude API calls.
"""

from .orchestrator import run_daily_pipeline, run_single_resort
from .decision_maker import pick_resorts_to_research
from .runner import run_resort_pipeline

__all__ = [
    "run_daily_pipeline",
    "run_single_resort",
    "pick_resorts_to_research",
    "run_resort_pipeline",
]
