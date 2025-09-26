"""Configuration settings for MailMind system."""

from __future__ import annotations

import os
from dataclasses import dataclass, field, fields
from typing import Annotated, Literal, Optional

from langchain_core.runnables import RunnableConfig, ensure_config


@dataclass(kw_only=True)
class MailMindConfig:
    """Configuration for MailMind system.
    
    This class manages all configuration settings for the MailMind system,
    including API keys, model settings, and operational parameters.
    """

    # LLM Configuration
    model: Annotated[str, {"__template_metadata__": {"kind": "llm"}}] = field(
        default="google_genai/gemini-1.5-flash",
        metadata={
            "description": "Primary LLM model for AI operations. Format: provider/model-name"
        },
    )

    model_temperature: float = field(
        default=0.1,
        metadata={
            "description": "Temperature for LLM responses (0.0-1.0). Lower = more deterministic"
        },
    )

    max_tokens: int = field(
        default=2048,
        metadata={"description": "Maximum tokens for LLM responses"},
    )
    # Gmail API Configuration
    gmail_client_id: Optional[str] = field(
        default=None,
        metadata={"description": "Gmail API client ID from Google Cloud Console"},
    )

    gmail_client_secret: Optional[str] = field(
        default=None,
        metadata={"description": "Gmail API client secret from Google Cloud Console"},
    )

    gmail_redirect_uri: str = field(
        default="http://localhost:8080/callback",
        metadata={"description": "OAuth redirect URI for Gmail authentication"},
    )

    # API Keys
    google_api_key: Optional[str] = field(
        default=None,
        metadata={"description": "Google API key for Gemini LLM"},
    )

    def __post_init__(self) -> None:
        """Load environment variables for fields that weren't explicitly set."""
        for f in fields(self):
            if not f.init:
                continue

            current_value = getattr(self, f.name)
            
            # Check if field uses default value or is None
            if current_value is None or current_value == f.default:
                env_key = f.name.upper()
                env_value = os.environ.get(env_key)
                
                if env_value is not None:
                    # Convert environment variable to appropriate type
                    field_type = str(f.type)
                    if "int" in field_type:
                        env_value = int(env_value)
                    elif "float" in field_type:
                        env_value = float(env_value)
                    elif "bool" in field_type:
                        env_value = env_value.lower() in ("true", "1", "yes", "on")
                    
                    setattr(self, f.name, env_value)

        # Validate required fields
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate configuration settings."""
        errors = []

        # Check required API keys
        if not self.google_api_key:
            errors.append("GOOGLE_API_KEY is required for LLM operations")

        if not self.gmail_client_id or not self.gmail_client_secret:
            errors.append("Gmail API credentials (GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET) are required")

        # Validate numeric ranges
        if not (0.0 <= float(self.model_temperature) <= 1.0):
            errors.append("model_temperature must be between 0.0 and 1.0")

        if int(self.max_tokens) <= 0:
            errors.append("max_tokens must be positive")

        if int(self.timeout_seconds) <= 0:
            errors.append("timeout_seconds must be positive")

        if int(self.retry_attempts) < 0:
            errors.append("retry_attempts must be non-negative")

        if errors:
            raise ValueError(f"Configuration validation failed:\n" + "\n".join(f"  - {error}" for error in errors))

    @classmethod
    def from_runnable_config(cls, config: Optional[RunnableConfig] = None) -> MailMindConfig:
        """Create MailMindConfig from RunnableConfig.
        
        This method allows creating configuration from LangGraph's RunnableConfig,
        which is useful for runtime configuration management.
        
        Args:
            config: Optional RunnableConfig containing configurable parameters
            
        Returns:
            MailMindConfig instance with settings from the RunnableConfig
        """
        config = ensure_config(config)
        configurable = config.get("configurable", {})

        # Extract relevant fields
        _fields = {f.name for f in fields(cls) if f.init}
        config_values = {k: v for k, v in configurable.items() if k in _fields}

        return cls(**config_values)
