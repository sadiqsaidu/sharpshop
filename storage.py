"""Supabase storage operations for product images."""
import requests
from requests.auth import HTTPBasicAuth
from database import get_supabase
from typing import List
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")

def download_and_upload_image(twilio_image_url: str) -> str:
    """
    Download image from Twilio and upload to Supabase Storage.
    Returns the public URL of the uploaded image.
    """
    supabase = get_supabase()
    
    try:
        # Download image from Twilio with authentication
        auth = HTTPBasicAuth(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        response = requests.get(twilio_image_url, auth=auth, timeout=10)
        response.raise_for_status()
        image_data = response.content
        
        # Generate unique filename
        file_extension = "jpg"  # Default to jpg, Twilio usually sends jpg
        if "image/png" in response.headers.get("Content-Type", ""):
            file_extension = "png"
        
        filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = f"products/{filename}"
        
        # Upload to Supabase Storage
        upload_result = supabase.storage.from_("product-images").upload(
            file_path,
            image_data,
            file_options={"content-type": f"image/{file_extension}"}
        )
        
        print(f"Upload result: {upload_result}")
        
        # Get public URL
        public_url = supabase.storage.from_("product-images").get_public_url(file_path)
        
        print(f"Successfully uploaded image: {public_url}")
        return public_url
        
    except Exception as e:
        print(f"Error uploading image: {e}")
        return None


def process_images(twilio_image_urls: List[str]) -> List[str]:
    """
    Process multiple images from Twilio and return list of permanent URLs.
    """
    permanent_urls = []
    
    for url in twilio_image_urls:
        permanent_url = download_and_upload_image(url)
        if permanent_url:
            permanent_urls.append(permanent_url)
    
    return permanent_urls