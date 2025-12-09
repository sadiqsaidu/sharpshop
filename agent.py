"""LangGraph-based AI agent for inventory management."""
import json
import re
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
from openai import OpenAI

from config import GROQ_API_KEY, GROQ_BASE_URL, MODEL_NAME, ALLOWED_CATEGORIES
from tools import create_product, query_inventory, update_product, list_products

REQUIRED_FIELDS = ["title", "price", "category", "quantity", "condition"]
OPTIONAL_FIELDS = ["description", "size", "brand"]

SYSTEM_PROMPT = f"""You are a helpful WhatsApp assistant for sellers managing their inventory. You help them add products, query stock, and update listings.

When a seller wants to add a product, extract these details from their messages:
- title (required): product name
- price (required): in Naira, must be > 0
- category (required): one of {', '.join(ALLOWED_CATEGORIES)}
- quantity (required): stock count, must be >= 0
- condition (required): new, used, or refurbished
- description, size, brand (optional)

For queries, help search their inventory. For updates, identify the product and changes.

Always be conversational, friendly, and ask ONE clarifying question at a time for missing required fields.
When you have all required info, respond with a JSON block to execute the action:
```json
{{"action": "create_product", "data": {{...}}}}
```

Available actions: create_product, query_inventory, update_product, list_products"""


class AgentState(TypedDict):
    messages: list[dict]
    seller_id: str
    pending_action: str | None
    collected_data: dict
    image_urls: list[str]


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
    
    if state["image_urls"]:
        messages[0]["content"] += f"\n\nImages provided: {len(state['image_urls'])} image(s)"
    
    messages.extend(state["messages"])
    
    response = client.chat.completions.create(model=MODEL_NAME, messages=messages, temperature=0.7)
    assistant_msg = response.choices[0].message.content
    
    new_state = state.copy()
    new_state["messages"] = state["messages"] + [{"role": "assistant", "content": assistant_msg}]
    
    # Check for action JSON in response
    json_match = re.search(r'```json\s*(\{.*?\})\s*```', assistant_msg, re.DOTALL)
    if json_match:
        try:
            action_data = json.loads(json_match.group(1))
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
        if state["image_urls"]:
            data["image_urls"] = state["image_urls"]
        result = create_product(**data)
        if result["success"]:
            result_msg = f"✅ Product added! Your {data.get('title', 'item')} is now listed. (ID: {result['product_id']})"
        else:
            result_msg = f"❌ Couldn't add product: {result['error']}"
    
    elif action == "query_inventory":
        result = query_inventory(data.get("search_term", ""))
        if result["results"]:
            items = "\n".join([f"• {p['title']} - ₦{p['price']:,} ({p['quantity']} in stock)" for p in result["results"]])
            result_msg = f"📦 Found {result['total']} items:\n{items}"
        else:
            result_msg = "No products found matching your search."
    
    elif action == "update_product":
        result = update_product(data.get("product_id", ""), data.get("updates", {}))
        result_msg = f"✅ Product updated!" if result["success"] else f"❌ Update failed: {result['error']}"
    
    elif action == "list_products":
        result = list_products(data.get("limit", 10))
        if result["products"]:
            items = "\n".join([f"• {p['title']} - ₦{p['price']:,} ({p['quantity']} in stock)" for p in result["products"]])
            result_msg = f"📦 Your products:\n{items}"
        else:
            result_msg = "You don't have any products listed yet."
    
    new_state = state.copy()
    new_state["messages"] = state["messages"] + [{"role": "assistant", "content": result_msg}]
    new_state["pending_action"] = None
    new_state["collected_data"] = {}
    new_state["image_urls"] = []
    return new_state


def should_execute(state: AgentState) -> Literal["execute", "end"]:
    """Determine if we should execute an action or end."""
    if state["pending_action"] and state["collected_data"]:
        action = state["pending_action"]
        data = state["collected_data"]
        
        if action == "create_product":
            if all(f in data for f in REQUIRED_FIELDS):
                return "execute"
        elif action in ["query_inventory", "update_product", "list_products"]:
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


def create_initial_state(seller_id: str) -> AgentState:
    """Create initial state for a new conversation."""
    return {
        "messages": [],
        "seller_id": seller_id,
        "pending_action": None,
        "collected_data": {},
        "image_urls": []
    }


def chat(state: AgentState, user_message: str, image_urls: list[str] = None) -> AgentState:
    """Process a user message and return updated state."""
    new_state = state.copy()
    new_state["messages"] = state["messages"] + [{"role": "user", "content": user_message}]
    if image_urls:
        new_state["image_urls"] = state["image_urls"] + image_urls
    
    graph = build_graph()
    return graph.invoke(new_state)
