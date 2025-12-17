"""Animation system for smooth entity movement and effects."""

import math
import time
from typing import Tuple, Optional, Callable, List, Any
from dataclasses import dataclass


@dataclass
class Animation:
    """Base animation data class."""
    start_time: float
    duration: float
    start_value: Any
    end_value: Any
    easing_func: Callable[[float], float]
    on_complete: Optional[Callable[[], None]] = None


class EasingFunctions:
    """Collection of easing functions for animations."""
    
    @staticmethod
    def linear(t: float) -> float:
        """Linear interpolation."""
        return t
    
    @staticmethod
    def ease_in_quad(t: float) -> float:
        """Quadratic ease-in."""
        return t * t
    
    @staticmethod
    def ease_out_quad(t: float) -> float:
        """Quadratic ease-out."""
        return t * (2 - t)
    
    @staticmethod
    def ease_in_out_quad(t: float) -> float:
        """Quadratic ease-in-out."""
        if t < 0.5:
            return 2 * t * t
        return 1 - pow(-2 * t + 2, 2) / 2
    
    @staticmethod
    def ease_in_cubic(t: float) -> float:
        """Cubic ease-in."""
        return t * t * t
    
    @staticmethod
    def ease_out_cubic(t: float) -> float:
        """Cubic ease-out."""
        return 1 - pow(1 - t, 3)
    
    @staticmethod
    def ease_in_out_cubic(t: float) -> float:
        """Cubic ease-in-out."""
        if t < 0.5:
            return 4 * t * t * t
        return 1 - pow(-2 * t + 2, 3) / 2
    
    @staticmethod
    def ease_in_back(t: float) -> float:
        """Back ease-in (overshoot)."""
        c1 = 1.70158
        c3 = c1 + 1
        return c3 * t * t * t - c1 * t * t
    
    @staticmethod
    def ease_out_back(t: float) -> float:
        """Back ease-out (overshoot)."""
        c1 = 1.70158
        c3 = c1 + 1
        return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)
    
    @staticmethod
    def ease_out_elastic(t: float) -> float:
        """Elastic ease-out."""
        c4 = (2 * math.pi) / 3
        if t == 0:
            return 0
        if t == 1:
            return 1
        return pow(2, -10 * t) * math.sin((t * 10 - 0.75) * c4) + 1


class AnimationSystem:
    """Manages and updates all game animations."""
    
    def __init__(self):
        self._animations: List[Animation] = []
        self._running_animations: List[Animation] = []
        self._completed_animations: List[Animation] = []
    
    def update(self) -> None:
        """Update all running animations."""
        current_time = time.time()
        self._completed_animations.clear()
        
        for animation in self._running_animations[:]:  # Copy list to allow modification
            progress = (current_time - animation.start_time) / animation.duration
            
            if progress >= 1.0:
                # Animation complete
                progress = 1.0
                self._running_animations.remove(animation)
                self._completed_animations.append(animation)
                
                if animation.on_complete:
                    animation.on_complete()
            
            # Store progress for interpolation
            animation.current_progress = animation.easing_func(progress)
    
    def create_animation(self, start_value: Any, end_value: Any, duration: float,
                        easing_func: Callable[[float], float] = EasingFunctions.ease_out_quad,
                        delay: float = 0.0,
                        on_complete: Optional[Callable[[], None]] = None) -> Animation:
        """Create a new animation."""
        start_time = time.time() + delay
        animation = Animation(
            start_time=start_time,
            duration=duration,
            start_value=start_value,
            end_value=end_value,
            easing_func=easing_func,
            on_complete=on_complete
        )
        
        self._animations.append(animation)
        
        # Add to running animations after delay
        if delay <= 0:
            self._running_animations.append(animation)
        else:
            # Will be added to running animations when delay passes
            pass
        
        return animation
    
    def interpolate_position(self, animation: Animation) -> Tuple[float, float]:
        """Interpolate between two positions."""
        if not hasattr(animation, 'current_progress'):
            return animation.start_value
        
        t = animation.current_progress
        start_x, start_y = animation.start_value
        end_x, end_y = animation.end_value
        
        current_x = start_x + (end_x - start_x) * t
        current_y = start_y + (end_y - start_y) * t
        
        return (current_x, current_y)
    
    def interpolate_float(self, animation: Animation) -> float:
        """Interpolate between two float values."""
        if not hasattr(animation, 'current_progress'):
            return animation.start_value
        
        t = animation.current_progress
        return animation.start_value + (animation.end_value - animation.start_value) * t
    
    def interpolate_color(self, animation: Animation) -> Tuple[int, int, int]:
        """Interpolate between two RGB colors."""
        if not hasattr(animation, 'current_progress'):
            return animation.start_value
        
        t = animation.current_progress
        start_r, start_g, start_b = animation.start_value
        end_r, end_g, end_b = animation.end_value
        
        current_r = int(start_r + (end_r - start_r) * t)
        current_g = int(start_g + (end_g - start_g) * t)
        current_b = int(start_b + (end_b - start_b) * t)
        
        return (current_r, current_g, current_b)
    
    def stop_animation(self, animation: Animation) -> None:
        """Stop a specific animation."""
        if animation in self._running_animations:
            self._running_animations.remove(animation)
        
        if animation in self._animations:
            self._animations.remove(animation)
    
    def stop_all_animations(self) -> None:
        """Stop all running animations."""
        self._running_animations.clear()
        self._animations.clear()
        self._completed_animations.clear()
    
    def is_animation_running(self, animation: Animation) -> bool:
        """Check if an animation is currently running."""
        return animation in self._running_animations
    
    def get_running_count(self) -> int:
        """Get the number of currently running animations."""
        return len(self._running_animations)
    
    def cleanup_completed(self) -> None:
        """Remove completed animations from the main list."""
        for animation in self._completed_animations:
            if animation in self._animations:
                self._animations.remove(animation)
        self._completed_animations.clear()


class EntityAnimator:
    """Specialized animator for game entities."""
    
    def __init__(self, animation_system: AnimationSystem):
        self.animation_system = animation_system
        self._position_animations = {}
        self._scale_animations = {}
        self._rotation_animations = {}
        self._color_animations = {}
    
    def animate_position(self, entity_id: str, start_pos: Tuple[float, float], 
                        end_pos: Tuple[float, float], duration: float,
                        easing_func: Callable[[float], float] = EasingFunctions.ease_out_quad) -> Animation:
        """Animate entity position."""
        animation = self.animation_system.create_animation(
            start_pos, end_pos, duration, easing_func
        )
        self._position_animations[entity_id] = animation
        return animation
    
    def animate_scale(self, entity_id: str, start_scale: float, 
                     end_scale: float, duration: float,
                     easing_func: Callable[[float], float] = EasingFunctions.ease_out_elastic) -> Animation:
        """Animate entity scale."""
        animation = self.animation_system.create_animation(
            start_scale, end_scale, duration, easing_func
        )
        self._scale_animations[entity_id] = animation
        return animation
    
    def animate_rotation(self, entity_id: str, start_angle: float, 
                        end_angle: float, duration: float,
                        easing_func: Callable[[float], float] = EasingFunctions.ease_out_quad) -> Animation:
        """Animate entity rotation."""
        animation = self.animation_system.create_animation(
            start_angle, end_angle, duration, easing_func
        )
        self._rotation_animations[entity_id] = animation
        return animation
    
    def animate_color(self, entity_id: str, start_color: Tuple[int, int, int], 
                     end_color: Tuple[int, int, int], duration: float,
                     easing_func: Callable[[float], float] = EasingFunctions.ease_in_out_quad) -> Animation:
        """Animate entity color."""
        animation = self.animation_system.create_animation(
            start_color, end_color, duration, easing_func
        )
        self._color_animations[entity_id] = animation
        return animation
    
    def get_current_position(self, entity_id: str) -> Optional[Tuple[float, float]]:
        """Get current interpolated position for an entity."""
        if entity_id in self._position_animations:
            animation = self._position_animations[entity_id]
            return self.animation_system.interpolate_position(animation)
        return None
    
    def get_current_scale(self, entity_id: str) -> Optional[float]:
        """Get current interpolated scale for an entity."""
        if entity_id in self._scale_animations:
            animation = self._scale_animations[entity_id]
            return self.animation_system.interpolate_float(animation)
        return None
    
    def get_current_rotation(self, entity_id: str) -> Optional[float]:
        """Get current interpolated rotation for an entity."""
        if entity_id in self._rotation_animations:
            animation = self._rotation_animations[entity_id]
            return self.animation_system.interpolate_float(animation)
        return None
    
    def get_current_color(self, entity_id: str) -> Optional[Tuple[int, int, int]]:
        """Get current interpolated color for an entity."""
        if entity_id in self._color_animations:
            animation = self._color_animations[entity_id]
            return self.animation_system.interpolate_color(animation)
        return None
    
    def stop_entity_animations(self, entity_id: str) -> None:
        """Stop all animations for a specific entity."""
        for anim_dict in [self._position_animations, self._scale_animations, 
                          self._rotation_animations, self._color_animations]:
            if entity_id in anim_dict:
                animation = anim_dict[entity_id]
                self.animation_system.stop_animation(animation)
                del anim_dict[entity_id]