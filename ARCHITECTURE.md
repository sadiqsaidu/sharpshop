# 🏗️ SharpShop Architecture - How It All Works

## 🔄 Complete Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         YOUR SYSTEM                              │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│  WHATSAPP    │         │   PYTHON     │         │    REACT     │
│   (Seller)   │────────▶│   BACKEND    │────────▶│   FRONTEND   │
│              │         │              │         │  (Customer)  │
└──────────────┘         └──────────────┘         └──────────────┘
      ▲                         │                         ▲
      │                         ▼                         │
      │                  ┌──────────────┐                 │
      │                  │   SUPABASE   │─────────────────┘
      │                  │   DATABASE   │   (Realtime)
      │                  └──────────────┘
      │                         │
      └─────────────────────────┘
           (WhatsApp Checkout)
```

---

## 📱 Flow 1: Seller Adds Product (WhatsApp → Web)

```
1. Seller (WhatsApp)
   │
   │ Sends: "Add Nike shoes, 25000 naira, 10 stock, new, fashion"
   │
   ▼
2. Twilio (WhatsApp Gateway)
   │
   │ POST /whatsapp with message body
   │
   ▼
3. server.py (FastAPI)
   │
   │ - Receives webhook
   │ - Extracts message & sender phone
   │ - Downloads images (if any)
   │
   ▼
4. storage.py
   │
   │ - Downloads images from Twilio
   │ - Uploads to Supabase Storage
   │ - Returns permanent URLs
   │
   ▼
5. database.py
   │
   │ - get_or_create_trader(whatsapp_number)
   │ - Returns trader UUID
   │
   ▼
6. agent.py (LangGraph AI)
   │
   │ - Sends message to Groq (Llama 3.3)
   │ - AI extracts: name, price, category, stock, condition
   │ - Builds JSON: {"action": "create_product", "data": {...}}
   │
   ▼
7. tools.py
   │
   │ create_product(name, price, category, stock, ...)
   │
   ▼
8. Supabase Database
   │
   │ INSERT INTO products VALUES (...)
   │ ✅ Product saved!
   │
   ▼
9. Supabase Realtime
   │
   │ Broadcasts change to all subscribed clients
   │
   ▼
10. React Frontend (home.tsx)
    │
    │ - Receives realtime event
    │ - Invalidates React Query cache
    │ - Re-fetches products
    │ - Updates UI automatically
    │
    ▼
11. Customer sees new product instantly! 🎉
```

---

## 🛒 Flow 2: Customer Buys Product (Web → WhatsApp)

```
1. Customer (React App)
   │
   │ Browses products in TikTok-style feed
   │
   ▼
2. ProductCard.tsx
   │
   │ Clicks "Buy Now" button
   │
   ▼
3. handleBuyClick()
   │
   │ const message = "Hi, I'm interested in *Nike shoes* - ₦25,000"
   │ const url = `https://wa.me/${whatsappNumber}?text=${message}`
   │ window.open(url)
   │
   ▼
4. WhatsApp App Opens
   │
   │ - Opens chat with seller's WhatsApp number
   │ - Pre-fills message with product details
   │
   ▼
5. Customer & Seller Chat
   │
   │ - Customer asks questions
   │ - Seller responds
   │ - They negotiate & complete sale
   │
   ▼
6. Transaction Complete! 💰
```

---

## 🔧 Component Breakdown

### Python Backend Components

```
server.py
├─ FastAPI app
├─ POST /whatsapp endpoint
├─ Handles Twilio webhooks
└─ Manages user sessions (in-memory)

agent.py
├─ LangGraph state machine
├─ Groq API integration (AI)
├─ Conversation flow management
└─ Action execution logic

tools.py
├─ create_product()
├─ query_inventory()
├─ update_product()
└─ list_products()

database.py
├─ get_supabase()
└─ get_or_create_trader()

storage.py
├─ download_and_upload_image()
└─ process_images()

config.py
└─ Environment variables
```

### React Frontend Components

```
home.tsx
├─ Product feed (TikTok-style)
├─ Supabase Realtime subscription
└─ Auto-refresh on changes

ProductCard.tsx
├─ Individual product display
├─ Buy Now button
└─ WhatsApp redirect

seller-dashboard.tsx
├─ Seller's profile page
├─ Product list (read-only)
└─ WhatsApp contact info
```

---

## 🗄️ Database Schema

### traders table
```sql
id               UUID         PRIMARY KEY
user_id          UUID         NULLABLE (FK to users)
business_name    TEXT         "Nike Store"
whatsapp_number  TEXT         "+2348012345678"
address          TEXT         "123 Lagos St"
bio              TEXT         "Authentic sneakers"
created_at       TIMESTAMP    NOW()
```

### products table
```sql
id               UUID         PRIMARY KEY
trader_id        UUID         FK to traders.id
whatsapp_number  TEXT         "+2348012345678" (for checkout)
name             TEXT         "Nike Air Max"
price            NUMERIC      25000
category         TEXT         "fashion"
stock            INTEGER      10
condition        TEXT         "new"
description      TEXT         "Authentic Nike..."
size             TEXT         "42"
brand            TEXT         "Nike"
image            TEXT         "https://..."
created_at       TIMESTAMP    NOW()
```

---

## 🔐 Authentication Flow

### Seller Auth (WhatsApp)
```
1. Seller sends message to Twilio number
2. Twilio forwards to your webhook with 'From' field
3. database.py checks if trader exists by whatsapp_number
4. If not, creates new trader record
5. All products linked to this trader_id
```

### Customer Auth (React)
```
1. Customer signs up via auth modal
2. Creates record in 'users' table
3. Passport.js session-based auth
4. Can like/favorite products
```

---

## 🔄 Realtime Sync Mechanism

```
┌─────────────────────────────────────────────────────────┐
│ Supabase Realtime (Postgres LISTEN/NOTIFY)             │
└─────────────────────────────────────────────────────────┘

When: Python inserts product into Supabase
     │
     ▼
Postgres triggers NOTIFY event
     │
     ▼
Supabase Realtime broadcasts to all WebSocket clients
     │
     ▼
React app receives event via subscription
     │
     ▼
React Query invalidates cache
     │
     ▼
UI re-fetches and updates automatically
```

**Code in home.tsx:**
```typescript
useEffect(() => {
  const channel = supabase
    .channel('products-changes')
    .on('postgres_changes', 
        { event: '*', schema: 'public', table: 'products' },
        () => { queryClient.invalidateQueries(['/api/products']) }
    )
    .subscribe();
  
  return () => { supabase.removeChannel(channel) };
}, []);
```

---

## 📊 State Management

### Python (Agent State)
```python
AgentState = {
    "messages": [],              # Conversation history
    "trader_id": "uuid",         # Who's chatting
    "whatsapp_number": "+234...", # Their WhatsApp
    "pending_action": "create_product",  # What to do next
    "collected_data": {...},     # Extracted product info
    "image_urls": [...]          # Uploaded images
}
```

### React (Query State)
```typescript
// Server state (React Query)
const { data: products } = useQuery(['/api/products'])

// Local state (React Context)
const { user } = useAuth()

// Realtime state (Supabase)
supabase.channel('products-changes').subscribe()
```

---

## 🌐 API Endpoints

### Python Backend (FastAPI)
```
POST /whatsapp
├─ Accepts Twilio webhook
├─ Processes WhatsApp messages
└─ Returns TwiML response
```

### React Backend (Express)
```
GET  /api/products           # List all products
GET  /api/products/:id       # Get single product
GET  /api/trader/me          # Current seller's profile
GET  /api/traders/:id        # Public trader profile
GET  /api/products/trader/:id # Trader's products
POST /api/auth/login         # Customer login
POST /api/auth/signup        # Customer signup
POST /api/auth/logout        # Logout
```

---

## 🎯 Key Integration Points

### Point 1: WhatsApp → Supabase
**File:** `server.py` + `tools.py`
```python
# server.py receives message
trader = get_or_create_trader(whatsapp_number)

# tools.py inserts into Supabase
supabase.table("products").insert({
    "trader_id": trader["id"],
    "whatsapp_number": whatsapp_number,
    "name": "Nike shoes",
    ...
}).execute()
```

### Point 2: Supabase → React
**File:** `home.tsx`
```typescript
// Subscribe to changes
supabase.channel('products-changes')
  .on('postgres_changes', ...)
  .subscribe()

// Auto-refresh
queryClient.invalidateQueries(['/api/products'])
```

### Point 3: React → WhatsApp
**File:** `ProductCard.tsx`
```typescript
const handleBuyClick = () => {
  const message = `Hi, I'm interested in *${product.name}*`
  const url = `https://wa.me/${product.whatsappNumber}?text=${message}`
  window.open(url, '_blank')
}
```

---

## 📦 Dependencies

### Python
```
fastapi         # Web framework
uvicorn         # ASGI server
supabase        # Database client
openai          # Groq API (OpenAI-compatible)
langgraph       # AI agent framework
twilio          # WhatsApp integration
requests        # Image downloads
python-dotenv   # Environment variables
```

### React
```
@tanstack/react-query   # Server state management
@supabase/supabase-js   # Realtime subscriptions
framer-motion           # Animations
tailwindcss             # Styling
lucide-react            # Icons
```

---

## 🚀 Deployment Architecture

```
Production Setup:

┌──────────────┐
│   WhatsApp   │
│   Business   │
│   API (Meta) │
└──────┬───────┘
       │
       ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   Railway    │      │   Supabase   │      │   Vercel     │
│   (Python)   │◄────▶│   (Database) │◄────▶│   (React)    │
│   Backend    │      │   + Storage  │      │   Frontend   │
└──────────────┘      └──────────────┘      └──────────────┘
```

**Why this setup?**
- Railway: Persistent Python server for webhooks
- Supabase: Managed Postgres with Realtime
- Vercel: Static React hosting with CDN

---

## 🔍 Debugging Checklist

When something doesn't work:

```
┌─ WhatsApp not responding?
│  └─ Check server.log
│     └─ Check ngrok is running
│        └─ Check Twilio webhook URL
│
├─ Products not appearing in frontend?
│  └─ Check Supabase Table Editor
│     └─ Check Realtime is enabled
│        └─ Check browser console
│
├─ "Invalid API key"?
│  └─ Check .env file
│     └─ Use SERVICE ROLE KEY
│        └─ Restart server
│
└─ AI not extracting fields?
   └─ Check Groq API key
      └─ Check server logs
         └─ Test locally with test_agent.py
```

---

## 💡 Pro Tips

1. **Always check logs first:**
   ```powershell
   Get-Content server.log -Wait -Tail 50
   ```

2. **Test components separately:**
   - Database: `test_agent.py`
   - Server: `python server.py` → check http://localhost:8000/docs
   - Frontend: Check browser console

3. **Use Supabase dashboard:**
   - Table Editor to verify data
   - Logs to see API calls
   - Realtime inspector to monitor subscriptions

4. **Ngrok free tier resets every 2 hours:**
   - Update Twilio webhook when URL changes
   - Or upgrade to ngrok paid for static URLs

---

This architecture gives you:
✅ No-code experience for sellers (WhatsApp only)
✅ Modern shopping experience for customers (React)
✅ Real-time sync (Supabase Realtime)
✅ AI-powered inventory management (LangGraph + Groq)
✅ Scalable infrastructure (serverless-ready)
