"""
Voice Activity Detection (VAD) for real-time speech detection
"""

import numpy as np
import sounddevice as sd
import soundfile as sf
import tempfile
import os
import time
import logging
from typing import Optional

class VoiceActivityDetector:
    """Real-time voice activity detection"""
    
    def __init__(self, 
                 sample_rate: int = 16000,
                 chunk_size: int = 1024,
                 silence_threshold: float = 0.01,
                 silence_duration: float = 2.0):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        self.logger = logging.getLogger("voice_activity")
        
    def is_speech(self, audio_chunk: np.ndarray) -> bool:
        """Detect if audio chunk contains speech"""
        # Calculate RMS (Root Mean Square) energy
        rms = np.sqrt(np.mean(audio_chunk ** 2))
        return rms > self.silence_threshold
    
    async def record_with_vad(self) -> Optional[bytes]:
        """Record audio with voice activity detection"""
        try:
            self.logger.info("🎤 Listening... (speak anytime, will stop 2s after silence)")
            
            recorded_chunks = []
            silence_start = None
            is_recording = False
            
            # Start recording stream
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype=np.float32,
                blocksize=self.chunk_size
            ) as stream:
                
                while True:
                    # Read audio chunk
                    audio_chunk, overflowed = stream.read(self.chunk_size)
                    
                    if overflowed:
                        self.logger.warning("Audio buffer overflow")
                    
                    # Check for speech
                    has_speech = self.is_speech(audio_chunk.flatten())
                    
                    if has_speech:
                        # Speech detected
                        if not is_recording:
                            self.logger.info("🗣️  Speech detected, recording...")
                            is_recording = True
                        
                        # Reset silence timer
                        silence_start = None
                        recorded_chunks.append(audio_chunk.copy())
                        
                    else:
                        # Silence detected
                        if is_recording:
                            # Still add chunk (might be pause between words)
                            recorded_chunks.append(audio_chunk.copy())
                            
                            if silence_start is None:
                                # Start silence timer
                                silence_start = time.time()
                            else:
                                # Check if silence duration exceeded
                                silence_elapsed = time.time() - silence_start
                                if silence_elapsed >= self.silence_duration:
                                    self.logger.info("🔇 Silence detected, stopping recording")
                                    break
            
            if not recorded_chunks:
                self.logger.warning("No audio recorded")
                return None
            
            # Combine all chunks
            full_audio = np.concatenate(recorded_chunks, axis=0)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                sf.write(tmp_file.name, full_audio, self.sample_rate)
                tmp_path = tmp_file.name
            
            # Read as bytes
            with open(tmp_path, 'rb') as f:
                audio_bytes = f.read()
            
            # Cleanup
            try:
                os.unlink(tmp_path)
            except:
                pass
            
            duration = len(full_audio) / self.sample_rate
            self.logger.info(f"✅ Recorded {duration:.1f}s of audio ({len(audio_bytes)} bytes)")
            
            return audio_bytes
            
        except Exception as e:
            self.logger.error(f"VAD recording failed: {e}")
            return None

# Global VAD instance
voice_detector = VoiceActivityDetector()
