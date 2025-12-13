"""Script to delete the old AI Test Shop trader profile."""
from database import get_supabase

supabase = get_supabase()

# Delete the old "AI Test Shop" trader that's conflicting
old_trader_id = "963bea7f-6982-4d47-83c9-f3d6504542e5"

print(f"Deleting old 'AI Test Shop' trader profile: {old_trader_id}")

# First, update all products from this trader to use the correct Ahmfatya trader
new_trader_id = "4b64d960-3992-4952-b6a4-6af311e6bfe8"

products = supabase.table("products").select("id, name").eq("trader_id", old_trader_id).execute()
if products.data:
    print(f"\nFound {len(products.data)} products to reassign...")
    for product in products.data:
        supabase.table("products").update({
            "trader_id": new_trader_id,
            "trader_name": "Ahmfatya"
        }).eq("id", product["id"]).execute()
        print(f"  ✅ Updated product: {product['name']}")

# Now delete the old trader profile
supabase.table("traders").delete().eq("id", old_trader_id).execute()
print(f"\n✅ Deleted old trader profile")

# Also delete the dummy user
old_user_id = "54017b49-bb6e-46aa-a017-e8cece4597d0"
supabase.table("users").delete().eq("id", old_user_id).execute()
print(f"✅ Deleted dummy user account")

print("\n✅ Cleanup complete! All products now belong to Ahmfatya account.")
