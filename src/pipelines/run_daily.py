import asyncio
from datetime import datetime
from src.extractors.macro_yields import get_daily_market_metrics
from src.extractors.nse_fii_dii import get_fii_dii_flows
from src.extractors.rbi_liquidity import get_rbi_call_rate
from src.database.crud import insert_daily_macro, insert_market_environment, insert_newsletter
from src.engine.environment_score import calculate_risk_score
from src.engine.ai_generator import generate_newsletter_content
from src.utils.logger import get_logger

logger = get_logger(__name__)

async def run_daily_extraction():
    """Runs the full daily SaaS pipeline."""
    logger.info("Starting the daily pipeline...")
    
    today = datetime.now().date().isoformat()
    
    # Step 1: Extract all data
    market_data = await get_daily_market_metrics()
    fii_dii_data = await get_fii_dii_flows()
    rbi_data = await get_rbi_call_rate()
    
    daily_data = {
        "date": today,
        "india_vix": market_data.get("india_vix"),
        "us_10y_yield": market_data.get("us_10y_yield"),
        "fii_net_flow": fii_dii_data.get("fii_net_flow"),
        "dii_net_flow": fii_dii_data.get("dii_net_flow"),
        "rbi_call_rate": rbi_data.get("rbi_call_rate")
    }
    
    # Save raw data
    insert_daily_macro(daily_data)
    
    # Step 2: Calculate Risk Score
    risk_data = calculate_risk_score(daily_data)
    env_payload = {
        "date": today,
        "risk_score": risk_data["risk_score"],
        "status": risk_data["status"]
    }
    
    # Save risk score
    insert_market_environment(env_payload)
    
    # Step 3: Generate AI Newsletters
    ai_content = await generate_newsletter_content(daily_data, risk_data)
    
    newsletter_payload = {
        "date": today,
        "html_free": ai_content.get("ai_signal_free"),
        "html_premium": ai_content.get("ai_signal_premium"),
        "status": "pending"
    }
    
    # Save newsletters
    insert_newsletter(newsletter_payload)
    
    logger.info("Daily pipeline is completely finished.")

if __name__ == "__main__":
    asyncio.run(run_daily_extraction())