#!/usr/bin/env python3
"""
JARVIS Configuration Management System
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import re

@dataclass
class JarvisConfig:
    """JARVIS configuration data class"""
    
    # Temporal settings
    temporal_address: str
    temporal_timeout: int
    temporal_task_queue: str
    
    # LLM settings
    llm_provider: str
    llm_api_key: str
    llm_model: str
    llm_max_tokens: int
    
    # Database settings
    database_url: str
    database_pool_size: int
    
    # Email settings
    email_smtp_server: str
    email_smtp_port: int
    email_username: str
    email_password: str
    
    # Voice settings
    voice_tts_enabled: bool
    voice_stt_enabled: bool
    voice_speed: float
    
    # Monitoring settings
    monitoring_enabled: bool
    monitoring_log_level: str
    monitoring_metrics_port: int
    
    # Security settings
    security_allowed_commands: list
    security_sandbox_enabled: bool
    security_max_execution_time: int

class ConfigManager:
    """Configuration management system"""
    
    def __init__(self):
        self.config: Optional[JarvisConfig] = None
        self.environment = self._detect_environment()
        self.config_dir = Path(__file__).parent.parent / "config"
        self.logger = logging.getLogger("config_manager")
    
    def _detect_environment(self) -> str:
        """Detect current environment"""
        env = os.getenv("JARVIS_ENV", "development").lower()
        
        # Validate environment
        valid_envs = ["development", "production", "testing"]
        if env not in valid_envs:
            self.logger.warning(f"Invalid environment '{env}', defaulting to 'development'")
            env = "development"
        
        return env
    
    def _substitute_env_vars(self, value: Any) -> Any:
        """Substitute environment variables in config values"""
        if isinstance(value, str):
            # Find ${VAR_NAME} patterns
            pattern = r'\$\{([^}]+)\}'
            matches = re.findall(pattern, value)
            
            for var_name in matches:
                env_value = os.getenv(var_name)
                if env_value is None:
                    self.logger.warning(f"Environment variable '{var_name}' not found")
                    env_value = ""
                value = value.replace(f"${{{var_name}}}", env_value)
            
            return value
        
        elif isinstance(value, dict):
            return {k: self._substitute_env_vars(v) for k, v in value.items()}
        
        elif isinstance(value, list):
            return [self._substitute_env_vars(item) for item in value]
        
        return value
    
    def load_config(self) -> JarvisConfig:
        """Load configuration for current environment"""
        
        config_file = self.config_dir / "environments" / f"{self.environment}.yaml"
        
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_file}")
        
        try:
            with open(config_file, 'r') as f:
                raw_config = yaml.safe_load(f)
            
            # Substitute environment variables
            config_data = self._substitute_env_vars(raw_config)
            
            # Create config object
            self.config = JarvisConfig(
                # Temporal
                temporal_address=config_data["temporal"]["address"],
                temporal_timeout=config_data["temporal"]["timeout"],
                temporal_task_queue=config_data["temporal"]["task_queue"],
                
                # LLM
                llm_provider=config_data["llm"]["provider"],
                llm_api_key=config_data["llm"]["api_key"],
                llm_model=config_data["llm"]["model"],
                llm_max_tokens=config_data["llm"]["max_tokens"],
                
                # Database
                database_url=config_data["database"]["url"],
                database_pool_size=config_data["database"]["pool_size"],
                
                # Email
                email_smtp_server=config_data["email"]["smtp_server"],
                email_smtp_port=config_data["email"]["smtp_port"],
                email_username=config_data["email"]["username"],
                email_password=config_data["email"]["password"],
                
                # Voice
                voice_tts_enabled=config_data["voice"]["tts_enabled"],
                voice_stt_enabled=config_data["voice"]["stt_enabled"],
                voice_speed=config_data["voice"]["voice_speed"],
                
                # Monitoring
                monitoring_enabled=config_data["monitoring"]["enabled"],
                monitoring_log_level=config_data["monitoring"]["log_level"],
                monitoring_metrics_port=config_data["monitoring"]["metrics_port"],
                
                # Security
                security_allowed_commands=config_data["security"]["allowed_commands"],
                security_sandbox_enabled=config_data["security"]["sandbox_enabled"],
                security_max_execution_time=config_data["security"]["max_execution_time"]
            )
            
            self.logger.info(f"✅ Configuration loaded for environment: {self.environment}")
            return self.config
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load configuration: {e}")
            raise
    
    def validate_config(self) -> bool:
        """Validate configuration"""
        if not self.config:
            return False
        
        errors = []
        
        # Validate required fields
        if not self.config.temporal_address:
            errors.append("Temporal address is required")
        
        if not self.config.llm_provider:
            errors.append("LLM provider is required")
        
        if not self.config.database_url:
            errors.append("Database URL is required")
        
        # Validate numeric values
        if self.config.temporal_timeout <= 0:
            errors.append("Temporal timeout must be positive")
        
        if self.config.llm_max_tokens <= 0:
            errors.append("LLM max tokens must be positive")
        
        # Validate security settings
        if not self.config.security_allowed_commands:
            errors.append("At least one allowed command is required")
        
        if errors:
            for error in errors:
                self.logger.error(f"❌ Config validation error: {error}")
            return False
        
        self.logger.info("✅ Configuration validation passed")
        return True
    
    def get_config(self) -> JarvisConfig:
        """Get current configuration"""
        if not self.config:
            self.load_config()
        return self.config
    
    def reload_config(self) -> JarvisConfig:
        """Reload configuration"""
        self.config = None
        return self.load_config()
    
    def get_environment(self) -> str:
        """Get current environment"""
        return self.environment
    
    def print_config_summary(self):
        """Print configuration summary"""
        if not self.config:
            self.load_config()
        
        print(f"🔧 JARVIS Configuration Summary")
        print(f"Environment: {self.environment}")
        print(f"Temporal: {self.config.temporal_address}")
        print(f"LLM Provider: {self.config.llm_provider}")
        print(f"Database: {self.config.database_url}")
        print(f"Monitoring: {'Enabled' if self.config.monitoring_enabled else 'Disabled'}")
        print(f"Security: {'Sandbox Enabled' if self.config.security_sandbox_enabled else 'Sandbox Disabled'}")

# Global configuration manager
config_manager = ConfigManager()
