"""Test the AI agent with natural language product creation."""
from agent import create_initial_state, chat

# Create state for a test trader
print("Creating test trader...")
state = create_initial_state("+2347051268773", "AI Test Shop")
print(f"✅ Trader: {state['trader_name']} (ID: {state['trader_id']})\n")

# Test 1: Natural language product creation
print("=== Test 1: Add Product with Natural Language ===")
state = chat(state, "I have Nike sneakers for sale, 45000 naira, 5 in stock, fashion category")
print(f"Assistant: {state['messages'][-1]['content']}\n")

# Test 2: Query inventory
print("=== Test 2: Query Inventory ===")
state = chat(state, "show me my products")
print(f"Assistant: {state['messages'][-1]['content']}\n")

# Test 3: Search for specific item
print("=== Test 3: Search Inventory ===")
state = chat(state, "do I have any Nike products?")
print(f"Assistant: {state['messages'][-1]['content']}\n")

print("✅ AI Agent test completed!")
