"""Script to link your WhatsApp number to your existing user account."""
from database import get_supabase
import sys

def link_whatsapp_to_user(username: str, whatsapp_number: str):
    """Link a WhatsApp number to an existing user account."""
    supabase = get_supabase()
    
    # Find user by username
    user_result = supabase.table("users").select("*").eq("username", username).execute()
    
    if not user_result.data:
        print(f"❌ User '{username}' not found!")
        return False
    
    user = user_result.data[0]
    user_id = user["id"]
    
    print(f"✅ Found user: {user['username']} (ID: {user_id})")
    
    # Check if user already has a trader profile
    trader_result = supabase.table("traders").select("*").eq("user_id", user_id).execute()
    
    if trader_result.data:
        # Update existing trader with WhatsApp number
        trader = trader_result.data[0]
        trader_id = trader["id"]
        business_name = trader["business_name"]
        
        update_result = supabase.table("traders").update({
            "whatsapp_number": whatsapp_number
        }).eq("id", trader_id).execute()
        
        print(f"✅ Updated trader profile with WhatsApp number: {whatsapp_number}")
        print(f"   Trader: {business_name}")
    else:
        # Create new trader profile for this user
        import uuid
        trader_id = str(uuid.uuid4())
        business_name = user.get("business_name") or f"{username}'s Shop"
        
        new_trader = supabase.table("traders").insert({
            "id": trader_id,
            "user_id": user_id,
            "whatsapp_number": whatsapp_number,
            "business_name": business_name
        }).execute()
        
        print(f"✅ Created trader profile with WhatsApp number: {whatsapp_number}")
        print(f"   Business: {business_name}")
    
    # Update products to use the correct trader
    products_result = supabase.table("products").select("id, name").eq(
        "whatsapp_number", whatsapp_number
    ).execute()
    
    if products_result.data:
        print(f"\n📦 Found {len(products_result.data)} products to update...")
        for product in products_result.data:
            supabase.table("products").update({
                "trader_id": trader_id,
                "trader_name": business_name
            }).eq("id", product["id"]).execute()
        print(f"✅ Updated {len(products_result.data)} products")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python link_whatsapp.py <username> <whatsapp_number>")
        print("Example: python link_whatsapp.py myusername +2347051268773")
        sys.exit(1)
    
    username = sys.argv[1]
    whatsapp_number = sys.argv[2]
    
    print(f"\n🔗 Linking WhatsApp number to user account...")
    print(f"   Username: {username}")
    print(f"   WhatsApp: {whatsapp_number}\n")
    
    if link_whatsapp_to_user(username, whatsapp_number):
        print("\n✅ Successfully linked! Future WhatsApp uploads will appear under your account.")
    else:
        print("\n❌ Failed to link account.")
