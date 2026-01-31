#!/usr/bin/env python3
"""
Audio File Manager - Professional audio file organization for JARVIS
"""

import os
import time
import asyncio
from pathlib import Path
from typing import Optional, List
from datetime import datetime, timedelta
import logging

class AudioFileManager:
    """Professional audio file management system"""
    
    def __init__(self, base_dir: str = "audio"):
        self.base_dir = Path(base_dir)
        self.tts_dir = self.base_dir / "tts"
        self.stt_dir = self.base_dir / "stt" 
        self.temp_dir = self.base_dir / "temp"
        
        # Configuration
        self.max_files_per_dir = 100
        self.max_age_hours = 24
        self.max_total_size_mb = 50
        
        self.logger = logging.getLogger("audio_manager")
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create audio directory structure"""
        for directory in [self.tts_dir, self.stt_dir, self.temp_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Audio directories initialized: {self.base_dir}")
    
    def generate_tts_filename(self, prefix: str = "jarvis_speech") -> str:
        """Generate unique TTS filename"""
        timestamp = int(time.time())
        filename = f"{prefix}_{timestamp}.mp3"
        return str(self.tts_dir / filename)
    
    def generate_stt_filename(self, prefix: str = "recorded_audio") -> str:
        """Generate unique STT filename"""
        timestamp = int(time.time())
        filename = f"{prefix}_{timestamp}.wav"
        return str(self.stt_dir / filename)
    
    def generate_temp_filename(self, prefix: str = "temp_audio", extension: str = "wav") -> str:
        """Generate unique temporary filename"""
        timestamp = int(time.time())
        filename = f"{prefix}_{timestamp}.{extension}"
        return str(self.temp_dir / filename)
    
    async def cleanup_old_files(self):
        """Clean up old audio files"""
        try:
            cutoff_time = time.time() - (self.max_age_hours * 3600)
            total_cleaned = 0
            
            # Clean each directory
            for directory in [self.tts_dir, self.stt_dir, self.temp_dir]:
                cleaned = await self._cleanup_directory(directory, cutoff_time)
                total_cleaned += cleaned
            
            if total_cleaned > 0:
                self.logger.info(f"Cleaned up {total_cleaned} old audio files")
            
            return total_cleaned
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
            return 0
    
    async def _cleanup_directory(self, directory: Path, cutoff_time: float) -> int:
        """Clean up files in specific directory"""
        if not directory.exists():
            return 0
        
        cleaned_count = 0
        audio_files = list(directory.glob("*.*"))
        
        # Sort by modification time (oldest first)
        audio_files.sort(key=lambda f: f.stat().st_mtime)
        
        # Remove old files
        for file in audio_files:
            try:
                if file.stat().st_mtime < cutoff_time:
                    file.unlink()
                    cleaned_count += 1
            except Exception as e:
                self.logger.warning(f"Failed to delete {file}: {e}")
        
        # Limit number of files per directory
        remaining_files = list(directory.glob("*.*"))
        if len(remaining_files) > self.max_files_per_dir:
            # Remove oldest files beyond limit
            remaining_files.sort(key=lambda f: f.stat().st_mtime)
            excess_files = remaining_files[:-self.max_files_per_dir]
            
            for file in excess_files:
                try:
                    file.unlink()
                    cleaned_count += 1
                except Exception as e:
                    self.logger.warning(f"Failed to delete excess file {file}: {e}")
        
        return cleaned_count
    
    def get_storage_stats(self) -> dict:
        """Get audio storage statistics"""
        stats = {
            "directories": {},
            "total_files": 0,
            "total_size_mb": 0.0
        }
        
        for dir_name, directory in [("tts", self.tts_dir), ("stt", self.stt_dir), ("temp", self.temp_dir)]:
            if directory.exists():
                files = list(directory.glob("*.*"))
                total_size = sum(f.stat().st_size for f in files)
                
                stats["directories"][dir_name] = {
                    "files": len(files),
                    "size_mb": total_size / (1024 * 1024),
                    "path": str(directory)
                }
                
                stats["total_files"] += len(files)
                stats["total_size_mb"] += total_size / (1024 * 1024)
        
        return stats
    
    async def cleanup_temp_files(self):
        """Clean up all temporary files immediately"""
        if not self.temp_dir.exists():
            return 0
        
        temp_files = list(self.temp_dir.glob("*.*"))
        cleaned = 0
        
        for file in temp_files:
            try:
                file.unlink()
                cleaned += 1
            except Exception as e:
                self.logger.warning(f"Failed to delete temp file {file}: {e}")
        
        if cleaned > 0:
            self.logger.info(f"Cleaned up {cleaned} temporary files")
        
        return cleaned
    
    def is_storage_limit_exceeded(self) -> bool:
        """Check if storage limit is exceeded"""
        stats = self.get_storage_stats()
        return stats["total_size_mb"] > self.max_total_size_mb
    
    async def enforce_storage_limits(self):
        """Enforce storage limits by cleaning old files"""
        if self.is_storage_limit_exceeded():
            self.logger.warning("Storage limit exceeded, cleaning up files...")
            
            # First cleanup temp files
            await self.cleanup_temp_files()
            
            # Then cleanup old files
            await self.cleanup_old_files()
            
            # If still over limit, remove more files
            if self.is_storage_limit_exceeded():
                await self._aggressive_cleanup()
    
    async def _aggressive_cleanup(self):
        """More aggressive cleanup when storage limits are exceeded"""
        for directory in [self.temp_dir, self.stt_dir, self.tts_dir]:
            if not directory.exists():
                continue
            
            files = list(directory.glob("*.*"))
            files.sort(key=lambda f: f.stat().st_mtime)
            
            # Remove oldest 50% of files
            files_to_remove = files[:len(files)//2]
            
            for file in files_to_remove:
                try:
                    file.unlink()
                except Exception as e:
                    self.logger.warning(f"Aggressive cleanup failed for {file}: {e}")
            
            # Check if we're under limit now
            if not self.is_storage_limit_exceeded():
                break

# Global audio file manager
audio_manager = AudioFileManager()
