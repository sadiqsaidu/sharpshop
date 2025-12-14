"""Supabase database operations."""
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY
from typing import Optional
import uuid

def get_supabase() -> Client:
    """Get Supabase client."""
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def get_trader_by_whatsapp(whatsapp_number: str) -> Optional[dict]:
    """Get existing trader by WhatsApp number. Returns None if not found."""
    supabase = get_supabase()
    
    # Normalize WhatsApp number (remove spaces, ensure format is consistent)
    normalized_number = whatsapp_number.strip().replace(" ", "")
    
    print(f"🔍 Looking for registered seller with WhatsApp: {normalized_number}")
    
    # Try exact match first
    result = supabase.table("traders").select("*").eq("whatsapp_number", normalized_number).execute()
    if result.data and len(result.data) > 0:
        print(f"✅ Found registered seller: {result.data[0]['business_name']}")
        return result.data[0]
    
    # Try without + prefix
    if normalized_number.startswith("+"):
        alt_number = normalized_number[1:]
        result = supabase.table("traders").select("*").eq("whatsapp_number", alt_number).execute()
        if result.data and len(result.data) > 0:
            print(f"✅ Found registered seller (without +): {result.data[0]['business_name']}")
            return result.data[0]
    else:
        # Try with + prefix
        alt_number = f"+{normalized_number}"
        result = supabase.table("traders").select("*").eq("whatsapp_number", alt_number).execute()
        if result.data and len(result.data) > 0:
            print(f"✅ Found registered seller (with +): {result.data[0]['business_name']}")
            return result.data[0]
    
    # Try Nigerian format conversion (0xxx -> +234xxx)
    if normalized_number.startswith("0"):
        nigerian_format = f"+234{normalized_number[1:]}"
        result = supabase.table("traders").select("*").eq("whatsapp_number", nigerian_format).execute()
        if result.data and len(result.data) > 0:
            print(f"✅ Found registered seller (Nigerian format): {result.data[0]['business_name']}")
            return result.data[0]
    
    # Try reverse: +234xxx -> 0xxx
    if normalized_number.startswith("+234"):
        local_format = f"0{normalized_number[4:]}"
        result = supabase.table("traders").select("*").eq("whatsapp_number", local_format).execute()
        if result.data and len(result.data) > 0:
            print(f"✅ Found registered seller (local format): {result.data[0]['business_name']}")
            return result.data[0]
    
    print(f"❌ No registered seller found for WhatsApp: {normalized_number}")
    return None


# Keep old function name for backward compatibility but redirect to new function
def get_or_create_trader(whatsapp_number: str, business_name: str = "New Seller") -> Optional[dict]:
    """Deprecated: Use get_trader_by_whatsapp instead. Now only returns existing traders."""
    return get_trader_by_whatsapp(whatsapp_number)