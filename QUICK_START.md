# 🚀 SharpShop Quick Start Commands

## Initial Setup (One-Time)

```powershell
# 1. Create virtual environment
python -m venv venv

# 2. Activate it
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Update .env file with your keys
# GROQ_API_KEY=your_key
# SUPABASE_URL=your_url
# SUPABASE_KEY=your_service_role_key
```

---

## Testing Flow

### Step 1: Test Locally (No WhatsApp)
```powershell
# Activate environment
.\venv\Scripts\Activate.ps1

# Run test
python test_agent.py
```

**What this does:**
- Creates a test trader in Supabase
- Adds a product via AI agent
- Lists all products
- Searches inventory
- Verifies everything works

---

### Step 2: Start the Server
```powershell
# Terminal 1: Start FastAPI server
python server.py
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

### Step 3: Expose with Ngrok
```powershell
# Terminal 2: Start ngrok
ngrok http 8000
```

**Copy the HTTPS URL:**
```
Forwarding   https://abcd-1234.ngrok-free.app -> http://localhost:8000
```

---

### Step 4: Configure Twilio
1. Go to: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
2. Click **Sandbox settings**
3. Paste in "When a message comes in":
   ```
   https://your-ngrok-url.ngrok-free.app/whatsapp
   ```
4. Save

---

### Step 5: Join WhatsApp Sandbox
Send this message to the Twilio sandbox number:
```
join <your-sandbox-code>
```

---

## Testing Commands

### Add Product (Text Only)
```
Add Nike Air Max, 25000 naira, 10 in stock, new, fashion
```

### Add Product (With Image)
1. Send product image
2. Add caption: `Adidas shoes, 15000, 5 stock, new, fashion`

### List All Products
```
Show me all my products
```

### Search
```
Do I have any Nike?
```

---

## Verify Frontend Sync

1. Open React app: `http://localhost:5000`
2. Product should appear automatically
3. Click **Buy Now** → Opens WhatsApp

---

## Common Issues

### "Module not found"
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### "Invalid API key"
- Check `.env` file
- Use **SERVICE ROLE KEY** (not anon key)
- Restart server

### Products not in frontend
- Enable Realtime in Supabase
- Check `products` table in Supabase
- Verify `whatsapp_number` field exists

### Bot not responding
```powershell
# Check logs
Get-Content server.log -Tail 20

# Verify ngrok URL matches Twilio webhook
```

---

## Daily Development Workflow

```powershell
# 1. Activate environment
.\venv\Scripts\Activate.ps1

# 2. Start server
python server.py

# 3. In new terminal: Start ngrok
ngrok http 8000

# 4. Update Twilio webhook if ngrok URL changed

# 5. Test via WhatsApp
```

---

## Production Checklist

- [ ] Get Groq API key
- [ ] Create Supabase project
- [ ] Enable Realtime on `products` table
- [ ] Add `whatsapp_number` field to products
- [ ] Configure `.env` file
- [ ] Test locally with `test_agent.py`
- [ ] Set up Twilio WhatsApp sandbox
- [ ] Configure webhook
- [ ] Test end-to-end flow
- [ ] Deploy to production (Railway/Render/Fly.io)

---

## Useful Links

- **Groq Console**: https://console.groq.com/keys
- **Supabase Dashboard**: https://supabase.com/dashboard
- **Twilio Console**: https://console.twilio.com
- **Ngrok Dashboard**: https://dashboard.ngrok.com

---

## Need Help?

See detailed guide: [SETUP_GUIDE.md](SETUP_GUIDE.md)
