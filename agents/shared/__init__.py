"""Shared utilities for Snowthere agents."""

from .config import settings
from .supabase_client import get_supabase_client

__all__ = ["settings", "get_supabase_client"]
