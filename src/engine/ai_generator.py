import os
import asyncio
import google.generativeai as genai
from typing import Dict, Any
from src.utils.logger import get_logger

logger = get_logger(__name__)

# System instructions act as our compliance and persona guardrails
SYSTEM_INSTRUCTION = (
    "You are the Lead Quantitative Macro Analyst for '+Alpha', a premium SaaS for Indian retail investors. "
    "Your objective is to interpret daily macroeconomic and liquidity data. "
    "CRITICAL CONSTRAINTS: "
    "1. NEVER give direct financial advice (e.g., do not say 'buy', 'sell', 'hold', or recommend specific assets). "
    "2. Speak in directional, institutional terms (e.g., 'liquidity conditions are tightening', 'risk-off environment'). "
    "3. Format your output strictly in clean HTML (using <p>, <ul>, <li>, <strong>) without markdown code blocks like ```html."
)

def setup_gemini():
    api_key = os.getenv("GEMINI_API_KEY", "").strip().strip('"').strip("'")
    if not api_key:
        logger.critical("GEMINI_API_KEY missing from environment.")
        raise ValueError("Missing Gemini API Key.")
    genai.configure(api_key=api_key)

async def generate_tier_content(payload: Dict[str, Any], tier: str) -> str:
    """Generates tier-specific HTML insight using Gemini 2.5 Flash."""
    setup_gemini()
    
    # We use the official Gemini 2.5 Flash model
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=SYSTEM_INSTRUCTION
    )

    if tier == "free":
        prompt = (
            f"Here is today's data: {payload}. "
            "Write a concise, 2-paragraph high-level summary of the market environment. "
            "Keep it accessible but professional. Focus on the main takeaway."
        )
    elif tier == "premium":
        prompt = (
            f"Here is today's data: {payload}. "
            "Write a deep-dive macro analysis. Break down what the FII flows, yields, and liquidity metrics mean "
            "when combined with the current Risk Score. Provide historical context and advanced interpretation of "
            "how these factors typically impact Indian equities. Be highly detailed."
        )
    else:
        raise ValueError("Invalid tier provided.")

    try:
        logger.info(f"Generating {tier} AI content...")
        # Utilize the async native generation method
        response = await model.generate_content_async(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"AI generation failed for {tier}: {e}")
        return f"<p>Error generating {tier} insights. Please check system logs.</p>"

async def generate_newsletter_content(daily_data: Dict[str, Any], risk_data: Dict[str, Any]) -> Dict[str, str]:
    """Orchestrates generation for both tiers concurrently."""
    payload = {**daily_data, **risk_data}
    
    # Run both AI requests in parallel to reduce latency
    free_task = generate_tier_content(payload, "free")
    premium_task = generate_tier_content(payload, "premium")
    
    free_html, premium_html = await asyncio.gather(free_task, premium_task)
    
    return {
        "ai_signal_free": free_html,
        "ai_signal_premium": premium_html
    }