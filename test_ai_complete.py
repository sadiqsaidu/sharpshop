"""Test the AI agent - complete flow with all required fields."""
from agent import create_initial_state, chat

# Create state for a test trader
print("Creating test trader...")
state = create_initial_state("+2347051268773", "AI Test Shop")
print(f"✅ Trader: {state['trader_name']} (ID: {state['trader_id']})\n")

# Test: Add complete product in one message
print("=== Adding Product ===")
state = chat(state, "I want to sell Nike Air Jordan sneakers for 45000 naira, I have 5 pieces in stock, category is Fashion. They are brand new authentic sneakers from Nike.")
print(f"AI: {state['messages'][-1]['content']}\n")

# Check if product was created
if "Product added" in state['messages'][-1]['content']:
    print("✅ Product created successfully!")
    
    # Test: List products
    print("\n=== Listing Products ===")
    state = chat(state, "show me all my products")
    print(f"AI: {state['messages'][-1]['content']}\n")
    
    # Test: Search
    print("\n=== Searching for Nike ===")
    state = chat(state, "search for Nike")
    print(f"AI: {state['messages'][-1]['content']}\n")
else:
    print("⚠ Product not created yet, AI might need more info")

print("✅ Test completed!")
