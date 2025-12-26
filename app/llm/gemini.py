import logging
import google.genai.types as types
from google.genai import Client
from app.core.config import GEMINI_API_KEY
from app.llm.base import LLMClient
from app.llm.errors import LLMRateLimitError, LLMProviderError, LLMConfigurationError

logger = logging.getLogger(__name__)

class GeminiClient(LLMClient):
    def __init__(self):
        if not GEMINI_API_KEY:
            raise LLMConfigurationError("GEMINI_API_KEY not found in environment")
        try:
            self.client = Client(api_key=GEMINI_API_KEY)
            self.model = "gemini-2.0-flash-exp" # Default or from config
        except Exception as e:
            raise LLMConfigurationError(f"Failed to initialize Gemini client: {e}")

    def generate(self, prompt: str, temperature: float = 0.3, max_tokens: int = 512, meta: dict | None = None) -> str:
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                )
            )
            
            if not response.text:
                return ""
                
            return response.text

        except Exception as e:
            error_str = str(e).lower()
            if "quota" in error_str or "429" in error_str:
                raise LLMRateLimitError(f"Gemini Rate Limit: {e}")
            raise LLMProviderError(f"Gemini Error: {e}")
