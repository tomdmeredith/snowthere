"""MCP Server for Snowthere primitives.

Exposes all 50+ atomic primitives as MCP tools, enabling Claude Code
to orchestrate content creation autonomously.
"""

from .server import mcp

__all__ = ["mcp"]
