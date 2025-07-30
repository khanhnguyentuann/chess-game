"""
Game Configuration Management
Centralized configuration for the chess game application.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
import json
import yaml


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    console_output: bool = True


@dataclass
class PersistenceConfig:
    """Persistence configuration."""
    type: str = "memory"  # memory, file, database
    connection_string: Optional[str] = None
    file_path: Optional[str] = None
    auto_save: bool = True
    save_interval: int = 30  # seconds


@dataclass
class GameRulesConfig:
    """Game rules configuration."""
    enable_en_passant: bool = True
    enable_castling: bool = True
    enable_pawn_promotion: bool = True
    fifty_move_rule: bool = True
    threefold_repetition: bool = True
    time_control_enabled: bool = False
    default_time_minutes: int = 10
    increment_seconds: int = 0


@dataclass
class UIConfig:
    """User interface configuration."""
    theme: str = "classic"
    board_size: int = 640
    show_legal_moves: bool = True
    show_coordinates: bool = True
    auto_flip_board: bool = False
    animation_enabled: bool = True
    animation_speed: float = 0.3
    sound_enabled: bool = True


@dataclass
class AIConfig:
    """AI engine configuration."""
    default_engine: str = "internal"
    skill_level: int = 10  # 1-20
    search_depth: int = 15
    time_limit: float = 1.0
    engine_path: Optional[str] = None
    use_opening_book: bool = True
    use_endgame_tablebase: bool = False


@dataclass
class NetworkConfig:
    """Network/multiplayer configuration."""
    enable_multiplayer: bool = False
    server_host: str = "localhost"
    server_port: int = 8080
    max_players: int = 100
    game_timeout: int = 3600  # seconds


class GameConfig:
    """
    Main configuration class for the chess game application.
    Supports loading from files (JSON/YAML) and environment variables.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        # Default configurations
        self.logging = LoggingConfig()
        self.persistence = PersistenceConfig()
        self.game_rules = GameRulesConfig()
        self.ui = UIConfig()
        self.ai = AIConfig()
        self.network = NetworkConfig()
        
        # Load configuration from file if provided
        if config_path:
            self.load_from_file(config_path)
        
        # Override with environment variables
        self._load_from_environment()
    
    def load_from_file(self, config_path: str) -> None:
        """
        Load configuration from a file (JSON or YAML).
        
        Args:
            config_path: Path to configuration file
        """
        config_file = Path(config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                if config_file.suffix.lower() in ['.yaml', '.yml']:
                    config_data = yaml.safe_load(f)
                else:  # Assume JSON
                    config_data = json.load(f)
            
            self._apply_config_data(config_data)
            
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            raise ValueError(f"Invalid configuration file format: {e}")
    
    def save_to_file(self, config_path: str, format: str = "json") -> None:
        """
        Save current configuration to a file.
        
        Args:
            config_path: Path to save configuration
            format: File format ('json' or 'yaml')
        """
        config_data = self.to_dict()
        
        with open(config_path, 'w', encoding='utf-8') as f:
            if format.lower() == 'yaml':
                yaml.dump(config_data, f, default_flow_style=False, indent=2)
            else:  # JSON
                json.dump(config_data, f, indent=2)
    
    def _apply_config_data(self, config_data: Dict[str, Any]) -> None:
        """Apply configuration data to the config objects."""
        
        if 'logging' in config_data:
            self._update_dataclass(self.logging, config_data['logging'])
        
        if 'persistence' in config_data:
            self._update_dataclass(self.persistence, config_data['persistence'])
        
        if 'game_rules' in config_data:
            self._update_dataclass(self.game_rules, config_data['game_rules'])
        
        if 'ui' in config_data:
            self._update_dataclass(self.ui, config_data['ui'])
        
        if 'ai' in config_data:
            self._update_dataclass(self.ai, config_data['ai'])
        
        if 'network' in config_data:
            self._update_dataclass(self.network, config_data['network'])
    
    def _update_dataclass(self, obj, data: Dict[str, Any]) -> None:
        """Update dataclass fields from dictionary."""
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
    
    def _load_from_environment(self) -> None:
        """Load configuration from environment variables."""
        
        # Logging
        if os.getenv('CHESS_LOG_LEVEL'):
            self.logging.level = os.getenv('CHESS_LOG_LEVEL')
        if os.getenv('CHESS_LOG_FILE'):
            self.logging.file_path = os.getenv('CHESS_LOG_FILE')
        
        # Persistence
        if os.getenv('CHESS_PERSISTENCE_TYPE'):
            self.persistence.type = os.getenv('CHESS_PERSISTENCE_TYPE')
        if os.getenv('CHESS_DB_CONNECTION'):
            self.persistence.connection_string = os.getenv('CHESS_DB_CONNECTION')
        
        # AI
        if os.getenv('CHESS_AI_SKILL_LEVEL'):
            try:
                self.ai.skill_level = int(os.getenv('CHESS_AI_SKILL_LEVEL'))
            except ValueError:
                pass
        
        # UI
        if os.getenv('CHESS_BOARD_SIZE'):
            try:
                self.ui.board_size = int(os.getenv('CHESS_BOARD_SIZE'))
            except ValueError:
                pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'logging': {
                'level': self.logging.level,
                'file_path': self.logging.file_path,
                'max_file_size': self.logging.max_file_size,
                'backup_count': self.logging.backup_count,
                'format': self.logging.format,
                'console_output': self.logging.console_output
            },
            'persistence': {
                'type': self.persistence.type,
                'connection_string': self.persistence.connection_string,
                'file_path': self.persistence.file_path,
                'auto_save': self.persistence.auto_save,
                'save_interval': self.persistence.save_interval
            },
            'game_rules': {
                'enable_en_passant': self.game_rules.enable_en_passant,
                'enable_castling': self.game_rules.enable_castling,
                'enable_pawn_promotion': self.game_rules.enable_pawn_promotion,
                'fifty_move_rule': self.game_rules.fifty_move_rule,
                'threefold_repetition': self.game_rules.threefold_repetition,
                'time_control_enabled': self.game_rules.time_control_enabled,
                'default_time_minutes': self.game_rules.default_time_minutes,
                'increment_seconds': self.game_rules.increment_seconds
            },
            'ui': {
                'theme': self.ui.theme,
                'board_size': self.ui.board_size,
                'show_legal_moves': self.ui.show_legal_moves,
                'show_coordinates': self.ui.show_coordinates,
                'auto_flip_board': self.ui.auto_flip_board,
                'animation_enabled': self.ui.animation_enabled,
                'animation_speed': self.ui.animation_speed,
                'sound_enabled': self.ui.sound_enabled
            },
            'ai': {
                'default_engine': self.ai.default_engine,
                'skill_level': self.ai.skill_level,
                'search_depth': self.ai.search_depth,
                'time_limit': self.ai.time_limit,
                'engine_path': self.ai.engine_path,
                'use_opening_book': self.ai.use_opening_book,
                'use_endgame_tablebase': self.ai.use_endgame_tablebase
            },
            'network': {
                'enable_multiplayer': self.network.enable_multiplayer,
                'server_host': self.network.server_host,
                'server_port': self.network.server_port,
                'max_players': self.network.max_players,
                'game_timeout': self.network.game_timeout
            }
        }
    
    def validate(self) -> None:
        """Validate configuration values."""
        errors = []
        
        # Validate logging level
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.logging.level not in valid_levels:
            errors.append(f"Invalid logging level: {self.logging.level}")
        
        # Validate persistence type
        valid_types = ['memory', 'file', 'database']
        if self.persistence.type not in valid_types:
            errors.append(f"Invalid persistence type: {self.persistence.type}")
        
        # Validate AI skill level
        if not 1 <= self.ai.skill_level <= 20:
            errors.append(f"AI skill level must be 1-20, got: {self.ai.skill_level}")
        
        # Validate UI board size
        if self.ui.board_size < 400 or self.ui.board_size > 1200:
            errors.append(f"Board size must be 400-1200, got: {self.ui.board_size}")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
    
    def get_data_directory(self) -> Path:
        """Get the data directory for the application."""
        if self.persistence.file_path:
            return Path(self.persistence.file_path).parent
        
        # Default data directory
        home_dir = Path.home()
        data_dir = home_dir / ".chess_game"
        data_dir.mkdir(exist_ok=True)
        return data_dir
    
    def get_log_directory(self) -> Path:
        """Get the log directory for the application."""
        if self.logging.file_path:
            return Path(self.logging.file_path).parent
        
        # Default log directory
        data_dir = self.get_data_directory()
        log_dir = data_dir / "logs"
        log_dir.mkdir(exist_ok=True)
        return log_dir
