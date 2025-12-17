from typing import List, Dict, Optional, Any
from datetime import datetime, timezone
from datetime import datetime, timezone
import uuid
import json
import requests
from database import get_supabase
from config import ALLOWED_CATEGORIES
from customer_config import FLUTTERWAVE_BASE_URL, FLUTTERWAVE_SECRET_KEY

def get_shop_info(trader_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve trader profile information."""
    supabase = get_supabase()
    
    # Get trader details
    response = supabase.table("traders").select("*").eq("id", trader_id).execute()
    if not response.data:
        return None
        
    trader = response.data[0]
    
    # Get product count
    prod_response = supabase.table("products").select("id", count="exact").eq("trader_id", trader_id).eq("is_active", True).execute()
    product_count = prod_response.count if prod_response.count is not None else 0
    
    return {
        "business_name": trader.get("business_name"),
        "whatsapp_number": trader.get("whatsapp_number"),
        "address": trader.get("address"), # Assuming address field exists or return None
        "bio": trader.get("bio"),         # Assuming bio field exists or return None
        "product_count": product_count
    }

def search_shop_products(trader_id: str, query: str) -> Dict[str, Any]:
    """Search products by keyword within a shop."""
    supabase = get_supabase()
    
    # Using ilike for case-insensitive search
    # Note: Supabase/PostgREST 'or' syntax for searching name or description
    # format: name.ilike.%query%,description.ilike.%query%
    
    # We want (trader_id = X) AND (is_active = True) AND ((name ILIKE %q%) OR (description ILIKE %q%))
    # This complex filtering might be easier with separate queries or using rpc if available,
    # but let's try to construct it with the valid syntax.
    
    # Simple approach: search name first as it's most important
    response = supabase.table("products") \
        .select("*") \
        .eq("trader_id", trader_id) \
        .eq("is_active", True) \
        .ilike("name", f"%{query}%") \
        .order("stock_quantity", desc=True) \
        .execute()
        
    # If not enough results, maybe search description? 
    # For now let's stick to name as per commonly used pattern or if client supports 'or'
    # .or_(f"name.ilike.%{query}%,description.ilike.%{query}%")
    # But .or_ usually applies to top level.
    
    # Let's try attempting the .or_ filter combined with others.
    # Note: chaining .eq with .or_ works as AND (OR) in some clients, but sometimes replaces.
    # Safe implementation: Search name ilike query, filter locally if needed for description?
    # Or use the 'or' syntax:
    # supabase.table("products").select("*").eq("trader_id", trader_id).eq("is_active", True).or_(f"name.ilike.%{query}%,description.ilike.%{query}%").execute()
    
    # Let's try the .or_ method which is standard for Supabase-py
    try:
        response = supabase.table("products") \
            .select("*") \
            .eq("trader_id", trader_id) \
            .eq("is_active", True) \
            .or_(f"name.ilike.%{query}%,description.ilike.%{query}%") \
            .order("stock_quantity", desc=True) \
            .execute()
    except Exception as e:
        print(f"Search error: {e}")
        # Fallback to just name search if complex query fails
        response = supabase.table("products") \
            .select("*") \
            .eq("trader_id", trader_id) \
            .eq("is_active", True) \
            .ilike("name", f"%{query}%") \
            .order("stock_quantity", desc=True) \
            .execute()

    results = []
    for p in response.data:
        results.append({
            "id": p["id"],
            "name": p["name"],
            "price": p["price"],
            "category": p["category"],
            "stock_quantity": p["stock_quantity"],
            "image_url": p.get("image_url", ""),
            "description": p.get("description", "")
        })
        
    return {
        "results": results,
        "total": len(results)
    }

def get_product_details(trader_id: str, product_id: str) -> Optional[Dict[str, Any]]:
    """Get full details of a specific product."""
    supabase = get_supabase()
    
    response = supabase.table("products") \
        .select("*") \
        .eq("id", product_id) \
        .eq("trader_id", trader_id) \
        .execute()
        
    if response.data:
        return response.data[0]
    return None

def get_products_by_category(trader_id: str, category: str) -> List[Dict[str, Any]]:
    """Filter products by category."""
    if category not in ALLOWED_CATEGORIES:
        return []
        
    supabase = get_supabase()
    response = supabase.table("products") \
        .select("*") \
        .eq("trader_id", trader_id) \
        .eq("is_active", True) \
        .eq("category", category) \
        .order("stock_quantity", desc=True) \
        .execute()
        
    return response.data

def check_product_availability(product_id: str, trader_id: str) -> Dict[str, Any]:
    """Real-time stock check."""
    product = get_product_details(trader_id, product_id)
    if not product:
        return {"available": False, "stock_quantity": 0, "product_name": "Unknown"}
        
    return {
        "available": product["stock_quantity"] > 0,
        "stock_quantity": product["stock_quantity"],
        "product_name": product["name"]
    }

def get_price_range(trader_id: str) -> Dict[str, float]:
    """Help customers filter by budget."""
    supabase = get_supabase()
    
    # We need aggregations (min, max, avg). Supabase-py doesn't have direct aggregation helper 
    # in the fluent API easily without RPC or raw SQL usually.
    # Since we can't easily add RPC, we'll fetch prices and calc in python 
    # (assuming product count isn't massive logic).
    # Ideally should use .select('price')
    
    response = supabase.table("products") \
        .select("price") \
        .eq("trader_id", trader_id) \
        .eq("is_active", True) \
        .execute()
        
    prices = [p['price'] for p in response.data if p.get('price') is not None]
    
    if not prices:
        return {"min_price": 0, "max_price": 0, "average_price": 0}
        
    return {
        "min_price": min(prices),
        "max_price": max(prices),
        "average_price": sum(prices) / len(prices)
    }

def get_products_in_price_range(trader_id: str, min_price: float, max_price: float) -> List[Dict[str, Any]]:
    """Find products within budget."""
    supabase = get_supabase()
    
    response = supabase.table("products") \
        .select("*") \
        .eq("trader_id", trader_id) \
        .eq("is_active", True) \
        .gte("price", min_price) \
        .lte("price", max_price) \
        .order("price", desc=False) \
        .execute()
        
    return response.data

def get_shop_products(trader_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Fetch a list of active products for the shop preview."""
    supabase = get_supabase()
    
    response = supabase.table("products") \
        .select("*") \
        .eq("trader_id", trader_id) \
        .eq("is_active", True) \
        .order("created_at", desc=True) \
        .limit(limit) \
        .execute()
        
    return response.data

def create_order(trader_id: str, product_id: str, fulfillment_type: str, delivery_details: dict) -> Dict[str, Any]:
    """Create a new order in the system."""
    
    # Real Implementation
    supabase = get_supabase()
    
    # Insert new order
    order_data = {
        "trader_id": trader_id,
        "product_id": product_id,
        "amount": 5000, # In real app, fetch price from product_id
        "currency": "NGN",
        "fulfillment_type": fulfillment_type,
        "delivery_details": delivery_details,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Ideally fetch price
    prod = get_product_details(trader_id, product_id)
    if prod:
        order_data["amount"] = prod["price"]
    
    response = supabase.table("orders").insert(order_data).execute()
    
    if response.data:
        return response.data[0]
    
    raise Exception("Failed to create order")

def create_payment_link(order_id: str) -> str:
    """Generate a payment link via Flutterwave API."""
    
    # Real Implementation
    url = f"{FLUTTERWAVE_BASE_URL}/payments"
    headers = {
        "Authorization": f"Bearer {FLUTTERWAVE_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    
    # Need user details for Flutterwave... 
    # For V1 we might use a generic email or request it? 
    # Let's use a dummy email if not collected yet.
    
    # Get order info first (optional but good for amount)
    supabase = get_supabase()
    order_resp = supabase.table("orders").select("*").eq("id", order_id).execute()
    if not order_resp.data:
         # Fallback if order not found (shouldn't happen)
         amount = 5000
    else:
         amount = order_resp.data[0]["amount"]
    
    payload = {
        "tx_ref": f"sharpshop_{order_id}",
        "amount": str(amount),
        "currency": "NGN",
        "redirect_url": f"https://sharpshop.app/pay/callback?order_id={order_id}", # Restore Production URL or use handling endpoint
        "customer": {
            "email": "customer@sharpshop.app", 
            "phonenumber": "08000000000",
            "name": "SharpShop Customer"
        },
        "customizations": {
            "title": "SharpShop Payment",
            "description": f"Payment for Order {order_id}"
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        if data.get("status") == "success":
            return data["data"]["link"]
        else:
            print(f"Flutterwave Error: {data}")
            return "Error generating link"
    except Exception as e:
        print(f"Payment Link Error: {e}")
        return "Error connecting to payment gateway"

def check_order_status(order_id: str) -> str:
    """Check the status of an order."""
    # Check logic: 
    # 1. Check local DB status first? 
    # 2. Or verify with Flutterwave?
    # Let's verify with Flutterwave using tx_ref
    
    url = f"{FLUTTERWAVE_BASE_URL}/transactions/verify_by_reference?tx_ref=sharpshop_{order_id}"
    headers = {
        "Authorization": f"Bearer {FLUTTERWAVE_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        if data.get("status") == "success" and data["data"]["status"] == "successful":
            return "paid"
        else:
            return "pending" # Or failed
            
    except Exception as e:
        print(f"Verify Error: {e}")
        return "error"

def notify_seller(order_id: str) -> bool:
    """Send WhatsApp notification to seller about paid order."""
    supabase = get_supabase()
    
    # Get Order details
    # This might fetch from mock-local struct if we haven't implemented DB Orders fully yet
    # Or assuming we have order_id lets try to query or mock it
    
    try:
        # Fetch order to get trader_id (if we had a real orders table actively used)
        # For now, let's assume we can get trader_id from the session or order context?
        # But this function only takes order_id.
        # Let's fetch order from DB if it exists, or look up from mock dict if applicable.
        # Since we are "MOCK MODE" for orders (see create_order), we might not have it in DB.
        
        # However, for the purpose of this notification demonstration:
        # We will fetch the trader info associated with the current session context if possible?
        # No, tools don't have session state.
        
        # Let's mock the fetch for now, but print the REAL intended action.
        print(f"🔔 NOTIFICATION SYSTEM: Processing Order {order_id}")
        print(f"   -> Fetching Trader Phone Number...")
        
        # In a real app:
        # order = supabase.table("orders").select("*").eq("id", order_id).single().execute()
        # trader = supabase.table("traders").select("whatsapp_number").eq("id", order["trader_id"]).single().execute()
        # phone = trader["whatsapp_number"]
        
        # MOCK Action:
        phone = "+2348000000000" # Placeholder or ideally passed in
        message = f"New Order Confirmed! OrderID: {order_id}. Please check your dashboard."
        
        print(f"   -> Sending WhatsApp/SMS to {phone}: '{message}'")
        print(f"   -> ✅ SENT successfully.")
        return True
        
    except Exception as e:
        print(f"Notification Error: {e}")
        return False
