"""Test AI agent with debug output."""
from agent import create_initial_state, chat

# Create state
state = create_initial_state("+2347051268773", "Debug Shop")
print(f"Initial state: trader_id={state['trader_id']}, trader_name={state['trader_name']}\n")

# Send message
print("Sending message...")
state = chat(state, "Nike sneakers 45000 naira 5 in stock fashion category")

print(f"\nFinal state:")
print(f"  pending_action: {state.get('pending_action')}")
print(f"  collected_data: {state.get('collected_data')}")
print(f"  last message: {state['messages'][-1]['content'][:200]}")
