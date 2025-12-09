# SharpShop — Inventory Management Agent 🛍️🤖

Welcome to SharpShop — a smart WhatsApp chatbot that helps sellers manage their inventory. It uses **LangGraph** for conversational flow and **Groq** (Llama 3) for intelligence.

## Features
- 🤖 **Conversational AI**: Understands natural language to manage inventory.
- 📦 **Inventory Actions**: Create, query, update, and list products.
- 📱 **WhatsApp Integration**: Works directly via Twilio Sandbox.
- ⚡ **Fast Inference**: Powered by Groq.

## Prerequisites
- Python 3.12+
- [Ngrok](https://ngrok.com/) (for local testing)
- [Twilio Account](https://www.twilio.com/) (for WhatsApp Sandbox)
- [Groq API Key](https://console.groq.com/)

## Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/<your-username>/sharpshop.git
   cd sharpshop
   ```

2. **Create and activate a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   Create a `.env` file in the root directory:
   ```bash
   GROQ_API_KEY=your_groq_api_key_here
   ```

## Running the Bot

1. **Start the Server**
   ```bash
   python server.py
   ```
   The server will start on `http://0.0.0.0:8000`.

2. **Expose Localhost via Ngrok**
   In a separate terminal:
   ```bash
   ngrok http 8000
   ```
   Copy the HTTPS URL (e.g., `https://1234-56-78.ngrok-free.app`).

3. **Configure Twilio Sandbox**
   - Go to [Twilio Console > Messaging > Try it out > Send a WhatsApp message](https://console.twilio.com/).
   - Connect your phone to the sandbox.
   - Go to **Sandbox Settings**.
   - Paste your Ngrok URL appended with `/whatsapp` into the **"When a message comes in"** field.
     - Example: `https://1234-56-78.ngrok-free.app/whatsapp`
   - Save settings.

## Usage

Send messages to the Twilio Sandbox number:

- **Add Product**: "I want to add Nike Shoes for 20000 naira, 5 in stock, new condition."
- **Query**: "Do I have any shoes?"
- **List**: "Show me all my products."
- **Update**: "Update the price of Nike Shoes to 22000."

## Project Structure
- `server.py`: FastAPI server handling Twilio webhooks.
- `agent.py`: LangGraph agent logic and state management.
- `tools.py`: Mock inventory tools (replace with real DB calls).
- `config.py`: Configuration settings.
