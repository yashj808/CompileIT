"""
Gemini API wrapper.
Handles: rate limiting, retries, temperature, model selection, token counting.
"""
import os
import asyncio
from typing import Optional
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
if "GEMINI_API_KEY" in os.environ:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])

async def call_gemini(
    system: str,
    user: str,
    temperature: float = 0.1,
    model: str = "gemini-1.5-flash",
    max_tokens: int = 8192,
    max_retries: int = 3
) -> str:
    """
    Call Gemini with system + user message.
    Returns raw text response.
    Retries on rate limit with exponential backoff.
    """
    if "GEMINI_API_KEY" not in os.environ:
        raise RuntimeError("GEMINI_API_KEY not found in environment")

    gemini_model = genai.GenerativeModel(
        model_name=model,
        system_instruction=system,
        generation_config=genai.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            response_mime_type="application/json"   # Force JSON output
        )
    )
    
    for attempt in range(max_retries):
        try:
            response = await asyncio.to_thread(
                gemini_model.generate_content, user
            )
            return response.text
        except Exception as e:
            if "quota" in str(e).lower() or "rate" in str(e).lower():
                wait = 2 ** attempt
                await asyncio.sleep(wait)
                continue
            raise
    
    raise RuntimeError(f"Gemini API failed after {max_retries} retries")
