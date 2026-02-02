"""
Qwen OAuth Authentication Manager
Professional implementation for Qwen cloud API with token management
"""

import json
import time
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class QwenOAuthToken:
    """Qwen OAuth token data"""
    access_token: str
    token_type: str
    refresh_token: str
    resource_url: str
    expiry_date: int
    
    @property
    def is_expired(self) -> bool:
        """Check if token is expired (with 5 minute buffer)"""
        current_time = int(time.time() * 1000)  # Convert to milliseconds
        buffer_time = 5 * 60 * 1000  # 5 minutes in milliseconds
        return current_time >= (self.expiry_date - buffer_time)
    
    @property
    def authorization_header(self) -> str:
        """Get authorization header value"""
        return f"{self.token_type} {self.access_token}"

class QwenAuthManager:
    """Manages Qwen OAuth authentication and token refresh"""
    
    def __init__(self, creds_path: str = "/home/krawin/.qwen/oauth_creds.json"):
        self.creds_path = Path(creds_path)
        self.logger = logging.getLogger("qwen_auth")
        self._token: Optional[QwenOAuthToken] = None
        
    def load_token(self) -> Optional[QwenOAuthToken]:
        """Load OAuth token from credentials file"""
        try:
            if not self.creds_path.exists():
                self.logger.error(f"Qwen credentials file not found: {self.creds_path}")
                return None
            
            with open(self.creds_path, 'r') as f:
                creds_data = json.load(f)
            
            token = QwenOAuthToken(
                access_token=creds_data["access_token"],
                token_type=creds_data["token_type"],
                refresh_token=creds_data["refresh_token"],
                resource_url=creds_data["resource_url"],
                expiry_date=creds_data["expiry_date"]
            )
            
            self._token = token
            self.logger.info("✅ Qwen OAuth token loaded successfully")
            
            if token.is_expired:
                self.logger.warning("⚠️ Qwen token is expired, refresh needed")
            
            return token
            
        except Exception as e:
            self.logger.error(f"Failed to load Qwen token: {e}")
            return None
    
    def get_valid_token(self) -> Optional[QwenOAuthToken]:
        """Get a valid (non-expired) token"""
        if not self._token:
            self._token = self.load_token()
        
        if not self._token:
            return None
        
        if self._token.is_expired:
            self.logger.warning("Token expired, attempting refresh...")
            # TODO: Implement token refresh logic
            # For now, reload from file (assuming external refresh)
            self._token = self.load_token()
        
        return self._token
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests"""
        token = self.get_valid_token()
        if not token:
            raise ValueError("No valid Qwen authentication token available")
        
        return {
            "Authorization": token.authorization_header,
            "Content-Type": "application/json"
        }
    
    def is_authenticated(self) -> bool:
        """Check if we have valid authentication"""
        token = self.get_valid_token()
        return token is not None and not token.is_expired
    
    def get_base_url(self) -> str:
        """Get the base URL for API requests"""
        token = self.get_valid_token()
        if not token:
            raise ValueError("No valid token to determine base URL")
        
        # Return base URL without /chat/completions (will be added by client)
        return f"https://{token.resource_url}/v1"

# Global auth manager instance
qwen_auth = QwenAuthManager()
