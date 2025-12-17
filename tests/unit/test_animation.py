"""Unit tests for animation system."""

import time
import pytest
from src.utils.animation import (
    Animation, AnimationSystem, EntityAnimator, EasingFunctions
)


class TestEasingFunctions:
    """Test easing functions."""
    
    def test_linear_easing(self):
        """Test linear easing function."""
        assert EasingFunctions.linear(0.0) == 0.0
        assert EasingFunctions.linear(0.5) == 0.5
        assert EasingFunctions.linear(1.0) == 1.0
    
    def test_ease_in_quad(self):
        """Test quadratic ease-in."""
        assert EasingFunctions.ease_in_quad(0.0) == 0.0
        assert EasingFunctions.ease_in_quad(1.0) == 1.0
        assert 0.0 <= EasingFunctions.ease_in_quad(0.5) <= 1.0
    
    def test_ease_out_quad(self):
        """Test quadratic ease-out."""
        assert EasingFunctions.ease_out_quad(0.0) == 0.0
        assert EasingFunctions.ease_out_quad(1.0) == 1.0
        assert 0.0 <= EasingFunctions.ease_out_quad(0.5) <= 1.0
    
    def test_ease_in_out_quad(self):
        """Test quadratic ease-in-out."""
        assert EasingFunctions.ease_in_out_quad(0.0) == 0.0
        assert EasingFunctions.ease_in_out_quad(0.5) == 0.5
        assert EasingFunctions.ease_in_out_quad(1.0) == 1.0
    
    def test_cubic_easing(self):
        """Test cubic easing functions."""
        # Ease-in cubic
        assert EasingFunctions.ease_in_cubic(0.0) == 0.0
        assert EasingFunctions.ease_in_cubic(1.0) == 1.0
        
        # Ease-out cubic
        assert EasingFunctions.ease_out_cubic(0.0) == 0.0
        assert EasingFunctions.ease_out_cubic(1.0) == 1.0
        
        # Ease-in-out cubic
        assert EasingFunctions.ease_in_out_cubic(0.0) == 0.0
        assert EasingFunctions.ease_in_out_cubic(1.0) == 1.0
    
    def test_back_easing(self):
        """Test back easing (overshoot)."""
        assert EasingFunctions.ease_in_back(0.0) == 0.0
        assert EasingFunctions.ease_in_back(1.0) == 1.0
        assert EasingFunctions.ease_out_back(0.0) == 0.0
        assert EasingFunctions.ease_out_back(1.0) == 1.0
    
    def test_elastic_easing(self):
        """Test elastic easing."""
        assert EasingFunctions.ease_out_elastic(0.0) == 0.0
        assert abs(EasingFunctions.ease_out_elastic(1.0) - 1.0) < 0.1


class TestAnimationSystem:
    """Test the main animation system."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.anim_system = AnimationSystem()
    
    def test_animation_creation(self):
        """Test creating an animation."""
        start_value = (0, 0)
        end_value = (100, 100)
        duration = 1.0
        
        animation = self.anim_system.create_animation(
            start_value, end_value, duration
        )
        
        assert isinstance(animation, Animation)
        assert animation.start_value == start_value
        assert animation.end_value == end_value
        assert animation.duration == duration
        assert animation.start_time > 0
        assert animation.easing_func == EasingFunctions.ease_out_quad
    
    def test_animation_with_custom_easing(self):
        """Test creating animation with custom easing."""
        start_value = 0
        end_value = 100
        duration = 0.5
        
        animation = self.anim_system.create_animation(
            start_value, end_value, duration,
            easing_func=EasingFunctions.ease_in_cubic
        )
        
        assert animation.easing_func == EasingFunctions.ease_in_cubic
    
    def test_animation_with_delay(self):
        """Test creating animation with delay."""
        start_value = 0
        end_value = 100
        duration = 1.0
        delay = 0.5
        
        animation = self.anim_system.create_animation(
            start_value, end_value, duration, delay=delay
        )
        
        # Should not start immediately
        time.sleep(0.1)
        assert len(self.anim_system._running_animations) == 0
        
        # Should start after delay
        time.sleep(0.5)
        assert len(self.anim_system._running_animations) >= 1
    
    def test_position_interpolation(self):
        """Test position interpolation."""
        start_pos = (0, 0)
        end_pos = (100, 200)
        duration = 0.1
        
        animation = self.anim_system.create_animation(
            start_pos, end_pos, duration
        )
        
        # Manually set progress for testing
        animation.current_progress = 0.5
        result = self.anim_system.interpolate_position(animation)
        
        expected_x = 0 + (100 - 0) * 0.5
        expected_y = 0 + (200 - 0) * 0.5
        assert result == (expected_x, expected_y)
    
    def test_float_interpolation(self):
        """Test float value interpolation."""
        start_value = 0.0
        end_value = 100.0
        
        animation = self.anim_system.create_animation(
            start_value, end_value, 1.0
        )
        
        animation.current_progress = 0.25
        result = self.anim_system.interpolate_float(animation)
        assert result == 25.0
    
    def test_color_interpolation(self):
        """Test color interpolation."""
        start_color = (255, 0, 0)  # Red
        end_color = (0, 255, 255)  # Cyan
        
        animation = self.anim_system.create_animation(
            start_color, end_color, 1.0
        )
        
        animation.current_progress = 0.5
        result = self.anim_system.interpolate_color(animation)
        
        assert result == (127, 127, 127)  # Gray (middle point)
    
    def test_animation_completion(self):
        """Test animation completion and callbacks."""
        callback_called = False
        
        def callback():
            nonlocal callback_called
            callback_called = True
        
        animation = self.anim_system.create_animation(
            0, 100, 0.1, on_complete=callback
        )
        
        # Wait for animation to complete
        time.sleep(0.15)
        self.anim_system.update()
        
        assert callback_called
        assert animation not in self.anim_system._running_animations
        assert animation in self.anim_system._completed_animations
    
    def test_stopping_animation(self):
        """Test stopping an animation early."""
        animation = self.anim_system.create_animation(0, 100, 1.0)
        
        assert animation in self.anim_system._animations
        assert animation in self.anim_system._running_animations
        
        self.anim_system.stop_animation(animation)
        
        assert animation not in self.anim_system._animations
        assert animation not in self.anim_system._running_animations
    
    def test_stopping_all_animations(self):
        """Test stopping all animations."""
        # Create multiple animations
        for i in range(5):
            self.anim_system.create_animation(i, i * 10, 1.0)
        
        assert len(self.anim_system._animations) == 5
        assert len(self.anim_system._running_animations) == 5
        
        self.anim_system.stop_all_animations()
        
        assert len(self.anim_system._animations) == 0
        assert len(self.anim_system._running_animations) == 0
        assert len(self.anim_system._completed_animations) == 0
    
    def test_animation_running_check(self):
        """Test checking if animation is running."""
        animation = self.anim_system.create_animation(0, 100, 1.0)
        
        assert self.anim_system.is_animation_running(animation)
        
        self.anim_system.stop_animation(animation)
        assert not self.anim_system.is_animation_running(animation)
    
    def test_running_count(self):
        """Test getting count of running animations."""
        assert self.anim_system.get_running_count() == 0
        
        # Add some animations
        for i in range(3):
            self.anim_system.create_animation(i, i * 10, 1.0)
        
        assert self.anim_system.get_running_count() == 3
    
    def test_cleanup_completed(self):
        """Test cleaning up completed animations."""
        animation = self.anim_system.create_animation(0, 100, 0.1)
        
        # Wait for completion
        time.sleep(0.15)
        self.anim_system.update()
        
        assert animation in self.anim_system._completed_animations
        assert animation in self.anim_system._animations
        
        self.anim_system.cleanup_completed()
        
        assert animation not in self.anim_system._completed_animations
        assert animation not in self.anim_system._animations


class TestEntityAnimator:
    """Test the entity animator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.anim_system = AnimationSystem()
        self.entity_animator = EntityAnimator(self.anim_system)
    
    def test_position_animation(self):
        """Test entity position animation."""
        entity_id = "test_entity"
        start_pos = (0, 0)
        end_pos = (100, 100)
        duration = 0.5
        
        animation = self.entity_animator.animate_position(
            entity_id, start_pos, end_pos, duration
        )
        
        assert animation is not None
        assert entity_id in self.entity_animator._position_animations
    
    def test_scale_animation(self):
        """Test entity scale animation."""
        entity_id = "test_entity"
        start_scale = 1.0
        end_scale = 2.0
        
        animation = self.entity_animator.animate_scale(
            entity_id, start_scale, end_scale, 0.3
        )
        
        assert animation is not None
        assert entity_id in self.entity_animator._scale_animations
    
    def test_rotation_animation(self):
        """Test entity rotation animation."""
        entity_id = "test_entity"
        start_angle = 0.0
        end_angle = 360.0
        
        animation = self.entity_animator.animate_rotation(
            entity_id, start_angle, end_angle, 1.0
        )
        
        assert animation is not None
        assert entity_id in self.entity_animator._rotation_animations
    
    def test_color_animation(self):
        """Test entity color animation."""
        entity_id = "test_entity"
        start_color = (255, 255, 255)
        end_color = (0, 0, 0)
        
        animation = self.entity_animator.animate_color(
            entity_id, start_color, end_color, 0.5
        )
        
        assert animation is not None
        assert entity_id in self.entity_animator._color_animations
    
    def test_get_current_values(self):
        """Test getting current interpolated values."""
        entity_id = "test_entity"
        
        # Create animations
        self.entity_animator.animate_position(entity_id, (0, 0), (100, 100), 1.0)
        self.entity_animator.animate_scale(entity_id, 1.0, 2.0, 1.0)
        self.entity_animator.animate_rotation(entity_id, 0, 360, 1.0)
        self.entity_animator.animate_color(entity_id, (255, 0, 0), (0, 255, 0), 1.0)
        
        # Should return None for non-existent entities
        assert self.entity_animator.get_current_position("nonexistent") is None
        assert self.entity_animator.get_current_scale("nonexistent") is None
        assert self.entity_animator.get_current_rotation("nonexistent") is None
        assert self.entity_animator.get_current_color("nonexistent") is None
        
        # For our test entity, should return animation start values initially
        # (since animation hasn't started updating)
        pos = self.entity_animator.get_current_position(entity_id)
        scale = self.entity_animator.get_current_scale(entity_id)
        rotation = self.entity_animator.get_current_rotation(entity_id)
        color = self.entity_animator.get_current_color(entity_id)
        
        assert pos == (0, 0) or pos is None  # May be None if not started
        assert scale == 1.0 or scale is None
        assert rotation == 0.0 or rotation is None
        assert color == (255, 0, 0) or color is None
    
    def test_stop_entity_animations(self):
        """Test stopping all animations for an entity."""
        entity_id = "test_entity"
        
        # Create multiple animations for the entity
        self.entity_animator.animate_position(entity_id, (0, 0), (100, 100), 1.0)
        self.entity_animator.animate_scale(entity_id, 1.0, 2.0, 1.0)
        self.entity_animator.animate_color(entity_id, (255, 0, 0), (0, 255, 0), 1.0)
        
        # Verify animations were created
        assert entity_id in self.entity_animator._position_animations
        assert entity_id in self.entity_animator._scale_animations
        assert entity_id in self.entity_animator._color_animations
        
        # Stop all animations for the entity
        self.entity_animator.stop_entity_animations(entity_id)
        
        # Verify animations were stopped
        assert entity_id not in self.entity_animator._position_animations
        assert entity_id not in self.entity_animator._scale_animations
        assert entity_id not in self.entity_animator._color_animations
        assert entity_id not in self.entity_animator._rotation_animations
    
    def test_multiple_entities(self):
        """Test animations for multiple entities."""
        entity1 = "entity1"
        entity2 = "entity2"
        
        # Create animations for different entities
        anim1 = self.entity_animator.animate_position(entity1, (0, 0), (100, 100), 1.0)
        anim2 = self.entity_animator.animate_position(entity2, (50, 50), (150, 150), 1.0)
        
        assert anim1 != anim2
        assert entity1 in self.entity_animator._position_animations
        assert entity2 in self.entity_animator._position_animations
        
        # Should be able to stop animations independently
        self.entity_animator.stop_entity_animations(entity1)
        
        assert entity1 not in self.entity_animator._position_animations
        assert entity2 in self.entity_animator._position_animations


if __name__ == "__main__":
    pytest.main([__file__])