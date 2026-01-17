# Snowthere MCP Server

MCP (Model Context Protocol) server that exposes all Snowthere primitives as tools for Claude Code orchestration.

## Overview

This server enables Claude Code to autonomously:
- Research ski resorts using Exa, SerpAPI, and Tavily
- Generate family-focused content in "instagram mom" voice
- Manage the resort database (CRUD operations)
- Handle publication lifecycle
- Track costs and maintain audit logs

## 55 Tools Available

### Research (5)
- `tool_exa_search` - Semantic search via Exa
- `tool_serp_search` - Google search via SerpAPI
- `tool_tavily_search` - AI-powered web research
- `tool_search_resort_info` - Comprehensive multi-source research
- `tool_scrape_url` - Fetch and parse URLs

### Content (4)
- `tool_write_section` - Generate content sections
- `tool_generate_faq` - Create FAQ sections
- `tool_apply_voice` - Transform content voice
- `tool_generate_seo_meta` - SEO metadata

### Database - Resorts (8)
- `tool_list_resorts` - List/filter resorts
- `tool_get_resort` - Get by ID
- `tool_get_resort_by_slug` - Get by URL slug
- `tool_create_resort` - Create new resort
- `tool_update_resort` - Update resort info
- `tool_delete_resort` - Delete resort
- `tool_search_resorts` - Search resorts
- `tool_get_resort_full` - Get complete resort data

### Database - Content & Metrics (10)
- `tool_get_resort_content` / `tool_update_resort_content`
- `tool_get_resort_costs` / `tool_update_resort_costs`
- `tool_get_resort_family_metrics` / `tool_update_resort_family_metrics`
- `tool_list_ski_passes` / `tool_get_ski_pass` / etc.
- `tool_get_resort_calendar` / `tool_update_resort_calendar`

### Publishing (11)
- `tool_publish_resort` - Set status to published
- `tool_unpublish_resort` - Revert to draft
- `tool_archive_resort` - Soft delete
- `tool_restore_resort` - Restore archived
- `tool_revalidate_*` - Trigger Vercel ISR
- `tool_get_publish_candidates` - Find ready drafts
- `tool_get_stale_resorts` - Find outdated content

### System (14)
- Cost tracking: `tool_log_cost`, `tool_get_daily_spend`, `tool_check_budget`
- Audit: `tool_log_reasoning`, `tool_read_audit_log`
- Queue: `tool_queue_task`, `tool_get_next_task`, `tool_update_task_status`

## Installation

### Prerequisites

```bash
# From agents/ directory
pip install -r requirements.txt

# Or with UV
uv sync
```

### Add to Claude Code

**Option 1: Stdio Transport (Recommended for local)**

```bash
claude mcp add snowthere -- python -m mcp_server.server
```

**Option 2: HTTP Transport (For remote/shared)**

```bash
# Start server
python -m mcp_server.server --transport streamable-http --port 8000

# Add to Claude Code
claude mcp add --transport http snowthere http://localhost:8000/mcp
```

## Configuration

Required environment variables (in `.env`):

```bash
# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=eyJ...

# Research APIs
EXA_API_KEY=xxx
SERPAPI_API_KEY=xxx
TAVILY_API_KEY=xxx

# AI
ANTHROPIC_API_KEY=xxx

# Vercel (optional, for revalidation)
VERCEL_URL=https://snowthere.vercel.app
VERCEL_REVALIDATE_TOKEN=xxx
```

## Usage Examples

Once added to Claude Code, you can use natural language:

### Research a Resort
```
Research Park City ski resort in Utah. Gather info about family-friendliness,
prices, terrain, and parent reviews.
```

### Generate Content
```
Using the research data, generate a complete family ski guide for Park City
in instagram_mom voice. Include all sections: quick_take, getting_there,
where_to_stay, lift_tickets, on_mountain, off_mountain, and FAQ.
```

### Manage Publication
```
Show me all draft resorts that are ready to publish (confidence > 0.7).
```

### Check System Status
```
What's our daily API spend? Show me the cost breakdown by API.
```

### Full Pipeline
```
Complete pipeline for Zermatt, Switzerland:
1. Research the resort comprehensively
2. Generate all content sections
3. Store in database
4. If confidence > 0.8, publish automatically
5. Log all reasoning
```

## Autonomous Operation

The server is designed for autonomous operation:

1. **Budget Enforcement**: Use `tool_check_budget` before expensive operations
2. **Confidence Scoring**: Research returns confidence scores for auto-publish decisions
3. **Audit Trail**: All actions logged via `tool_log_reasoning`
4. **Queue Management**: Tasks can be queued and processed autonomously

## Voice Profiles

Available voice profiles for content generation:

| Profile | Tone | Best For |
|---------|------|----------|
| `instagram_mom` | Encouraging, relatable | Resort pages, comparisons |
| `practical_mom` | No-nonsense, budget-focused | Pass guides, itineraries |
| `excited_mom` | Enthusiastic, inspirational | Topic guides, listicles |
| `budget_mom` | Cost-focused, value-oriented | Budget content |

## Architecture

```
Claude Code (Orchestrator)
    │
    ├── MCP Protocol
    │
    ▼
MCP Server (this)
    │
    ├── Research Primitives → Exa, SerpAPI, Tavily
    ├── Content Primitives → Claude API
    ├── Database Primitives → Supabase
    ├── Publishing Primitives → Vercel ISR
    └── System Primitives → Logging, Queue
```

## Development

```bash
# Run with debug output
python -m mcp_server.server --debug

# Test with MCP Inspector
npx -y @modelcontextprotocol/inspector

# Then connect to: stdio:python -m mcp_server.server
```
