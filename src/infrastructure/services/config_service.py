"""
Configuration Service
Infrastructure service for managing application configuration.
"""

import os
from typing import Any, Dict, Optional

from ...shared.config.game_config import GameConfig


class ConfigService:
    """Service for managing application configuration."""
    
    def __init__(self):
        """Initialize configuration service."""
        self._config: Dict[str, Any] = {}
        self._load_environment_variables()
        self._load_default_config()
    
    def _load_environment_variables(self) -> None:
        """Load configuration from environment variables."""
        self._config.update({
            "debug": os.getenv("DEBUG", "false").lower() == "true",
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "database_url": os.getenv("DATABASE_URL", "memory://"),
            "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379"),
            "notification_service": os.getenv("NOTIFICATION_SERVICE", "dummy"),
            "event_publishing": os.getenv("EVENT_PUBLISHING", "true").lower() == "true",
        })
    
    def _load_default_config(self) -> None:
        """Load default configuration values."""
        default_config = {
            "game": {
                "time_control": {
                    "enabled": False,
                    "initial_time": 600,  # 10 minutes
                    "increment": 0,
                },
                "ai": {
                    "enabled": False,
                    "depth": 3,
                    "engine": "stockfish",
                },
                "ui": {
                    "theme": "classic",
                    "animations": True,
                    "sound_enabled": True,
                },
                "persistence": {
                    "auto_save": True,
                    "save_interval": 30,  # seconds
                },
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file": None,
            },
            "performance": {
                "max_moves_history": 1000,
                "cache_size": 1000,
                "async_operations": True,
            },
        }
        
        # Merge with existing config
        self._merge_config(self._config, default_config)
    
    def _merge_config(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """Recursively merge configuration dictionaries."""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._merge_config(target[key], value)
            else:
                target[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.
        
        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split(".")
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value by key.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split(".")
        config = self._config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
    
    def get_game_config(self) -> GameConfig:
        """Get game configuration."""
        game_config = self.get("game", {})
        return GameConfig(
            time_control_enabled=game_config.get("time_control", {}).get("enabled", False),
            initial_time=game_config.get("time_control", {}).get("initial_time", 600),
            increment=game_config.get("time_control", {}).get("increment", 0),
            ai_enabled=game_config.get("ai", {}).get("enabled", False),
            ai_depth=game_config.get("ai", {}).get("depth", 3),
            ai_engine=game_config.get("ai", {}).get("engine", "stockfish"),
            theme=game_config.get("ui", {}).get("theme", "classic"),
            animations_enabled=game_config.get("ui", {}).get("animations", True),
            sound_enabled=game_config.get("ui", {}).get("sound_enabled", True),
            auto_save=game_config.get("persistence", {}).get("auto_save", True),
            save_interval=game_config.get("persistence", {}).get("save_interval", 30),
        )
    
    def is_debug_mode(self) -> bool:
        """Check if debug mode is enabled."""
        return self.get("debug", False)
    
    def get_log_level(self) -> str:
        """Get log level."""
        return self.get("log_level", "INFO")
    
    def get_database_url(self) -> str:
        """Get database URL."""
        return self.get("database_url", "memory://")
    
    def is_event_publishing_enabled(self) -> bool:
        """Check if event publishing is enabled."""
        return self.get("event_publishing", True)
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get all configuration."""
        return self._config.copy()
    
    def update_from_dict(self, config_dict: Dict[str, Any]) -> None:
        """
        Update configuration from dictionary.
        
        Args:
            config_dict: Dictionary with configuration updates
        """
        self._merge_config(self._config, config_dict)
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values."""
        self._config.clear()
        self._load_environment_variables()
        self._load_default_config() 