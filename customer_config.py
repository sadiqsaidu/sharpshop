import os
from dotenv import load_dotenv

load_dotenv()

# Model settings
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
ALLOWED_CATEGORIES = ["Electronics", "Fashion", "Footwear", "Accessories", "Home & Living"]

MODEL_NAME = os.getenv("CUSTOMER_AGENT_MODEL", "llama-3.3-70b-versatile")
MODEL_TEMPERATURE = 0.7
MAX_TOKENS = 500

# Session settings
SESSION_TTL = int(os.getenv("CUSTOMER_SESSION_TTL", "1800"))
MAX_SESSION_MESSAGES = int(os.getenv("CUSTOMER_MAX_SESSION_MESSAGES", "50"))
MAX_SESSION_DURATION = 7200  # 2 hours
CLEANUP_INTERVAL = 300  # 5 minutes

# Rate limiting
RATE_LIMIT_PER_MINUTE = int(os.getenv("CUSTOMER_RATE_LIMIT_PER_MINUTE", "30"))
RATE_LIMIT_PER_HOUR = int(os.getenv("CUSTOMER_RATE_LIMIT_PER_HOUR", "1000"))
MAX_CONCURRENT_SESSIONS = int(os.getenv("CUSTOMER_MAX_CONCURRENT_SESSIONS", "10000"))

# Response settings
MAX_PRODUCTS_IN_RESPONSE = 5
INCLUDE_PRODUCT_IMAGES = True
ENCOURAGE_WHATSAPP_CONTACT = True

# Payment Settings
FLUTTERWAVE_SECRET_KEY = os.getenv("FLUTTERWAVE_SECRET_KEY", "")
FLUTTERWAVE_BASE_URL = "https://api.flutterwave.com/v3"
