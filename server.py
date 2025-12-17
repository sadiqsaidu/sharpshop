"""FastAPI server for WhatsApp chatbot."""
from fastapi import FastAPI, Form, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from twilio.twiml.messaging_response import MessagingResponse
from agent import create_initial_state, chat
from database import get_trader_by_whatsapp
from storage import process_images
import uvicorn
import logging
import os

# Configure logging
logging.basicConfig(
    filename='server.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    force=True
)

app = FastAPI()

# CORS Configuration for production
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5000")
allowed_origins = [
    frontend_url,
    "https://sharpshop.app",
    "https://www.sharpshop.app",
    "https://sharpshop-frontend-011b1462cb27.herokuapp.com",
    "http://localhost:5000",
    "http://localhost:8001",
    "http://0.0.0.0:8001"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store
user_sessions = {}

@app.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    """Handle incoming WhatsApp messages."""
    form_data = await request.form()
    incoming_msg = form_data.get('Body', '').strip()
    sender_id = form_data.get('From', '')
    
    # Check for media (images)
    num_media = int(form_data.get('NumMedia', 0))
    twilio_image_urls = []
    if num_media > 0:
        for i in range(num_media):
            media_url = form_data.get(f'MediaUrl{i}')
            if media_url:
                twilio_image_urls.append(media_url)
    
    logging.info(f"Received message from {sender_id}: {incoming_msg}")
    
    # Extract WhatsApp number without 'whatsapp:' prefix
    whatsapp_number = sender_id.replace('whatsapp:', '')
    
    # Check if this is a registered seller
    trader = get_trader_by_whatsapp(whatsapp_number)
    
    if trader is None:
        # Not a registered seller - send rejection message
        logging.warning(f"❌ Unregistered WhatsApp number attempted to upload: {whatsapp_number}")
        resp = MessagingResponse()
        resp.message("⚠️ Sorry, this WhatsApp number is not registered as a seller on SharpShop.\n\nTo upload products, please register as a seller at https://sharpshop.app first using this same WhatsApp number.")
        return Response(content=str(resp), media_type="application/xml")
    
    # Process images - download from Twilio and upload to Supabase
    permanent_image_urls = []
    if twilio_image_urls:
        logging.info(f"Processing {len(twilio_image_urls)} images...")
        permanent_image_urls = process_images(twilio_image_urls)
        logging.info(f"Uploaded {len(permanent_image_urls)} images to Supabase")

    # Get or create user state
    if sender_id not in user_sessions:
        user_sessions[sender_id] = create_initial_state(whatsapp_number, trader["business_name"])
    
    state = user_sessions[sender_id]
    
    # Add image URL to state if provided
    image_url = permanent_image_urls[0] if permanent_image_urls else None
    
    # Process message through agent
    try:
        new_state = chat(state, incoming_msg, image_url)
        user_sessions[sender_id] = new_state
        
        # Get the last assistant message
        response_text = "Sorry, I didn't understand that."
        for msg in reversed(new_state["messages"]):
            if msg["role"] == "assistant":
                response_text = msg["content"]
                break
    except Exception as e:
        logging.error(f"Error processing message: {e}")
        response_text = "Sorry, I encountered an error processing your request."

    # Send response back to Twilio
    resp = MessagingResponse()
    resp.message(response_text)
    
    return Response(content=str(resp), media_type="application/xml")


# --- Customer Agent API ---
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
from customer_sessions import create_session, get_session, update_session, cleanup_expired_sessions
from customer_agent import handle_customer_chat
from customer_tools import get_shop_info
from starlette.concurrency import run_in_threadpool

class CustomerChatRequest(BaseModel):
    trader_id: str
    message: str
    session_id: Optional[str] = None

class CustomerChatResponse(BaseModel):
    session_id: str
    reply: str
    products: List[dict] = []
    timestamp: str

class NewSessionRequest(BaseModel):
    trader_id: str

class NewSessionResponse(BaseModel):
    session_id: str
    trader_name: str
    created_at: str

@app.post("/api/chat/customer", response_model=CustomerChatResponse)
async def customer_chat(request: CustomerChatRequest):
    """Handle customer chat messages via web interface."""
    
    # 1. Get or create session
    session = None
    if request.session_id:
        session = get_session(request.session_id)
            
    if not session:
        # Check if trader exists
        shop_info = get_shop_info(request.trader_id)
        if not shop_info:
             return Response(content="Shop not found", status_code=404)
             
        session = create_session(request.trader_id, shop_info["business_name"], shop_info["whatsapp_number"])

    # 2. Process message
    # Run agent in threadpool to avoid blocking event loop
    new_state = await run_in_threadpool(handle_customer_chat, session["state"], request.message)
    
    # 3. Update session
    update_session(session["session_id"], new_state)
    
    # 4. Extract reply
    assistant_msg = next((m["content"] for m in reversed(new_state["messages"]) if m["role"] == "assistant"), "No response generated")
    
    # Extract products from tool results
    products = []
    tool_result = new_state["context"].get("tool_result")
    if isinstance(tool_result, dict):
        if "results" in tool_result:
             products = tool_result["results"][:5] # Limit to 5
        elif "available" in tool_result:
             pass
    elif isinstance(tool_result, list):
        products = tool_result[:5]
        
    return CustomerChatResponse(
        session_id=session["session_id"],
        reply=assistant_msg,
        products=products,
        timestamp=datetime.now(timezone.utc).isoformat()
    )

@app.post("/api/chat/customer/session/new", response_model=NewSessionResponse)
async def create_new_customer_session(request: NewSessionRequest):
    """Explicitly create a new session."""
    shop_info = get_shop_info(request.trader_id)
    if not shop_info:
        return Response(content="Shop not found", status_code=404)
        
    session = create_session(request.trader_id, shop_info["business_name"], shop_info["whatsapp_number"])
    
    return NewSessionResponse(
        session_id=session["session_id"],
        trader_name=shop_info["business_name"],
        created_at=datetime.now(timezone.utc).isoformat()
    )

@app.delete("/api/chat/customer/session/{session_id}")
async def end_customer_session(session_id: str):
    """Cleanup session on close."""
    from customer_sessions import sessions
    if session_id in sessions:
        del sessions[session_id]
    return Response(status_code=204)

@app.get("/api/chat/customer/session/{session_id}/history")
async def get_session_history_endpoint(session_id: str):
    session = get_session(session_id)
    if not session:
        return Response(content="Session not found", status_code=404)
        
    return {
        "session_id": session_id,
        "messages": session["state"]["messages"]
    }

@app.get("/api/shop/{trader_id}/preview")
async def get_shop_preview(trader_id: str):
    """Get aggregated shop info and products for preview."""
    
    # Run DB calls in threadpool
    from customer_tools import get_shop_products
    
    shop_info = await run_in_threadpool(get_shop_info, trader_id)
    if not shop_info:
        return Response(content="Shop not found", status_code=404)
        
    products = await run_in_threadpool(get_shop_products, trader_id)
    
    return {
        "shop": shop_info,
        "products": products
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)