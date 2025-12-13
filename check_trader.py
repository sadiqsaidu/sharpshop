"""Quick script to check trader profile."""
from database import get_supabase

supabase = get_supabase()

# Check trader profile for user Ahmfatya
user_result = supabase.table("users").select("id, username, business_name").eq("username", "Ahmfatya").execute()
if user_result.data:
    user = user_result.data[0]
    print(f"User: {user['username']}")
    print(f"User ID: {user['id']}")
    print(f"Business Name: {user.get('business_name')}")
    
    # Get trader profile
    trader_result = supabase.table("traders").select("*").eq("user_id", user['id']).execute()
    if trader_result.data:
        trader = trader_result.data[0]
        print(f"\nTrader ID: {trader['id']}")
        print(f"WhatsApp Number: {trader['whatsapp_number']}")
        print(f"Business Name: {trader['business_name']}")
    else:
        print("\n❌ No trader profile found!")
else:
    print("❌ User not found!")

# Also check what the get_or_create_trader function returns
print("\n--- Testing get_or_create_trader ---")
from database import get_or_create_trader
trader = get_or_create_trader("+2347051268773", "AI Test Shop")
print(f"Returned Trader ID: {trader['id']}")
print(f"Returned Business Name: {trader['business_name']}")
