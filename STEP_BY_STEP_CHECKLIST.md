# ✅ SharpShop Setup Checklist - Follow These Steps

## Part 1: Get Your API Keys (15 minutes)

### ☐ Step 1.1: Get Groq API Key
1. Go to: https://console.groq.com/keys
2. Sign up/login (free account)
3. Click **"Create API Key"**
4. Copy the key (starts with `gsk_`)
5. Save it somewhere safe

### ☐ Step 1.2: Get Supabase Credentials
1. Go to: https://supabase.com/dashboard
2. Click **"New Project"**
3. Create project (takes 2-3 minutes)
4. Go to **Settings** → **API**
5. Copy:
   - **Project URL** (e.g., `https://abc123.supabase.co`)
   - **service_role key** (the secret one, NOT anon key)

### ☐ Step 1.3: Update `.env` File
1. Open `c:\Users\OMEN\Documents\GitHub\sharpshop\.env`
2. Replace with your real values:
   ```env
   GROQ_API_KEY=gsk_your_actual_key_here
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```
3. Save the file

---

## Part 2: Set Up Supabase Database (10 minutes)

### ☐ Step 2.1: Verify Tables Exist
1. Go to Supabase Dashboard → **Table Editor**
2. Check if these tables exist:
   - `traders`
   - `products`
   - `users`

### ☐ Step 2.2: Add `whatsapp_number` to Products
1. Click on **products** table
2. Check if `whatsapp_number` column exists
3. If not, click **"+ New Column"**:
   - Name: `whatsapp_number`
   - Type: `text`
   - Default value: (leave empty)
   - Allow nullable: ✅
4. Click **Save**

### ☐ Step 2.3: Enable Realtime
1. Go to **Database** → **Replication**
2. Find `products` table
3. Toggle **Enable Realtime** to ON (green)
4. Click **Save**

---

## Part 3: Install Python Backend (10 minutes)

### ☐ Step 3.0: Install Python (FIRST!)
**You need Python 3.12+**

**Option A - Microsoft Store (Easiest):**
1. Open Microsoft Store
2. Search for "Python 3.12"
3. Click **Install**
4. Wait for installation to complete
5. Close and reopen PowerShell

**Option B - Official Website:**
1. Go to: https://www.python.org/downloads/
2. Download **Python 3.12** or newer
3. Run installer
4. ⚠️ **CHECK "Add Python to PATH"** ✅
5. Click **Install Now**
6. Close and reopen PowerShell

**Verify installation:**
```powershell
python --version
```
Expected: `Python 3.12.x`

### ☐ Step 3.1: Navigate to Project
You're already here! Your PowerShell is at:
```powershell
C:\Users\OMEN\Documents\GitHub\sharpshop
```

### ☐ Step 3.2: Create Virtual Environment
```powershell
python -m venv venv
```

**Expected output:** (takes 30 seconds, creates `venv` folder, no errors)

### ☐ Step 3.3: Activate Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```

**Expected:** `(venv)` appears before your prompt

### ☐ Step 3.4: Install Dependencies
```powershell
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed fastapi-0.109.0 uvicorn-0.27.0 supabase-2.3.0 ...
```

---

## Part 4: Test Locally (5 minutes)

### ☐ Step 4.1: Run Test Script
```powershell
python test_agent.py
```

### ☐ Step 4.2: Verify Output
**You should see:**
```
✅ Trader created: Test Shop (uuid-here)

--- Test 1: Adding Product ---
Bot: ✅ Product added! Your Nike Air Max shoes is now listed.

--- Test 2: List Products ---
Bot: 📦 Your products:
• Nike Air Max shoes - ₦25,000 (10 in stock)

✅ All tests completed!
```

**If you see errors:**
- Check `.env` file has correct keys
- Verify Supabase tables exist
- Make sure virtual environment is activated

### ☐ Step 4.3: Check Supabase
1. Go to Supabase Dashboard → **Table Editor** → **products**
2. You should see the Nike Air Max product
3. Verify `whatsapp_number` field is filled

---

## Part 5: Test Frontend Sync (5 minutes)

### ☐ Step 5.1: Start React Frontend
Open **new PowerShell window**:
```powershell
cd "C:\Users\OMEN\Documents\GitHub\sharpshop\Sharp-Shop FrontEnd\Sharp-Shop"
npm run dev
```

### ☐ Step 5.2: Open in Browser
Go to: `http://localhost:5000`

### ☐ Step 5.3: Verify Product Appears
- You should see "Nike Air Max shoes" in the feed
- Price should be ₦25,000
- Click **Buy Now** → should try to open WhatsApp

**If product doesn't appear:**
- Check Supabase Realtime is enabled
- Check browser console for errors
- Verify `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY` in frontend `.env`

---

## Part 6: WhatsApp Integration (15 minutes)

### ☐ Step 6.1: Create Twilio Account
1. Go to: https://www.twilio.com/try-twilio
2. Sign up (free trial, no credit card)
3. Verify your phone number

### ☐ Step 6.2: Join WhatsApp Sandbox
1. Go to: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
2. You'll see instructions like:
   ```
   Send "join <code>" to +1 415 523 8886
   ```
3. Send that message from your WhatsApp
4. Wait for confirmation

### ☐ Step 6.3: Start Python Server
Back in your first PowerShell (with venv activated):
```powershell
python server.py
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### ☐ Step 6.4: Install & Start Ngrok
Open **new PowerShell window**:

**Option A - Download manually:**
1. Go to: https://ngrok.com/download
2. Download Windows version
3. Extract to a folder
4. Run: `.\ngrok.exe http 8000`

**Option B - Install via Chocolatey:**
```powershell
choco install ngrok
ngrok http 8000
```

**Expected output:**
```
Forwarding   https://1234-abcd-5678.ngrok-free.app -> http://localhost:8000
```

**Copy the HTTPS URL!**

### ☐ Step 6.5: Configure Twilio Webhook
1. Go to: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
2. Scroll down, click **Sandbox settings**
3. Find **"When a message comes in"** field
4. Paste: `https://your-ngrok-url.ngrok-free.app/whatsapp`
   - Replace with YOUR actual ngrok URL
   - Don't forget `/whatsapp` at the end!
5. Click **Save**

---

## Part 7: End-to-End Test (10 minutes)

### ☐ Test 7.1: Send WhatsApp Message
Open WhatsApp on your phone, send to Twilio number:
```
Add Adidas sneakers, 15000 naira, 5 in stock, new, fashion
```

**Expected bot response:**
```
✅ Product added! Your Adidas sneakers is now listed.
```

### ☐ Test 7.2: Check Frontend
1. Go to browser with React app open
2. Product should appear **automatically** (no refresh!)
3. You should see "Adidas sneakers - ₦15,000"

### ☐ Test 7.3: Test Checkout
1. Click **Buy Now** on the product
2. Should redirect to WhatsApp with message:
   ```
   Hi, I'm interested in *Adidas sneakers* - ₦15,000
   ```

### ☐ Test 7.4: List Products
Send to WhatsApp:
```
Show me all my products
```

**Expected:**
```
📦 Your products:
• Nike Air Max shoes - ₦25,000 (10 in stock)
• Adidas sneakers - ₦15,000 (5 in stock)
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError"
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Issue: "Invalid API key"
- Check `.env` file
- Make sure you used **SERVICE ROLE KEY** (not anon)
- Restart `python server.py`

### Issue: Bot not responding on WhatsApp
```powershell
# Check server logs
Get-Content server.log -Tail 20
```
- Verify ngrok is running
- Check Twilio webhook URL is correct
- Make sure server is running

### Issue: Products not in frontend
- Enable Realtime in Supabase
- Check products table has data
- Verify frontend .env has Supabase credentials

---

## Success Criteria

You're done when:
✅ Local test passes (`test_agent.py`)
✅ Product appears in Supabase
✅ Product appears in React frontend
✅ WhatsApp message creates product
✅ Product auto-appears in frontend
✅ Buy Now button opens WhatsApp

---

## Next: Check the logs!

### Server logs:
```powershell
Get-Content server.log -Wait -Tail 50
```

### Supabase logs:
Dashboard → **Logs** → **API Logs**

---

## Your Current Progress

Mark each part as you complete it:
- [ ] Part 1: API Keys (15 min)
- [ ] Part 2: Supabase Setup (10 min)
- [ ] Part 3: Python Install (5 min)
- [ ] Part 4: Local Test (5 min)
- [ ] Part 5: Frontend Sync (5 min)
- [ ] Part 6: WhatsApp Integration (15 min)
- [ ] Part 7: End-to-End Test (10 min)

**Total Time: ~60 minutes**

---

🎉 Once all parts are checked, you have a fully working WhatsApp-first e-commerce platform!
