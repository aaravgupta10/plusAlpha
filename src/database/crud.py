from typing import Dict, Any
from src.database.client import get_supabase_client
from src.utils.logger import get_logger

logger = get_logger(__name__)
supabase = get_supabase_client()

def insert_daily_macro(data: Dict[str, Any]) -> bool:
    """Saves the daily market data into the Supabase table."""
    try:
        # data should include date, india_vix, us_10y_yield, rbi_call_rate, fii_net_flow, dii_net_flow
        response = supabase.table("daily_macro_data").insert(data).execute()
        
        if response.data:
            logger.info("Daily macro data saved to database.")
            return True
        return False
        
    except Exception as e:
        logger.error(f"Failed to save daily data: {e}")
        return False

def insert_market_environment(data: Dict[str, Any]) -> bool:
    """Saves the calculated risk score to the database."""
    try:
        response = supabase.table("market_environment").insert(data).execute()
        if response.data:
            logger.info("Market environment score saved.")
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to save market environment: {e}")
        return False

def insert_newsletter(data: Dict[str, Any]) -> bool:
    """Saves the final AI HTML content for the emails."""
    try:
        response = supabase.table("newsletters").insert(data).execute()
        if response.data:
            logger.info("Newsletter HTML saved successfully.")
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to save newsletter: {e}")
        return False

def insert_monthly_macro(data: Dict[str, Any]) -> bool:
    """Saves the monthly economic data to the database."""
    try:
        response = supabase.table("monthly_macro_data").insert(data).execute()
        if response.data:
            logger.info("Monthly macro data saved to database.")
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to save monthly data: {e}")
        return False