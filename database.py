"""Supabase database operations."""
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY
from typing import Optional
import uuid

def get_supabase() -> Client:
    """Get Supabase client."""
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def get_or_create_trader(whatsapp_number: str, business_name: str = "New Seller") -> dict:
    """Get existing trader or create new one by WhatsApp number."""
    supabase = get_supabase()
    
    # Normalize WhatsApp number (remove spaces, ensure format is consistent)
    normalized_number = whatsapp_number.strip().replace(" ", "")
    
    # Try to get existing trader by exact WhatsApp number match
    result = supabase.table("traders").select("*").eq("whatsapp_number", normalized_number).execute()
    
    if result.data and len(result.data) > 0:
        print(f"✅ Found existing trader for {normalized_number}: {result.data[0]['business_name']}")
        return result.data[0]
    
    # Also try without the + prefix in case it's stored differently
    if normalized_number.startswith("+"):
        result = supabase.table("traders").select("*").eq("whatsapp_number", normalized_number[1:]).execute()
        if result.data and len(result.data) > 0:
            print(f"✅ Found existing trader (without +): {result.data[0]['business_name']}")
            return result.data[0]
    else:
        # Try with + prefix
        result = supabase.table("traders").select("*").eq("whatsapp_number", f"+{normalized_number}").execute()
        if result.data and len(result.data) > 0:
            print(f"✅ Found existing trader (with +): {result.data[0]['business_name']}")
            return result.data[0]
    
    print(f"⚠️ No existing trader found for {normalized_number}, creating new one...")
    
    # Create a dummy user first (since userId is required)
    user_id = str(uuid.uuid4())
    supabase.table("users").insert({
        "id": user_id,
        "username": f"whatsapp_{normalized_number}",
        "password": "dummy_password",  # In production, use proper auth
        "role": "seller",
        "business_name": business_name
    }).execute()
    
    # Create new trader linked to the user
    trader_id = str(uuid.uuid4())
    new_trader = supabase.table("traders").insert({
        "id": trader_id,
        "user_id": user_id,
        "whatsapp_number": normalized_number,
        "business_name": business_name
    }).execute()
    
    print(f"✅ Created new trader: {business_name}")
    return new_trader.data[0]