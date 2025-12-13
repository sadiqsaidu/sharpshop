# WhatsApp to Supabase Integration Guide

This guide explains how to connect your Python WhatsApp bot to the SharpShop Supabase database.

## Architecture Overview

```
WhatsApp Message → Meta Cloud API → Python FastAPI Backend → Supabase → React Frontend (Real-time)
```

## 1. Python Dependencies

Install the Supabase Python client in your FastAPI backend:

```bash
pip install supabase
```

## 2. Connect to Supabase from Python

```python
from supabase import create_client, Client
import os

# Your Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Use service role for backend

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
```

## 3. Product Management Functions

### Add Product (from WhatsApp message)

```python
def create_product(trader_id: str, product_data: dict):
    """
    Create a new product from WhatsApp message
    
    Args:
        trader_id: The trader's UUID from traders table
        product_data: Extracted product information
            {
                "name": "Nike Air Max",
                "price": 20000,
                "description": "Brand new sneakers",
                "image_url": "https://...",
                "category": "Footwear",
                "stock_quantity": 5,
                "whatsapp_number": "2348012345678"
            }
    """
    response = supabase.table("products").insert({
        "trader_id": trader_id,
        "trader_name": get_trader_name(trader_id),  # Fetch from traders table
        "name": product_data["name"],
        "price": product_data["price"],
        "description": product_data.get("description", ""),
        "image_url": product_data["image_url"],
        "category": product_data["category"],
        "stock_quantity": product_data["stock_quantity"],
        "whatsapp_number": product_data["whatsapp_number"],
        "is_active": True
    }).execute()
    
    return response.data

def get_trader_name(trader_id: str):
    """Get trader business name from traders table"""
    response = supabase.table("traders").select("business_name").eq("id", trader_id).single().execute()
    return response.data["business_name"]
```

### Update Product Stock

```python
def update_product_stock(product_name: str, trader_id: str, new_quantity: int):
    """
    Update product stock from WhatsApp message like "Update Nike stock to 10"
    """
    response = supabase.table("products")\
        .update({"stock_quantity": new_quantity})\
        .eq("trader_id", trader_id)\
        .ilike("name", f"%{product_name}%")\
        .execute()
    
    return response.data

def update_product_price(product_name: str, trader_id: str, new_price: int):
    """
    Update product price from WhatsApp message like "Change Nike price to 25k"
    """
    response = supabase.table("products")\
        .update({"price": new_price})\
        .eq("trader_id", trader_id)\
        .ilike("name", f"%{product_name}%")\
        .execute()
    
    return response.data
```

### Query Products

```python
def get_trader_products(trader_id: str):
    """
    Get all products for a trader
    Responds to: "Show me all my products"
    """
    response = supabase.table("products")\
        .select("*")\
        .eq("trader_id", trader_id)\
        .execute()
    
    return response.data

def search_products(trader_id: str, keyword: str):
    """
    Search trader's products
    Responds to: "How many Nikes do I have?"
    """
    response = supabase.table("products")\
        .select("*")\
        .eq("trader_id", trader_id)\
        .ilike("name", f"%{keyword}%")\
        .execute()
    
    return response.data
```

### Delete Product

```python
def delete_product(product_name: str, trader_id: str):
    """
    Delete/deactivate a product
    Responds to: "Delete Nike shoes"
    """
    response = supabase.table("products")\
        .update({"is_active": False})\
        .eq("trader_id", trader_id)\
        .ilike("name", f"%{product_name}%")\
        .execute()
    
    return response.data
```

## 4. Trader Authentication

### Get Trader by WhatsApp Number

```python
def get_trader_by_whatsapp(whatsapp_number: str):
    """
    Identify which trader is sending the WhatsApp message
    """
    response = supabase.table("traders")\
        .select("id, business_name, user_id")\
        .eq("whatsapp_number", whatsapp_number)\
        .single()\
        .execute()
    
    return response.data if response.data else None

def register_trader_whatsapp(user_id: str, whatsapp_number: str):
    """
    Link a trader's WhatsApp number during onboarding
    """
    response = supabase.table("traders")\
        .update({"whatsapp_number": whatsapp_number})\
        .eq("user_id", user_id)\
        .execute()
    
    return response.data
```

## 5. Image Upload Workflow

```python
import requests
from supabase.storage import StorageException

def upload_product_image(image_url: str, trader_id: str, product_name: str):
    """
    Download image from WhatsApp Media URL and upload to Supabase Storage
    
    Args:
        image_url: WhatsApp media URL (requires Meta API access token)
        trader_id: Trader UUID for folder organization
        product_name: Used for filename
    """
    # Download image from WhatsApp
    headers = {"Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}"}
    image_response = requests.get(image_url, headers=headers)
    
    if image_response.status_code != 200:
        raise Exception("Failed to download WhatsApp image")
    
    # Generate unique filename
    import uuid
    file_extension = image_url.split(".")[-1] or "jpg"
    filename = f"{trader_id}/{uuid.uuid4()}.{file_extension}"
    
    # Upload to Supabase Storage
    response = supabase.storage.from_("product-images").upload(
        filename,
        image_response.content,
        {"content-type": f"image/{file_extension}"}
    )
    
    # Get public URL
    public_url = supabase.storage.from_("product-images").get_public_url(filename)
    
    return public_url
```

## 6. Real-time Updates (Automatic)

When you use `supabase.table("products").insert()` or `.update()` from Python:
- The change is immediately written to Supabase
- Supabase broadcasts the change via Realtime
- The React frontend receives the update within milliseconds
- The product feed auto-refreshes **without page reload**

✅ No additional configuration needed! The frontend already subscribes to changes.

## 7. Example LangGraph Agent Flow

```python
from langgraph.graph import StateGraph, END

class ProductState:
    trader_id: str
    whatsapp_number: str
    message: str
    extracted_data: dict
    
def identify_trader(state: ProductState):
    """Step 1: Identify trader from WhatsApp number"""
    trader = get_trader_by_whatsapp(state.whatsapp_number)
    if not trader:
        return {"error": "Trader not found. Please register first."}
    state.trader_id = trader["id"]
    return state

def extract_product_info(state: ProductState):
    """Step 2: Use AI to extract product details from message"""
    # Use GPT-4 or Claude to parse natural language
    # Example: "Add Nike Air Max, 20k, size 42"
    # Extracted: {name: "Nike Air Max", price: 20000, ...}
    pass

def create_product_node(state: ProductState):
    """Step 3: Create product in Supabase"""
    result = create_product(state.trader_id, state.extracted_data)
    return {"success": True, "product": result}

# Build graph
workflow = StateGraph(ProductState)
workflow.add_node("identify", identify_trader)
workflow.add_node("extract", extract_product_info)
workflow.add_node("create", create_product_node)
# ... add edges
```

## 8. Environment Variables

Add to your Python `.env`:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
WHATSAPP_ACCESS_TOKEN=your-meta-api-token
WHATSAPP_PHONE_NUMBER_ID=your-whatsapp-business-phone-id
```

## 9. Testing the Integration

### Test Product Creation

```python
# Simulate WhatsApp message: "Add Nike Shoes, 20000"
trader_id = "your-trader-uuid"
product_data = {
    "name": "Nike Shoes",
    "price": 20000,
    "description": "Brand new sneakers",
    "image_url": "https://example.com/image.jpg",
    "category": "Footwear",
    "stock_quantity": 5,
    "whatsapp_number": "2348012345678"
}

result = create_product(trader_id, product_data)
print("Product created:", result)
```

### Verify in Frontend

1. Open the SharpShop web app
2. The new product should appear **instantly** in the feed
3. No refresh needed - powered by Supabase Realtime!

## 10. Error Handling

```python
from supabase.lib.client_options import ClientOptions

try:
    response = supabase.table("products").insert(data).execute()
except Exception as e:
    # Log error and send WhatsApp reply
    error_message = f"Sorry, I couldn't add the product. Error: {str(e)}"
    send_whatsapp_message(whatsapp_number, error_message)
```

## Next Steps

1. ✅ Set up Supabase Storage for product images
2. ✅ Configure Row Level Security (RLS) policies
3. ✅ Implement trader authentication via WhatsApp
4. ✅ Build LangGraph agent for NLP extraction
5. ✅ Test end-to-end flow: WhatsApp → Database → Web

---

**Questions?** The frontend is now ready to receive real-time updates from your Python backend!
