import logging
import time
from typing import List, Dict, Any, Optional

from app.llm.base import LLMClient
from app.llm.errors import LLMError, LLMRateLimitError, LLMConfigurationError
from app.llm.gemini import GeminiClient
from app.llm.groq import GroqClient
from app.llm.ollama import OllamaClient

logger = logging.getLogger(__name__)

class LLMWrapper:
    """
    Orchestrates multiple LLM providers with fallback logic.
    """
    
    def __init__(self, provider_names: List[str] = None):
        """
        Args:
            provider_names: List of provider names in priority order (e.g. ["groq", "gemini", "ollama"])
        """
        self.providers: List[LLMClient] = []
        self.provider_names = provider_names or ["gemini"] # Default
        
        self._initialize_providers()

    def _initialize_providers(self):
        """Instantiate providers based on names."""
        for name in self.provider_names:
            try:
                if name == "gemini":
                    self.providers.append(GeminiClient())
                elif name == "groq":
                    self.providers.append(GroqClient())
                elif name == "ollama":
                    self.providers.append(OllamaClient())
                else:
                    logger.warning(f"Unknown provider name: {name}")
            except LLMConfigurationError as e:
                logger.warning(f"Skipping provider {name} due to config error: {e}")
            except Exception as e:
                logger.error(f"Failed to init provider {name}: {e}")

        if not self.providers:
            logger.warning("No LLM providers successfully initialized. generated text will fail.")

    def generate(self, prompt: str, temperature: float = 0.3, max_tokens: int = 512, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Try generating text from providers in order.
        
        Returns:
            Dict containing:
            - text: str
            - provider: str (name of provider that succeeded)
            - model: str
        """
        errors = []
        
        for client in self.providers:
            provider_name = client.__class__.__name__.replace("Client", "")
            try:
                # logger.info(f"Attempting generation with {provider_name}...")
                start_time = time.time()
                
                text = client.generate(prompt, temperature, max_tokens, meta)
                
                duration = time.time() - start_time
                # logger.info(f"Success with {provider_name} in {duration:.2f}s")
                
                return {
                    "text": text,
                    "provider": provider_name,
                    "duration": duration
                }
                
            except LLMRateLimitError as e:
                logger.warning(f"Rate limit hit for {provider_name}: {e}")
                errors.append(f"{provider_name}: Rate Limit")
            except Exception as e:
                logger.error(f"Error with {provider_name}: {e}")
                errors.append(f"{provider_name}: {str(e)}")
                
        # If we get here, all providers failed
        error_summary = "; ".join(errors)
        raise LLMError(f"All LLM providers failed: {error_summary}")
