# Deployment Guide

Deploy the Focus Group Chat API to Vercel.

## Prerequisites

- [Vercel CLI](https://vercel.com/docs/cli) installed
- Vercel account
- Anthropic API key

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login
```

---

## Quick Deploy

```bash
cd focus_group

# First time: Link to Vercel project
vercel link

# Add API key as secret (one time)
vercel secrets add anthropic-api-key "sk-ant-..."

# Deploy to production
vercel --prod
```

Done. Your API is live at `https://your-project.vercel.app`

---

## Step-by-Step Setup

### 1. Project Structure

Ensure your project has these files:

```
focus_group/
├── api.py              # FastAPI entry point
├── engine.py           # Core engine
├── audiences.json      # Persona configurations
├── requirements.txt    # Python dependencies
└── vercel.json         # Vercel configuration
```

### 2. Verify vercel.json

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api.py",
      "use": "@vercel/python",
      "config": {
        "maxLambdaSize": "50mb"
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api.py"
    }
  ],
  "env": {
    "ANTHROPIC_API_KEY": "@anthropic-api-key"
  }
}
```

### 3. Verify requirements.txt

```
anthropic>=0.18.0
fastapi>=0.109.0
uvicorn>=0.27.0
pydantic>=2.0.0
mangum>=0.17.0
```

### 4. Add Secret

The API key must be stored as a Vercel secret:

```bash
# Add the secret
vercel secrets add anthropic-api-key "sk-ant-api03-..."

# Verify it exists
vercel secrets ls
```

### 5. Deploy

```bash
# Preview deployment (creates unique URL)
vercel

# Production deployment
vercel --prod
```

### 6. Verify Deployment

```bash
# Health check
curl https://your-project.vercel.app/

# Expected response:
# {"status":"ok","service":"focus-group-api","version":"2.0.0","mode":"stateless"}

# List audiences
curl https://your-project.vercel.app/audiences

# Test a question
curl -X POST https://your-project.vercel.app/audiences/premium_chocolate/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What do you think of premium chocolate?"}'
```

---

## Environment Variables

### Via Vercel Dashboard

1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Select your project
3. Settings → Environment Variables
4. Add: `ANTHROPIC_API_KEY` = your key

### Via CLI

```bash
# Using secrets (recommended)
vercel secrets add anthropic-api-key "sk-ant-..."

# Or via env (shows in dashboard)
vercel env add ANTHROPIC_API_KEY production
```

---

## Timeouts

### Default Limits

| Plan | Timeout |
|------|---------|
| Hobby | 10 seconds |
| Pro | 60 seconds |
| Enterprise | 900 seconds |

### Impact

With 3 responders:
- Responder selection: ~1-2s
- Response generation: ~2-3s × 3 = 6-9s
- **Total: ~8-12s**

**Hobby plan may timeout.** Options:
1. Upgrade to Pro
2. Reduce responders (edit `_select_responders` to return fewer)
3. Use faster model (Haiku for selection)

### Configuring Timeout

In `vercel.json`:

```json
{
  "functions": {
    "api.py": {
      "maxDuration": 60
    }
  }
}
```

---

## CORS Configuration

### Current (Development)

```python
# api.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all
    ...
)
```

### Production (Recommended)

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://www.yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

---

## Adding Authentication

The API is currently public. For production, consider adding authentication.

### Option 1: API Key Header

```python
from fastapi import Header, HTTPException

API_KEYS = {"your-secret-key-here"}

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

@app.post("/audiences/{audience_id}/ask")
async def ask_group(
    audience_id: str,
    request: AskRequest,
    api_key: str = Depends(verify_api_key)
):
    ...
```

### Option 2: Vercel Authentication

Use [Vercel's built-in authentication](https://vercel.com/docs/security/authentication) for team projects.

---

## Monitoring

### Vercel Dashboard

- Real-time logs: Project → Functions → Logs
- Analytics: Project → Analytics
- Errors: Project → Functions → Errors

### Adding Custom Logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/audiences/{audience_id}/ask")
async def ask_group(audience_id: str, request: AskRequest):
    logger.info(f"Question received for {audience_id}")
    # ... rest of handler
```

Logs appear in Vercel Functions logs.

---

## Updating Deployment

### Code Changes

```bash
# Make changes locally
# Test locally: uvicorn api:app --reload

# Deploy preview
vercel

# Test preview URL
curl https://your-project-xyz.vercel.app/

# Deploy to production
vercel --prod
```

### Adding New Audiences

1. Edit `audiences.json` locally
2. Test locally
3. Deploy: `vercel --prod`

```bash
# Verify new audience
curl https://your-project.vercel.app/audiences
```

---

## Troubleshooting

### "Serverless Function has timed out"

**Cause:** Response generation taking too long

**Solutions:**
1. Upgrade to Pro plan (60s timeout)
2. Reduce responder count:
   ```python
   # In engine.py _select_responders
   if selected and len(selected) > 2:
       return selected[:2]  # Cap at 2 responders
   ```

### "Module not found: anthropic"

**Cause:** Missing dependency

**Solution:** Ensure `requirements.txt` includes:
```
anthropic>=0.18.0
```

### "ANTHROPIC_API_KEY not set"

**Cause:** Secret not linked

**Solutions:**
```bash
# Check secret exists
vercel secrets ls

# Re-add if missing
vercel secrets add anthropic-api-key "sk-ant-..."

# Redeploy
vercel --prod
```

### "CORS error" in browser

**Cause:** Origin not allowed

**Solution:** Update CORS in `api.py`:
```python
allow_origins=["https://yourdomain.com"]
```

### "Cold start" slow first request

**Cause:** Serverless function initializing

**Expected:** First request may take 2-3s extra. Subsequent requests faster.

**Mitigation:** Use [Vercel cron](https://vercel.com/docs/cron-jobs) to keep warm:
```json
{
  "crons": [{
    "path": "/",
    "schedule": "*/5 * * * *"
  }]
}
```

---

## Cost Estimation

### Vercel

| Plan | Cost | Included |
|------|------|----------|
| Hobby | Free | 100GB bandwidth, 100 hours functions |
| Pro | $20/mo | 1TB bandwidth, 1000 hours functions |

### Anthropic API

| Model | Cost | Per Question (3 responders) |
|-------|------|----------------------------|
| Claude Sonnet | $3/$15 per 1M tokens | ~$0.01-0.02 |

**Rough estimate:** 1000 questions/month ≈ $10-20 Anthropic API cost

---

## Local Development

Always test locally before deploying:

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key
export ANTHROPIC_API_KEY="sk-ant-..."

# Run server
uvicorn api:app --reload

# Test
curl http://localhost:8000/
curl http://localhost:8000/audiences
```

---

## Checklist

Before going live:

- [ ] API key stored as Vercel secret
- [ ] CORS configured for your domain
- [ ] Tested all endpoints
- [ ] Checked timeout settings (Pro plan if needed)
- [ ] Added authentication (if public-facing)
- [ ] Monitoring configured
