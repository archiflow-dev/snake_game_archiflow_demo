"""Animation and interpolation system for Phase 4."""

import time
from typing import List, Callable, Any, Dict
import math


class Animation:
    """Base class for all animations."""
    
    def __init__(self, duration: float, easing: str = "linear"):
        self.duration = duration
        self.easing = easing
        self.start_time = None
        self.is_running = False
        self.current_time = 0.0
        self.is_complete = False
    
    def start(self) -> None:
        """Start the animation."""
        self.start_time = time.time()
        self.is_running = True
        self.is_complete = False
        self.current_time = 0.0
    
    def update(self, dt: float) -> float:
        """Update animation and return progress (0.0 to 1.0)."""
        if not self.is_running:
            return 1.0
        
        self.current_time += dt
        progress = min(self.current_time / self.duration, 1.0)
        
        if progress >= 1.0:
            self.is_complete = True
            self.is_running = False
            return 1.0
        
        return self._apply_easing(progress)
    
    def _apply_easing(self, t: float) -> float:
        """Apply easing function to progress value."""
        if self.easing == "linear":
            return t
        elif self.easing == "ease_in":
            return t * t
        elif self.easing == "ease_out":
            return 1.0 - (1.0 - t) * (1.0 - t)
        elif self.easing == "ease_in_out":
            return t * t * (3.0 - 2.0 * t)
        elif self.easing == "bounce":
            if t < 0.5:
                return 2.0 * t * t
            else:
                return 1.0 - 2.0 * (1.0 - t) * (1.0 - t)
        else:
            return t
    
    def get_progress(self) -> float:
        """Get current progress of animation."""
        if not self.is_running:
            return 1.0 if self.is_complete else 0.0
        return min(self.current_time / self.duration, 1.0)


class Interpolator:
    """Handles smooth interpolation between positions."""
    
    @staticmethod
    def lerp(start: Any, end: Any, t: float) -> Any:
        """Linear interpolation between two values."""
        if isinstance(start, (int, float)):
            return start + (end - start) * t
        elif isinstance(start, (list, tuple)):
            if isinstance(start, tuple):
                return tuple(Interpolator.lerp(s, e, t) for s, e in zip(start, end))
            else:
                return [Interpolator.lerp(s, e, t) for s, e in zip(start, end)]
        else:
            return end if t >= 1.0 else start
    
    @staticmethod
    def slerp(start: Any, end: Any, t: float) -> Any:
        """Spherical interpolation for rotations."""
        diff = end - start
        return start + diff * t
    
    @staticmethod
    def bezier(start: Any, control: Any, end: Any, t: float) -> Any:
        """Quadratic bezier interpolation."""
        inv_t = 1.0 - t
        return (inv_t * inv_t * start) + (2 * inv_t * t * control) + (t * t * end)


class AnimationManager:
    """Manages multiple animations and interpolation."""
    
    def __init__(self):
        self.animations: Dict[str, Animation] = {}
        self.interpolators: Dict[str, Dict[str, Any]] = {}
        self.global_time_scale = 1.0
    
    def create_animation(self, name: str, duration: float, easing: str = "linear") -> Animation:
        """Create a new animation."""
        animation = Animation(duration, easing)
        self.animations[name] = animation
        return animation
    
    def start_animation(self, name: str) -> None:
        """Start an animation by name."""
        if name in self.animations:
            self.animations[name].start()
    
    def update_animation(self, name: str, dt: float) -> float:
        """Update a specific animation."""
        if name in self.animations:
            return self.animations[name].update(dt * self.global_time_scale)
        return 0.0
    
    def is_animation_complete(self, name: str) -> bool:
        """Check if an animation is complete."""
        return self.animations.get(name, Animation()).is_complete if name in self.animations else True
    
    def set_time_scale(self, scale: float) -> None:
        """Set global time scale for all animations."""
        self.global_time_scale = max(0.1, min(3.0, scale))
    
    def clean_completed_animations(self) -> None:
        """Remove completed animations."""
        completed = [name for name, anim in self.animations.items() if anim.is_complete]
        for name in completed:
            del self.animations[name]
    
    def get_all_progress(self) -> Dict[str, float]:
        """Get progress of all active animations."""
        return {name: anim.get_progress() for name, anim in self.animations.items()}
    
    def create_interpolation(self, name: str, start: Any, end: Any, duration: float) -> None:
        """Create an interpolation between two values."""
        self.interpolators[name] = {
            'start': start,
            'end': end,
            'duration': duration,
            'current': 0.0,
            'active': True
        }
    
    def update_interpolation(self, name: str, dt: float) -> Any:
        """Update an interpolation and return current value."""
        if name not in self.interpolators or not self.interpolators[name]['active']:
            return self.interpolators[name]['end'] if name in self.interpolators else None
        
        interp = self.interpolators[name]
        interp['current'] += dt / interp['duration']
        
        if interp['current'] >= 1.0:
            interp['active'] = False
            return interp['end']
        
        t = min(interp['current'], 1.0)
        return Interpolator.lerp(interp['start'], interp['end'], t)
    
    def is_interpolation_complete(self, name: str) -> bool:
        """Check if interpolation is complete."""
        return not self.interpolators.get(name, {}).get('active', False)


class Particle:
    """Simple particle effect."""
    
    def __init__(self, x: float, y: float, vx: float = 0.0, vy: float = 0.0,
                 color: tuple = (255, 255, 255), size: float = 3.0,
                 lifetime: float = 1.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.initial_size = size
    
    def update(self, dt: float) -> bool:
        """Update particle. Returns False when particle should be removed."""
        self.lifetime -= dt
        
        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Apply gravity
        self.vy += 200.0 * dt  # Simple gravity
        
        # Fade out
        self.size = self.initial_size * self.lifetime / self.max_lifetime
        
        return self.lifetime <= 0


class ParticleSystem:
    """Manages multiple particle effects."""
    
    def __init__(self, max_particles: int = 100):
        self.particles: List[Particle] = []
        self.max_particles = max_particles
    
    def emit_particles(self, x: float, y: float, count: int = 10, 
                      color: tuple = (255, 255, 255), 
                      velocity_range: tuple = (50.0, 150.0)):
        """Emit particles at a specific position."""
        import random
        
        for _ in range(min(count, self.max_particles - len(self.particles))):
            vx = random.uniform(-velocity_range[0], velocity_range[0])
            vy = random.uniform(-velocity_range[1], velocity_range[1])
            
            particle = Particle(x, y, vx, vy, color=color, lifetime=random.uniform(0.5, 1.5))
            self.particles.append(particle)
    
    def update(self, dt: float) -> None:
        """Update all particles."""
        self.particles = [p for p in self.particles if p.update(dt)]
    
    def get_particles(self) -> List[Particle]:
        """Get all active particles."""
        return self.particles.copy()
    
    def clear(self) -> None:
        """Clear all particles."""
        self.particles.clear()
    
    def get_particle_count(self) -> int:
        """Get current particle count."""
        return len(self.particles)


class ScreenShake:
    """Screen shake effect for impacts."""
    
    def __init__(self, intensity: float = 10.0, duration: float = 0.3):
        self.intensity = intensity
        self.duration = duration
        self.current_time = 0.0
        self.is_active = False
    
    def start(self, intensity: float = None, duration: float = None) -> None:
        """Start screen shake with optional parameters."""
        self.intensity = intensity if intensity is not None else self.intensity
        self.duration = duration if duration is not None else self.duration
        self.current_time = 0.0
        self.is_active = True
    
    def update(self, dt: float) -> tuple[int, int]:
        """Update screen shake and return offset."""
        if not self.is_active:
            return (0, 0)
        
        self.current_time += dt
        progress = min(self.current_time / self.duration, 1.0)
        
        if progress >= 1.0:
            self.is_active = False
            return (0, 0)
        
        # Calculate shake with falloff
        falloff = 1.0 - progress
        shake_x = (random.random() - 0.5) * self.intensity * falloff
        shake_y = (random.random() - 0.5) * self.intensity * falloff
        
        return (int(shake_x), int(shake_y))