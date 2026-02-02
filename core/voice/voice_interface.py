#!/usr/bin/env python3
"""
Voice Integration - TTS/STT for JARVIS
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from pathlib import Path
import json
from .speech_cleaner import speech_cleaner
from .audio_manager import audio_manager
from .multi_stt import MultiProviderSTT, STTConfig, STTProvider

@dataclass
class VoiceConfig:
    """Voice configuration"""
    tts_provider: str = "edge"  # edge, google, openai
    stt_provider: str = "google"  # google, whisper, azure
    voice_name: str = "en-GB-RyanNeural"
    speech_rate: str = "+0%"
    speech_pitch: str = "-5Hz"
    language: str = "en-US"
    
class TTSEngine:
    """Text-to-Speech engine"""
    
    def __init__(self, config: VoiceConfig):
        self.config = config
        self.logger = logging.getLogger("tts_engine")
    
    async def speak_text(self, text: str, output_file: Optional[str] = None) -> Union[str, bytes]:
        """Convert text to speech"""
        
        if self.config.tts_provider == "edge":
            return await self._edge_tts(text, output_file)
        elif self.config.tts_provider == "google":
            return await self._google_tts(text, output_file)
        elif self.config.tts_provider == "openai":
            return await self._openai_tts(text, output_file)
        else:
            raise ValueError(f"Unknown TTS provider: {self.config.tts_provider}")
    
    async def _edge_tts(self, text: str, output_file: Optional[str] = None) -> Union[str, bytes]:
        """Microsoft Edge TTS (free)"""
        try:
            import edge_tts
            
            communicate = edge_tts.Communicate(
                text=text,
                voice=self.config.voice_name,
                rate=self.config.speech_rate,
                pitch=self.config.speech_pitch
            )
            
            if output_file:
                await communicate.save(output_file)
                self.logger.info(f"Speech saved to: {output_file}")
                return output_file
            else:
                # Return audio bytes
                audio_bytes = b""
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_bytes += chunk["data"]
                
                self.logger.info(f"Generated speech: {len(audio_bytes)} bytes")
                return audio_bytes
                
        except ImportError:
            self.logger.error("edge-tts not installed. Run: pip install edge-tts")
            raise
        except Exception as e:
            self.logger.error(f"Edge TTS failed: {e}")
            raise
    
    async def _google_tts(self, text: str, output_file: Optional[str] = None) -> Union[str, bytes]:
        """Google Cloud TTS"""
        try:
            from google.cloud import texttospeech
            
            client = texttospeech.TextToSpeechClient()
            
            synthesis_input = texttospeech.SynthesisInput(text=text)
            voice = texttospeech.VoiceSelectionParams(
                language_code=self.config.language,
                ssml_gender=texttospeech.SsmlVoiceGender.MALE
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )
            
            response = client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            if output_file:
                with open(output_file, "wb") as f:
                    f.write(response.audio_content)
                return output_file
            else:
                return response.audio_content
                
        except ImportError:
            self.logger.error("google-cloud-texttospeech not installed")
            raise
        except Exception as e:
            self.logger.error(f"Google TTS failed: {e}")
            raise
    
    async def _openai_tts(self, text: str, output_file: Optional[str] = None) -> Union[str, bytes]:
        """OpenAI TTS"""
        try:
            import openai
            
            client = openai.AsyncOpenAI()
            
            response = await client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=text
            )
            
            audio_bytes = response.content
            
            if output_file:
                with open(output_file, "wb") as f:
                    f.write(audio_bytes)
                return output_file
            else:
                return audio_bytes
                
        except ImportError:
            self.logger.error("openai not installed")
            raise
        except Exception as e:
            self.logger.error(f"OpenAI TTS failed: {e}")
            raise



class VoiceInterface:
    """Main voice interface for JARVIS"""
    
    def __init__(self, config: Optional[VoiceConfig] = None):
        self.config = config or VoiceConfig()
        self.logger = logging.getLogger("voice_interface")
        
        self.tts_engine = TTSEngine(self.config)
        
        # Create STT configuration
        stt_config = STTConfig(
            primary_provider=STTProvider.SPEECH_RECOGNITION,
            fallback_providers=[STTProvider.WHISPER_LOCAL, STTProvider.GOOGLE_CLOUD],
            language=self.config.language
        )
        self.stt_engine = MultiProviderSTT(stt_config)
        
        self.conversation_mode = False
    
    async def speak(self, text: str, save_file: bool = False) -> Optional[str]:
        """Speak text using TTS"""
        try:
            # Clean text for natural speech
            cleaned_text = speech_cleaner.clean_for_speech(text)
            
            if save_file:
                # Use audio manager for organized file storage
                output_file = audio_manager.generate_tts_filename()
                result = await self.tts_engine.speak_text(cleaned_text, output_file)
                self.logger.info(f"JARVIS spoke: '{text[:50]}...' -> saved to {result}")
                
                # Cleanup old files periodically
                await audio_manager.cleanup_old_files()
                return result
            else:
                audio_bytes = await self.tts_engine.speak_text(cleaned_text)
                self.logger.info(f"JARVIS spoke: '{text[:50]}...' ({len(audio_bytes)} bytes)")
                
                # Play audio bytes through speakers
                await self._play_audio_bytes(audio_bytes)
                return None
                
        except Exception as e:
            self.logger.error(f"Speech failed: {e}")
            return None
    
    async def _play_audio_bytes(self, audio_bytes: bytes):
        """Play audio bytes through speakers"""
        try:
            import sounddevice as sd
            import soundfile as sf
            import tempfile
            import os
            from pathlib import Path
            
            # Save audio bytes to temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
                tmp_file.write(audio_bytes)
                tmp_path = tmp_file.name
            
            try:
                # Read audio file and play
                data, sample_rate = sf.read(tmp_path)
                sd.play(data, sample_rate)
                sd.wait()  # Wait for playback to complete
                self.logger.info("🔊 Audio playback completed")
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(tmp_path)
                except:
                    pass
                    
        except ImportError:
            self.logger.error("sounddevice/soundfile required for audio playback")
        except Exception as e:
            self.logger.error(f"Audio playback failed: {e}")
    
    async def listen(self, duration: int = 2) -> str:
        """Listen for speech and convert to text"""
        try:
            text = await self.stt_engine.transcribe_microphone(duration)
            self.logger.info(f"Heard: '{text}'")
            return text
            
        except Exception as e:
            self.logger.error(f"Listening failed: {e}")
            return ""
    
    async def transcribe_file(self, audio_file: str) -> str:
        """Transcribe audio file to text"""
        try:
            # For now, use microphone transcription method
            # TODO: Implement file-based transcription in MultiProviderSTT
            self.logger.warning("File transcription not yet implemented in MultiProviderSTT")
            return ""
            
        except Exception as e:
            self.logger.error(f"Transcription failed: {e}")
            return ""
    
    async def voice_conversation(self, llm_manager, session_id: str = "voice_session"):
        """Start voice conversation with JARVIS"""
        
        self.conversation_mode = True
        self.logger.info("Starting voice conversation mode...")
        
        await self.speak("Hello! I'm JARVIS. I'm ready for voice conversation. Say something!")
        
        try:
            while self.conversation_mode:
                # Listen for user input
                print("🎤 Listening... (speak now)")
                user_speech = await self.listen(duration=2)
                
                if not user_speech.strip():
                    await self.speak("I didn't hear anything. Please try again.")
                    continue
                
                if "goodbye" in user_speech.lower() or "exit" in user_speech.lower():
                    await self.speak("Goodbye! It was nice talking with you.")
                    break
                
                print(f"👤 You said: {user_speech}")
                
                # Get LLM response
                try:
                    llm_response = await llm_manager.generate(
                        prompt=user_speech,
                        system_prompt="You are JARVIS, an AI assistant. Keep responses conversational and under 100 words for voice interaction."
                    )
                    
                    response_text = llm_response.content
                    print(f"🤖 JARVIS: {response_text}")
                    
                    # Speak response
                    await self.speak(response_text)
                    
                except Exception as e:
                    error_msg = "I'm having trouble processing that. Could you try again?"
                    print(f"❌ Error: {e}")
                    await self.speak(error_msg)
        
        except KeyboardInterrupt:
            await self.speak("Voice conversation ended.")
        finally:
            # Clean up LLM sessions
            try:
                await llm_manager.cleanup()
            except:
                pass
        
        self.conversation_mode = False
    
    def stop_conversation(self):
        """Stop voice conversation"""
        self.conversation_mode = False

# Global voice interface
voice_interface = VoiceInterface()
