import asyncio
from datetime import datetime
from src.extractors.macro_monthly import get_monthly_indicators
from src.database.crud import insert_monthly_macro, insert_newsletter
from src.engine.ai_generator import generate_tier_content
from src.utils.logger import get_logger

logger = get_logger(__name__)

async def run_monthly_extraction():
    """Runs the monthly pipeline for macro statistics."""
    logger.info("Starting the monthly macro pipeline...")
    
    # Use the 1st of the current month
    today = datetime.now().date()
    first_of_month = today.replace(day=1).isoformat()
    
    # Step 1: Extract Monthly Data
    monthly_data = await get_monthly_indicators()
    monthly_data["month_year"] = first_of_month
    
    # Step 2: Save to Supabase
    insert_monthly_macro(monthly_data)
    
    # Step 3: Generate the Monthly Statistics Analysis
    # We pass the monthly data to the AI to create a specialized report
    logger.info("Generating specialized monthly newsletters...")
    
    free_task = generate_tier_content(monthly_data, "free")
    premium_task = generate_tier_content(monthly_data, "premium")
    
    free_html, premium_html = await asyncio.gather(free_task, premium_task)
    
    newsletter_payload = {
        "date": first_of_month,
        "html_free": free_html,
        "html_premium": premium_html,
        "status": "pending"
    }
    
    # Save monthly newsletter
    insert_newsletter(newsletter_payload)
    
    logger.info("Monthly pipeline completely finished.")

if __name__ == "__main__":
    asyncio.run(run_monthly_extraction())