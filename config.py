"""OpenRouter API configuration for LangGraph agent."""
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
MODEL_NAME = "llama-3.3-70b-versatile"

ALLOWED_CATEGORIES = ["fashion", "electronics", "home", "beauty", "sports", "food", "books", "other"]
ALLOWED_CONDITIONS = ["new", "used", "refurbished"]
# sk-or-v1-b93a7608d387418744ef03b2bbd33c1590b68df67cbcde8a96133daf2bb2d35fER_API_KEY