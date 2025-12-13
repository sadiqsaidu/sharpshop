"""LangGraph-based AI agent for inventory management."""
import json
import re
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from openai import OpenAI
from database import get_or_create_trader

from config import GROQ_API_KEY, GROQ_BASE_URL, MODEL_NAME, ALLOWED_CATEGORIES
from tools import create_product, query_inventory, update_product, list_products

REQUIRED_FIELDS = ["name", "price", "category", "stock"]
OPTIONAL_FIELDS = ["description", "image"]

SYSTEM_PROMPT = f"""You are a helpful WhatsApp assistant for sellers managing their inventory. You help them add products, query stock, and update listings.

When a seller wants to add a product, extract these details from their messages:
- name (required): product name
- price (required): in Naira, must be > 0
- category (required): one of {', '.join(ALLOWED_CATEGORIES)}
- stock (required): stock count, must be >= 0
- description (optional but recommended): product description

**IMPORTANT**: 
- If the seller sends an image with product details, you SHOULD ask for a description to make the listing more attractive
- Example: "Great! I can see you have [product name] for ₦[price]. Can you tell me a bit more about it? What's special about this item?"
- If they already provided a description or context in their message, you can proceed without asking
- Once you have name, price, category, stock (and ideally description), output the JSON action

Output format (respond with ONLY the JSON, nothing else):
```json
{{"action": "create_product", "data": {{"name": "Nike sneakers", "price": 45000, "category": "Fashion", "stock": 5, "description": "Brand new Nike sneakers in excellent condition"}}}}
```

For queries/searches:
```json
{{"action": "query_inventory", "data": {{"search_term": "Nike"}}}}
```

For listing all products:
```json
{{"action": "list_products", "data": {{}}}}
```

For updating a product (price, stock, etc.):
- First, you need to find the product by searching for it
- Then use the product name to update it
```json
{{"action": "update_product", "data": {{"product_name": "esp32 microcontroller", "updates": {{"price": 11000}}}}}}
```
Note: You can update: price, stock_quantity, description, name, category, is_active"""


class AgentState(TypedDict):
    messages: list[dict]
    trader_id: str
    trader_name: str
    whatsapp_number: str
    pending_action: str | None
    collected_data: dict
    image_url: str | None


def create_client() -> OpenAI:
    return OpenAI(base_url=GROQ_BASE_URL, api_key=GROQ_API_KEY)


def process_message(state: AgentState) -> AgentState:
    """Process incoming message and generate response."""
    client = create_client()
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Add context about collected data if any
    if state["collected_data"]:
        context = f"\n\nCurrent collected data: {json.dumps(state['collected_data'])}"
        missing = [f for f in REQUIRED_FIELDS if f not in state["collected_data"]]
        if missing:
            context += f"\nMissing required fields: {', '.join(missing)}"
        messages[0]["content"] += context
    
    if state["image_url"]:
        messages[0]["content"] += f"\n\nImage provided: {state['image_url']}"
    
    messages.extend(state["messages"])
    
    response = client.chat.completions.create(model=MODEL_NAME, messages=messages, temperature=0.7)
    assistant_msg = response.choices[0].message.content
    
    new_state = state.copy()
    new_state["messages"] = state["messages"] + [{"role": "assistant", "content": assistant_msg}]
    
    # Check for action JSON in response (with or without markdown code blocks)
    json_match = re.search(r'```json\s*(\{.*?\})\s*```', assistant_msg, re.DOTALL)
    if not json_match:
        # Try finding complete JSON object (matching braces)
        start_idx = assistant_msg.find('{"action"')
        if start_idx >= 0:
            # Find matching closing brace
            brace_count = 0
            in_string = False
            escape = False
            for i, char in enumerate(assistant_msg[start_idx:], start=start_idx):
                if escape:
                    escape = False
                    continue
                if char == '\\':
                    escape = True
                    continue
                if char == '"' and not escape:
                    in_string = not in_string
                if not in_string:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            json_str = assistant_msg[start_idx:i+1]
                            break
            else:
                json_str = None
        else:
            json_str = None
    else:
        json_str = json_match.group(1)
    
    if json_str:
        try:
            action_data = json.loads(json_str)
            new_state["pending_action"] = action_data.get("action")
            new_state["collected_data"] = action_data.get("data", {})
        except json.JSONDecodeError:
            pass
    
    return new_state


def execute_action(state: AgentState) -> AgentState:
    """Execute the pending action if data is complete."""
    action = state["pending_action"]
    data = state["collected_data"]
    result_msg = ""
    
    if action == "create_product":
        # Add trader info and image
        data["trader_id"] = state["trader_id"]
        data["trader_name"] = state["trader_name"]
        data["whatsapp_number"] = state["whatsapp_number"]
        if state["image_url"]:
            data["image"] = state["image_url"]
        result = create_product(**data)
        if result["success"]:
            result_msg = f"✅ Product added! Your {data.get('name', 'item')} is now listed. (ID: {result['product_id']})"
        else:
            result_msg = f"❌ Couldn't add product: {result['error']}"
    
    elif action == "query_inventory":
        result = query_inventory(data.get("search_term", ""), state["trader_id"])
        if result["results"]:
            items = "\n".join([f"• {p['name']} - ₦{p['price']:,} ({p['stock_quantity']} in stock)" for p in result["results"]])
            result_msg = f"📦 Found {result['total']} items:\n{items}"
        else:
            result_msg = "No products found matching your search."
    
    elif action == "update_product":
        # First search for the product by name
        product_name = data.get("product_name", "")
        if not product_name:
            result_msg = "❌ I need the product name to update it. Which product do you want to update?"
        else:
            search_result = query_inventory(product_name, state["trader_id"])
            if not search_result["results"]:
                result_msg = f"❌ I couldn't find any product matching '{product_name}'. Please check the name and try again."
            elif len(search_result["results"]) > 1:
                items = "\n".join([f"• {p['name']} (ID: {p['id'][:8]}...)" for p in search_result["results"]])
                result_msg = f"I found multiple products:\n{items}\n\nPlease be more specific about which one to update."
            else:
                # Found exactly one product
                product = search_result["results"][0]
                product_id = product["id"]
                updates = data.get("updates", {})
                
                # Normalize field names: "stock" -> "stock_quantity"
                if "stock" in updates:
                    updates["stock_quantity"] = updates.pop("stock")
                
                result = update_product(product_id, updates, state["trader_id"])
                
                if result["success"]:
                    # Show what was updated
                    updated_fields = ", ".join([f"{k}: {v}" for k, v in updates.items()])
                    result_msg = f"✅ Updated {product['name']}! Changed: {updated_fields}"
                else:
                    result_msg = f"❌ Update failed: {result['error']}"
    
    elif action == "list_products":
        result = list_products(state["trader_id"], data.get("limit", 10))
        if result["products"]:
            items = "\n".join([f"• {p['name']} - ₦{p['price']:,} ({p['stock_quantity']} in stock)" for p in result["products"]])
            result_msg = f"📦 Your {result['total']} products:\n{items}"
        else:
            result_msg = "You haven't added any products yet."
    
    new_state = state.copy()
    new_state["messages"] = state["messages"] + [{"role": "assistant", "content": result_msg}]
    new_state["pending_action"] = None
    new_state["collected_data"] = {}
    new_state["image_url"] = None
    return new_state


def should_execute(state: AgentState) -> Literal["execute", "end"]:
    """Determine if we should execute an action or end."""
    if state["pending_action"] and state["collected_data"]:
        return "execute"
    return "end"


def build_graph() -> StateGraph:
    """Build the LangGraph state machine."""
    graph = StateGraph(AgentState)
    graph.add_node("process", process_message)
    graph.add_node("execute", execute_action)
    graph.set_entry_point("process")
    graph.add_conditional_edges("process", should_execute, {"execute": "execute", "end": END})
    graph.add_edge("execute", END)
    return graph.compile()


def create_initial_state(whatsapp_number: str, business_name: str = "My Shop") -> AgentState:
    """Create initial state for a new conversation - auto-creates trader."""
    trader = get_or_create_trader(whatsapp_number, business_name)
    return {
        "messages": [],
        "trader_id": trader["id"],
        "trader_name": trader["business_name"],
        "whatsapp_number": whatsapp_number,
        "pending_action": None,
        "collected_data": {},
        "image_url": None
    }


def chat(state: AgentState, user_message: str, image_url: str = None) -> AgentState:
    """Process a user message and return updated state."""
    new_state = state.copy()
    new_state["messages"] = state["messages"] + [{"role": "user", "content": user_message}]
    if image_url:
        new_state["image_url"] = image_url
    
    graph = build_graph()
    return graph.invoke(new_state)
