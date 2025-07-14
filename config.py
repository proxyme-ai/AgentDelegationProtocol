"""Configuration management for Agent Delegation Protocol."""

import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class Config:
    """Application configuration."""
    
    # JWT Configuration
    jwt_secret: str = os.environ.get("JWT_SECRET", "jwt-signing-secret")
    jwt_algorithm: str = "HS256"
    
    # Token Expiry (in minutes)
    access_token_expiry: int = int(os.environ.get("ACCESS_TOKEN_EXPIRY_MINUTES", "5"))
    delegation_token_expiry: int = int(os.environ.get("DELEGATION_TOKEN_EXPIRY_MINUTES", "10"))
    
    # File Storage
    agents_file: str = os.environ.get("AGENTS_FILE", "agents.json")
    users_file: str = os.environ.get("USERS_FILE", "users.json")
    
    # Server Configuration
    auth_server_host: str = os.environ.get("AUTH_SERVER_HOST", "localhost")
    auth_server_port: int = int(os.environ.get("AUTH_SERVER_PORT", "5000"))
    resource_server_host: str = os.environ.get("RESOURCE_SERVER_HOST", "localhost")
    resource_server_port: int = int(os.environ.get("RESOURCE_SERVER_PORT", "6000"))
    frontend_port: int = int(os.environ.get("FRONTEND_PORT", "7000"))
    
    # Keycloak Integration
    keycloak_url: Optional[str] = os.environ.get("KEYCLOAK_URL")
    keycloak_realm: str = os.environ.get("KEYCLOAK_REALM", "master")
    keycloak_client_id: Optional[str] = os.environ.get("KEYCLOAK_CLIENT_ID")
    keycloak_client_secret: Optional[str] = os.environ.get("KEYCLOAK_CLIENT_SECRET")
    redirect_uri: str = os.environ.get("REDIRECT_URI", "http://localhost:5000/callback")
    
    # Security Settings
    cors_origins: list = os.environ.get("CORS_ORIGINS", "").split(",") if os.environ.get("CORS_ORIGINS") else []
    rate_limit_per_minute: int = int(os.environ.get("RATE_LIMIT_PER_MINUTE", "60"))
    
    # Logging
    log_level: str = os.environ.get("LOG_LEVEL", "INFO")
    log_format: str = os.environ.get("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    @property
    def auth_server_url(self) -> str:
        """Get the full auth server URL."""
        return f"http://{self.auth_server_host}:{self.auth_server_port}"
    
    @property
    def resource_server_url(self) -> str:
        """Get the full resource server URL."""
        return f"http://{self.resource_server_host}:{self.resource_server_port}"
    
    @property
    def is_keycloak_enabled(self) -> bool:
        """Check if Keycloak integration is enabled."""
        return bool(self.keycloak_url and self.keycloak_client_id and self.keycloak_client_secret)
    
    def validate(self) -> None:
        """Validate configuration."""
        if len(self.jwt_secret) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters long")
        
        if self.access_token_expiry <= 0:
            raise ValueError("ACCESS_TOKEN_EXPIRY_MINUTES must be positive")
        
        if self.delegation_token_expiry <= 0:
            raise ValueError("DELEGATION_TOKEN_EXPIRY_MINUTES must be positive")
        
        if self.keycloak_url and not self.keycloak_client_id:
            raise ValueError("KEYCLOAK_CLIENT_ID required when KEYCLOAK_URL is set")


# Global configuration instance
config = Config()

# Validate configuration on import
try:
    config.validate()
except ValueError as e:
    print(f"Configuration error: {e}")
    print("Please check your environment variables or .env file")
    exit(1)