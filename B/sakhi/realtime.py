"""
Real-time voice translation loop.
Captures audio → transcribes → translates → speaks.
"""

import sounddevice as sd
import numpy as np
import logging
import signal
import sys
from typing import Optional
import time

from .stt import WhisperSTT
from .langchain_llm import TranslatorLLM
from .tts import TextToSpeech

logger = logging.getLogger(__name__)


class RealtimeTranslator:
    """Real-time voice translation system."""
    
    def __init__(
        self,
        src_lang: str,
        tgt_lang: str,
        chunk_seconds: float = 3.0,
        whisper_model: str = "base",
        mbart_model: str = "facebook/mbart-large-50-many-to-many-mmt",
        sample_rate: int = 16000,
    ):
        """
        Initialize real-time translator.
        
        Args:
            src_lang: Source language (en, hi, te, ta, kn, auto)
            tgt_lang: Target language (en, hi, te, ta, kn)
            chunk_seconds: Audio chunk length in seconds
            whisper_model: Whisper model size
            mbart_model: MBART model name
            sample_rate: Audio sample rate (16kHz recommended)
        """
        self.src_lang = src_lang
        self.tgt_lang = tgt_lang
        self.chunk_seconds = chunk_seconds
        self.sample_rate = sample_rate
        self.running = False
        
        # Validate languages
        supported = ["en", "hi", "te", "ta", "kn"]
        if src_lang != "auto" and src_lang not in supported:
            raise ValueError(f"Unsupported source language: {src_lang}")
        if tgt_lang not in supported:
            raise ValueError(f"Unsupported target language: {tgt_lang}")
        
        logger.info(f"Initializing Sakhi: {src_lang} -> {tgt_lang}")
        
        # Initialize components
        logger.info("Loading STT model...")
        self.stt = WhisperSTT(model_size=whisper_model)
        
        logger.info("Loading translation model...")
        self.translator_llm = TranslatorLLM(model_name=mbart_model)
        
        logger.info("Loading TTS engine...")
        self.tts = TextToSpeech(use_gtts_fallback=True)
        
        logger.info("Sakhi initialized successfully!")
    
    def start(self):
        """Start real-time translation loop."""
        self.running = True
        
        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        
        logger.info("\n" + "="*60)
        logger.info("🎤 Sakhi is listening...")
        logger.info(f"   Source: {self.src_lang.upper()}")
        logger.info(f"   Target: {self.tgt_lang.upper()}")
        logger.info(f"   Chunk: {self.chunk_seconds}s")
        logger.info("   Press Ctrl+C to stop")
        logger.info("="*60 + "\n")
        
        try:
            self._run_loop()
        except KeyboardInterrupt:
            logger.info("\nStopping Sakhi...")
        except Exception as e:
            logger.error(f"Error in translation loop: {e}", exc_info=True)
        finally:
            self.stop()
    
    def _run_loop(self):
        """Main translation loop."""
        chunk_samples = int(self.sample_rate * self.chunk_seconds)
        
        while self.running:
            try:
                # Record audio chunk
                logger.debug(f"Recording {self.chunk_seconds}s audio...")
                audio = self._record_audio(chunk_samples)
                
                # Check if audio has meaningful content (simple energy check)
                if not self._has_speech(audio):
                    logger.debug("No speech detected, skipping...")
                    continue
                
                # Transcribe
                logger.info("🎤 Transcribing...")
                transcription = self.stt.transcribe(
                    audio,
                    language=None if self.src_lang == "auto" else self.src_lang,
                    sample_rate=self.sample_rate
                )
                
                text = transcription["text"]
                detected_lang = transcription["language"]
                
                if not text.strip():
                    logger.debug("Empty transcription, skipping...")
                    continue
                
                # Determine source language
                actual_src = detected_lang if self.src_lang == "auto" else self.src_lang
                
                # Normalize language code (Whisper returns 'en', 'hi', etc.)
                actual_src = actual_src[:2].lower()
                
                logger.info(f"📝 Transcribed ({actual_src}): {text}")
                
                # Skip if same as target language
                if actual_src == self.tgt_lang:
                    logger.info("⚠️  Source and target languages are the same, skipping translation")
                    continue
                
                # Translate using LangChain LLM wrapper
                logger.info(f"🔄 Translating {actual_src} -> {self.tgt_lang}...")
                prompt = f"TRANSLATE from {actual_src} to {self.tgt_lang}: {text}"
                translation = self.translator_llm.invoke(prompt)
                
                logger.info(f"✅ Translation ({self.tgt_lang}): {translation}")
                
                # Speak translation
                logger.info("🔊 Speaking...")
                self.tts.speak(translation, language=self.tgt_lang)
                
                # Show cache stats
                cache_size = self.translator_llm.get_cache_size()
                logger.debug(f"Translation cache size: {cache_size}")
                
            except Exception as e:
                logger.error(f"Error processing audio chunk: {e}", exc_info=True)
                time.sleep(0.5)  # Brief pause before retrying
    
    def _record_audio(self, num_samples: int) -> np.ndarray:
        """
        Record audio from microphone.
        
        Args:
            num_samples: Number of samples to record
            
        Returns:
            Audio data as numpy array
        """
        try:
            audio = sd.rec(
                num_samples,
                samplerate=self.sample_rate,
                channels=1,
                dtype=np.float32,
                blocking=True
            )
            return audio.flatten()
        except Exception as e:
            logger.error(f"Failed to record audio: {e}")
            logger.error("Make sure your microphone is connected and PortAudio is installed")
            raise
    
    def _has_speech(self, audio: np.ndarray, threshold: float = 0.01) -> bool:
        """
        Simple energy-based speech detection.
        
        Args:
            audio: Audio data
            threshold: Energy threshold
            
        Returns:
            True if audio likely contains speech
        """
        energy = np.sqrt(np.mean(audio ** 2))
        return energy > threshold
    
    def _signal_handler(self, sig, frame):
        """Handle Ctrl+C gracefully."""
        logger.info("\n\nReceived interrupt signal, stopping...")
        self.running = False
    
    def stop(self):
        """Stop the translator."""
        self.running = False
        logger.info("Sakhi stopped. Goodbye! 👋")


def run_realtime_translator(
    src_lang: str,
    tgt_lang: str,
    chunk_seconds: float = 3.0,
    whisper_model: str = "base",
    mbart_model: str = "facebook/mbart-large-50-many-to-many-mmt",
):
    """
    Run real-time translator.
    
    Args:
        src_lang: Source language (en, hi, te, ta, kn, auto)
        tgt_lang: Target language (en, hi, te, ta, kn)
        chunk_seconds: Audio chunk length
        whisper_model: Whisper model size
        mbart_model: MBART model name
    """
    translator = RealtimeTranslator(
        src_lang=src_lang,
        tgt_lang=tgt_lang,
        chunk_seconds=chunk_seconds,
        whisper_model=whisper_model,
        mbart_model=mbart_model,
    )
    translator.start()
