"""
Text-to-speech wrapper with pyttsx3 (offline) and gTTS fallback.
Detects if target language is supported.
"""

import pyttsx3
from gtts import gTTS
import os
import tempfile
import logging
from typing import Optional
import platform

logger = logging.getLogger(__name__)


class TextToSpeech:
    """Text-to-speech with pyttsx3 and gTTS fallback."""
    
    # Language support mapping
    # pyttsx3 support varies by platform; gTTS supports many languages
    GTTS_LANG_MAP = {
        "en": "en",
        "hi": "hi",
        "te": "te",
        "ta": "ta",
        "kn": "kn",
    }
    
    def __init__(self, use_gtts_fallback: bool = True):
        """
        Initialize TTS engine.
        
        Args:
            use_gtts_fallback: Use gTTS if pyttsx3 fails (requires internet)
        """
        self.use_gtts_fallback = use_gtts_fallback
        self.pyttsx3_engine = None
        
        # Try to initialize pyttsx3
        try:
            self.pyttsx3_engine = pyttsx3.init()
            logger.info("pyttsx3 TTS engine initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize pyttsx3: {e}")
            if not use_gtts_fallback:
                raise
    
    def speak(self, text: str, language: str = "en", save_path: Optional[str] = None):
        """
        Speak text using TTS.
        
        Args:
            text: Text to speak
            language: Language code (en, hi, te, ta, kn)
            save_path: Optional path to save audio file (MP3)
        """
        if not text.strip():
            logger.warning("Empty text provided to TTS")
            return
        
        logger.info(f"Speaking ({language}): {text[:50]}...")
        
        # Try pyttsx3 first (offline, fast)
        if self.pyttsx3_engine and language == "en":
            try:
                self._speak_pyttsx3(text, save_path)
                return
            except Exception as e:
                logger.warning(f"pyttsx3 failed: {e}, trying gTTS fallback")
        
        # For Indian languages or if pyttsx3 fails, use gTTS
        if self.use_gtts_fallback and language in self.GTTS_LANG_MAP:
            try:
                self._speak_gtts(text, language, save_path)
                return
            except Exception as e:
                logger.error(f"gTTS failed: {e}")
        
        # Fallback: print to console
        logger.warning(f"TTS not available for language '{language}', printing to console")
        print(f"\n[{language.upper()}] {text}\n")
    
    def _speak_pyttsx3(self, text: str, save_path: Optional[str] = None):
        """Speak using pyttsx3 (offline)."""
        if save_path:
            self.pyttsx3_engine.save_to_file(text, save_path)
            self.pyttsx3_engine.runAndWait()
            logger.info(f"Audio saved to: {save_path}")
        else:
            self.pyttsx3_engine.say(text)
            self.pyttsx3_engine.runAndWait()
    
    def _speak_gtts(self, text: str, language: str, save_path: Optional[str] = None):
        """Speak using gTTS (requires internet)."""
        gtts_lang = self.GTTS_LANG_MAP.get(language, "en")
        tts = gTTS(text=text, lang=gtts_lang, slow=False)
        
        if save_path:
            tts.save(save_path)
            logger.info(f"Audio saved to: {save_path}")
            # Play the saved file
            self._play_audio(save_path)
        else:
            # Save to temp file and play
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                tmp_path = tmp.name
            
            tts.save(tmp_path)
            self._play_audio(tmp_path)
            
            # Clean up temp file
            try:
                os.remove(tmp_path)
            except Exception as e:
                logger.warning(f"Failed to remove temp file {tmp_path}: {e}")
    
    def _play_audio(self, audio_path: str):
        """Play audio file using platform-specific command."""
        system = platform.system()
        
        try:
            if system == "Windows":
                # Use pygame for real-time playback on Windows
                try:
                    import pygame
                    pygame.mixer.init()
                    pygame.mixer.music.load(audio_path)
                    pygame.mixer.music.play()
                    # Wait for playback to finish
                    while pygame.mixer.music.get_busy():
                        pygame.time.Clock().tick(10)
                    pygame.mixer.quit()
                except ImportError:
                    # Fallback to winsound for WAV files or os.system
                    logger.warning("pygame not installed, using fallback playback")
                    os.system(f'powershell -c (New-Object Media.SoundPlayer "{audio_path}").PlaySync()')
            elif system == "Darwin":  # macOS
                os.system(f'afplay {audio_path}')
            else:  # Linux
                os.system(f'mpg123 {audio_path} || ffplay -nodisp -autoexit {audio_path}')
        except Exception as e:
            logger.error(f"Failed to play audio: {e}")
    
    def set_rate(self, rate: int):
        """Set speech rate (pyttsx3 only)."""
        if self.pyttsx3_engine:
            self.pyttsx3_engine.setProperty('rate', rate)
    
    def set_volume(self, volume: float):
        """Set volume 0.0 to 1.0 (pyttsx3 only)."""
        if self.pyttsx3_engine:
            self.pyttsx3_engine.setProperty('volume', volume)
    
    def get_voices(self):
        """Get available voices (pyttsx3 only)."""
        if self.pyttsx3_engine:
            return self.pyttsx3_engine.getProperty('voices')
        return []
    
    def set_voice(self, voice_id: str):
        """Set voice by ID (pyttsx3 only)."""
        if self.pyttsx3_engine:
            self.pyttsx3_engine.setProperty('voice', voice_id)


def create_tts(use_gtts_fallback: bool = True) -> TextToSpeech:
    """
    Create TextToSpeech instance.
    
    Args:
        use_gtts_fallback: Use gTTS if pyttsx3 fails
        
    Returns:
        TextToSpeech instance
    """
    return TextToSpeech(use_gtts_fallback=use_gtts_fallback)
