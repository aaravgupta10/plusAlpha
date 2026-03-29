import asyncio
import yfinance as yf
from typing import Dict, Optional
from src.utils.logger import get_logger

logger = get_logger(__name__)

async def fetch_ticker_data(ticker_symbol: str) -> Optional[float]:
    """Runs synchronous yfinance network calls in a separate thread."""
    def _fetch():
        ticker = yf.Ticker(ticker_symbol)
        # Fetching the last 5 days to ensure we get the latest closing price 
        # even if a weekend/holiday just passed.
        hist = ticker.history(period="5d")
        if hist.empty:
            raise ValueError(f"No data returned for {ticker_symbol}")
        return float(hist['Close'].iloc[-1])

    for attempt in range(3):
        try:
            return await asyncio.to_thread(_fetch)
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed for {ticker_symbol}: {e}")
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    logger.error(f"All attempts failed for {ticker_symbol}")
    return None

async def get_daily_market_metrics() -> Dict[str, Optional[float]]:
    """Fetches VIX and US 10Y Yield concurrently."""
    logger.info("Initiating market metrics extraction...")
    
    # ^INDIAVIX for India Volatility, ^TNX for US 10-Year Treasury Yield
    tasks = [
        fetch_ticker_data("^INDIAVIX"),
        fetch_ticker_data("^TNX")
    ]
    
    results = await asyncio.gather(*tasks)
    
    metrics = {
        "india_vix": results[0],
        "us_10y_yield": results[1]
    }
    
    logger.info(f"Market metrics retrieved: {metrics}")
    return metrics