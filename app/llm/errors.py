class LLMError(Exception):
    """Base exception for LLM errors."""
    pass

class LLMRateLimitError(LLMError):
    """Raised when an LLM provider hits rate limits."""
    pass

class LLMTimeoutError(LLMError):
    """Raised when an LLM request times out."""
    pass

class LLMProviderError(LLMError):
    """Raised for general provider API errors (500s, auth, etc)."""
    pass

class LLMConfigurationError(LLMError):
    """Raised when a provider is missing API keys or config."""
    pass
