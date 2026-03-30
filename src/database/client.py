import os
from supabase import create_client, Client
from dotenv import load_dotenv
from src.utils.logger import get_logger

load_dotenv(override=True)
logger = get_logger(__name__)

def get_supabase_client() -> Client:
    url = os.getenv("SUPABASE_URL", "").strip().strip('"').strip("'")
    key = os.getenv("SUPABASE_KEY", "").strip().strip('"').strip("'")

    if not url or not key:
        logger.critical("Supabase keys are missing.")
        raise ValueError("Check your .env file for Supabase keys.")

    try:
        return create_client(url, key)
    except Exception as e:
        logger.critical(f"Database connection failed: {e}")
        raise