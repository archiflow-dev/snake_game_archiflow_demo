"""Enhanced snake entity for hexagonal grid."""

from typing import List, Optional, Tuple
from ..grids.hex_grid import HexCoord
from .hex_snake import HexSnake, HexDirection


class HexSnakeEnhanced(HexSnake):
    """Enhanced snake with additional Phase 4 features."""
    
    def __init__(self, start_position: HexCoord, start_direction: HexDirection = HexDirection.E, 
                 start_length: int = 3, personality: str = "balanced"):
        super().__init__(start_position, start_direction, start_length)
        self.personality = personality
        self.power_up_time = 0.0
        self.speed_boost_time = 0.0
        self.invincible_time = 0.0
        self.special_effects = []
    
    def apply_power_up(self, power_type: str, duration: float) -> None:
        """Apply a power-up to the snake."""
        self.power_up_time = duration
        self.special_effects.append(power_type)
    
    def apply_speed_boost(self, duration: float, speed_multiplier: float) -> None:
        """Apply speed boost to the snake."""
        self.speed_boost_time = duration
    
    def apply_invincibility(self, duration: float) -> None:
        """Apply temporary invincibility."""
        self.invincible_time = duration
    
    def update_effects(self, dt: float) -> None:
        """Update all timed effects."""
        if self.power_up_time > 0:
            self.power_up_time -= dt
        
        if self.speed_boost_time > 0:
            self.speed_boost_time -= dt
        
        if self.invincible_time > 0:
            self.invincible_time -= dt
        
        # Remove expired effects
        self.special_effects = [
            effect for effect in self.special_effects 
            if self._effect_duration(effect) > 0
        ]
    
    def _effect_duration(self, effect: str) -> float:
        """Get duration for a specific effect."""
        # Simplified effect durations
        durations = {
            'speed_boost': self.speed_boost_time,
            'power_up': self.power_up_time,
            'invincibility': self.invincible_time
        }
        return durations.get(effect, 0.0)
    
    def get_current_speed_multiplier(self) -> float:
        """Get current speed multiplier including boosts."""
        base_multiplier = 1.0
        
        if self.speed_boost_time > 0:
            base_multiplier *= 1.5
        
        return base_multiplier
    
    def is_invincible(self) -> bool:
        """Check if snake is currently invincible."""
        return self.invincible_time > 0
    
    def has_active_effects(self) -> bool:
        """Check if snake has any active effects."""
        return len(self.special_effects) > 0
    
    def get_active_effects(self) -> List[str]:
        """Get list of currently active effects."""
        return self.special_effects.copy()
    
    def move_with_speed(self, base_dt: float) -> Optional[HexCoord]:
        """Move the snake with current speed multiplier."""
        speed_mult = self.get_current_speed_multiplier()
        adjusted_dt = base_dt * speed_mult
        
        # Temporarily adjust movement speed by calling move multiple times
        # This is a simplification - in reality, you'd adjust the timing
        return self.move()