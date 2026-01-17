# Railway Deployment Guide

Deploy the Snowthere agents pipeline to Railway for daily automated content generation.

## Quick Deploy via Dashboard

1. **Login to Railway**: https://railway.app/

2. **Create New Project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose `tomdmeredith/snowthere`

3. **Configure Root Directory**:
   - Click on the service
   - Go to Settings → General
   - Set **Root Directory** to: `agents`

4. **Add Environment Variables**:
   Go to Variables tab and add:

   ```
   SUPABASE_URL=https://xfmsyqlvyepppgvypsms.supabase.co
   SUPABASE_SERVICE_KEY=<your-service-key>
   ANTHROPIC_API_KEY=<your-key>
   EXA_API_KEY=<your-key>
   BRAVE_API_KEY=<your-key>
   TAVILY_API_KEY=<your-key>
   DAILY_BUDGET_LIMIT=5.00
   ```

5. **Enable Cron**:
   - Go to Settings → Cron
   - Enable cron job
   - Schedule: `0 8 * * *` (8am UTC daily)

6. **Deploy**: Railway will auto-deploy from main branch

## Quick Deploy via CLI

```bash
cd agents

# Login to Railway
railway login

# Create new project
railway init

# Link to existing project (if already created)
railway link

# Set environment variables
railway variables set SUPABASE_URL="https://xfmsyqlvyepppgvypsms.supabase.co"
railway variables set SUPABASE_SERVICE_KEY="your-key"
railway variables set ANTHROPIC_API_KEY="your-key"
railway variables set EXA_API_KEY="your-key"
railway variables set BRAVE_API_KEY="your-key"
railway variables set TAVILY_API_KEY="your-key"
railway variables set DAILY_BUDGET_LIMIT="5.00"

# Deploy
railway up
```

## Test Locally First

Before deploying, test the pipeline locally:

```bash
cd agents

# Dry run (see what would happen)
python cron.py --dry-run

# Single resort test
python cron.py --resort "Zermatt" --country "Switzerland" --no-publish

# Full pipeline with low limit
python cron.py --max-resorts 1
```

## Configuration Files

| File | Purpose |
|------|---------|
| `railway.toml` | Railway-specific config (cron schedule, replicas) |
| `nixpacks.toml` | Build configuration (Python 3.11) |
| `requirements.txt` | Python dependencies |
| `cron.py` | Entry point for the pipeline |

## Monitoring

- **Railway Dashboard**: View logs, metrics, and deployment status
- **Supabase**: Check `agent_audit_log` table for detailed reasoning trails
- **Cost Tracking**: Check `api_costs` table for daily spend

## Cron Schedule

Default: `0 8 * * *` (8am UTC daily)

Adjust in `railway.toml` or Railway dashboard for different schedules:
- `0 */6 * * *` - Every 6 hours
- `0 8,20 * * *` - 8am and 8pm UTC
- `0 8 * * 1-5` - Weekdays only at 8am
