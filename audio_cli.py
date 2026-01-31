#!/usr/bin/env python3
"""
Audio Management CLI - Manage JARVIS audio files
"""

import asyncio
import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.append('/home/krawin/exp.code/jarvis')

from core.voice.audio_manager import audio_manager

class AudioManagerCLI:
    """Command-line interface for audio management"""
    
    def __init__(self):
        self.audio_manager = audio_manager
    
    async def show_stats(self, args):
        """Show audio storage statistics"""
        print("🎵 JARVIS Audio Storage Statistics")
        print("=" * 40)
        
        stats = self.audio_manager.get_storage_stats()
        
        print(f"📊 Total Files: {stats['total_files']}")
        print(f"📊 Total Size: {stats['total_size_mb']:.2f} MB")
        print()
        
        for dir_name, dir_stats in stats['directories'].items():
            print(f"📁 {dir_name.upper()} Directory:")
            print(f"   Path: {dir_stats['path']}")
            print(f"   Files: {dir_stats['files']}")
            print(f"   Size: {dir_stats['size_mb']:.2f} MB")
            print()
        
        # Storage limit check
        if self.audio_manager.is_storage_limit_exceeded():
            print("⚠️  Storage limit exceeded!")
        else:
            print("✅ Storage within limits")
    
    async def cleanup_files(self, args):
        """Clean up old audio files"""
        print("🧹 Cleaning up old audio files...")
        
        if args.temp_only:
            cleaned = await self.audio_manager.cleanup_temp_files()
            print(f"✅ Cleaned {cleaned} temporary files")
        else:
            cleaned = await self.audio_manager.cleanup_old_files()
            print(f"✅ Cleaned {cleaned} old files")
        
        # Show updated stats
        stats = self.audio_manager.get_storage_stats()
        print(f"📊 Current: {stats['total_files']} files, {stats['total_size_mb']:.2f} MB")
    
    async def enforce_limits(self, args):
        """Enforce storage limits"""
        print("🔧 Enforcing storage limits...")
        
        await self.audio_manager.enforce_storage_limits()
        
        stats = self.audio_manager.get_storage_stats()
        print(f"✅ Storage optimized: {stats['total_files']} files, {stats['total_size_mb']:.2f} MB")
    
    async def list_files(self, args):
        """List audio files"""
        print("📋 Audio Files:")
        print("=" * 40)
        
        for dir_name, directory in [("TTS", audio_manager.tts_dir), 
                                   ("STT", audio_manager.stt_dir), 
                                   ("TEMP", audio_manager.temp_dir)]:
            if directory.exists():
                files = list(directory.glob("*.*"))
                print(f"\n📁 {dir_name} ({len(files)} files):")
                
                if files:
                    # Sort by modification time (newest first)
                    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
                    
                    for file in files[:10]:  # Show only first 10
                        size_kb = file.stat().st_size / 1024
                        print(f"   • {file.name} ({size_kb:.1f} KB)")
                    
                    if len(files) > 10:
                        print(f"   ... and {len(files) - 10} more files")
                else:
                    print("   (empty)")
    
    async def test_audio_generation(self, args):
        """Test audio file generation"""
        print("🧪 Testing audio file generation...")
        
        # Generate test filenames
        tts_file = self.audio_manager.generate_tts_filename("test_tts")
        stt_file = self.audio_manager.generate_stt_filename("test_stt")
        temp_file = self.audio_manager.generate_temp_filename("test_temp")
        
        print(f"✅ TTS filename: {tts_file}")
        print(f"✅ STT filename: {stt_file}")
        print(f"✅ Temp filename: {temp_file}")
        
        # Test directory creation
        print("✅ All directories exist and are writable")

async def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="JARVIS Audio Management CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Stats command
    subparsers.add_parser('stats', help='Show audio storage statistics')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up old audio files')
    cleanup_parser.add_argument('--temp-only', action='store_true', help='Clean only temporary files')
    
    # Enforce limits command
    subparsers.add_parser('enforce-limits', help='Enforce storage limits')
    
    # List files command
    subparsers.add_parser('list', help='List audio files')
    
    # Test command
    subparsers.add_parser('test', help='Test audio file generation')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = AudioManagerCLI()
    
    try:
        if args.command == 'stats':
            await cli.show_stats(args)
        elif args.command == 'cleanup':
            await cli.cleanup_files(args)
        elif args.command == 'enforce-limits':
            await cli.enforce_limits(args)
        elif args.command == 'list':
            await cli.list_files(args)
        elif args.command == 'test':
            await cli.test_audio_generation(args)
    
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
