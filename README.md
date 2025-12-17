# SharpShop — WhatsApp-First E-Commerce Platform 🛍️🤖

Welcome to **SharpShop** — a headless e-commerce platform where Nigerian traders manage inventory via WhatsApp, and customers shop through a TikTok-style React storefront.

## Architecture
- 🤖 **WhatsApp Bot (Python)**: AI agent for sellers to add/manage products via chat
- 🛍️ **Customer Agent (Python)**: AI assistant on web storefront for finding products and buying
- 📊 **Supabase Database**: Real-time bridge between WhatsApp and web
- 🎨 **React Frontend**: TikTok-style vertical product feed with instant updates
- ⚡ **AI-Powered**: Uses LangGraph + Groq (Llama 3.3) for natural language understanding

## Features
- 🤖 **Conversational AI (Seller)**: Sellers add products by chatting in WhatsApp
- 💬 **Conversational AI (Customer)**: Customers chat with AI on the web to find specific items, check stock, and get payment links
- 📦 **Real-time Sync**: Products appear instantly in the React storefront
- 💳 **Agent Payments**: Customer Agent generates secure payment links directly in chat
- ⚡ **Image Support**: Upload product photos from WhatsApp → stored in Supabase
- 🎯 **No Dashboard Needed**: Sellers never touch a website

## Prerequisites
- **Python 3.12+**
- **Supabase Account** ([supabase.com](https://supabase.com))
- **Groq API Key** ([console.groq.com](https://console.groq.com/keys))
- **Twilio Account** ([twilio.com](https://www.twilio.com/)) for WhatsApp
- **Ngrok** ([ngrok.com](https://ngrok.com/download)) for local testing
## Quick Start

### 📖 **COMPLETE SETUP GUIDE**: See [SETUP_GUIDE.md](SETUP_GUIDE.md)

### TL;DR Version:

1. **Install dependencies**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. **Configure `.env`**
   ```env
   GROQ_API_KEY=your_groq_key
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your_service_role_key
   ```

3. **Test locally**
   ```powershell
   python test_agent.py
   ```

4. **Start server**
## How It Works

### For Sellers (via WhatsApp):
1. Send message to bot: *"Add Nike shoes, 25000 naira, 10 in stock, new, fashion"*
2. Bot extracts product details using AI
3. Saves to Supabase database
4. Product appears **instantly** in the React storefront

### For Customers (via Web):
1. Browse products in TikTok-style feed
2. Click **"Buy Now"** on any product
3. Redirected to seller's WhatsApp with pre-filled message
4. Complete purchase through WhatsApp chat

### For Customers (via Chat):
1. Ask "Do you have wired mouse?" or "Show me cheap sneakers"
2. AI checks real-time stock and shows results
3. Say "I'll take it" -> AI generates a secure **Flutterwave payment link**
4. Pay online -> Seller gets notified via WhatsApp automatically

## Project Structure
```
sharpshop/
├── server.py           # FastAPI webhook handler for WhatsApp
├── agent.py            # Seller AI Agent (LangGraph)
├── customer_agent.py   # Customer AI Agent (LangGraph)
├── tools.py            # Seller Tools
├── customer_tools.py   # Customer Tools (Search, Stock, Orders)
├── database.py         # Trader authentication & creation
├── storage.py          # Image upload to Supabase Storage
├── config.py           # Environment variables & settings
├── customer_config.py  # Customer Agent settings
├── test_agent.py       # Local testing without WhatsApp
├── SETUP_GUIDE.md      # Complete setup instructions
└── Sharp-Shop FrontEnd/ # React storefront (separate folder)
```

## Testing Examples

**Add Product:**
```
"Add Adidas sneakers for 15000 naira, 5 in stock, new condition, fashion category"
```

**With Image:**
Send photo + caption: *"Gucci bag, 45000, 2 in stock, new, fashion"*

**List Products:**
```
"Show me all my products"
```

**Search:**
```
"Do I have any Nike products?"
```

## Deployment

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for:
- WhatsApp configuration (Twilio)
- Supabase Realtime setup
- Production deployment options
- Troubleshooting common issues
## Project Structure
- `server.py`: FastAPI server handling Twilio webhooks.
- `agent.py`: LangGraph agent logic and state management.
- `tools.py`: Mock inventory tools (replace with real DB calls).
- `config.py`: Configuration settings.
