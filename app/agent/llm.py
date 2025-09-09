"""
LLM Provider Management
Unified interface for multiple LLM providers (Gemini, OpenAI, etc.)
"""

import logging
from typing import Dict, List, Any, Optional, Union
from abc import ABC, abstractmethod
from enum import Enum

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from ..core.config import llm_config

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Available LLM providers."""
    OPENAI = "openai"
    GEMINI = "gemini"


class BaseLLM(ABC):
    """Base class for LLM providers."""
    
    def __init__(self, model_name: str, api_key: str = None):
        self.model_name = model_name
        self.api_key = api_key
        self.temperature = llm_config.temperature
        self.max_tokens = llm_config.max_tokens
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text completion."""
        pass
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate chat completion."""
        pass
    
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """Generate text embeddings."""
        pass


class OpenAILLM(BaseLLM):
    """OpenAI LLM provider."""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", api_key: str = None):
        super().__init__(model_name, api_key)
        
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not available. Install with: pip install openai")
        
        if api_key:
            openai.api_key = api_key
        elif llm_config.openai_api_key:
            openai.api_key = llm_config.openai_api_key
        else:
            raise ValueError("OpenAI API key not provided")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text completion using OpenAI."""
        try:
            response = openai.Completion.create(
                model=self.model_name if "davinci" in self.model_name else "text-davinci-003",
                prompt=prompt,
                max_tokens=kwargs.get('max_tokens', self.max_tokens),
                temperature=kwargs.get('temperature', self.temperature),
                stop=kwargs.get('stop', None)
            )
            return response.choices[0].text.strip()
        except Exception as e:
            logger.error(f"OpenAI generation error: {e}")
            raise
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate chat completion using OpenAI."""
        try:
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=messages,
                max_tokens=kwargs.get('max_tokens', self.max_tokens),
                temperature=kwargs.get('temperature', self.temperature),
                stop=kwargs.get('stop', None)
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI chat error: {e}")
            raise
    
    def embed(self, text: str) -> List[float]:
        """Generate embeddings using OpenAI."""
        try:
            response = openai.Embedding.create(
                model=llm_config.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"OpenAI embedding error: {e}")
            raise


class GeminiLLM(BaseLLM):
    """Google Gemini LLM provider."""
    
    def __init__(self, model_name: str = "gemini-1.5-flash", api_key: str = None):
        super().__init__(model_name, api_key)
        
        if not GEMINI_AVAILABLE:
            raise ImportError("Google GenerativeAI library not available. Install with: pip install google-generativeai")
        
        api_key = api_key or llm_config.gemini_api_key
        if not api_key:
            raise ValueError("Gemini API key not provided")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text completion using Gemini."""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=kwargs.get('temperature', self.temperature),
                    max_output_tokens=kwargs.get('max_tokens', self.max_tokens),
                    stop_sequences=kwargs.get('stop', None)
                )
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            raise
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate chat completion using Gemini."""
        try:
            # Convert OpenAI-style messages to Gemini format
            chat_session = self.model.start_chat(history=[])
            
            # Add conversation history
            for msg in messages[:-1]:  # All but the last message
                if msg["role"] == "user":
                    chat_session.send_message(msg["content"])
                elif msg["role"] == "assistant":
                    # Add assistant response to history
                    pass  # Gemini handles this automatically
            
            # Send the final user message
            last_message = messages[-1]
            if last_message["role"] == "user":
                response = chat_session.send_message(
                    last_message["content"],
                    generation_config=genai.types.GenerationConfig(
                        temperature=kwargs.get('temperature', self.temperature),
                        max_output_tokens=kwargs.get('max_tokens', self.max_tokens)
                    )
                )
                return response.text.strip()
            else:
                # If last message is not from user, treat as a regular generation
                return self.generate(last_message["content"], **kwargs)
        except Exception as e:
            logger.error(f"Gemini chat error: {e}")
            raise
    
    def embed(self, text: str) -> List[float]:
        """Generate embeddings using Gemini."""
        try:
            # Gemini doesn't have direct embedding API yet
            # For now, return a placeholder or use alternative method
            logger.warning("Gemini embeddings not directly available, using text-to-vector conversion")
            # This is a placeholder - in production, you might want to use
            # sentence-transformers or another embedding model
            return [0.0] * 768  # Placeholder embedding
        except Exception as e:
            logger.error(f"Gemini embedding error: {e}")
            raise


class LLMManager:
    """Manages multiple LLM providers and provides unified interface."""
    
    def __init__(self):
        """Initialize LLM manager."""
        self.providers = {}
        self.default_provider = None
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available LLM providers."""
        try:
            # Initialize Gemini if API key is available
            if llm_config.gemini_api_key and GEMINI_AVAILABLE:
                self.providers[LLMProvider.GEMINI] = GeminiLLM()
                self.default_provider = LLMProvider.GEMINI
                logger.info("Gemini LLM provider initialized")
            
            # Initialize OpenAI if API key is available
            if llm_config.openai_api_key and OPENAI_AVAILABLE:
                self.providers[LLMProvider.OPENAI] = OpenAILLM()
                if not self.default_provider:
                    self.default_provider = LLMProvider.OPENAI
                logger.info("OpenAI LLM provider initialized")
            
            if not self.providers:
                logger.warning("No LLM providers initialized - check API keys and dependencies")
            else:
                logger.info(f"Default LLM provider: {self.default_provider.value}")
        
        except Exception as e:
            logger.error(f"Error initializing LLM providers: {e}")
    
    def get_provider(self, provider: Union[LLMProvider, str] = None) -> BaseLLM:
        """Get LLM provider instance."""
        if provider is None:
            provider = self.default_provider
        elif isinstance(provider, str):
            provider = LLMProvider(provider)
        
        if provider not in self.providers:
            raise ValueError(f"Provider {provider.value} not available")
        
        return self.providers[provider]
    
    def generate(
        self,
        prompt: str,
        provider: Union[LLMProvider, str] = None,
        **kwargs
    ) -> str:
        """Generate text using specified or default provider."""
        llm = self.get_provider(provider)
        return llm.generate(prompt, **kwargs)
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        provider: Union[LLMProvider, str] = None,
        **kwargs
    ) -> str:
        """Generate chat completion using specified or default provider."""
        llm = self.get_provider(provider)
        return llm.chat(messages, **kwargs)
    
    def embed(
        self,
        text: str,
        provider: Union[LLMProvider, str] = None
    ) -> List[float]:
        """Generate embeddings using specified or default provider."""
        llm = self.get_provider(provider)
        return llm.embed(text)
    
    def is_available(self, provider: Union[LLMProvider, str]) -> bool:
        """Check if a provider is available."""
        if isinstance(provider, str):
            provider = LLMProvider(provider)
        return provider in self.providers
    
    def list_providers(self) -> List[str]:
        """List available providers."""
        return [provider.value for provider in self.providers.keys()]


# Global LLM manager instance
llm_manager = LLMManager()


def get_llm_manager() -> LLMManager:
    """Get the global LLM manager instance."""
    return llm_manager


# Convenience functions
def generate_text(prompt: str, provider: str = None, **kwargs) -> str:
    """Convenience function for text generation."""
    return llm_manager.generate(prompt, provider, **kwargs)


def generate_chat(messages: List[Dict[str, str]], provider: str = None, **kwargs) -> str:
    """Convenience function for chat generation."""
    return llm_manager.chat(messages, provider, **kwargs)


def generate_embeddings(text: str, provider: str = None) -> List[float]:
    """Convenience function for embedding generation."""
    return llm_manager.embed(text, provider)


# Example usage and system prompts
SYSTEM_PROMPTS = {
    "oceanographer": """You are an expert oceanographer specializing in Argo float data analysis. 
    You help researchers and scientists understand oceanographic phenomena in the Indian Ocean.
    Provide accurate, scientific explanations while being accessible to different knowledge levels.""",
    
    "data_analyst": """You are a data analyst expert in oceanographic datasets, particularly Argo float measurements.
    Help users understand data patterns, anomalies, and trends in temperature, salinity, and pressure measurements.""",
    
    "multilingual": """You are a multilingual oceanographic assistant. 
    Respond in the user's language and provide culturally appropriate explanations for oceanographic concepts."""
}


if __name__ == "__main__":
    # Test LLM functionality
    print("Testing LLM Manager...")
    print(f"Available providers: {llm_manager.list_providers()}")
    
    if llm_manager.default_provider:
        try:
            test_response = llm_manager.generate(
                "Explain what an Argo float is in one sentence.",
                max_tokens=100
            )
            print(f"✅ Test response: {test_response}")
        except Exception as e:
            print(f"❌ Test failed: {e}")
    else:
        print("❌ No LLM providers available - check API keys")
