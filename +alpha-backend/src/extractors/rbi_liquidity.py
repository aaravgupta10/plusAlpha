import asyncio
from typing import Dict, Optional
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from src.utils.logger import get_logger

logger = get_logger(__name__)

async def get_rbi_call_rate() -> Dict[str, Optional[float]]:
    """Gets the latest interbank call rate from the RBI website."""
    url = "https://www.rbi.org.in/"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
        )
        page = await context.new_page()
        
        try:
            logger.info("Loading the RBI website...")
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            
            # Wait for the market trends table to load on the page
            await page.wait_for_selector("#wrapper", timeout=10000) 
            
            # We look for the row that has the Call Rate. 
            # Note: This selector might need a small update based on the live RBI site structure.
            rate_element = page.locator("td:has-text('Weighted Average Call Rate') + td")
            rate_text = await rate_element.first.inner_text()
            
            call_rate = float(rate_text.strip())
            logger.info(f"RBI Call Rate extracted: {call_rate}")
            
            return {"rbi_call_rate": call_rate}
            
        except PlaywrightTimeoutError:
            logger.error("RBI website took too long to load.")
            return {"rbi_call_rate": None}
        except Exception as e:
            logger.error(f"Error extracting RBI data: {e}")
            return {"rbi_call_rate": None}
        finally:
            await browser.close()