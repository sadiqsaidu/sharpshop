import time
import uuid
from typing import Dict, TypedDict, Optional, List, Literal
from datetime import datetime, timezone
from customer_config import SESSION_TTL, MAX_SESSION_MESSAGES, MAX_SESSION_DURATION

class CustomerAgentState(TypedDict):
    messages: list[dict]
    trader_id: str
    trader_name: str
    whatsapp_number: str
    session_id: str
    created_at: str
    last_activity: str
    context: dict
    # Payment & Fulfillment State
    product_id: Optional[str]
    order_id: Optional[str]
    fulfillment_type: Optional[Literal["delivery", "pickup"]]
    delivery_details: Optional[Dict[str, str]]
    payment_link: Optional[str]
    status: Literal[
        "browsing",
        "awaiting_fulfillment",
        "awaiting_payment",
        "collecting_delivery_details",
        "paid",
        "completed",
    ]

class Session(TypedDict):
    session_id: str
    trader_id: str
    state: CustomerAgentState
    created_at: float
    last_activity: float
    message_count: int

# In-memory session store
sessions: Dict[str, Session] = {}

def create_session(trader_id: str, trader_name: str, whatsapp_number: str) -> Session:
    """Create a new session for a customer interacting with a specific trader."""
    session_id = str(uuid.uuid4())
    now_ts = time.time()
    now_iso = datetime.now(timezone.utc).isoformat()
    
    initial_state: CustomerAgentState = {
        "messages": [],
        "trader_id": trader_id,
        "trader_name": trader_name,
        "whatsapp_number": whatsapp_number,
        "session_id": session_id,
        "created_at": now_iso,
        "last_activity": now_iso,
        "context": {},
        "product_id": None,
        "order_id": None,
        "fulfillment_type": None,
        "delivery_details": None,
        "payment_link": None,
        "status": "browsing"
    }
    
    session: Session = {
        "session_id": session_id,
        "trader_id": trader_id,
        "state": initial_state,
        "created_at": now_ts,
        "last_activity": now_ts,
        "message_count": 0
    }
    
    sessions[session_id] = session
    return session

def get_session(session_id: str) -> Optional[Session]:
    """Retrieve a session by ID, checking for expiration."""
    session = sessions.get(session_id)
    if not session:
        return None
        
    now = time.time()
    
    # Check TTL
    if now - session["last_activity"] > SESSION_TTL:
        del sessions[session_id]
        return None
        
    # Check max duration
    if now - session["created_at"] > MAX_SESSION_DURATION:
        del sessions[session_id]
        return None
        
    # Update last activity
    session["last_activity"] = now
    session["state"]["last_activity"] = datetime.now(timezone.utc).isoformat()
    return session

def update_session(session_id: str, state: CustomerAgentState) -> None:
    """Update session state."""
    if session_id in sessions:
        sessions[session_id]["state"] = state
        sessions[session_id]["message_count"] = len(state["messages"])
        
def cleanup_expired_sessions() -> int:
    """Remove expired sessions to free memory. Returns count of removed sessions."""
    now = time.time()
    expired = []
    
    for sid, session in sessions.items():
        if (now - session["last_activity"] > SESSION_TTL) or \
           (now - session["created_at"] > MAX_SESSION_DURATION):
            expired.append(sid)
            
    for sid in expired:
        del sessions[sid]
        
    return len(expired)
