"""Test the database connection and product creation without AI agent."""
from database import get_or_create_trader
from tools import create_product, list_products, query_inventory

# Create a test trader
test_whatsapp = "+2348012345678"
print(f"Creating test trader with WhatsApp: {test_whatsapp}")
trader = get_or_create_trader(test_whatsapp, "Test Shop")
print(f"✅ Trader created: {trader['business_name']} (ID: {trader['id']})")

# Test 1: Add a product manually (without AI)
print("\n--- Test 1: Adding Product ---")
result = create_product(
    name="Nike Air Max shoes",
    price=25000,
    category="Fashion",
    stock=10,
    trader_id=trader["id"],
    trader_name=trader["business_name"],
    whatsapp_number=test_whatsapp,
    description="Authentic Nike Air Max sneakers",
    image="https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500"
)

if result["success"]:
    print(f"✅ Product added! (ID: {result['product_id']})")
else:
    print(f"❌ Error: {result['error']}")

# Test 2: List all products for this trader
print("\n--- Test 2: List Products ---")
products_result = list_products(trader["id"])

if products_result["success"]:
    print(f"📦 Found {products_result['total']} products:")
    for p in products_result["products"]:
        print(f"  • {p['name']} - ₦{p['price']:,} ({p['stock_quantity']} in stock)")
else:
    print(f"❌ Error: {products_result['error']}")

# Test 3: Search inventory
print("\n--- Test 3: Search for 'Nike' ---")
search_result = query_inventory("Nike", trader["id"])

if search_result["success"]:
    print(f"📦 Found {search_result['total']} items:")
    for p in search_result["results"]:
        print(f"  • {p['name']} - ₦{p['price']:,} ({p['stock_quantity']} in stock)")
else:
    print(f"❌ Error: {search_result['error']}")

print("\n✅ All tests completed!")
print("\n🌐 Now check your frontend at http://localhost:5000 to see if the product appears!")
print("   (Make sure your React app is running and Supabase Realtime is enabled)")

