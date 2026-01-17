"""
LangChain-compatible LLM wrapper for MBART translator.
Accepts prompts like: "TRANSLATE from en to hi: Hello world"
Returns only the translated text.
"""

from typing import Any, List, Optional, Mapping
from langchain_core.language_models.llms import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from pydantic import Field, model_validator
import re
import logging

from .translator import MBARTTranslator

logger = logging.getLogger(__name__)


class TranslatorLLM(LLM):
    """
    LangChain LLM wrapper for MBART translator.
    
    Prompt format: "TRANSLATE from {src_lang} to {tgt_lang}: {text}"
    Example: "TRANSLATE from en to hi: Hello, how are you?"
    """
    
    translator: Optional[MBARTTranslator] = Field(default=None, exclude=True)
    model_name: str = "facebook/mbart-large-50-many-to-many-mmt"
    
    @model_validator(mode='after')
    def initialize_translator(self):
        """Initialize translator after model validation."""
        if self.translator is None:
            self.translator = MBARTTranslator(model_name=self.model_name)
        return self
    
    @property
    def _llm_type(self) -> str:
        """Return identifier for this LLM."""
        return "mbart_translator"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """
        Execute translation based on prompt.
        
        Args:
            prompt: Translation prompt in format "TRANSLATE from {src} to {tgt}: {text}"
            stop: Stop sequences (not used)
            run_manager: Callback manager (not used)
            
        Returns:
            Translated text only
        """
        # Parse prompt
        match = re.match(
            r"TRANSLATE from (\w+) to (\w+):\s*(.+)",
            prompt.strip(),
            re.IGNORECASE | re.DOTALL
        )
        
        if not match:
            raise ValueError(
                f"Invalid prompt format. Expected: 'TRANSLATE from <src> to <tgt>: <text>'\n"
                f"Got: {prompt}"
            )
        
        src_lang = match.group(1).lower()
        tgt_lang = match.group(2).lower()
        text = match.group(3).strip()
        
        # Validate languages
        supported = ["en", "hi", "te", "ta", "kn"]
        if src_lang not in supported:
            raise ValueError(f"Unsupported source language: {src_lang}. Supported: {supported}")
        if tgt_lang not in supported:
            raise ValueError(f"Unsupported target language: {tgt_lang}. Supported: {supported}")
        
        # Translate
        logger.info(f"Translating ({src_lang} -> {tgt_lang}): {text[:50]}...")
        translation = self.translator.translate(text, src_lang, tgt_lang)
        
        return translation
    
    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Return identifying parameters."""
        return {
            "model_name": self.model_name,
            "llm_type": self._llm_type,
        }
    
    def get_cache_size(self) -> int:
        """Get number of cached translations."""
        return self.translator.get_cache_size()
    
    def clear_cache(self):
        """Clear translation cache."""
        self.translator.clear_cache()


# Convenience function
def create_translator_llm(model_name: str = "facebook/mbart-large-50-many-to-many-mmt") -> TranslatorLLM:
    """
    Create a TranslatorLLM instance.
    
    Args:
        model_name: MBART model name from Hugging Face
        
    Returns:
        TranslatorLLM instance
    """
    return TranslatorLLM(model_name=model_name)
