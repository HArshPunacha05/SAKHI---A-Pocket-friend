"""
MBART-based translator with caching and helper functions.
Supports: en, hi, te, ta, kn
"""

import torch
from transformers import MBartForConditionalGeneration, MBart50TokenizerFast
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class MBARTTranslator:
    """MBART translator with translation caching."""
    
    # Language code mapping for MBART-50
    LANG_CODE_MAP = {
        "en": "en_XX",
        "hi": "hi_IN",
        "te": "te_IN",
        "ta": "ta_IN",
        "kn": "kn_IN",
    }
    
    def __init__(self, model_name: str = "facebook/mbart-large-50-many-to-many-mmt"):
        """
        Initialize MBART translator.
        
        Args:
            model_name: Hugging Face model name
        """
        logger.info(f"Loading MBART model: {model_name}")
        
        # Determine device
        if torch.cuda.is_available():
            self.device = "cuda"
        elif torch.backends.mps.is_available():
            self.device = "mps"
        else:
            self.device = "cpu"
        
        logger.info(f"Using device: {self.device}")
        
        # Load model and tokenizer
        self.tokenizer = MBart50TokenizerFast.from_pretrained(model_name)
        self.model = MBartForConditionalGeneration.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()
        
        # Translation cache: (src_lang, tgt_lang, text) -> translation
        self.cache: Dict[tuple, str] = {}
        
        logger.info("MBART model loaded successfully")
    
    def translate(self, text: str, src_lang: str, tgt_lang: str) -> str:
        """
        Translate text from source to target language.
        
        Args:
            text: Input text
            src_lang: Source language code (en, hi, te, ta, kn)
            tgt_lang: Target language code (en, hi, te, ta, kn)
            
        Returns:
            Translated text
        """
        # Check cache
        cache_key = (src_lang, tgt_lang, text.strip())
        if cache_key in self.cache:
            logger.debug(f"Cache hit for: {text[:50]}...")
            return self.cache[cache_key]
        
        # Validate language codes
        if src_lang not in self.LANG_CODE_MAP:
            raise ValueError(f"Unsupported source language: {src_lang}")
        if tgt_lang not in self.LANG_CODE_MAP:
            raise ValueError(f"Unsupported target language: {tgt_lang}")
        
        # Map to MBART language codes
        src_code = self.LANG_CODE_MAP[src_lang]
        tgt_code = self.LANG_CODE_MAP[tgt_lang]
        
        # Tokenize
        self.tokenizer.src_lang = src_code
        encoded = self.tokenizer(text, return_tensors="pt", padding=True)
        encoded = {k: v.to(self.device) for k, v in encoded.items()}
        
        # Generate translation
        with torch.no_grad():
            generated_tokens = self.model.generate(
                **encoded,
                forced_bos_token_id=self.tokenizer.lang_code_to_id[tgt_code],
                max_length=512,
                num_beams=5,
                early_stopping=True,
            )
        
        # Decode
        translation = self.tokenizer.batch_decode(
            generated_tokens, skip_special_tokens=True
        )[0]
        
        # Cache result
        self.cache[cache_key] = translation
        logger.debug(f"Translated ({src_lang}->{tgt_lang}): {text[:50]}... -> {translation[:50]}...")
        
        return translation
    
    def clear_cache(self):
        """Clear translation cache."""
        self.cache.clear()
        logger.info("Translation cache cleared")
    
    def get_cache_size(self) -> int:
        """Get number of cached translations."""
        return len(self.cache)


def get_supported_languages():
    """Return list of supported language codes."""
    return list(MBARTTranslator.LANG_CODE_MAP.keys())


def validate_language(lang_code: str) -> bool:
    """Check if language code is supported."""
    return lang_code in MBARTTranslator.LANG_CODE_MAP
