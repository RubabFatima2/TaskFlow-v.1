"""
Gemini service wrapper using OpenAI-compatible endpoint.

[Task]: T011
[From]: speckit.specify, speckit.plan §ADR-001, research.md §1

Uses Gemini's OpenAI-compatible REST API via AsyncOpenAI client.
This enables the OpenAI Agents SDK to work with Gemini 2.0 Flash.
"""

import logging
from openai import AsyncOpenAI
from app.config import settings

logger = logging.getLogger(__name__)

# Gemini OpenAI-compatible endpoint
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"


def create_gemini_client() -> AsyncOpenAI:
    """
    Create an AsyncOpenAI client configured for Gemini API.

    Returns:
        AsyncOpenAI client pointing to Gemini's OpenAI-compatible endpoint.
    """
    return AsyncOpenAI(
        api_key=settings.GEMINI_API_KEY,
        base_url=GEMINI_BASE_URL,
    )


# Singleton client instance
gemini_client = create_gemini_client()
