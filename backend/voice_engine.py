"""
Voice Module - Speech-to-Text (STT) and Text-to-Speech (TTS) capabilities
"""
import os
import io
import tempfile
from pathlib import Path
from typing import Optional, Tuple
import base64

from backend.config import settings


class VoiceEngine:
    """
    Voice processing engine for STT and TTS
    """
    
    def __init__(self):
        self.voice_enabled = settings.voice_enabled
        self.tts_provider = settings.tts_provider
        self.audio_dir = settings.audio_dir
        
        # Initialize engines on demand
        self._whisper_model = None
        self._recognizer = None
    
    # ========== Speech-to-Text (STT) ==========
    
    def transcribe_audio(
        self, 
        audio_path: Path = None,
        audio_bytes: bytes = None
    ) -> str:
        """
        Transcribe audio to text using Whisper
        
        Args:
            audio_path: Path to audio file
            audio_bytes: Raw audio bytes
            
        Returns:
            Transcribed text
        """
        if not self.voice_enabled:
            raise RuntimeError("Voice mode is disabled")
        
        # Save bytes to temp file if needed
        if audio_bytes and not audio_path:
            temp_file = tempfile.NamedTemporaryFile(
                suffix=".wav", 
                delete=False
            )
            temp_file.write(audio_bytes)
            temp_file.close()
            audio_path = Path(temp_file.name)
        
        if not audio_path or not audio_path.exists():
            raise ValueError("No valid audio provided")
        
        try:
            # Try Whisper first
            return self._transcribe_whisper(audio_path)
        except Exception as e:
            print(f"⚠️ Whisper failed: {e}, trying SpeechRecognition...")
            # Fallback to SpeechRecognition
            return self._transcribe_speech_recognition(audio_path)
    
    def _transcribe_whisper(self, audio_path: Path) -> str:
        """Transcribe using OpenAI Whisper (local)"""
        try:
            import whisper
            
            if self._whisper_model is None:
                print("🔄 Loading Whisper model (base)...")
                self._whisper_model = whisper.load_model("base")
                print("✅ Whisper model loaded")
            
            result = self._whisper_model.transcribe(str(audio_path))
            return result["text"].strip()
            
        except ImportError:
            raise ImportError("Whisper not installed. Run: pip install openai-whisper")
    
    def _transcribe_speech_recognition(self, audio_path: Path) -> str:
        """Transcribe using Google Speech Recognition API"""
        try:
            import speech_recognition as sr
            
            if self._recognizer is None:
                self._recognizer = sr.Recognizer()
            
            with sr.AudioFile(str(audio_path)) as source:
                audio = self._recognizer.record(source)
            
            text = self._recognizer.recognize_google(audio)
            return text.strip()
            
        except ImportError:
            raise ImportError("SpeechRecognition not installed")
        except sr.UnknownValueError:
            return "[Speech not recognized]"
        except sr.RequestError as e:
            return f"[Speech recognition error: {e}]"
    
    # ========== Text-to-Speech (TTS) ==========
    
    def text_to_speech(
        self, 
        text: str, 
        output_path: Path = None,
        return_bytes: bool = False
    ) -> Tuple[Optional[Path], Optional[bytes]]:
        """
        Convert text to speech
        
        Args:
            text: Text to convert
            output_path: Optional output file path
            return_bytes: Whether to return audio bytes
            
        Returns:
            Tuple of (output_path, audio_bytes)
        """
        if not self.voice_enabled:
            raise RuntimeError("Voice mode is disabled")
        
        if self.tts_provider == "gtts":
            return self._tts_gtts(text, output_path, return_bytes)
        else:
            # Default to gTTS
            return self._tts_gtts(text, output_path, return_bytes)
    
    def _tts_gtts(
        self, 
        text: str, 
        output_path: Path = None,
        return_bytes: bool = False
    ) -> Tuple[Optional[Path], Optional[bytes]]:
        """Text-to-speech using Google TTS"""
        try:
            from gtts import gTTS
            
            # Generate speech
            tts = gTTS(text=text, lang='en', slow=False)
            
            # Prepare output
            if output_path is None:
                output_path = self.audio_dir / f"speech_{hash(text) % 10000}.mp3"
            
            # Save to file
            tts.save(str(output_path))
            
            # Read bytes if requested
            audio_bytes = None
            if return_bytes:
                with open(output_path, 'rb') as f:
                    audio_bytes = f.read()
            
            return output_path, audio_bytes
            
        except ImportError:
            raise ImportError("gTTS not installed. Run: pip install gTTS")
    
    def speak_question(self, question: str) -> Tuple[Path, bytes]:
        """Speak a viva question"""
        return self.text_to_speech(
            f"Your question is: {question}",
            return_bytes=True
        )
    
    def speak_feedback(self, score: int, feedback: str) -> Tuple[Path, bytes]:
        """Speak evaluation feedback"""
        text = f"Your score is {score} out of 10. {feedback}"
        return self.text_to_speech(text, return_bytes=True)
    
    def audio_to_base64(self, audio_bytes: bytes) -> str:
        """Convert audio bytes to base64 for web transmission"""
        return base64.b64encode(audio_bytes).decode('utf-8')
    
    def base64_to_audio(self, base64_str: str) -> bytes:
        """Convert base64 string to audio bytes"""
        return base64.b64decode(base64_str)


# Singleton instance
_voice_engine: Optional[VoiceEngine] = None


def get_voice_engine() -> VoiceEngine:
    """Get voice engine instance"""
    global _voice_engine
    if _voice_engine is None:
        _voice_engine = VoiceEngine()
    return _voice_engine
