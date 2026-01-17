import speech_recognition as sr
from gtts import gTTS
from io import BytesIO
import tempfile
import os


class AudioHandler:
    def __init__(self):
        self.recognizer = sr.Recognizer()
    
    def transcribe_audio(self, audio_bytes: bytes, language: str = "en") -> str:
        """Transcribe audio to text using Google Speech Recognition"""
        try:
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
                temp_audio.write(audio_bytes)
                temp_audio_path = temp_audio.name
            
            # Load and recognize
            with sr.AudioFile(temp_audio_path) as source:
                audio_data = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio_data, language=language)
            
            # Clean up
            os.unlink(temp_audio_path)
            
            return text
        except Exception as e:
            print(f"Transcription error: {e}")
            return ""
    
    def text_to_speech(self, text: str, language: str = "en") -> bytes:
        """Convert text to speech using gTTS"""
        try:
            tts = gTTS(text=text, lang=language, slow=False)
            audio_buffer = BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            return audio_buffer.read()
        except Exception as e:
            print(f"TTS error: {e}")
            return b""
    
    def recognize_from_microphone(self, language: str = "en") -> str:
        """Capture audio from microphone and transcribe"""
        try:
            with sr.Microphone() as source:
                print("Listening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5)
                
                text = self.recognizer.recognize_google(audio, language=language)
                return text
        except Exception as e:
            print(f"Microphone recognition error: {e}")
            return ""