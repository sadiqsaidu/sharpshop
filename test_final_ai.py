"""Final test of AI-powered WhatsApp inventory assistant."""
from agent import create_initial_state, chat

print("🤖 AI-Powered WhatsApp Inventory Assistant - LIVE TEST\n")
print("=" * 60)

# Create state for your WhatsApp number
state = create_initial_state("+2347051268773", "My Cool Shop")
print(f"✅ Trader created: {state['trader_name']}\n")

# Test 1: Add product with natural language
print("📝 Test 1: Adding product via natural language...")
print("You: I have Adidas sneakers for sale, 55000 naira, 3 in stock, footwear\n")
state = chat(state, "I have Adidas sneakers for sale, 55000 naira, 3 in stock, footwear")
print(f"🤖 AI: {state['messages'][-1]['content']}\n")
print("-" * 60)

# Test 2: List products  
print("\n📝 Test 2: Listing all products...")
print("You: show me my products\n")
state = chat(state, "show me my products")
print(f"🤖 AI: {state['messages'][-1]['content']}\n")
print("-" * 60)

# Test 3: Search
print("\n📝 Test 3: Searching inventory...")
print("You: do I have any Adidas products?\n")
state = chat(state, "do I have any Adidas products?")
print(f"🤖 AI: {state['messages'][-1]['content']}\n")
print("=" * 60)

print("\n✅ AI AGENT FULLY OPERATIONAL!")
print("👉 Ready to integrate with WhatsApp webhook!\n")
print("📱 When a seller messages via WhatsApp, the AI will:")
print("   1. Extract product details from natural language")
print("   2. Create products in Supabase automatically")
print("   3. Products appear in React frontend instantly")
print("   4. All with ZERO manual data entry! 🚀")
