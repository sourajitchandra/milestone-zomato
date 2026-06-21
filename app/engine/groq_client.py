"""Groq API client wrapper module."""

import time
import logging
from groq import Groq, APIError, APIConnectionError, APITimeoutError, RateLimitError
from app.config import get_settings

logger = logging.getLogger(__name__)

class GroqClient:
    """Wrapper class for the Groq SDK client."""

    def __init__(self) -> None:
        """Initializes the Groq client after verifying credentials."""
        settings = get_settings()
        settings.require_groq_api_key()
        self.client = Groq(api_key=settings.groq_api_key)
        self.model = settings.groq_model
        self.temperature = settings.groq_temperature
        self.max_tokens = settings.groq_max_tokens

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        """Sends a request to Groq chat completions API with retries on transient errors.

        Args:
            system_prompt (str): System prompt containing behavior guidelines.
            user_prompt (str): User prompt containing context and preferences.

        Returns:
            str: Raw LLM response content.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        attempts = 2
        for attempt in range(1, attempts + 1):
            try:
                logger.info("Calling Groq API (model: %s, attempt %d/%d)", self.model, attempt, attempts)
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    response_format={"type": "json_object"},
                )
                
                content = response.choices[0].message.content
                if not content:
                    raise APIError("Empty response content from Groq API", request=None, message="Empty response")
                return content
                
            except (APIConnectionError, APITimeoutError, RateLimitError) as e:
                logger.warning("Transient Groq API error on attempt %d: %s", attempt, e)
                if attempt < attempts:
                    time.sleep(1)
                    continue
                else:
                    logger.error("Max retry attempts reached for transient Groq API error")
                    raise
            except Exception as e:
                logger.error("Non-transient error calling Groq API: %s", e)
                raise
        return ""
