"""
Multi-LLM Provider Abstraction Layer
Supports: Gemini, Mistral
Allows teachers to choose which LLM to use for their chatbots
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from config import settings


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate a response from the LLM"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if this provider is configured and available"""
        pass
    
    @abstractmethod
    def list_models(self) -> List[str]:
        """List available models for this provider"""
        pass


class GeminiProvider(LLMProvider):
    """Google Gemini API Provider"""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.GEMINI_MODEL
        self._configure()
    
    def _configure(self):
        if settings.GEMINI_API_KEY:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.genai = genai
        else:
            self.genai = None
    
    def is_available(self) -> bool:
        return bool(settings.GEMINI_API_KEY)
    
    def list_models(self) -> List[str]:
        """Return list of recommended Gemini models"""
        return [
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
            "gemini-1.5-flash",
            "gemini-1.5-pro",
        ]
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self.is_available():
            return "❌ Gemini API key not configured"
        
        try:
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            model = self.genai.GenerativeModel(self.model_name)
            response = model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"❌ Gemini Error: {str(e)}"


class MistralProvider(LLMProvider):
    """Mistral AI API Provider"""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.MISTRAL_MODEL
        if self.model_name and ":" in self.model_name:
             self.model_name = self.model_name.split(":")[0]
        self.api_key = settings.MISTRAL_API_KEY
        self.client = None
        self._configure()
    
    def _configure(self):
        if self.api_key:
            try:
                from mistralai import Mistral
                self.client = Mistral(api_key=self.api_key)
            except ImportError:
                self.client = None
    
    def is_available(self) -> bool:
        return bool(self.api_key and self.client)
    
    def list_models(self) -> List[str]:
        """Return list of recommended Mistral models"""
        return [
            "mistral-small-latest",
            "mistral-medium-latest",
            "mistral-large-latest",
            "open-mistral-7b",
            "open-mixtral-8x7b",
            "codestral-latest",
        ]
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self.is_available():
            return "❌ Mistral API key not configured or mistralai package not installed"
        
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.complete(
                model=self.model_name,
                messages=messages
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ CRITICAL MISTRAL ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"❌ Mistral Error: {str(e)}"


# Provider Registry
PROVIDERS = {
    "gemini": GeminiProvider,
    "mistral": MistralProvider,
}


def get_llm_provider(provider_name: str, model_name: str = None) -> LLMProvider:
    """
    Get an LLM provider instance
    
    Args:
        provider_name: 'gemini' or 'mistral'
        model_name: Optional specific model name
        
    Returns:
        LLMProvider instance
    """
    provider_class = PROVIDERS.get(provider_name.lower())
    if not provider_class:
        raise ValueError(f"Unknown provider: {provider_name}. Available: {list(PROVIDERS.keys())}")
    
    return provider_class(model_name=model_name)


def get_available_providers() -> Dict[str, bool]:
    """Get a dict of provider names and their availability status"""
    return {
        "gemini": bool(settings.GEMINI_API_KEY),
        "mistral": bool(settings.MISTRAL_API_KEY),
    }


def get_all_models() -> Dict[str, List[str]]:
    """Get all available models by provider"""
    return {
        "gemini": GeminiProvider().list_models(),
        "mistral": MistralProvider().list_models(),
    }
