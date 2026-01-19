# Deployment Guide - Snowthere Family Ski Directory

This guide covers deploying both the **frontend** (Vercel) and **agents pipeline** (Railway).

## Prerequisites

1. **Supabase Project** active at `xfmsyqlvyepppgvypsms.supabase.co`
2. **API Keys** available:
   - Anthropic (Claude API)
   - Exa (semantic search)
   - Brave (web search)
   - Tavily (research)
3. **Vercel account** (hobby tier is fine)
4. **Railway account** (starter plan works)

---

## Step 1: Frontend Deployment (Vercel)

### Option A: Deploy via Dashboard

1. Go to [vercel.com](https://vercel.com) and log in
2. Click "Add New Project"
3. Import the repository
4. **Configure:**
   - Framework Preset: Next.js
   - Root Directory: `apps/web`
   - Build Command: `npm run build`
   - Output Directory: `.next`

5. **Add Environment Variables:**
   ```
   NEXT_PUBLIC_SUPABASE_URL=https://xfmsyqlvyepppgvypsms.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=<your-anon-key>
   NEXT_PUBLIC_GA_MEASUREMENT_ID=G-CZ56J0HBHH
   ```

6. Click "Deploy"

### Option B: Deploy via CLI

```bash
cd apps/web

# Install Vercel CLI
npm i -g vercel

# Login (if not already)
vercel login

# Deploy to preview
vercel

# Deploy to production
vercel --prod
```

### Get Revalidation Token

After deployment, create a revalidation secret for ISR:

1. Go to Vercel Dashboard → Project Settings → Environment Variables
2. Add a new variable:
   - Name: `REVALIDATE_SECRET`
   - Value: Generate a random 32-character string
3. Copy this value - you'll need it for the agents config

### Verify Frontend

- Visit your Vercel URL
- Check `/resorts/switzerland/zermatt` loads correctly
- Verify styles and components render properly

---

## Step 2: Agents Pipeline Deployment (Railway)

### Option A: Deploy via Dashboard

1. Go to [railway.app](https://railway.app) and log in
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. **Configure:**
   - Root Directory: `agents`

5. **Add Environment Variables:**
   ```
   SUPABASE_URL=https://xfmsyqlvyepppgvypsms.supabase.co
   SUPABASE_SERVICE_KEY=<your-service-key>
   ANTHROPIC_API_KEY=<your-key>
   EXA_API_KEY=<your-key>
   BRAVE_API_KEY=<your-key>
   TAVILY_API_KEY=<your-key>
   DAILY_BUDGET_LIMIT=20.00
   VERCEL_URL=<your-vercel-deployment-url>
   VERCEL_REVALIDATE_TOKEN=<the-secret-from-step-1>
   ```

6. **Enable Cron Job:**
   - Go to Settings → Cron
   - Enable cron
   - Schedule: `0 8 * * *` (8am UTC daily)

7. Deploy (automatic on push to main)

### Option B: Deploy via CLI

```bash
cd agents

# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project (first time only)
railway init

# Or link to existing project
railway link

# Set environment variables
railway variables set SUPABASE_URL="https://xfmsyqlvyepppgvypsms.supabase.co"
railway variables set SUPABASE_SERVICE_KEY="<your-key>"
railway variables set ANTHROPIC_API_KEY="<your-key>"
railway variables set EXA_API_KEY="<your-key>"
railway variables set BRAVE_API_KEY="<your-key>"
railway variables set TAVILY_API_KEY="<your-key>"
railway variables set DAILY_BUDGET_LIMIT="20.00"
railway variables set VERCEL_URL="<your-vercel-url>"
railway variables set VERCEL_REVALIDATE_TOKEN="<your-secret>"

# Deploy
railway up
```

---

## Step 3: Test the Pipeline

### Test Locally First

```bash
cd agents

# Activate virtual environment
source .venv/bin/activate

# Install dependencies (if not done)
pip install -r requirements.txt

# Validate environment
python railway_check.py

# Dry run (see what would happen)
python cron.py --dry-run

# Test single resort
python cron.py --resort "Zermatt" --country "Switzerland" --no-publish

# Run pipeline with 1 resort
python cron.py --max-resorts 1
```

### Trigger Railway Manually

1. Go to Railway Dashboard → your project
2. Click "Deploy" → "Trigger Deploy"
3. Or run: `railway run python cron.py --max-resorts 1`

### Verify Results

After a successful run:

1. **Check Supabase:**
   - `resorts` table: New resort should appear
   - `resort_content` table: Content should be populated
   - `agent_audit_log` table: Reasoning trail should exist
   - `api_costs` table: Cost entries should be logged

2. **Check Vercel:**
   - Visit the resort page to see if it displays
   - ISR should revalidate automatically (if configured)

---

## Environment Variables Reference

### Frontend (Vercel)

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anonymous key (public) |
| `NEXT_PUBLIC_GA_MEASUREMENT_ID` | Google Analytics 4 ID |
| `REVALIDATE_SECRET` | Secret for ISR revalidation |

### Agents (Railway)

| Variable | Description |
|----------|-------------|
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_SERVICE_KEY` | Supabase service role key (secret) |
| `ANTHROPIC_API_KEY` | Claude API key |
| `EXA_API_KEY` | Exa semantic search API key |
| `BRAVE_API_KEY` | Brave search API key |
| `TAVILY_API_KEY` | Tavily research API key |
| `DAILY_BUDGET_LIMIT` | Maximum daily API spend (default: 20.00) |
| `VERCEL_URL` | Vercel deployment URL for revalidation |
| `VERCEL_REVALIDATE_TOKEN` | Secret token for triggering ISR |

---

## Monitoring

### Railway Logs

```bash
railway logs
```

Or view in Railway Dashboard → your project → Logs

### Supabase Queries

```sql
-- Recent pipeline runs
SELECT * FROM agent_audit_log
WHERE agent_name = 'pipeline_runner'
ORDER BY created_at DESC LIMIT 20;

-- Daily API costs
SELECT * FROM api_costs
WHERE created_at > NOW() - INTERVAL '7 days'
ORDER BY created_at DESC;

-- Resort statuses
SELECT name, status, last_refreshed, created_at
FROM resorts
ORDER BY created_at DESC;
```

### Vercel Analytics

- Go to Vercel Dashboard → Project → Analytics
- Monitor page views, performance, and errors

---

## Troubleshooting

### Pipeline Fails to Start

1. Check Railway logs for errors
2. Run `python railway_check.py` locally to validate environment
3. Ensure all environment variables are set

### Content Not Saving

1. Check Supabase connection:
   ```bash
   python -c "from shared.supabase_client import get_supabase_client; get_supabase_client()"
   ```
2. Verify `SUPABASE_SERVICE_KEY` is correct (not the anon key)

### ISR Not Revalidating

1. Verify `VERCEL_URL` and `VERCEL_REVALIDATE_TOKEN` are set
2. Check that the revalidation endpoint exists in Vercel
3. Test manually:
   ```bash
   curl -X POST "https://your-vercel-url/api/revalidate?secret=YOUR_SECRET&path=/resorts/switzerland/zermatt"
   ```

### High API Costs

1. Check `DAILY_BUDGET_LIMIT` is set correctly
2. Review `api_costs` table for expensive operations
3. Reduce `--max-resorts` during testing

---

## Maintenance

### Update Dependencies

```bash
# Frontend
cd apps/web
npm update

# Agents
cd agents
pip install --upgrade -r requirements.txt
```

### Rotate API Keys

1. Generate new key in provider dashboard
2. Update in Railway environment variables
3. Redeploy: `railway up` or push to GitHub

### Database Migrations

```bash
cd supabase
supabase db push  # Apply new migrations
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Deploy frontend | `cd apps/web && vercel --prod` |
| Deploy agents | `cd agents && railway up` |
| View Railway logs | `railway logs` |
| Test pipeline locally | `python cron.py --dry-run` |
| Run single resort | `python cron.py --resort "Name" --country "Country"` |
| Check environment | `python railway_check.py` |
