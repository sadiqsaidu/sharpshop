# 🚀 SharpShop Python Backend - Complete Setup & Testing Guide

## ✅ What I Fixed

1. **Schema Alignment**: Updated all code to match your frontend schema:
   - `sellers` → `traders`
   - `seller_id` → `trader_id`
   - `title` → `name`
   - `quantity` → `stock`
   - `image_urls` → `image` (single URL)

2. **Added Missing Function**: `should_execute()` in `agent.py`

3. **WhatsApp Integration**: Products now include `whatsapp_number` for customer checkout

4. **Created `.env` Template**: For your API keys

---

## 📋 STEP 1: Install Python Dependencies

Open PowerShell in the project root:

```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

**Expected Output:**
```
Successfully installed fastapi-0.109.0 uvicorn-0.27.0 supabase-2.3.0 ...
```

---

## 📋 STEP 2: Configure Environment Variables

1. Open `.env` file in the root directory
2. Get your Groq API key from: https://console.groq.com/keys
3. Get your Supabase credentials from: https://supabase.com/dashboard/project/_/settings/api

Update `.env`:
```env
GROQ_API_KEY=gsk_your_actual_groq_key_here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_service_role_key_here
```

⚠️ **CRITICAL**: Use the **SERVICE ROLE KEY** (not anon key) for full database access!

---

## 📋 STEP 3: Verify Supabase Database Schema

Your `traders` table should have these columns:
- `id` (uuid, primary key)
- `user_id` (uuid, nullable)
- `business_name` (text)
- `whatsapp_number` (text)
- `address` (text, nullable)
- `bio` (text, nullable)
- `created_at` (timestamp)

Your `products` table should have:
- `id` (uuid, primary key)
- `trader_id` (uuid, foreign key to traders.id)
- `whatsapp_number` (text) ← **IMPORTANT**: For customer checkout
- `name` (text)
- `price` (numeric)
- `category` (text)
- `stock` (integer)
- `condition` (text)
- `description` (text, nullable)
- `size` (text, nullable)
- `brand` (text, nullable)
- `image` (text)
- `created_at` (timestamp)

**Check in Supabase Dashboard** → Table Editor

---

## 📋 STEP 4: Enable Supabase Realtime

1. Go to Supabase Dashboard → **Database** → **Replication**
2. Find `products` table
3. Toggle **Enable Realtime** to ON
4. Click **Save**

This allows your React frontend to receive instant updates!

---

## 📋 STEP 5: Test Locally (Without WhatsApp)

Create a test script:

```powershell
# Create test file
New-Item test_agent.py -ItemType File
```

Add this code to `test_agent.py`:

```python
"""Test the agent locally without WhatsApp."""
from agent import create_initial_state, chat
from database import get_or_create_trader

# Create a test trader
test_whatsapp = "+2348012345678"
trader = get_or_create_trader(test_whatsapp, "Test Shop")
print(f"✅ Trader created: {trader['business_name']} ({trader['id']})")

# Initialize conversation state
state = create_initial_state(trader_id=trader["id"], whatsapp_number=test_whatsapp)

# Test 1: Add a product
print("\n--- Test 1: Adding Product ---")
state = chat(state, "I want to add Nike Air Max shoes, 25000 naira, 10 in stock, new condition, fashion category")

# Print last response
for msg in reversed(state["messages"]):
    if msg["role"] == "assistant":
        print(f"Bot: {msg['content']}")
        break

# Test 2: List products
print("\n--- Test 2: List Products ---")
state = chat(state, "Show me all my products")

for msg in reversed(state["messages"]):
    if msg["role"] == "assistant":
        print(f"Bot: {msg['content']}")
        break

# Test 3: Search inventory
print("\n--- Test 3: Search ---")
state = chat(state, "Do I have any Nike products?")

for msg in reversed(state["messages"]):
    if msg["role"] == "assistant":
        print(f"Bot: {msg['content']}")
        break

print("\n✅ All tests completed!")
```

Run the test:

```powershell
python test_agent.py
```

**Expected Output:**
```
✅ Trader created: Test Shop (uuid-here)

--- Test 1: Adding Product ---
Bot: ✅ Product added! Your Nike Air Max shoes is now listed.

--- Test 2: List Products ---
Bot: 📦 Your products:
• Nike Air Max shoes - ₦25,000 (10 in stock)

--- Test 3: Search ---
Bot: 📦 Found 1 items:
• Nike Air Max shoes - ₦25,000 (10 in stock)

✅ All tests completed!
```

---

## 📋 STEP 6: Verify Frontend Sync

1. Open your React app in browser: `http://localhost:5000`
2. Check if the product appears in the feed
3. Try clicking **Buy Now** - should open WhatsApp with pre-filled message

If it doesn't appear:
- Check Supabase Table Editor → products table
- Verify Realtime is enabled
- Check browser console for errors

---

## 📋 STEP 7: Set Up WhatsApp (Twilio)

### A. Create Twilio Account
1. Go to: https://www.twilio.com/try-twilio
2. Sign up and verify your phone number
3. Go to **Console** → **Messaging** → **Try it out** → **Send a WhatsApp message**

### B. Join Sandbox
1. Send the join code to the Twilio sandbox number (e.g., `join <your-code>`)
2. You'll receive a confirmation message

### C. Start the Server
```powershell
python server.py
```

**Expected Output:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### D. Expose with Ngrok
Open **new PowerShell window**:

```powershell
# Download ngrok from https://ngrok.com/download
# Or install via Chocolatey: choco install ngrok

# Expose port 8000
ngrok http 8000
```

**Expected Output:**
```
Forwarding   https://abcd-1234-5678.ngrok-free.app -> http://localhost:8000
```

### E. Configure Twilio Webhook
1. Go to Twilio Console → **Messaging** → **Try it out** → **Send a WhatsApp message**
2. Click **Sandbox settings**
3. In **"When a message comes in"**, paste:
   ```
   https://your-ngrok-url.ngrok-free.app/whatsapp
   ```
4. Save

---

## 📋 STEP 8: Test End-to-End Flow

### Test 1: Add Product via WhatsApp

Send this to the Twilio sandbox number:

```
Add Adidas sneakers for 15000 naira, 5 in stock, new condition, fashion category
```

**Expected Bot Response:**
```
✅ Product added! Your Adidas sneakers is now listed.
```

**Verify in Frontend:**
1. Go to `http://localhost:5000`
2. Product should appear automatically (no refresh!)
3. Click **Buy Now**
4. Should open WhatsApp with message: "Hi, I'm interested in *Adidas sneakers* - ₦15,000"

---

### Test 2: Add Product with Image

1. Take a photo with your phone
2. Send image + caption to Twilio number:
   ```
   Gucci bag, 45000 naira, 2 in stock, new, fashion
   ```

**Expected Bot Response:**
```
✅ Product added! Your Gucci bag is now listed.
```

**Verify:** Product image should appear in frontend

---

### Test 3: List Products

Send to WhatsApp:
```
Show me all my products
```

**Expected Bot Response:**
```
📦 Your products:
• Adidas sneakers - ₦15,000 (5 in stock)
• Gucci bag - ₦45,000 (2 in stock)
```

---

### Test 4: Search

Send to WhatsApp:
```
Do I have any Adidas?
```

**Expected Bot Response:**
```
📦 Found 1 items:
• Adidas sneakers - ₦15,000 (5 in stock)
```

---

## 🐛 Troubleshooting

### Issue 1: "ModuleNotFoundError: No module named 'supabase'"
**Solution:**
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

### Issue 2: "supabase.exceptions.APIError: Invalid API key"
**Solution:**
- Check `.env` file has correct `SUPABASE_KEY`
- Use **SERVICE ROLE KEY** (not anon key)
- Restart server after updating `.env`

---

### Issue 3: Products not appearing in frontend
**Solution:**
1. Enable Realtime in Supabase (Step 4)
2. Check products table in Supabase - verify data exists
3. Check browser console for errors
4. Verify `whatsapp_number` field exists in products

---

### Issue 4: Ngrok "Too many connections"
**Solution:**
- Free ngrok resets URL after 2 hours
- Update Twilio webhook with new ngrok URL
- Or upgrade to ngrok paid plan for static URLs

---

### Issue 5: Bot not responding on WhatsApp
**Check:**
1. Server is running (`python server.py`)
2. Ngrok is running and showing same URL in Twilio
3. Check `server.log` file for errors:
   ```powershell
   Get-Content server.log -Tail 20
   ```

---

## 📊 Monitoring & Logs

### View Server Logs
```powershell
# Real-time logs
Get-Content server.log -Wait -Tail 50
```

### Check Database
Supabase Dashboard → **Table Editor** → products

### Test Realtime
Supabase Dashboard → **Database** → **Replication** → Click eye icon on `products`

---

## 🎯 Next Steps

1. **Production Deployment:**
   - Deploy to Railway/Render/Fly.io
   - Get permanent WhatsApp Business API number (Meta)
   - Use production Supabase project

2. **Enhance Agent:**
   - Add image recognition (detect product from photo)
   - Support bulk uploads
   - Add analytics ("How many products sold this week?")

3. **Frontend Features:**
   - Seller analytics dashboard
   - Product performance tracking
   - Customer inquiry management

---

## ✅ Success Checklist

- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] `.env` configured with real keys
- [ ] Supabase Realtime enabled
- [ ] Local test passed (`test_agent.py`)
- [ ] Server running (`python server.py`)
- [ ] Ngrok exposing server
- [ ] Twilio webhook configured
- [ ] WhatsApp message sent successfully
- [ ] Product appears in frontend
- [ ] Buy Now button opens WhatsApp

---

## 🆘 Need Help?

**Check Logs First:**
```powershell
# Server logs
Get-Content server.log -Tail 50

# Supabase logs
# Dashboard → Logs → API Logs
```

**Common Issues:**
- Wrong Supabase key (use service role)
- Realtime not enabled
- Schema mismatch (run migrations)
- Ngrok URL expired

**Test Each Component:**
1. Database: Run `test_agent.py`
2. Server: Check `http://localhost:8000/docs`
3. WhatsApp: Check Twilio logs
4. Frontend: Check browser console

Good luck! 🚀
