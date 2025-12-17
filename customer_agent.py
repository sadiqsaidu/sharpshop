import json
import re
from typing import TypedDict, Literal, List, Optional
from langgraph.graph import StateGraph, END
from openai import OpenAI
from customer_config import (
    MODEL_NAME, GROQ_BASE_URL, GROQ_API_KEY, 
    MAX_TOKENS, MODEL_TEMPERATURE, ALLOWED_CATEGORIES
)
from customer_tools import (
    get_shop_info, search_shop_products, get_product_details, 
    get_products_by_category, check_product_availability, 
    get_price_range, get_products_in_price_range,
    create_order, create_payment_link, check_order_status, notify_seller
)
from customer_sessions import CustomerAgentState

# Define the state again here or import? I can use the TypedDict from customer_sessions
# But LangGraph needs it to be passed to StateGraph. 
# The one in customer_sessions is good.

def create_client() -> OpenAI:
    return OpenAI(base_url=GROQ_BASE_URL, api_key=GROQ_API_KEY)

# Intent Classification System Prompt
# State Management System Prompt
STATE_SYSTEM_PROMPT = """You are the brain of a shopping assistant. Manage the conversation flow based on the current state.

Current State: {status}
Current Product ID: {product_id}
Current Order ID: {order_id}

3. Transitions:
4. **IMPORTANT**: Only check for search queries if current state is BROWSING.
5. 1. BROWSING:
   - User expresses intent to buy a specific product OR just mentions a product keyword (e.g., "wired", "mouse")? -> Output tool="search_shop_products", args={{"query": "keyword"}}.
   - **CRITICAL**: If the user sends a short message like "wired", "mouse", "solar", ASSUME IT IS A SEARCH QUERY.
   - **EXCEPTION**: If the user says "hi", "hello", "hey", "good morning", etc. -> Output tool=null (Chit-chat). DO NOT SEARCH "hi".
   - User asks generic questions? -> Output tool="search_shop_products" (if product related) or null (if pure chitchat).
2. PRODUCT_SELECTED:
   - User confirms they want to buy? -> Output next_state="awaiting_payment".
   - User wants to keep looking? -> Output next_state="browsing".
3. AWAITING_PAYMENT:
   - User asks for link again? -> Output tool="create_payment_link".
   - User says "paid"? -> Output tool="check_order_status".
   - If payment confirmed (status=paid)? -> Output next_state="collecting_delivery_details".
4. COLLECTING_DELIVERY_DETAILS:
   - User says "cancel" or "stop"? -> Output next_state="browsing".
   - User provides Name, Phone, AND Address (long enough string)? -> Output updates={{"delivery_details": ...}}, next_state="paid".
   - User provides short/incomplete text (e.g. "df", "hi")? -> Output next_state=null (STAY IN STATE).
   - **CRITICAL**: Do NOT search. Just reject invalid input. Valid info must be substantial.
5. PAID:
   - Conversation ends or loops back to browsing.

Output JSON ONLY:
{{
  "tool": "tool_name" or null,
  "args": {{ "arg": "value" }},
  "next_state": "new_state_name" or null,
  "state_updates": {{ "key": "value" }}
}}
"""

# Response Generation System Prompt
# Response Generation System Prompt
RESPONSE_SYSTEM_PROMPT = """You are a helpful sales assistant for "{shop_name}".
Your goal is to be friendly and persuade customers to buy.

CURRENT STATUS: {status}
PAYMENT LINK: {payment_link}

GUIDELINES:
- **Tone**: Friendly, human, and professional.
- **Conciseness**: VITAL. Do NOT list categories or generic "Welcome" text if you found a specific product.
- **Directness**: If the user asked for X and you found X, talk ONLY about X.

INSTRUCTIONS BY STATUS:
- **browsing**: 
  - IF TOOL RETURNED 'message' (Pre-formatted): **YOU MUST USE THIS MESSAGE EXACTLY**. Do not rewrite it.
  - IF SEARCH RESULTS FOUND: "I found [Product Name] (Stock: [Qty]). Price: [Price]. \n\n[Display Image if available]\n\n[IF LINK EXISTS: Here is your link to buy: [Pay Now]({{payment_link}})]\n[IF NO LINK: Would you like to buy this?]"
  - IF NO SEARCH PERFORMED (User said 'hi', 'hello', etc.): "Welcome to [Shop Name]! I'm here to help you find the perfect product. What are you looking for today?"
  - IF NO RESULTS FOUND (After search): Apologize and suggest categories.
- **product_selected**: "Great! To buy, click here: [Pay Now]({{payment_link}})."
- **awaiting_payment**:
  - IF PAYMENT LINK EXISTS: "Here is your link: [Pay Now]({{payment_link}})."
  - IF NOT: "Generating link..."
- **collecting_delivery_details**: 
  - IF PREVIOUS TOOL OUTPUT WAS 'check_order_status': "Payment received! Please give me your **Name**, **Phone**, and **Address**."
  - IF USER SENT GIBBERISH/INVALID INFO: "That doesn't look like your details. Maybe it was a mistake? Please provide your **Name**, **Phone**, and **Address**."
- **paid**: "Order confirmed! We will deliver to **{delivery_address}**."
"""

def process_message(state: CustomerAgentState) -> CustomerAgentState:
    """Parse intent and update state."""
    client = create_client()
    
    current_status = state.get("status", "browsing")
    
    # Format categories for prompt inputs if needed, 
    # but mainly we need to pass current state vars
    
    # IMPORTANT: The decision model needs some history; sending only the last user
    # message makes it default to tool=null too often.
    history = state.get("messages", [])[-8:]
    messages = [
        {"role": "system", "content": STATE_SYSTEM_PROMPT.format(
            status=current_status,
            product_id=state.get("product_id"),
            order_id=state.get("order_id")
        )}
    ]
    messages.extend(history)
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.1,
            response_format={"type": "json_object"}
        )
    except Exception as e:
        print(f"API Error in process_message: {e}")
        # Return state as is, maybe loop logic will retry or fail gracefully
        return state
    
    try:
        decision = json.loads(response.choices[0].message.content)
        state["context"]["decision"] = decision

        # Lightweight debug logging (helps trace tool selection issues)
        try:
            print(
                "[customer_agent] decision",
                {
                    "session_id": state.get("session_id"),
                    "status": state.get("status"),
                    "tool": decision.get("tool"),
                    "args": decision.get("args"),
                    "next_state": decision.get("next_state"),
                },
            )
        except Exception:
            pass
        
        # Apply state updates immediately
        if decision.get("next_state"):
            state["status"] = decision["next_state"]
        
        if decision.get("state_updates"):
            for k, v in decision["state_updates"].items():
                if k == "delivery_details" and state.get("delivery_details"):
                    # Merge details if partial
                    state["delivery_details"].update(v)
                else:
                    state[k] = v
            
            # If status transitioned to PAID just now (via decision), trigger notification
            if decision.get("next_state") == "paid":
                 if state.get("order_id"):
                      notify_seller(state["order_id"])
                    
    except Exception as e:
        print(f"Decision Parse Error: {e}")
        state["context"]["decision"] = {"tool": None}
        
    return state

def execute_tools(state: CustomerAgentState) -> CustomerAgentState:
    """Execute the selected tool."""
    decision = state["context"].get("decision", {})
    tool_name = decision.get("tool")
    args = decision.get("args", {})
    trader_id = state["trader_id"]
    
    result = None
    
    try:
        if tool_name == "search_shop_products":
            # STATE RESET: New search means new interaction context.
            # We must clear old order IDs and links to avoid confusion.
            state["order_id"] = None
            state["payment_link"] = None
            state["status"] = "browsing" # Default back to browsing until we find something
            
            result = search_shop_products(trader_id, args.get("query", ""))
            
            # SMART SEARCH LOGIC (Aggressive):
            # If results found (<= 3), generate links for ALL of them immediately.
            # This avoids "asking questions" and gives the user immediate buy options.
            if result.get("results"):
                 # Limit to top 3 to avoid spamming/latency
                 top_results = result["results"][:3]
                 enhanced_message = "Here is what I found:\n"
                 
                 for p in top_results:
                      try:
                          # Check availability first
                          stock_res = check_product_availability(p["id"], trader_id)
                          if stock_res.get("available"):
                               # Create Order
                               order_res = create_order(trader_id, p["id"], "delivery", {})
                               if "id" in order_res:
                                    link = create_payment_link(order_res["id"])
                                    # Append to product info for display
                                    p["payment_link"] = link
                                    p["order_id"] = order_res["id"]
                                    enhanced_message += f"\n- **{p['name']}**\n  Price: {p['price']} | Stock: {p['stock_quantity']}\n  [Buy Now]({link})\n"
                          else:
                               enhanced_message += f"\n- **{p['name']}** (Out of Stock)\n"
                      except Exception as inner_e:
                          print(f"[customer_agent] ERROR processing product {p.get('id')}: {inner_e}")
                          enhanced_message += f"\n- **{p['name']}**\n  Price: {p['price']}\n"
                 
                 # If only one result, we also update state vars for context
                 if len(top_results) == 1:
                      # We need to find the order_id we just created.
                      # Ideally we should have stored it in p, or we can assume it's the one we just made.
                      # Let's update `p` in the loop above to include `order_id`.
                      state["product_id"] = top_results[0]["id"]
                      state["payment_link"] = top_results[0].get("payment_link")
                      state["order_id"] = top_results[0].get("order_id")
                      
                      if state["payment_link"]:
                          state["status"] = "awaiting_payment"
                 
                 result["message"] = enhanced_message
            else:
                 result = {"error": "No products found", "message": "I couldn't find exactly that. try checking our categories?"}
            
        elif tool_name == "check_product_availability":
            # If we are checking availability to Select a product
            p_id = args.get("product_id") or state.get("product_id")
            if not p_id and args.get("product_name"):
                 # search first
                 search_res = search_shop_products(trader_id, args.get("product_name"))
                 if search_res["results"]:
                     p_id = search_res["results"][0]["id"]
                     # Auto-select if confident? For now just check
            
            if p_id:
                result = check_product_availability(p_id, trader_id)
                # CHAINING LOGIC: If available, immediately create order + payment link
                if result.get("available"):
                     state["product_id"] = p_id
                     # Check if we already have an active order for this product to avoid dups?
                     # For simplicity, create new if none exists
                     order_res = create_order(
                        trader_id, 
                        p_id, 
                        "delivery", # Default to delivery
                        {}
                     )
                     if "id" in order_res:
                        state["order_id"] = order_res["id"]
                        link = create_payment_link(state["order_id"])
                        state["payment_link"] = link
                        state["status"] = "awaiting_payment"
                        
                        # Add to result so LLM sees it
                        result["order_created"] = True
                        result["payment_link"] = link
                        result["message"] = "Order initialized. Link generated."
            else:
                result = {"error": "Product not identified"}
                
        elif tool_name == "create_order":
             # Usually called automatically when entering AWAITING_PAYMENT?
             pass 
             
        elif tool_name == "create_payment_link":
             order_id = state.get("order_id")
             if order_id:
                 result = create_payment_link(order_id)
                 state["payment_link"] = result
             else:
                 result = "Error: No order ID"
                 
        elif tool_name == "check_order_status":
             order_id = state.get("order_id")
             if order_id:
                 status = check_order_status(order_id)
                 result = {"status": status}
                 if status == "paid":
                     state["status"] = "paid"
                     notify_seller(order_id)
             else:
                 result = "Error: No order ID"
                 
        # ... other existing tools ...
        elif tool_name == "get_shop_info":
            result = get_shop_info(trader_id)
            
        else:
            # Handle special logic for automatic actions based on state
            pass

    except Exception as e:
        result = {"error": str(e)}
        
    # Automatic Actions Logic outside explicit tool calls
    # REMOVED: Previous logic that created order on entering awaiting_payment
    # Reason: We now do it eagerly in check_product_availability
    pass
    
    # If checking status returns PAID, decide next step
    if state["context"].get("decision", {}).get("tool") == "check_order_status":
        if isinstance(result, dict) and result.get("status") == "paid":
             # CHECK IF DETAILS ALREADY EXIST
             if state.get("delivery_details") and len(str(state["delivery_details"])) > 10:
                  state["status"] = "paid"
                  # Notify seller immediately since we are skipping the collection step
                  if state.get("order_id"):
                      notify_seller(state["order_id"])
             else:
                  state["status"] = "collecting_delivery_details"
    
    state["context"]["tool_result"] = result

    try:
        print(
            "[customer_agent] tool_result",
            {
                "session_id": state.get("session_id"),
                "status": state.get("status"),
                "tool": state.get("context", {}).get("decision", {}).get("tool"),
                "result_keys": list(result.keys()) if isinstance(result, dict) else type(result).__name__,
                "total": result.get("total") if isinstance(result, dict) else None,
                "has_message": bool(result.get("message")) if isinstance(result, dict) else False,
            },
        )
    except Exception:
        pass
    return state

def synthesize_response(state: CustomerAgentState) -> CustomerAgentState:
    """Generate final response using tool results."""
    client = create_client()
    
    tool_results = state["context"].get("tool_result")
    user_message = state["messages"][-1]["content"]
    
    system_msg = RESPONSE_SYSTEM_PROMPT.format(
        shop_name=state["trader_name"],
        whatsapp=state["whatsapp_number"],
        status=state.get("status", "browsing"),
        payment_link=state.get("payment_link", "Generating..."),
        product_id=state.get("product_id", "current product"),
        delivery_address=(state.get("delivery_details") or {}).get("address") or (state.get("delivery_details") or {}).get("Address", "your address"),
        tool_results=json.dumps(tool_results, indent=2) if tool_results else "No data found.",
        user_message=user_message
    )
    
    # We pass the conversation history too for context?
    # The spec says "Conversation history" in state, so yes.
    # But we want the system prompt to guide the latest answer.
    
    messages = [{"role": "system", "content": system_msg}]
    # Append recent history (last 5 messages) to keep context?
    # state["messages"] includes the last user message.
    # We need to be careful not to duplicate the last message if we used it in prompt explicitly.
    # Actually, simpler: System Prompt + History. 
    # But we injected tool results in System Prompt.
    
    # Correct approach:
    # 1. System Prompt (with tool results)
    # 2. History (excluding last message if we want to treat it specially, but usually just include it)
    
    # Let's rebuild messages
    msgs = [{"role": "system", "content": system_msg}]
    # Add previous messages? 
    # Providing full history might confuse the tool context if not careful, 
    # but strictly speaking `synthesize_response` is generating the answer to the *last* message.
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=msgs,
            temperature=0.7,
            max_tokens=MAX_TOKENS
        )
        reply = response.choices[0].message.content
    except Exception as e:
        print(f"API Error in synthesize_response: {e}")
        reply = "I'm experiencing high traffic right now. Please try again in 10-20 seconds."

    state["messages"].append({"role": "assistant", "content": reply})
    return state

def generate_response(state: CustomerAgentState) -> CustomerAgentState:
    """Generate response without tools (chit-chat or state-based fallback)."""
    client = create_client()
    
    # Use the same state-aware system prompt, but with no tool results
    user_message = state["messages"][-1]["content"]
    
    # Check if we should use the specialized prompt or a generic one?
    # Actually, RESPONSE_SYSTEM_PROMPT is designed to handle all states.
    # We just pass "No data found" for tool results.
    
    system_msg = RESPONSE_SYSTEM_PROMPT.format(
        shop_name=state["trader_name"],
        whatsapp=state["whatsapp_number"],
        status=state.get("status", "browsing"),
        payment_link=state.get("payment_link", "Generating..."),
        product_id=state.get("product_id", "current product"),
        delivery_address=(state.get("delivery_details") or {}).get("address") or (state.get("delivery_details") or {}).get("Address", "your address"),
        tool_results="No specific tool output. Proceed based on status.",
        user_message=user_message
    )
    
    # Combine with history? 
    # synthesize_response logic was: [System] + (maybe history?)
    # Let's trust the System Prompt to guide the immediate response especially for invalid input rejection.
    
    messages = [{"role": "system", "content": system_msg}]
    # We can perform a lightweight append of recent context if needed, 
    # but for "rejecting invalid input", the system prompt instruction is forceful enough.
    # To be safe for chitchat, we include history.
    messages.extend(state["messages"][-3:]) 
    
    # Combined Logic
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.7,
            max_tokens=MAX_TOKENS
        )
        reply = response.choices[0].message.content
    except Exception as e:
        print(f"API Error in synthesize_response: {e}")
        reply = "I'm experiencing high traffic right now. Please try again in a moment."
    
    state["messages"].append({"role": "assistant", "content": reply})
    return state

def decide_next_step(state: CustomerAgentState) -> Literal["execute_tools", "generate_response"]:
    decision = state["context"].get("decision", {})
    # Always go to tools to handle automatic state actions if in specific states?
    # Or if tool is set.
    if decision.get("tool") or state["status"] in ["awaiting_payment", "paid"]:
        # We might need to execute automated logic even if no explicit tool called by LLM
        return "execute_tools"
    return "generate_response"

def build_customer_graph() -> StateGraph:
    graph = StateGraph(CustomerAgentState)
    
    graph.add_node("process_message", process_message)
    graph.add_node("execute_tools", execute_tools)
    graph.add_node("synthesize_response", synthesize_response)
    graph.add_node("generate_response", generate_response)
    
    graph.set_entry_point("process_message")
    
    graph.add_conditional_edges(
        "process_message",
        decide_next_step
    )
    
    graph.add_edge("execute_tools", "synthesize_response")
    graph.add_edge("synthesize_response", END)
    graph.add_edge("generate_response", END)
    
    return graph.compile()

# Public function to handle chat
def handle_customer_chat(session_state: CustomerAgentState, user_message: str) -> CustomerAgentState:
    # Append user message to state
    session_state["messages"].append({"role": "user", "content": user_message})
    
    app = build_customer_graph()
    final_state = app.invoke(session_state)
    
    return final_state
