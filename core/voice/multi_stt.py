"""
Multi-provider Speech-to-Text (STT) system with fallback support
"""

import logging
import asyncio
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum

class STTProvider(Enum):
    """Available STT providers"""
    WHISPER_LOCAL = "whisper_local"
    GOOGLE_CLOUD = "google_cloud"
    AZURE = "azure"
    OPENAI_WHISPER = "openai_whisper"
    SPEECH_RECOGNITION = "speech_recognition"

@dataclass
class STTConfig:
    """STT configuration"""
    primary_provider: STTProvider = STTProvider.SPEECH_RECOGNITION
    fallback_providers: List[STTProvider] = None
    timeout: int = 10
    language: str = "en-US"
    
    def __post_init__(self):
        if self.fallback_providers is None:
            self.fallback_providers = [
                STTProvider.WHISPER_LOCAL,
                STTProvider.SPEECH_RECOGNITION
            ]

class BaseSTTProvider(ABC):
    """Base class for STT providers"""
    
    def __init__(self, config: STTConfig):
        self.config = config
        self.logger = logging.getLogger(f"stt_{self.__class__.__name__.lower()}")
        self._available = None
    
    @abstractmethod
    async def transcribe_audio(self, audio_data: bytes) -> str:
        """Transcribe audio bytes to text"""
        pass
    
    @abstractmethod
    async def transcribe_microphone(self, duration: int = 5) -> str:
        """Record from microphone and transcribe"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available"""
        pass
    
    def get_name(self) -> str:
        """Get provider name"""
        return self.__class__.__name__.replace("STTProvider", "").lower()

class SpeechRecognitionSTT(BaseSTTProvider):
    """Speech Recognition library STT (offline fallback)"""
    
    def is_available(self) -> bool:
        if self._available is None:
            try:
                import speech_recognition as sr
                import sounddevice as sd
                import soundfile as sf
                self._available = True
                self.logger.info("✅ SpeechRecognition STT available")
            except ImportError as e:
                self._available = False
                self.logger.warning(f"❌ SpeechRecognition STT not available: {e}")
        return self._available
    
    async def transcribe_microphone(self, duration: int = 5) -> str:
        """Record and transcribe using speech_recognition"""
        if not self.is_available():
            raise RuntimeError("speech_recognition not available")
        
        try:
            import speech_recognition as sr
            from .voice_activity_detector import voice_detector
            
            # Use VAD for recording
            self.logger.info("🎤 Using voice activity detection...")
            audio_bytes = await voice_detector.record_with_vad()
            
            if not audio_bytes:
                self.logger.warning("No audio recorded")
                return ""
            
            # Save audio bytes to temp file for speech_recognition
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                tmp_file.write(audio_bytes)
                tmp_path = tmp_file.name
            
            try:
                # Use speech_recognition to transcribe
                recognizer = sr.Recognizer()
                
                # Adjust for ambient noise
                with sr.AudioFile(tmp_path) as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = recognizer.record(source)
                
                # Try Google Web Speech API first (free tier)
                try:
                    text = recognizer.recognize_google(audio, language=self.config.language)
                    if text.strip():
                        self.logger.info(f"✅ Google Web Speech: '{text}'")
                        return text.strip()
                except sr.UnknownValueError:
                    self.logger.warning("Google Web Speech could not understand audio")
                except sr.RequestError as e:
                    self.logger.warning(f"Google Web Speech error: {e}")
                
                # Fallback to offline Sphinx (if available)
                try:
                    text = recognizer.recognize_sphinx(audio)
                    if text.strip():
                        self.logger.info(f"✅ Sphinx offline: '{text}'")
                        return text.strip()
                except sr.UnknownValueError:
                    self.logger.warning("Sphinx could not understand audio")
                except sr.RequestError as e:
                    self.logger.warning(f"Sphinx error: {e}")
                
                self.logger.warning("No speech recognized by any method")
                return ""
                
            finally:
                # Clean up temp file
                try:
                    os.unlink(tmp_path)
                except:
                    pass
                
        except Exception as e:
            self.logger.error(f"Speech recognition failed: {e}")
            import traceback
            self.logger.debug(f"Full traceback: {traceback.format_exc()}")
            return ""
    
    async def transcribe_audio(self, audio_data: bytes) -> str:
        """Transcribe audio bytes"""
        # Implementation for audio bytes transcription
        return ""

class WhisperLocalSTT(BaseSTTProvider):
    """Local Whisper STT"""
    
    def is_available(self) -> bool:
        if self._available is None:
            try:
                import whisper
                self._available = True
                self.logger.info("✅ Whisper STT available")
            except ImportError as e:
                self._available = False
                self.logger.warning(f"❌ Whisper STT not available: {e}")
        return self._available
    
    async def transcribe_microphone(self, duration: int = 5) -> str:
        """Record and transcribe using local Whisper"""
        if not self.is_available():
            raise RuntimeError("whisper not available")
        
        try:
            import whisper
            import sounddevice as sd
            import soundfile as sf
            import numpy as np
            import tempfile
            import os
            
            # Load model (cache it)
            if not hasattr(self, '_model'):
                self._model = whisper.load_model("base")
            
            # Record audio
            sample_rate = 16000
            self.logger.info(f"🎤 Recording for {duration} seconds...")
            audio_data = sd.rec(int(duration * sample_rate), 
                              samplerate=sample_rate, 
                              channels=1, dtype=np.float32)
            sd.wait()
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                sf.write(tmp_file.name, audio_data, sample_rate)
                tmp_path = tmp_file.name
            
            try:
                # Transcribe using Whisper
                result = self._model.transcribe(tmp_path)
                text = result["text"].strip()
                self.logger.info(f"✅ Whisper transcribed: '{text}'")
                return text
            finally:
                os.unlink(tmp_path)
                
        except Exception as e:
            self.logger.error(f"Whisper transcription failed: {e}")
            return ""
    
    async def transcribe_audio(self, audio_data: bytes) -> str:
        """Transcribe audio bytes"""
        # Implementation for audio bytes transcription
        return ""

class GoogleCloudSTT(BaseSTTProvider):
    """Google Cloud Speech-to-Text"""
    
    def is_available(self) -> bool:
        if self._available is None:
            try:
                from google.cloud import speech
                import os
                # Check for credentials
                has_credentials = bool(
                    os.getenv('GOOGLE_APPLICATION_CREDENTIALS') or
                    os.getenv('GOOGLE_CLOUD_PROJECT')
                )
                self._available = has_credentials
                if has_credentials:
                    self.logger.info("✅ Google Cloud STT available")
                else:
                    self.logger.warning("❌ Google Cloud STT: No credentials found")
            except ImportError as e:
                self._available = False
                self.logger.warning(f"❌ Google Cloud STT not available: {e}")
        return self._available
    
    async def transcribe_microphone(self, duration: int = 5) -> str:
        """Record and transcribe using Google Cloud"""
        if not self.is_available():
            raise RuntimeError("Google Cloud STT not available")
        
        try:
            from google.cloud import speech
            import sounddevice as sd
            import soundfile as sf
            import numpy as np
            
            # Record audio
            sample_rate = 16000
            self.logger.info(f"🎤 Recording for {duration} seconds...")
            audio_data = sd.rec(int(duration * sample_rate), 
                              samplerate=sample_rate, 
                              channels=1, dtype=np.float32)
            sd.wait()
            
            # Convert to bytes
            audio_bytes = (audio_data * 32767).astype(np.int16).tobytes()
            
            # Transcribe
            client = speech.SpeechClient()
            audio = speech.RecognitionAudio(content=audio_bytes)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=sample_rate,
                language_code=self.config.language,
            )
            
            response = client.recognize(config=config, audio=audio)
            
            if response.results:
                text = response.results[0].alternatives[0].transcript
                self.logger.info(f"✅ Google Cloud transcribed: '{text}'")
                return text
            else:
                return ""
                
        except Exception as e:
            self.logger.error(f"Google Cloud STT failed: {e}")
            return ""
    
    async def transcribe_audio(self, audio_data: bytes) -> str:
        """Transcribe audio bytes"""
        # Implementation for audio bytes transcription
        return ""

class MultiProviderSTT:
    """Multi-provider STT with automatic fallback"""
    
    def __init__(self, config: STTConfig = None):
        self.config = config or STTConfig()
        self.logger = logging.getLogger("multi_stt")
        
        # Initialize providers
        self.providers = {
            STTProvider.SPEECH_RECOGNITION: SpeechRecognitionSTT(self.config),
            STTProvider.WHISPER_LOCAL: WhisperLocalSTT(self.config),
            STTProvider.GOOGLE_CLOUD: GoogleCloudSTT(self.config),
        }
        
        # Check available providers
        self.available_providers = []
        for provider_type, provider in self.providers.items():
            if provider.is_available():
                self.available_providers.append(provider_type)
                self.logger.info(f"✅ {provider.get_name()} STT available")
            else:
                self.logger.warning(f"❌ {provider.get_name()} STT not available")
    
    async def transcribe_microphone(self, duration: int = 2) -> str:
        """Transcribe microphone input with fallback"""
        
        # Try primary provider first
        if self.config.primary_provider in self.available_providers:
            try:
                provider = self.providers[self.config.primary_provider]
                result = await provider.transcribe_microphone(duration)
                if result.strip():
                    return result
            except Exception as e:
                self.logger.warning(f"Primary provider {self.config.primary_provider} failed: {e}")
        
        # Try fallback providers
        for fallback_provider in self.config.fallback_providers:
            if fallback_provider in self.available_providers:
                try:
                    provider = self.providers[fallback_provider]
                    self.logger.info(f"🔄 Trying fallback: {provider.get_name()}")
                    result = await provider.transcribe_microphone(duration)
                    if result.strip():
                        return result
                except Exception as e:
                    self.logger.warning(f"Fallback provider {fallback_provider} failed: {e}")
        
        self.logger.error("All STT providers failed")
        return ""
    
    def get_status(self) -> Dict[str, Any]:
        """Get STT system status"""
        return {
            "primary_provider": self.config.primary_provider.value,
            "available_providers": [p.value for p in self.available_providers],
            "fallback_providers": [p.value for p in self.config.fallback_providers],
            "total_providers": len(self.providers),
            "working_providers": len(self.available_providers)
        }

# Convenience function
def create_stt_engine(config: STTConfig = None) -> MultiProviderSTT:
    """Create STT engine with default configuration"""
    return MultiProviderSTT(config)
