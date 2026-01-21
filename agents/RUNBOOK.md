# Snowthere Agent Pipeline - Runbook

Operations guide for the autonomous content generation pipeline.

## Table of Contents

- [Environment Setup](#environment-setup)
- [Manual Steps](#manual-steps)
- [Daily Operations](#daily-operations)
- [Troubleshooting](#troubleshooting)
- [Railway Configuration](#railway-configuration)

---

## Environment Setup

### Required Environment Variables

```bash
# Supabase (Required)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key

# AI APIs (Required)
ANTHROPIC_API_KEY=sk-ant-...

# Research APIs (Required - at least one)
EXA_API_KEY=your-exa-key
BRAVE_API_KEY=your-brave-key
TAVILY_API_KEY=your-tavily-key

# Image Generation (Optional - enables UGC photos)
GOOGLE_API_KEY=your-google-key              # For Gemini image gen
GOOGLE_PLACES_API_KEY=your-places-key       # For UGC photos (can be same as GOOGLE_API_KEY)
REPLICATE_API_TOKEN=your-replicate-token    # Fallback image generation

# Publishing (Required for ISR)
VERCEL_URL=https://www.snowthere.com
VERCEL_REVALIDATE_TOKEN=your-token

# Budget Controls
DAILY_BUDGET_LIMIT=5.00                     # Default: $5.00
```

### Verify Railway Environment

Check Railway dashboard for these variables:
- `GOOGLE_PLACES_API_KEY` or `GOOGLE_API_KEY` (may explain Google Places failures)
- `DAILY_BUDGET_LIMIT` (if not set, defaults to $5.00)

---

## Manual Steps

### Create Storage Bucket (One-time Setup)

The `resort-images` bucket is required for storing AI-generated images and UGC photos.

1. Go to Supabase Dashboard → Storage
2. Click "New bucket"
3. Configure:
   - **Name:** `resort-images`
   - **Public:** Yes
   - **File size limit:** 5MB
   - **Allowed MIME types:** `image/png, image/jpeg, image/webp`
4. Click "Create bucket"

### Apply Database Migrations

If trail map data isn't being saved, verify migration 004 is applied:

```sql
-- Check if trail_map_data column exists
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'resorts'
AND column_name = 'trail_map_data';
```

If not present, apply migration manually or via Supabase CLI:
```bash
supabase db push
```

---

## Daily Operations

### Running the Pipeline

```bash
# Navigate to agents directory
cd agents

# Daily pipeline (up to 4 resorts)
python cron.py

# Limit to fewer resorts
python cron.py --max-resorts 2

# Dry run (see what would happen)
python cron.py --dry-run

# Single resort (manual trigger)
python cron.py --resort "Zermatt" --country "Switzerland"

# Use mixed selection (discovery + stale + queue)
python cron.py --use-mixed-selection

# Run discovery first
python cron.py --run-discovery
```

### Monitoring

Check Railway logs for:
- `✓ Published with issues` - Resort published but queued for improvement
- `✓ Approval Panel: APPROVED` - Clean publish
- `Extracted coordinates:` - Nominatim working
- `Sources: X` in approval panel - Source passing working

### Cost Monitoring

Daily spend is tracked in `agent_cost_log` table. Check current spend:
```sql
SELECT SUM(amount) as total, date(created_at) as day
FROM agent_cost_log
WHERE created_at > NOW() - INTERVAL '1 day'
GROUP BY day;
```

---

## Troubleshooting

### "No sources provided" in Approval Panel

**Symptom:** TrustGuard always votes IMPROVE because no sources provided.

**Fix:** Verify `flatten_sources()` is being called. Check `research.py`:
```python
organized["sources"] = flatten_sources(organized)
```

### Google Places Not Finding Resorts

**Symptom:** UGC photos stage returns "Could not find Google Place"

**Fixes:**
1. Verify `GOOGLE_PLACES_API_KEY` or `GOOGLE_API_KEY` is set in Railway
2. Coordinates help significantly - check if `extract_coordinates()` is returning values
3. Multi-strategy search now tries 5 different query formats

### Trail Map Data Not Saved

**Symptom:** Trail map stage completes but data not visible in database.

**Fix:** Verify the save code is uncommented in `runner.py`:
```python
if trail_map_data:
    trail_map_result = update_resort(resort_id, {"trail_map_data": trail_map_data})
```

### All Resorts Going to Draft

**Symptom:** Pipeline completes but resorts saved as draft, not published.

**Fix:** The publish-first model should always publish. Check:
1. Is `auto_publish=True` being passed?
2. Is there an exception in the approval panel that's falling through to draft?
3. Check logs for "Published with issues" vs "draft"

### Budget Exceeded Early

**Symptom:** Pipeline stops after 1-2 resorts with "budget_exceeded"

**Fix:**
1. Check `DAILY_BUDGET_LIMIT` env var (default: $5.00)
2. Each resort costs ~$1.50-2.00
3. Increase limit or reduce `--max-resorts`

---

## Railway Configuration

### Cron Schedule

The pipeline runs daily at 8am UTC. Configure in Railway:

```
cron = "0 8 * * *"
```

### Health Check

Railway health check configuration:
```toml
[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 300
```

### Active Project

Currently using `creative-spontaneity` for the cron job. Consider migrating to `snowthere-agents` for clearer naming.

---

## Quality Improvement Queue

The publish-first model queues resorts for continuous improvement. View pending items:

```sql
SELECT
    resort_name,
    country,
    payload->>'priority' as priority,
    payload->>'issues' as issues,
    created_at
FROM content_queue
WHERE task_type = 'quality_improvement'
AND status = 'pending'
ORDER BY created_at;
```

These items will be picked up in the next pipeline run via mixed selection.

---

## Verification After Changes

After implementing pipeline changes, verify with a local test:

```bash
cd agents
python3 cron.py --resort "Verbier" --country "Switzerland"
```

**Check logs for:**
- `"Extracted coordinates: X.XXXX, Y.YYYY"` - Nominatim working
- `Sources: X` (should be > 0) - Source flattening working
- `"Published but queued for improvement"` OR `"APPROVED"` - Publish-first model
- Trail map data in result - Persistence enabled

**Expected outcome:**
- Resort **PUBLISHED** (not draft)
- If issues exist, visible in quality_improvement queue
- Trail map data visible in database
