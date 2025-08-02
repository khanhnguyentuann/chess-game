"""
Save Manager - Handles game save/load operations
Provides centralized save file management with proper error handling.
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime


class SaveManager:
    """Manages game save files with proper directory structure and error handling."""
    
    def __init__(self, saves_dir: str = "saves"):
        """
        Initialize the save manager.
        
        Args:
            saves_dir: Directory to store save files (relative to project root)
        """
        # Configure logging first
        self.logger = logging.getLogger(__name__)
        
        self.saves_dir = Path(saves_dir)
        self._ensure_saves_directory()
    
    def _ensure_saves_directory(self) -> None:
        """Ensure the saves directory exists."""
        try:
            self.saves_dir.mkdir(exist_ok=True)
            self.logger.info(f"Save directory ready: {self.saves_dir.absolute()}")
        except Exception as e:
            self.logger.error(f"Failed to create saves directory: {e}")
            raise
    
    def get_save_file_path(self, filename: str = "saved_game.json") -> Path:
        """
        Get the full path to a save file.
        
        Args:
            filename: Name of the save file
            
        Returns:
            Full path to the save file
        """
        return self.saves_dir / filename
    
    def save_game(self, game_data: Dict[str, Any], filename: str = "saved_game.json") -> bool:
        """
        Save game data to file.
        
        Args:
            game_data: Game data to save
            filename: Name of the save file
            
        Returns:
            True if save was successful, False otherwise
        """
        try:
            save_path = self.get_save_file_path(filename)
            
            # Add metadata
            game_data['_save_metadata'] = {
                'saved_at': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            # Write to temporary file first, then rename (atomic operation)
            temp_path = save_path.with_suffix('.tmp')
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(game_data, f, indent=2, ensure_ascii=False)
            
            # Atomic rename
            temp_path.replace(save_path)
            
            self.logger.info(f"Game saved successfully: {save_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save game: {e}")
            return False
    
    def load_game(self, filename: str = "saved_game.json") -> Optional[Dict[str, Any]]:
        """
        Load game data from file.
        
        Args:
            filename: Name of the save file
            
        Returns:
            Game data if successful, None otherwise
        """
        try:
            save_path = self.get_save_file_path(filename)
            
            if not save_path.exists():
                self.logger.info(f"No save file found: {save_path}")
                return None
            
            with open(save_path, 'r', encoding='utf-8') as f:
                game_data = json.load(f)
            
            self.logger.info(f"Game loaded successfully: {save_path}")
            return game_data
            
        except Exception as e:
            self.logger.error(f"Failed to load game: {e}")
            return None
    
    def delete_save(self, filename: str = "saved_game.json") -> bool:
        """
        Delete a save file.
        
        Args:
            filename: Name of the save file to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            save_path = self.get_save_file_path(filename)
            
            if save_path.exists():
                save_path.unlink()
                self.logger.info(f"Save file deleted: {save_path}")
                return True
            else:
                self.logger.info(f"Save file not found for deletion: {save_path}")
                return True  # Consider it successful if file doesn't exist
                
        except Exception as e:
            self.logger.error(f"Failed to delete save file: {e}")
            return False
    
    def has_save_file(self, filename: str = "saved_game.json") -> bool:
        """
        Check if a save file exists.
        
        Args:
            filename: Name of the save file to check
            
        Returns:
            True if save file exists, False otherwise
        """
        save_path = self.get_save_file_path(filename)
        return save_path.exists()
    
    def get_save_info(self, filename: str = "saved_game.json") -> Optional[Dict[str, Any]]:
        """
        Get information about a save file without loading the full game data.
        
        Args:
            filename: Name of the save file
            
        Returns:
            Save file information if successful, None otherwise
        """
        try:
            save_path = self.get_save_file_path(filename)
            
            if not save_path.exists():
                return None
            
            # Get file stats
            stat = save_path.stat()
            
            # Load minimal data for info
            with open(save_path, 'r', encoding='utf-8') as f:
                game_data = json.load(f)
            
            return {
                'filename': filename,
                'size_bytes': stat.st_size,
                'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'game_id': game_data.get('id'),
                'move_count': game_data.get('move_count', 0),
                'current_player': game_data.get('current_player'),
                'state': game_data.get('state'),
                'created_at': game_data.get('created_at')
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get save info: {e}")
            return None
    
    def list_save_files(self) -> list:
        """
        List all save files in the saves directory.
        
        Returns:
            List of save file information
        """
        save_files = []
        
        try:
            for file_path in self.saves_dir.glob("*.json"):
                if file_path.is_file():
                    info = self.get_save_info(file_path.name)
                    if info:
                        save_files.append(info)
            
            self.logger.info(f"Found {len(save_files)} save files")
            return save_files
            
        except Exception as e:
            self.logger.error(f"Failed to list save files: {e}")
            return []


# Global instance for easy access
save_manager = SaveManager() 