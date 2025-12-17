"""Configuration management for the snake game."""

import json
from typing import Dict, Any, Tuple
from pathlib import Path


class Config:
    """Manages game configuration and settings."""
    
    def __init__(self):
        self._config: Dict[str, Any] = {}
        self._load_default_config()
    
    @property
    def screen_width(self) -> int:
        """Get screen width from configuration."""
        return self.get("window.width", 800)
    
    @property
    def screen_height(self) -> int:
        """Get screen height from configuration."""
        return self.get("window.height", 600)
    
    @property
    def grid_width(self) -> int:
        """Get grid width from configuration."""
        return self.get("game.grid_size", [20, 15])[0]
    
    @property
    def grid_height(self) -> int:
        """Get grid height from configuration."""
        return self.get("game.grid_size", [20, 15])[1]
    
    @property
    def background_color(self) -> Tuple[int, int, int]:
        """Get background color."""
        return self.get("window.background_color", (0, 0, 0))


class GameConfig(Config):
    """Extended configuration for Phase 3 game features."""
    
    def __init__(self):
        super().__init__()
        self._load_phase3_config()
    
    def _load_phase3_config(self) -> None:
        """Load Phase 3 specific configuration."""
        phase3_config = {
            "window": {
                "width": 1200,
                "height": 800,
                "title": "Advanced Snake Game - Phase 3",
                "background_color": (10, 10, 30)
            },
            "game": {
                "grid_size": [120, 90],
                "starting_speed": 3.0,  # Slower starting speed
                "fps": 60,
                "ai_snake_count": 2,
                "ai_difficulty": 0.3,  # Easier AI by default
                "time_limit": None  # For timed modes
            },
            "ai": {
                "max_difficulty": 1.0,
                "min_difficulty": 0.1,
                "default_personalities": ["balanced", "aggressive", "cautious"],
                "pathfinding_update_rate": 0.5  # Seconds between AI recalculation
            },
            "multiplayer": {
                "max_snakes": 8,
                "food_items": 5,
                "food_spawn_rate": 0.1
            },
            "leaderboard": {
                "max_entries": 100,
                "auto_save": True
            },
            "replay": {
                "max_replays": 50,
                "auto_cleanup": True
            }
        }
        
        self._merge_config(phase3_config)
    
    def _load_default_config(self) -> None:
        """Load default game configuration."""
        self._config = {
            "window": {
                "width": 800,
                "height": 600,
                "title": "Advanced Snake Game"
            },
            "game": {
                "grid_size": [20, 15],
                "starting_speed": 5.0,
                "fps": 60
            },
            "snake": {
                "starting_length": 3,
                "growth_per_food": 1
            },
            "food": {
                "points": 10,
                "spawn_delay": 0
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports nested keys with dots)."""
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value by key (supports nested keys with dots)."""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def load_from_file(self, file_path: str) -> None:
        """Load configuration from JSON file."""
        try:
            with open(file_path, 'r') as f:
                file_config = json.load(f)
                self._merge_config(file_config)
        except (FileNotFoundError, json.JSONDecodeError):
            pass  # Keep default config if file doesn't exist or is invalid
    
    def _merge_config(self, file_config: Dict[str, Any]) -> None:
        """Merge file configuration with default configuration."""
        def deep_merge(base: Dict, update: Dict) -> Dict:
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    base[key] = deep_merge(base[key], value)
                else:
                    base[key] = value
            return base
        
        self._config = deep_merge(self._config, file_config)