"""FastAPI server for WhatsApp chatbot."""
from fastapi import FastAPI, Form, Request, Response
from twilio.twiml.messaging_response import MessagingResponse
from agent import create_initial_state, chat
import uvicorn

import logging

# Configure logging
logging.basicConfig(
    filename='server.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    force=True
)

app = FastAPI()

# In-memory session store (for demo purposes)
# In production, use Redis or a database
user_sessions = {}

@app.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    """Handle incoming WhatsApp messages."""
    form_data = await request.form()
    incoming_msg = form_data.get('Body', '').strip()
    sender_id = form_data.get('From', '')
    
    # Check for media (images)
    num_media = int(form_data.get('NumMedia', 0))
    image_urls = []
    if num_media > 0:
        for i in range(num_media):
            media_url = form_data.get(f'MediaUrl{i}')
            if media_url:
                image_urls.append(media_url)
    
    logging.info(f"Received message from {sender_id}: {incoming_msg}")
    if image_urls:
        logging.info(f"Received {len(image_urls)} images")

    # Get or create user state
    if sender_id not in user_sessions:
        user_sessions[sender_id] = create_initial_state(seller_id=sender_id)
    
    state = user_sessions[sender_id]
    
    # Process message through agent
    try:
        new_state = chat(state, incoming_msg, image_urls)
        user_sessions[sender_id] = new_state
        
        # Get the last assistant message
        response_text = "Sorry, I didn't understand that."
        for msg in reversed(new_state["messages"]):
            if msg["role"] == "assistant":
                response_text = msg["content"]
                break
    except Exception as e:
        print(f"Error processing message: {e}")
        response_text = "Sorry, I encountered an error processing your request."

    # Send response back to Twilio
    resp = MessagingResponse()
    resp.message(response_text)
    
    return Response(content=str(resp), media_type="application/xml")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
