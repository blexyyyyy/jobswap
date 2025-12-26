from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class LLMClient(ABC):
    """
    Abstract interface for all LLM providers.
    """
    
    @abstractmethod
    def generate(self, prompt: str, temperature: float = 0.3, max_tokens: int = 512, meta: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate text from the LLM.
        
        Args:
            prompt (str): The input prompt.
            temperature (float): Sampling temperature (0.0 to 1.0).
            max_tokens (int): Maximum output tokens.
            meta (dict, optional): Extra metadata (e.g. specialized model parameters).

        Returns:
            str: The generated text response.
            
        Raises:
            LLMRateLimitError: If rate limited.
            LLMProviderError: If the API fails.
        """
        pass
