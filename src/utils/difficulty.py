"""Dynamic difficulty scaling system for the snake game."""

import math
from typing import Dict, List, Tuple, Callable
from dataclasses import dataclass
from enum import Enum


class DifficultyMode(Enum):
    """Different difficulty scaling modes."""
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    LOGARITHMIC = "logarithmic"
    STEP_FUNCTION = "step_function"
    ADAPTIVE = "adaptive"


@dataclass
class DifficultyThreshold:
    """Defines a difficulty threshold with corresponding settings."""
    score_threshold: int
    speed_multiplier: float
    food_spawn_rate: float
    points_per_food: int
    description: str


class DifficultyManager:
    """Manages dynamic difficulty scaling based on player performance."""
    
    def __init__(self):
        # Base game settings
        self.base_speed = 1.0  # Game speed multiplier
        self.base_food_points = 10
        self.base_food_spawn_rate = 1.0
        
        # Current difficulty state
        self.current_score = 0
        self.current_speed_multiplier = 1.0
        self.current_food_points = self.base_food_points
        self.current_food_spawn_rate = self.base_food_spawn_rate
        self.current_difficulty_level = 0
        
        # Difficulty settings
        self.difficulty_mode = DifficultyMode.STEP_FUNCTION
        self.enable_adaptive_scaling = True
        self.performance_window_size = 10
        
        # Performance tracking for adaptive difficulty
        self.recent_death_times: List[float] = []
        self.recent_food_times: List[float] = []
        self.avg_session_time = 0
        self.consecutive_deaths = 0
        
        # Predefined difficulty thresholds
        self.thresholds = self._create_default_thresholds()
        
        # Custom scaling functions
        self.custom_scaling_functions: Dict[str, Callable[[int], float]] = {}
    
    def _create_default_thresholds(self) -> List[DifficultyThreshold]:
        """Create default difficulty thresholds."""
        return [
            DifficultyThreshold(0, 1.0, 1.0, 10, "Beginner"),
            DifficultyThreshold(50, 1.2, 1.0, 10, "Easy"),
            DifficultyThreshold(100, 1.4, 1.0, 15, "Normal"),
            DifficultyThreshold(150, 1.6, 1.1, 15, "Medium"),
            DifficultyThreshold(250, 1.8, 1.1, 20, "Hard"),
            DifficultyThreshold(400, 2.0, 1.2, 20, "Very Hard"),
            DifficultyThreshold(600, 2.3, 1.2, 25, "Expert"),
            DifficultyThreshold(800, 2.6, 1.3, 25, "Master"),
            DifficultyThreshold(1000, 3.0, 1.3, 30, "Legendary"),
            DifficultyThreshold(1500, 3.5, 1.4, 30, "Impossible"),
        ]
    
    def update_score(self, new_score: int) -> None:
        """Update the current score and recalculate difficulty."""
        old_score = self.current_score
        self.current_score = new_score
        
        # Only recalculate if score changed significantly
        if self._should_recalculate_difficulty(old_score, new_score):
            self._recalculate_difficulty()
    
    def _should_recalculate_difficulty(self, old_score: int, new_score: int) -> bool:
        """Determine if difficulty should be recalculated."""
        if self.difficulty_mode == DifficultyMode.STEP_FUNCTION:
            # Only recalculate if we crossed a threshold
            old_threshold = self._get_threshold_for_score(old_score)
            new_threshold = self._get_threshold_for_score(new_score)
            return old_threshold != new_threshold
        else:
            # For continuous modes, recalculate more frequently
            return (new_score - old_score) >= 10
    
    def _recalculate_difficulty(self) -> None:
        """Recalculate all difficulty parameters based on current score."""
        if self.difficulty_mode == DifficultyMode.STEP_FUNCTION:
            self._calculate_step_difficulty()
        elif self.difficulty_mode == DifficultyMode.LINEAR:
            self._calculate_linear_difficulty()
        elif self.difficulty_mode == DifficultyMode.EXPONENTIAL:
            self._calculate_exponential_difficulty()
        elif self.difficulty_mode == DifficultyMode.LOGARITHMIC:
            self._calculate_logarithmic_difficulty()
        elif self.difficulty_mode == DifficultyMode.ADAPTIVE:
            self._calculate_adaptive_difficulty()
        
        # Apply custom scaling if available
        self._apply_custom_scaling()
    
    def _calculate_step_difficulty(self) -> None:
        """Calculate difficulty using step function (discrete levels)."""
        threshold = self._get_threshold_for_score(self.current_score)
        
        if threshold:
            self.current_speed_multiplier = threshold.speed_multiplier
            self.current_food_points = threshold.points_per_food
            self.current_food_spawn_rate = threshold.food_spawn_rate
            self.current_difficulty_level = self.thresholds.index(threshold)
    
    def _calculate_linear_difficulty(self) -> None:
        """Calculate difficulty using linear scaling."""
        # Linear speed increase from 1.0 to 3.0 over score 0-1000
        speed_factor = min(3.0, 1.0 + (self.current_score / 500))
        self.current_speed_multiplier = speed_factor
        
        # Linear point increase from 10 to 30 over score 0-1000
        self.current_food_points = int(min(30, 10 + (self.current_score / 50)))
        
        # Food spawn rate increases slightly
        self.current_food_spawn_rate = min(1.5, 1.0 + (self.current_score / 2000))
    
    def _calculate_exponential_difficulty(self) -> None:
        """Calculate difficulty using exponential scaling."""
        # Exponential speed increase
        speed_factor = 1.0 + math.pow(self.current_score / 100, 1.5) / 10
        self.current_speed_multiplier = min(4.0, speed_factor)
        
        # Points increase exponentially
        point_factor = 10 + math.pow(self.current_score / 50, 1.2)
        self.current_food_points = int(min(50, point_factor))
        
        self.current_food_spawn_rate = min(2.0, 1.0 + math.sqrt(self.current_score / 100))
    
    def _calculate_logarithmic_difficulty(self) -> None:
        """Calculate difficulty using logarithmic scaling (gentle curve)."""
        # Logarithmic speed increase - gentle at first, flattens out
        if self.current_score > 0:
            speed_factor = 1.0 + math.log(self.current_score + 1) / 5
            self.current_speed_multiplier = min(2.5, speed_factor)
        
        # Points increase logarithmically
        if self.current_score > 0:
            point_factor = 10 + math.log(self.current_score + 1) * 2
            self.current_food_points = int(min(25, point_factor))
        
        self.current_food_spawn_rate = min(1.3, 1.0 + math.log(self.current_score + 1) / 10)
    
    def _calculate_adaptive_difficulty(self) -> None:
        """Calculate difficulty based on player performance."""
        # Base calculation from step function
        self._calculate_step_difficulty()
        
        # Adjust based on recent performance
        if len(self.recent_death_times) >= 3:
            avg_death_score = sum(self.recent_death_times[-3:]) / 3
            
            # If player is dying early, reduce difficulty
            if avg_death_score < 50:
                self.current_speed_multiplier *= 0.8
                self.current_speed_multiplier = max(0.5, self.current_speed_multiplier)
            # If player is doing very well, increase difficulty
            elif avg_death_score > 200:
                self.current_speed_multiplier *= 1.2
                self.current_speed_multiplier = min(5.0, self.current_speed_multiplier)
        
        # Adjust for consecutive deaths
        if self.consecutive_deaths >= 2:
            self.current_speed_multiplier *= 0.9
            self.consecutive_deaths = 0
    
    def _apply_custom_scaling(self) -> None:
        """Apply any custom scaling functions."""
        for param_name, scaling_func in self.custom_scaling_functions.items():
            try:
                scaled_value = scaling_func(self.current_score)
                
                if param_name == "speed":
                    self.current_speed_multiplier = scaled_value
                elif param_name == "points":
                    self.current_food_points = int(scaled_value)
                elif param_name == "spawn_rate":
                    self.current_food_spawn_rate = scaled_value
            except Exception as e:
                print(f"Error applying custom scaling for {param_name}: {e}")
    
    def _get_threshold_for_score(self, score: int) -> DifficultyThreshold:
        """Get the appropriate difficulty threshold for a score."""
        for threshold in reversed(self.thresholds):
            if score >= threshold.score_threshold:
                return threshold
        return self.thresholds[0]
    
    def get_current_difficulty_name(self) -> str:
        """Get the name of the current difficulty level."""
        threshold = self._get_threshold_for_score(self.current_score)
        return threshold.description if threshold else "Unknown"
    
    def get_difficulty_progress(self) -> float:
        """Get progress to next difficulty level (0.0 to 1.0)."""
        if self.difficulty_mode != DifficultyMode.STEP_FUNCTION:
            return min(1.0, self.current_score / 1000.0)
        
        current_threshold = self._get_threshold_for_score(self.current_score)
        current_index = self.thresholds.index(current_threshold)
        
        if current_index >= len(self.thresholds) - 1:
            return 1.0
        
        next_threshold = self.thresholds[current_index + 1]
        if next_threshold.score_threshold == current_threshold.score_threshold:
            return 0.0
        
        progress = (self.current_score - current_threshold.score_threshold) / \
                  (next_threshold.score_threshold - current_threshold.score_threshold)
        return max(0.0, min(1.0, progress))
    
    def set_difficulty_mode(self, mode: DifficultyMode) -> None:
        """Change the difficulty scaling mode."""
        self.difficulty_mode = mode
        self._recalculate_difficulty()
    
    def add_custom_threshold(self, threshold: DifficultyThreshold) -> None:
        """Add a custom difficulty threshold."""
        self.thresholds.append(threshold)
        self.thresholds.sort(key=lambda t: t.score_threshold)
        self._recalculate_difficulty()
    
    def add_custom_scaling_function(self, parameter: str, func: Callable[[int], float]) -> None:
        """Add a custom scaling function for a parameter."""
        self.custom_scaling_functions[parameter] = func
        self._recalculate_difficulty()
    
    def record_death(self, score: int) -> None:
        """Record a player death for adaptive difficulty."""
        self.recent_death_times.append(score)
        self.consecutive_deaths += 1
        
        # Keep only recent deaths
        if len(self.recent_death_times) > self.performance_window_size:
            self.recent_death_times.pop(0)
    
    def record_food_eaten(self, time_since_last: float) -> None:
        """Record food consumption timing for adaptive difficulty."""
        self.recent_food_times.append(time_since_last)
        
        # Keep only recent food times
        if len(self.recent_food_times) > self.performance_window_size:
            self.recent_food_times.pop(0)
    
    def reset_difficulty(self) -> None:
        """Reset difficulty to initial state."""
        self.current_score = 0
        self.current_speed_multiplier = 1.0
        self.current_food_points = self.base_food_points
        self.current_food_spawn_rate = self.base_food_spawn_rate
        self.current_difficulty_level = 0
        self.consecutive_deaths = 0
        self.recent_death_times.clear()
        self.recent_food_times.clear()
    
    def get_difficulty_stats(self) -> Dict[str, any]:
        """Get current difficulty statistics."""
        return {
            "current_score": self.current_score,
            "difficulty_level": self.current_difficulty_level,
            "difficulty_name": self.get_current_difficulty_name(),
            "speed_multiplier": self.current_speed_multiplier,
            "points_per_food": self.current_food_points,
            "food_spawn_rate": self.current_food_spawn_rate,
            "progress_to_next": self.get_difficulty_progress(),
            "consecutive_deaths": self.consecutive_deaths,
            "difficulty_mode": self.difficulty_mode.value
        }