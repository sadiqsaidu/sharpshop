"""Check traders in database to diagnose WhatsApp number matching issue."""
from database import get_supabase

supabase = get_supabase()

# Get all traders
result = supabase.table("traders").select("id, business_name, whatsapp_number, user_id").execute()

print("=" * 80)
print("ALL TRADERS IN DATABASE:")
print("=" * 80)

for trader in result.data:
    print(f"\nID: {trader['id']}")
    print(f"Business Name: {trader['business_name']}")
    print(f"WhatsApp Number: {trader.get('whatsapp_number', 'NOT SET')}")
    print(f"User ID: {trader['user_id']}")
    print("-" * 80)

print(f"\nTotal traders: {len(result.data)}")

# Show which numbers we're looking for
test_numbers = ["+2349010674385", "2349010674385", "+2348071014732", "+2348077048651"]
print("\n" + "=" * 80)
print("TESTING NUMBER LOOKUPS:")
print("=" * 80)

for num in test_numbers:
    result = supabase.table("traders").select("business_name, whatsapp_number").eq("whatsapp_number", num).execute()
    if result.data:
        print(f"✅ {num} → Found: {result.data[0]['business_name']}")
    else:
        print(f"❌ {num} → NOT FOUND")
