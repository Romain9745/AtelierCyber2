import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("GOOGLE_API_KEY")

if not SECRET_KEY:
    raise ValueError("GOOGLE_API_KEY is missing from .env file!")

google_api_key = SECRET_KEY