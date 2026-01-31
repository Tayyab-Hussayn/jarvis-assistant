#!/usr/bin/env python3
"""
JARVIS Configuration CLI - Manage configuration settings
"""

import sys
import argparse
import os
from pathlib import Path

# Add project root to path
sys.path.append('/home/krawin/exp.code/jarvis')

from core.config.config_manager import config_manager

class ConfigCLI:
    """Configuration management CLI"""
    
    def __init__(self):
        self.config_manager = config_manager
    
    def show_config(self, args):
        """Show current configuration"""
        try:
            config = self.config_manager.get_config()
            
            print("🔧 JARVIS Configuration")
            print("=" * 40)
            print(f"Environment: {self.config_manager.get_environment()}")
            print()
            
            print("📡 Temporal:")
            print(f"  Address: {config.temporal_address}")
            print(f"  Timeout: {config.temporal_timeout}s")
            print(f"  Task Queue: {config.temporal_task_queue}")
            print()
            
            print("🤖 LLM:")
            print(f"  Provider: {config.llm_provider}")
            print(f"  Model: {config.llm_model}")
            print(f"  API Key: {'***' if config.llm_api_key else 'Not Set'}")
            print(f"  Max Tokens: {config.llm_max_tokens}")
            print()
            
            print("💾 Database:")
            print(f"  URL: {config.database_url}")
            print(f"  Pool Size: {config.database_pool_size}")
            print()
            
            print("📧 Email:")
            print(f"  SMTP Server: {config.email_smtp_server}")
            print(f"  SMTP Port: {config.email_smtp_port}")
            print(f"  Username: {'***' if config.email_username else 'Not Set'}")
            print()
            
            print("🔊 Voice:")
            print(f"  TTS Enabled: {config.voice_tts_enabled}")
            print(f"  STT Enabled: {config.voice_stt_enabled}")
            print(f"  Speed: {config.voice_speed}")
            print()
            
            print("📊 Monitoring:")
            print(f"  Enabled: {config.monitoring_enabled}")
            print(f"  Log Level: {config.monitoring_log_level}")
            print(f"  Metrics Port: {config.monitoring_metrics_port}")
            print()
            
            print("🔒 Security:")
            print(f"  Sandbox Enabled: {config.security_sandbox_enabled}")
            print(f"  Max Execution Time: {config.security_max_execution_time}s")
            print(f"  Allowed Commands: {', '.join(config.security_allowed_commands)}")
            
        except Exception as e:
            print(f"❌ Error loading configuration: {e}")
    
    def validate_config(self, args):
        """Validate current configuration"""
        try:
            config = self.config_manager.load_config()
            is_valid = self.config_manager.validate_config()
            
            if is_valid:
                print("✅ Configuration is valid")
            else:
                print("❌ Configuration validation failed")
                return 1
                
        except Exception as e:
            print(f"❌ Error validating configuration: {e}")
            return 1
        
        return 0
    
    def set_environment(self, args):
        """Set environment"""
        env = args.environment.lower()
        valid_envs = ["development", "production", "testing"]
        
        if env not in valid_envs:
            print(f"❌ Invalid environment. Valid options: {', '.join(valid_envs)}")
            return 1
        
        os.environ["JARVIS_ENV"] = env
        print(f"✅ Environment set to: {env}")
        print("💡 To make this permanent, add 'export JARVIS_ENV={env}' to your ~/.bashrc")
        
        # Reload config with new environment
        self.config_manager.reload_config()
        print(f"🔄 Configuration reloaded for {env} environment")
        
        return 0
    
    def create_env_file(self, args):
        """Create .env file from template"""
        template_path = Path("/home/krawin/exp.code/jarvis/.env.template")
        env_path = Path("/home/krawin/exp.code/jarvis/.env")
        
        if env_path.exists() and not args.force:
            print(f"❌ .env file already exists. Use --force to overwrite.")
            return 1
        
        if not template_path.exists():
            print(f"❌ Template file not found: {template_path}")
            return 1
        
        try:
            # Copy template to .env
            with open(template_path, 'r') as template:
                content = template.read()
            
            with open(env_path, 'w') as env_file:
                env_file.write(content)
            
            print(f"✅ Created .env file: {env_path}")
            print("💡 Edit the .env file to set your configuration values")
            
        except Exception as e:
            print(f"❌ Error creating .env file: {e}")
            return 1
        
        return 0
    
    def test_config(self, args):
        """Test configuration by loading and validating"""
        print("🧪 Testing configuration...")
        
        try:
            # Test loading
            config = self.config_manager.load_config()
            print(f"✅ Config loaded for environment: {self.config_manager.get_environment()}")
            
            # Test validation
            is_valid = self.config_manager.validate_config()
            print(f"✅ Validation: {'PASSED' if is_valid else 'FAILED'}")
            
            # Test key components
            print("\n🔍 Component Tests:")
            
            # Test Temporal connection (basic)
            print(f"  Temporal Address: {config.temporal_address} ✅")
            
            # Test LLM config
            if config.llm_api_key:
                print(f"  LLM API Key: Set ✅")
            else:
                print(f"  LLM API Key: Not Set ⚠️")
            
            # Test database URL
            if config.database_url:
                print(f"  Database URL: Set ✅")
            else:
                print(f"  Database URL: Not Set ❌")
            
            print("\n🎯 Configuration test completed")
            
        except Exception as e:
            print(f"❌ Configuration test failed: {e}")
            return 1
        
        return 0

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="JARVIS Configuration Management")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Show config command
    subparsers.add_parser('show', help='Show current configuration')
    
    # Validate config command
    subparsers.add_parser('validate', help='Validate configuration')
    
    # Set environment command
    env_parser = subparsers.add_parser('set-env', help='Set environment')
    env_parser.add_argument('environment', choices=['development', 'production', 'testing'],
                           help='Environment to set')
    
    # Create .env file command
    env_file_parser = subparsers.add_parser('create-env', help='Create .env file from template')
    env_file_parser.add_argument('--force', action='store_true', help='Overwrite existing .env file')
    
    # Test config command
    subparsers.add_parser('test', help='Test configuration')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    cli = ConfigCLI()
    
    try:
        if args.command == 'show':
            return cli.show_config(args)
        elif args.command == 'validate':
            return cli.validate_config(args)
        elif args.command == 'set-env':
            return cli.set_environment(args)
        elif args.command == 'create-env':
            return cli.create_env_file(args)
        elif args.command == 'test':
            return cli.test_config(args)
    
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
