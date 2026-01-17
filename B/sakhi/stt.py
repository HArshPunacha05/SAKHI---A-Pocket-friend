"""
Whisper-based speech-to-text helper functions.
Supports local Whisper models (no API required).
"""

import whisper
import torch
import numpy as np
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class WhisperSTT:
    """Whisper speech-to-text wrapper."""
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize Whisper STT.
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
        """
        logger.info(f"Loading Whisper model: {model_size}")
        
        # Determine device
        if torch.cuda.is_available():
            self.device = "cuda"
        elif torch.backends.mps.is_available():
            self.device = "mps"
        else:
            self.device = "cpu"
        
        logger.info(f"Using device: {self.device}")
        
        # Load Whisper model
        self.model = whisper.load_model(model_size, device=self.device)
        self.model_size = model_size
        
        logger.info(f"Whisper model '{model_size}' loaded successfully")
    
    def transcribe(
        self,
        audio: np.ndarray,
        language: Optional[str] = None,
        sample_rate: int = 16000
    ) -> Dict[str, str]:
        """
        Transcribe audio to text.
        
        Args:
            audio: Audio data as numpy array (float32, -1 to 1)
            language: Language code (en, hi, te, ta, kn) or None for auto-detect
            sample_rate: Audio sample rate (Whisper expects 16kHz)
            
        Returns:
            Dictionary with 'text' and 'language' keys
        """
        # Ensure audio is float32
        if audio.dtype != np.float32:
            audio = audio.astype(np.float32)
        
        # Normalize audio to [-1, 1] if needed
        if audio.max() > 1.0 or audio.min() < -1.0:
            audio = audio / np.abs(audio).max()
        
        # Resample if needed (Whisper expects 16kHz)
        if sample_rate != 16000:
            logger.warning(f"Audio sample rate is {sample_rate}Hz, Whisper expects 16kHz")
            # Simple resampling (for production, use librosa or scipy)
            from scipy import signal
            num_samples = int(len(audio) * 16000 / sample_rate)
            audio = signal.resample(audio, num_samples)
        
        # Transcribe
        logger.debug(f"Transcribing audio (length: {len(audio)/16000:.2f}s, language: {language or 'auto'})")
        
        result = self.model.transcribe(
            audio,
            language=language,
            fp16=(self.device == "cuda"),  # Use FP16 on CUDA for speed
            verbose=False
        )
        
        text = result["text"].strip()
        detected_lang = result.get("language", language or "unknown")
        
        logger.info(f"Transcribed ({detected_lang}): {text[:100]}...")
        
        return {
            "text": text,
            "language": detected_lang
        }
    
    def transcribe_file(self, audio_path: str, language: Optional[str] = None) -> Dict[str, str]:
        """
        Transcribe audio file.
        
        Args:
            audio_path: Path to audio file
            language: Language code or None for auto-detect
            
        Returns:
            Dictionary with 'text' and 'language' keys
        """
        logger.info(f"Transcribing file: {audio_path}")
        
        result = self.model.transcribe(
            audio_path,
            language=language,
            fp16=(self.device == "cuda"),
            verbose=False
        )
        
        text = result["text"].strip()
        detected_lang = result.get("language", language or "unknown")
        
        logger.info(f"Transcribed ({detected_lang}): {text[:100]}...")
        
        return {
            "text": text,
            "language": detected_lang
        }


def create_whisper_stt(model_size: str = "base") -> WhisperSTT:
    """
    Create WhisperSTT instance.
    
    Args:
        model_size: Whisper model size (tiny, base, small, medium, large)
        
    Returns:
        WhisperSTT instance
    """
    return WhisperSTT(model_size=model_size)


def get_supported_whisper_models():
    """Return list of supported Whisper model sizes."""
    return ["tiny", "base", "small", "medium", "large"]
