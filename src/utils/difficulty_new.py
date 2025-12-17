"""Dynamic difficulty system for Phase 4."""

import math
from typing import Dict, List, Callable, Any
from enum import Enum


class Difficulty(Enum):
    """Game difficulty levels."""
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"
    EXPERT = "expert"
    
    @property
    def speed_multiplier(self) -> float:
        """Get speed multiplier for this difficulty."""
        multipliers = {
            Difficulty.EASY: 0.8,
            Difficulty.NORMAL: 1.0,
            Difficulty.HARD: 1.3,
            Difficulty.EXPERT: 1.6
        }
        return multipliers.get(self, 1.0)
    
    @property
    def ai_intelligence(self) -> float:
        """Get AI intelligence level for this difficulty."""
        intelligence = {
            Difficulty.EASY: 0.3,
            Difficulty.NORMAL: 0.5,
            Difficulty.HARD: 0.7,
            Difficulty.EXPERT: 0.9
        }
        return intelligence.get(self, 0.5)
    
    @property
    def score_multiplier(self) -> float:
        """Get score multiplier for this difficulty."""
        multipliers = {
            Difficulty.EASY: 0.5,
            Difficulty.NORMAL: 1.0,
            Difficulty.HARD: 1.5,
            Difficulty.EXPERT: 2.0
        }
        return multipliers.get(self, 1.0)


class DifficultyManager:
    """Manages dynamic difficulty scaling during gameplay."""
    
    def __init__(self):
        self.current_difficulty = Difficulty.NORMAL
        self.base_speed = 3.0  # Base game speed
        self.current_speed = self.base_speed
        self.score = 0
        self.difficulty_thresholds = [
            (50, Difficulty.EASY),
            (100, Difficulty.NORMAL),
            (200, Difficulty.HARD),
            (500, Difficulty.EXPERT)
        ]
        self.speed_change_history: List[float] = []
        self.performance_history: List[float] = []
        
        # Dynamic difficulty parameters
        self.adaptive_enabled = True
        self.adaptation_rate = 0.01  # How quickly difficulty adapts
        self.performance_target_fps = 55  # Target FPS for adaptation
    
    def set_difficulty(self, difficulty: Difficulty) -> None:
        """Set static difficulty level."""
        self.current_difficulty = difficulty
        self._update_game_speed()
    
    def set_base_speed(self, speed: float) -> None:
        """Set base game speed."""
        self.base_speed = speed
        self._update_game_speed()
    
    def update_score(self, points: int) -> None:
        """Update score and check for difficulty progression."""
        self.score += points
        self._check_difficulty_progression()
    
    def update_performance(self, fps: float) -> None:
        """Update performance metrics for adaptive difficulty."""
        if not self.adaptive_enabled:
            return
        
        self.performance_history.append(fps)
        if len(self.performance_history) > 60:  # Keep 60 seconds of history
            self.performance_history.pop(0)
        
        self._adapt_difficulty_based_on_performance()
    
    def _update_game_speed(self) -> None:
        """Update game speed based on current difficulty."""
        old_speed = self.current_speed
        self.current_speed = self.base_speed * self.current_difficulty.speed_multiplier
        
        # Record speed change for smooth transitions
        if abs(self.current_speed - old_speed) > 0.1:
            self.speed_change_history.append(self.current_speed)
            if len(self.speed_change_history) > 10:
                self.speed_change_history.pop(0)
    
    def _check_difficulty_progression(self) -> None:
        """Check if difficulty should increase based on score."""
        for threshold, difficulty in self.difficulty_thresholds:
            if self.score >= threshold and self.current_difficulty.value < difficulty.value:
                self.current_difficulty = difficulty
                self._update_game_speed()
                break
    
    def _adapt_difficulty_based_on_performance(self) -> None:
        """Adapt difficulty based on player performance."""
        if len(self.performance_history) < 30:  # Need at least 30 seconds of data
            return
        
        avg_fps = sum(self.performance_history) / len(self.performance_history)
        
        # If player is struggling (low FPS), make it easier
        if avg_fps < self.performance_target_fps:
            # Consider making game easier
            if self.current_difficulty != Difficulty.EASY:
                if self.current_difficulty == Difficulty.EXPERT:
                    self.set_difficulty(Difficulty.HARD)
                elif self.current_difficulty == Difficulty.HARD:
                    self.set_difficulty(Difficulty.NORMAL)
                elif self.current_difficulty == Difficulty.NORMAL:
                    self.set_difficulty(Difficulty.EASY)
        # If player is doing well, consider making it harder
        elif avg_fps > self.performance_target_fps + 5:
            # Consider making game harder
            if self.current_difficulty != Difficulty.EXPERT:
                if self.current_difficulty == Difficulty.EASY:
                    self.set_difficulty(Difficulty.NORMAL)
                elif self.current_difficulty == Difficulty.NORMAL:
                    self.set_difficulty(Difficulty.HARD)
                elif self.current_difficulty == Difficulty.HARD:
                    self.set_difficulty(Difficulty.EXPERT)
    
    def get_interpolated_speed(self) -> float:
        """Get smoothly interpolated speed for transitions."""
        if not self.speed_change_history:
            return self.current_speed
        
        # Use the last few speed changes to interpolate
        recent_speeds = self.speed_change_history[-3:]
        if len(recent_speeds) >= 2:
            # Simple linear interpolation between last two speeds
            t = 0.1  # Interpolation factor
            return recent_speeds[-1] + (self.current_speed - recent_speeds[-1]) * t
        
        return self.current_speed
    
    def get_difficulty_info(self) -> Dict[str, Any]:
        """Get comprehensive difficulty information."""
        return {
            'current_difficulty': self.current_difficulty.value,
            'current_speed': self.current_speed,
            'score': self.score,
            'base_speed': self.base_speed,
            'speed_multiplier': self.current_difficulty.speed_multiplier,
            'score_multiplier': self.current_difficulty.score_multiplier,
            'ai_intelligence': self.current_difficulty.ai_intelligence,
            'next_threshold': self._get_next_threshold(),
            'adaptive_enabled': self.adaptive_enabled,
            'avg_performance_fps': sum(self.performance_history) / len(self.performance_history) if self.performance_history else 0
        }
    
    def _get_next_threshold(self) -> int:
        """Get the next difficulty threshold."""
        for i, (threshold, difficulty) in enumerate(self.difficulty_thresholds):
            if self.current_difficulty.value < difficulty.value:
                return threshold
        return float('inf')
    
    def reset(self) -> None:
        """Reset difficulty manager to initial state."""
        self.current_difficulty = Difficulty.NORMAL
        self.score = 0
        self.current_speed = self.base_speed
        self.speed_change_history.clear()
        self.performance_history.clear()
    
    def enable_adaptive_difficulty(self, enabled: bool = True) -> None:
        """Enable or disable adaptive difficulty."""
        self.adaptive_enabled = enabled
    
    def set_adaptation_parameters(self, rate: float = 0.01, target_fps: int = 55) -> None:
        """Set adaptive difficulty parameters."""
        self.adaptation_rate = max(0.001, min(0.1, rate))
        self.performance_target_fps = max(30, min(120, target_fps))
    
    def get_difficulty_curve(self) -> List[Dict[str, Any]]:
        """Get difficulty progression curve for analysis."""
        curve = []
        for threshold, difficulty in self.difficulty_thresholds:
            curve.append({
                'score': threshold,
                'difficulty': difficulty.value,
                'speed_multiplier': difficulty.speed_multiplier,
                'score_multiplier': difficulty.score_multiplier,
                'ai_intelligence': difficulty.ai_intelligence
            })
        return curve


class DynamicScoring:
    """Dynamic scoring system with multipliers and bonuses."""
    
    def __init__(self):
        self.base_score = 10
        self.current_score = 0
        self.multiplier = 1.0
        self.combo_count = 0
        self.combo_multiplier = 1.0
        self.last_food_time = 0.0
        self.combo_timeout = 2.0  # Seconds to reset combo
        
        # Scoring parameters
        self.speed_bonus_enabled = True
        self.chain_bonus_enabled = True
        self.difficulty_bonus_enabled = True
    
    def calculate_score(self, food_time: float, difficulty: Difficulty) -> int:
        """Calculate score with various multipliers and bonuses."""
        base_points = self.base_score
        
        # Difficulty multiplier
        difficulty_mult = difficulty.score_multiplier
        if self.difficulty_bonus_enabled:
            base_points = int(base_points * difficulty_mult)
        
        # Speed bonus (eating food quickly)
        speed_bonus = 1.0
        if self.speed_bonus_enabled and food_time - self.last_food_time < self.combo_timeout:
            speed_bonus = 1.5  # 50% bonus for quick eating
        
        # Combo bonus (multiple foods in sequence)
        combo_mult = 1.0
        if self.chain_bonus_enabled:
            combo_mult = min(3.0, 1.0 + self.combo_count * 0.5)
        
        # Apply all multipliers
        final_score = int(base_points * speed_bonus * combo_mult)
        
        # Update combo tracking
        if food_time - self.last_food_time < self.combo_timeout:
            self.combo_count += 1
        else:
            self.combo_count = 0
        
        self.last_food_time = food_time
        self.current_score += final_score
        self.multiplier = speed_bonus * combo_mult
        
        return final_score
    
    def get_score_info(self) -> Dict[str, Any]:
        """Get comprehensive scoring information."""
        return {
            'current_score': self.current_score,
            'multiplier': self.multiplier,
            'combo_count': self.combo_count,
            'combo_multiplier': self.combo_multiplier,
            'speed_bonus_enabled': self.speed_bonus_enabled,
            'chain_bonus_enabled': self.chain_bonus_enabled,
            'base_score': self.base_score
        }
    
    def reset(self) -> None:
        """Reset scoring system."""
        self.current_score = 0
        self.multiplier = 1.0
        self.combo_count = 0
        self.combo_multiplier = 1.0
        self.last_food_time = 0.0
    
    def set_base_score(self, score: int) -> None:
        """Set the base score value."""
        self.base_score = max(1, score)
    
    def enable_speed_bonus(self, enabled: bool = True) -> None:
        """Enable or disable speed bonus."""
        self.speed_bonus_enabled = enabled
    
    def enable_chain_bonus(self, enabled: bool = True) -> None:
        """Enable or disable chain bonus."""
        self.chain_bonus_enabled = enabled
    
    def set_combo_timeout(self, timeout: float) -> None:
        """Set the combo timeout duration."""
        self.combo_timeout = max(0.5, min(5.0, timeout))