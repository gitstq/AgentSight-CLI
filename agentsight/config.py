"""Configuration management for AgentSight-CLI.

Handles default settings, user preferences, and environment-based configuration.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

# Default configuration values
DEFAULT_CONFIG = {
    "cache_enabled": True,
    "cache_dir": "~/.agentsight/cache",
    "cache_ttl": 3600,  # Cache time-to-live in seconds (1 hour)
    "request_timeout": 30,  # HTTP request timeout in seconds
    "max_retries": 3,  # Maximum number of retry attempts
    "retry_delay": 2,  # Delay between retries in seconds
    "rate_limit_delay": 1.0,  # Delay between requests in seconds
    "user_agent": "AgentSight-CLI/1.0 (https://github.com/agentsight; data collection bot)",
    "default_format": "table",  # Default terminal output format
    "default_output_format": "json",  # Default file output format
    "max_items": 20,  # Maximum items to fetch per source
    "proxy": "",  # HTTP proxy URL (empty = no proxy)
    "verify_ssl": True,  # Whether to verify SSL certificates
}

CONFIG_FILE_NAME = "config.json"


class Config:
    """Manages AgentSight configuration.

    Configuration is loaded from (in order of priority):
    1. Environment variables (AGENT_SIGHT_*)
    2. User config file (~/.agentsight/config.json)
    3. Default values

    Attributes:
        cache_enabled: Whether caching is enabled.
        cache_dir: Directory for storing cached data.
        cache_ttl: Cache time-to-live in seconds.
        request_timeout: HTTP request timeout in seconds.
        max_retries: Maximum retry attempts for failed requests.
        retry_delay: Delay between retries in seconds.
        rate_limit_delay: Minimum delay between requests.
        user_agent: User-Agent string for HTTP requests.
        default_format: Default terminal display format.
        default_output_format: Default file output format.
        max_items: Maximum items to fetch per source.
        proxy: HTTP proxy URL.
        verify_ssl: Whether to verify SSL certificates.
    """

    def __init__(self, config_dir: Optional[str] = None):
        """Initialize configuration.

        Args:
            config_dir: Optional custom config directory path.
        """
        self._config_dir = Path(config_dir) if config_dir else Path.home() / ".agentsight"
        self._config_file = self._config_dir / CONFIG_FILE_NAME
        self._settings: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        """Load configuration from file and environment variables."""
        # Start with defaults
        self._settings = DEFAULT_CONFIG.copy()

        # Load from config file if it exists
        if self._config_file.exists():
            try:
                with open(self._config_file, "r", encoding="utf-8") as f:
                    file_config = json.load(f)
                self._settings.update(file_config)
            except (json.JSONDecodeError, IOError) as e:
                # If config file is corrupted, use defaults
                pass

        # Override with environment variables
        self._load_env_vars()

    def _load_env_vars(self) -> None:
        """Load configuration from environment variables.

        Environment variables are prefixed with AGENT_SIGHT_ and use
        uppercase keys with underscores.
        """
        env_mapping = {
            "AGENT_SIGHT_CACHE_ENABLED": ("cache_enabled", bool),
            "AGENT_SIGHT_CACHE_DIR": ("cache_dir", str),
            "AGENT_SIGHT_CACHE_TTL": ("cache_ttl", int),
            "AGENT_SIGHT_REQUEST_TIMEOUT": ("request_timeout", int),
            "AGENT_SIGHT_MAX_RETRIES": ("max_retries", int),
            "AGENT_SIGHT_RETRY_DELAY": ("retry_delay", int),
            "AGENT_SIGHT_RATE_LIMIT_DELAY": ("rate_limit_delay", float),
            "AGENT_SIGHT_USER_AGENT": ("user_agent", str),
            "AGENT_SIGHT_DEFAULT_FORMAT": ("default_format", str),
            "AGENT_SIGHT_DEFAULT_OUTPUT_FORMAT": ("default_output_format", str),
            "AGENT_SIGHT_MAX_ITEMS": ("max_items", int),
            "AGENT_SIGHT_PROXY": ("proxy", str),
            "AGENT_SIGHT_VERIFY_SSL": ("verify_ssl", bool),
        }

        for env_var, (key, var_type) in env_mapping.items():
            value = os.environ.get(env_var)
            if value is not None:
                try:
                    if var_type == bool:
                        self._settings[key] = value.lower() in ("true", "1", "yes")
                    else:
                        self._settings[key] = var_type(value)
                except (ValueError, TypeError):
                    pass

    def save(self) -> None:
        """Save current configuration to file."""
        self._config_dir.mkdir(parents=True, exist_ok=True)
        with open(self._config_file, "w", encoding="utf-8") as f:
            json.dump(self._settings, f, indent=2, ensure_ascii=False)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.

        Args:
            key: Configuration key name.
            default: Default value if key is not found.

        Returns:
            The configuration value.
        """
        return self._settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value.

        Args:
            key: Configuration key name.
            value: Configuration value.
        """
        self._settings[key] = value

    @property
    def cache_enabled(self) -> bool:
        return self._settings.get("cache_enabled", True)

    @property
    def cache_dir(self) -> str:
        return os.path.expanduser(self._settings.get("cache_dir", "~/.agentsight/cache"))

    @property
    def cache_ttl(self) -> int:
        return self._settings.get("cache_ttl", 3600)

    @property
    def request_timeout(self) -> int:
        return self._settings.get("request_timeout", 30)

    @property
    def max_retries(self) -> int:
        return self._settings.get("max_retries", 3)

    @property
    def retry_delay(self) -> int:
        return self._settings.get("retry_delay", 2)

    @property
    def rate_limit_delay(self) -> float:
        return self._settings.get("rate_limit_delay", 1.0)

    @property
    def user_agent(self) -> str:
        return self._settings.get("user_agent", "AgentSight-CLI/1.0")

    @property
    def default_format(self) -> str:
        return self._settings.get("default_format", "table")

    @property
    def default_output_format(self) -> str:
        return self._settings.get("default_output_format", "json")

    @property
    def max_items(self) -> int:
        return self._settings.get("max_items", 20)

    @property
    def proxy(self) -> str:
        return self._settings.get("proxy", "")

    @property
    def verify_ssl(self) -> bool:
        return self._settings.get("verify_ssl", True)
