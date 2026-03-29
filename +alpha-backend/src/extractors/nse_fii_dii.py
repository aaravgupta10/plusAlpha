import asyncio
from typing import Dict, Optional
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from src.utils.logger import get_logger

logger = get_logger(__name__)

async def get_fii_dii_flows() -> Dict[str, Optional[float]]:
    """Scrapes NSE for daily FII and DII net cash market flows."""
    url = "https://www.nseindia.com/reports/fii-dii"
    
    async with async_playwright() as p:
        # Launching with specific arguments to bypass basic headless detection
        browser = await p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()
        
        try:
            logger.info("Navigating to NSE FII/DII portal...")
            # Using domcontentloaded to speed up execution, we don't need all images to load
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            
            # Wait for the specific table to render (adjust selector based on actual NSE DOM)
            # This is a defensive wait to ensure the React/Angular frontend has populated the data
            await page.wait_for_selector("#fii_dii_table", timeout=10000) 
            
            # Extracting logic (Placeholder selectors - require live DOM inspection to finalize)
            fii_net = await page.locator("#fii_cash_net").inner_text()
            dii_net = await page.locator("#dii_cash_net").inner_text()
            
            # Clean and convert strings to floats (e.g., "1,200.50" -> 1200.50)
            fii_value = float(fii_net.replace(',', '').strip())
            dii_value = float(dii_net.replace(',', '').strip())
            
            logger.info(f"FII/DII data successfully extracted. FII: {fii_value}, DII: {dii_value}")
            return {"fii_net_flow": fii_value, "dii_net_flow": dii_value}
            
        except PlaywrightTimeoutError:
            logger.error("Timeout while attempting to load NSE FII/DII data. Protection may have blocked the request.")
            return {"fii_net_flow": None, "dii_net_flow": None}
        except Exception as e:
            logger.error(f"Unexpected error extracting institutional flows: {e}")
            return {"fii_net_flow": None, "dii_net_flow": None}
        finally:
            await browser.close()