# SharpShop Deployment Guide

## Overview
- **Frontend**: Vercel → `sharpshop.app`
- **Backend**: Heroku → `api.sharpshop.app`
- **Domain**: name.com

---

## Part 1: Deploy Backend to Heroku

### Step 1: Install Heroku CLI
Download and install from: https://devcenter.heroku.com/articles/heroku-cli

### Step 2: Login to Heroku
```bash
heroku login
```

### Step 3: Create Heroku App
```bash
cd c:\Users\OMEN\Documents\GitHub\sharpshop
heroku create sharpshop-api
```

### Step 4: Set Environment Variables
```bash
heroku config:set SUPABASE_URL=your_supabase_url
heroku config:set SUPABASE_KEY=your_supabase_anon_key
heroku config:set TWILIO_ACCOUNT_SID=your_twilio_account_sid
heroku config:set TWILIO_AUTH_TOKEN=your_twilio_auth_token
heroku config:set TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
heroku config:set GROQ_API_KEY=your_groq_api_key
heroku config:set FRONTEND_URL=https://sharpshop.app
```

### Step 5: Deploy to Heroku
```bash
git push heroku main
```

### Step 6: Get Your Heroku App URL
```bash
heroku apps:info
```
Note the URL (e.g., `https://sharpshop-api-xxxxx.herokuapp.com`)

### Step 7: Update Twilio Webhook
1. Go to Twilio Console → WhatsApp Sandbox
2. Update webhook URL to: `https://sharpshop-api-xxxxx.herokuapp.com/webhook`
3. Method: POST

---

## Part 2: Configure Custom Domain for Backend (api.sharpshop.app)

### Step 1: Add Custom Domain to Heroku
```bash
heroku domains:add api.sharpshop.app
```

This will give you a DNS target (e.g., `api.sharpshop.app.herokudns.com`)

### Step 2: Configure DNS at name.com
1. Log in to name.com
2. Go to your domain `sharpshop.app` → DNS Records
3. Add a **CNAME** record:
   - **Host**: `api`
   - **Type**: CNAME
   - **Answer**: `api.sharpshop.app.herokudns.com` (from Step 1)
   - **TTL**: 300

### Step 3: Wait for SSL Certificate
Heroku automatically provisions SSL certificates. Check status:
```bash
heroku certs:auto
```

### Step 4: Update Twilio Webhook (Final)
Update webhook URL to: `https://api.sharpshop.app/webhook`

---

## Part 3: Deploy Frontend to Vercel

### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

### Step 2: Login to Vercel
```bash
vercel login
```

### Step 3: Update Frontend API URL
Before deploying, update the API URL in your frontend:

**File**: `Sharp-Shop FrontEnd/Sharp-Shop/server/routes.ts`

Change the Supabase client initialization to use environment variables.

### Step 4: Deploy Frontend
```bash
cd "c:\Users\OMEN\Documents\GitHub\sharpshop\Sharp-Shop FrontEnd\Sharp-Shop"
vercel
```

Follow the prompts:
- Set up and deploy? **Y**
- Which scope? (select your account)
- Link to existing project? **N**
- What's your project's name? **sharpshop**
- In which directory is your code located? **.**
- Want to override settings? **N**

### Step 5: Set Environment Variables in Vercel
```bash
vercel env add VITE_SUPABASE_URL
# Paste your Supabase URL

vercel env add VITE_SUPABASE_ANON_KEY
# Paste your Supabase anon key

vercel env add VITE_API_URL
# Enter: https://api.sharpshop.app
```

### Step 6: Deploy to Production
```bash
vercel --prod
```

Note the deployment URL (e.g., `https://sharpshop-xxxxx.vercel.app`)

---

## Part 4: Configure Custom Domain for Frontend (sharpshop.app)

### Step 1: Add Domain in Vercel Dashboard
1. Go to https://vercel.com/dashboard
2. Select your `sharpshop` project
3. Go to **Settings** → **Domains**
4. Click **Add Domain**
5. Enter: `sharpshop.app` and `www.sharpshop.app`

### Step 2: Configure DNS at name.com
Vercel will show you DNS records. Add these at name.com:

**For root domain (sharpshop.app)**:
- **Type**: A
- **Host**: `@`
- **Answer**: `76.76.21.21` (Vercel's IP)
- **TTL**: 300

**For www subdomain**:
- **Type**: CNAME
- **Host**: `www`
- **Answer**: `cname.vercel-dns.com`
- **TTL**: 300

### Step 3: Wait for SSL Certificate
Vercel automatically provisions SSL certificates. This may take a few minutes.

---

## Part 5: Update Backend CORS

Update your backend to allow the new frontend URL:

**File**: `server.py`

Ensure the CORS configuration includes:
```python
import os

frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        frontend_url,
        "https://sharpshop.app",
        "https://www.sharpshop.app",
        "http://localhost:5000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Redeploy backend:
```bash
git add .
git commit -m "Update CORS for production domain"
git push heroku main
```

---

## Part 6: Final Testing

1. **Test Backend**: Visit `https://api.sharpshop.app/` (should show FastAPI docs)
2. **Test Frontend**: Visit `https://sharpshop.app` (should load your app)
3. **Test WhatsApp**: Send a message to your WhatsApp number
4. **Test Product Upload**: Upload a product via WhatsApp

---

## Troubleshooting

### Backend Issues
```bash
# View logs
heroku logs --tail

# Check dyno status
heroku ps

# Restart dyno
heroku restart
```

### Frontend Issues
```bash
# View deployment logs
vercel logs

# Redeploy
vercel --prod
```

### DNS Issues
- DNS changes can take 5-60 minutes to propagate
- Check DNS propagation: https://dnschecker.org
- Verify with: `nslookup api.sharpshop.app`

---

## Environment Variables Summary

### Heroku (Backend)
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_WHATSAPP_NUMBER`
- `GROQ_API_KEY`
- `FRONTEND_URL`

### Vercel (Frontend)
- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_ANON_KEY`
- `VITE_API_URL`

---

## GitHub Student Pack Benefits

With your GitHub Student Pack, you get:
- **Heroku**: Free credits (no credit card required initially)
- **Name.com**: Free domain for 1 year (you already have this)

Make sure to activate Heroku through the Student Pack for free credits!
