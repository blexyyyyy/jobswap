import os
import logging
from app.llm.base import LLMClient
from app.llm.errors import LLMRateLimitError, LLMProviderError, LLMConfigurationError

# Optional groq import - may not be installed
try:
    from groq import Groq, RateLimitError, APIError
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    Groq = None
    RateLimitError = Exception
    APIError = Exception

logger = logging.getLogger(__name__)

class GroqClient(LLMClient):
    def __init__(self):
        if not GROQ_AVAILABLE:
            raise LLMConfigurationError("groq package not installed. Run: pip install groq")
        
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise LLMConfigurationError("GROQ_API_KEY not found in environment")
        
        try:
            self.client = Groq(api_key=self.api_key)
            self.model = "llama3-70b-8192" # Default strong model
        except Exception as e:
            raise LLMConfigurationError(f"Failed to initialize Groq client: {e}")

    def generate(self, prompt: str, temperature: float = 0.3, max_tokens: int = 512, meta: dict | None = None) -> str:
        try:
            # Check for JSON mode request
            response_format = None
            if meta and meta.get("json_mode"):
                response_format = {"type": "json_object"}
                # Ensure prompt asks for JSON if not implicit
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                response_format=response_format
            )
            
            return completion.choices[0].message.content

        except RateLimitError as e:
            raise LLMRateLimitError(f"Groq Rate Limit: {e}")
        except APIError as e:
            raise LLMProviderError(f"Groq API Error: {e}")
        except Exception as e:
            raise LLMProviderError(f"Groq Unexpected Error: {e}")
