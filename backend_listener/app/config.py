import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY") or "SWgA-iqws5ZOGT7czLh4fxnM7ZBCanpa2ZkmpPzW954="

if not SECRET_KEY:
    raise ValueError("SECRET_KEY is missing from .env file!")

cipher = Fernet(SECRET_KEY.encode())