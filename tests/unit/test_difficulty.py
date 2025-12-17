"""Unit tests for difficulty scaling system."""

import pytest
from src.utils.difficulty import (
    DifficultyManager, DifficultyThreshold, DifficultyMode
)


class TestDifficultyThreshold:
    """Test difficulty threshold data class."""
    
    def test_threshold_creation(self):
        """Test creating a difficulty threshold."""
        threshold = DifficultyThreshold(
            score_threshold=100,
            speed_multiplier=1.5,
            food_spawn_rate=1.2,
            points_per_food=15,
            description="Medium"
        )
        
        assert threshold.score_threshold == 100
        assert threshold.speed_multiplier == 1.5
        assert threshold.food_spawn_rate == 1.2
        assert threshold.points_per_food == 15
        assert threshold.description == "Medium"


class TestDifficultyManager:
    """Test the main difficulty manager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.difficulty_manager = DifficultyManager()
    
    def test_initialization(self):
        """Test difficulty manager initialization."""
        assert self.difficulty_manager.current_score == 0
        assert self.difficulty_manager.current_speed_multiplier == 1.0
        assert self.difficulty_manager.current_food_points == 10
        assert self.difficulty_manager.current_food_spawn_rate == 1.0
        assert self.difficulty_manager.current_difficulty_level == 0
        assert len(self.difficulty_manager.thresholds) > 0
    
    def test_default_thresholds(self):
        """Test that default thresholds are properly configured."""
        thresholds = self.difficulty_manager.thresholds
        
        # Should be sorted by score threshold
        for i in range(len(thresholds) - 1):
            assert thresholds[i].score_threshold <= thresholds[i + 1].score_threshold
        
        # First threshold should be at score 0
        assert thresholds[0].score_threshold == 0
        
        # Speed multipliers should generally increase
        for i in range(1, len(thresholds)):
            assert thresholds[i].speed_multiplier >= thresholds[i-1].speed_multiplier
    
    def test_score_update_step_function(self):
        """Test score update with step function mode."""
        self.difficulty_manager.set_difficulty_mode(DifficultyMode.STEP_FUNCTION)
        
        # Initial state
        assert self.difficulty_manager.get_current_difficulty_name() == "Beginner"
        
        # Update to score 30 (should still be beginner)
        self.difficulty_manager.update_score(30)
        assert self.difficulty_manager.get_current_difficulty_name() == "Beginner"
        
        # Update to score 50 (should change to easy)
        self.difficulty_manager.update_score(50)
        assert self.difficulty_manager.get_current_difficulty_name() == "Easy"
        
        # Update to score 100 (should change to normal)
        self.difficulty_manager.update_score(100)
        assert self.difficulty_manager.get_current_difficulty_name() == "Normal"
    
    def test_score_update_linear_mode(self):
        """Test score update with linear mode."""
        self.difficulty_manager.set_difficulty_mode(DifficultyMode.LINEAR)
        
        self.difficulty_manager.update_score(250)
        
        # Should have intermediate values
        assert self.difficulty_manager.current_speed_multiplier > 1.0
        assert self.difficulty_manager.current_speed_multiplier < 3.0
        assert self.difficulty_manager.current_food_points > 10
        assert self.difficulty_manager.current_food_points < 30
    
    def test_score_update_exponential_mode(self):
        """Test score update with exponential mode."""
        self.difficulty_manager.set_difficulty_mode(DifficultyMode.EXPONENTIAL)
        
        self.difficulty_manager.update_score(200)
        
        # Should increase more rapidly than linear
        assert self.difficulty_manager.current_speed_multiplier > 1.0
        assert self.difficulty_manager.current_food_points > 10
    
    def test_score_update_logarithmic_mode(self):
        """Test score update with logarithmic mode."""
        self.difficulty_manager.set_difficulty_mode(DifficultyMode.LOGARITHMIC)
        
        self.difficulty_manager.update_score(200)
        
        # Should increase more gently
        assert self.difficulty_manager.current_speed_multiplier >= 1.0
        assert self.difficulty_manager.current_speed_multiplier <= 2.5
    
    def test_get_threshold_for_score(self):
        """Test getting appropriate threshold for score."""
        # Score below first threshold should return first
        threshold = self.difficulty_manager._get_threshold_for_score(0)
        assert threshold.score_threshold == 0
        
        # Score in middle should return appropriate threshold
        threshold = self.difficulty_manager._get_threshold_for_score(75)
        assert threshold.score_threshold == 50  # Should be "Easy"
        
        # Score above all thresholds should return last
        threshold = self.difficulty_manager._get_threshold_for_score(2000)
        assert threshold == self.difficulty_manager.thresholds[-1]
    
    def test_difficulty_progress(self):
        """Test difficulty progress calculation."""
        self.difficulty_manager.set_difficulty_mode(DifficultyMode.STEP_FUNCTION)
        
        # At beginning of threshold, progress should be 0
        self.difficulty_manager.update_score(50)
        progress = self.difficulty_manager.get_difficulty_progress()
        assert progress == 0.0
        
        # In middle of threshold, progress should be intermediate
        self.difficulty_manager.update_score(75)
        progress = self.difficulty_manager.get_difficulty_progress()
        assert 0.0 < progress < 1.0
        
        # At threshold boundary, progress should be 0 again
        self.difficulty_manager.update_score(100)
        progress = self.difficulty_manager.get_difficulty_progress()
        assert progress == 0.0
    
    def test_continuous_mode_progress(self):
        """Test progress calculation for continuous modes."""
        self.difficulty_manager.set_difficulty_mode(DifficultyMode.LINEAR)
        
        self.difficulty_manager.update_score(250)
        progress = self.difficulty_manager.get_difficulty_progress()
        assert progress == 0.25  # 250/1000
    
    def test_add_custom_threshold(self):
        """Test adding custom difficulty thresholds."""
        custom_threshold = DifficultyThreshold(
            score_threshold=75,
            speed_multiplier=1.3,
            food_spawn_rate=1.05,
            points_per_food=12,
            description="Custom Medium"
        )
        
        original_count = len(self.difficulty_manager.thresholds)
        self.difficulty_manager.add_custom_threshold(custom_threshold)
        
        assert len(self.difficulty_manager.thresholds) == original_count + 1
        assert custom_threshold in self.difficulty_manager.thresholds
        
        # Should be properly sorted
        thresholds = self.difficulty_manager.thresholds
        for i in range(len(thresholds) - 1):
            assert thresholds[i].score_threshold <= thresholds[i + 1].score_threshold
    
    def test_add_custom_scaling_function(self):
        """Test adding custom scaling functions."""
        # Custom speed scaling function
        def custom_speed(score):
            return 1.0 + (score / 100) ** 0.5  # Square root scaling
        
        self.difficulty_manager.add_custom_scaling_function("speed", custom_speed)
        
        self.difficulty_manager.update_score(100)
        # Custom function should be applied
        assert self.difficulty_manager.current_speed_multiplier == 2.0  # 1.0 + sqrt(1)
        
        # Test custom points function
        def custom_points(score):
            return 10 + int(score / 25)
        
        self.difficulty_manager.add_custom_scaling_function("points", custom_points)
        self.difficulty_manager.update_score(100)
        assert self.difficulty_manager.current_food_points == 14  # 10 + 4
    
    def test_record_death(self):
        """Test recording player deaths."""
        # Record some deaths
        self.difficulty_manager.record_death(25)
        self.difficulty_manager.record_death(40)
        self.difficulty_manager.record_death(30)
        
        assert len(self.difficulty_manager.recent_death_times) == 3
        assert self.difficulty_manager.recent_death_times == [25, 40, 30]
        
        # Test consecutive deaths
        assert self.difficulty_manager.consecutive_deaths == 3
        
        # Test window size
        for i in range(15):
            self.difficulty_manager.record_death(50)
        
        assert len(self.difficulty_manager.recent_death_times) == 10  # window size
        assert self.difficulty_manager.recent_death_times[-1] == 50
    
    def test_record_food_eaten(self):
        """Test recording food consumption timing."""
        # Record some food times
        times = [1.5, 2.0, 1.2, 3.1, 1.8]
        for t in times:
            self.difficulty_manager.record_food_eaten(t)
        
        assert len(self.difficulty_manager.recent_food_times) == 5
        assert self.difficulty_manager.recent_food_times == times
        
        # Test window size
        for i in range(15):
            self.difficulty_manager.record_food_eaten(2.0)
        
        assert len(self.difficulty_manager.recent_food_times) == 10  # window size
    
    def test_adaptive_difficulty(self):
        """Test adaptive difficulty based on performance."""
        self.difficulty_manager.set_difficulty_mode(DifficultyMode.ADAPTIVE)
        
        # Player dying early should reduce difficulty
        for i in range(3):
            self.difficulty_manager.record_death(20)
        
        self.difficulty_manager.update_score(50)
        original_speed = self.difficulty_manager.current_speed_multiplier
        
        self.difficulty_manager._calculate_adaptive_difficulty()
        adapted_speed = self.difficulty_manager.current_speed_multiplier
        
        assert adapted_speed < original_speed
        assert adapted_speed >= 0.5  # Minimum speed
        
        # Player doing well should increase difficulty
        self.difficulty_manager.reset_difficulty()
        for i in range(3):
            self.difficulty_manager.record_death(250)
        
        self.difficulty_manager.update_score(100)
        original_speed = self.difficulty_manager.current_speed_multiplier
        
        self.difficulty_manager._calculate_adaptive_difficulty()
        adapted_speed = self.difficulty_manager.current_speed_multiplier
        
        assert adapted_speed > original_speed
        assert adapted_speed <= 5.0  # Maximum speed
    
    def test_reset_difficulty(self):
        """Test resetting difficulty to initial state."""
        # Change some values
        self.difficulty_manager.update_score(150)
        self.difficulty_manager.record_death(50)
        self.difficulty_manager.consecutive_deaths = 3
        
        # Reset
        self.difficulty_manager.reset_difficulty()
        
        # Should be back to initial state
        assert self.difficulty_manager.current_score == 0
        assert self.difficulty_manager.current_speed_multiplier == 1.0
        assert self.difficulty_manager.current_food_points == 10
        assert self.difficulty_manager.current_food_spawn_rate == 1.0
        assert self.difficulty_manager.current_difficulty_level == 0
        assert self.difficulty_manager.consecutive_deaths == 0
        assert len(self.difficulty_manager.recent_death_times) == 0
        assert len(self.difficulty_manager.recent_food_times) == 0
    
    def test_get_difficulty_stats(self):
        """Test getting difficulty statistics."""
        self.difficulty_manager.update_score(125)
        
        stats = self.difficulty_manager.get_difficulty_stats()
        
        required_keys = [
            "current_score", "difficulty_level", "difficulty_name",
            "speed_multiplier", "points_per_food", "food_spawn_rate",
            "progress_to_next", "consecutive_deaths", "difficulty_mode"
        ]
        
        for key in required_keys:
            assert key in stats
        
        assert stats["current_score"] == 125
        assert stats["difficulty_mode"] == "step_function"
        assert isinstance(stats["progress_to_next"], float)
        assert 0.0 <= stats["progress_to_next"] <= 1.0
    
    def test_score_threshold_recalculation(self):
        """Test that difficulty is recalculated when crossing thresholds."""
        self.difficulty_manager.set_difficulty_mode(DifficultyMode.STEP_FUNCTION)
        
        # Track when difficulty changes
        original_difficulty = self.difficulty_manager.get_current_difficulty_name()
        
        # Update score just before threshold
        self.difficulty_manager.update_score(49)
        assert self.difficulty_manager.get_current_difficulty_name() == original_difficulty
        
        # Cross threshold
        self.difficulty_manager.update_score(50)
        assert self.difficulty_manager.get_current_difficulty_name() != original_difficulty
    
    def test_different_difficulty_modes(self):
        """Test switching between different difficulty modes."""
        score = 200
        
        for mode in DifficultyMode:
            self.difficulty_manager.reset_difficulty()
            self.difficulty_manager.set_difficulty_mode(mode)
            self.difficulty_manager.update_score(score)
            
            stats = self.difficulty_manager.get_difficulty_stats()
            assert stats["difficulty_mode"] == mode.value
            assert stats["current_score"] == score
            assert stats["speed_multiplier"] >= 1.0
            assert stats["points_per_food"] >= 10
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Very high score
        self.difficulty_manager.update_score(10000)
        assert self.difficulty_manager.current_speed_multiplier > 1.0
        
        # Negative score (shouldn't happen but test robustness)
        self.difficulty_manager.update_score(-10)
        assert self.difficulty_manager.current_speed_multiplier >= 1.0
        
        # Score that's exactly at threshold
        for threshold in self.difficulty_manager.thresholds:
            self.difficulty_manager.update_score(threshold.score_threshold)
            stats = self.difficulty_manager.get_difficulty_stats()
            assert stats["current_score"] == threshold.score_threshold


if __name__ == "__main__":
    pytest.main([__file__])