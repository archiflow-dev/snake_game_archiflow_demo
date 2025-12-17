"""Enhanced hexagonal snake with animation support."""

import math
import time
from typing import List, Optional, Dict, Any
from ..grids.hex_grid import HexGrid
from ..grids.grid_new import HexCoord
from ..entities.hex_snake_enhanced import HexSnakeEnhanced
from ..utils.animation_new import AnimationManager, ParticleSystem


class HexSnakeAnimated(HexSnakeEnhanced):
    """Hex snake with smooth animations and visual effects."""
    
    def __init__(self, start_position: HexCoord, start_direction, grid: HexGrid,
                 start_length: int = 3, personality: str = "balanced",
                 animation_speed: float = 1.0):
        # Initialize base snake
        super().__init__(start_position, start_direction, start_length, personality)
        
        self.grid = grid
        self.animation_speed = animation_speed
        
        # Animation state
        self.segment_animations: Dict[str, Any] = {}
        self.target_segments: List[HexCoord] = []
        self.interpolation_progress = 0.0
        
        # Visual effects
        self.trail_positions: List[Tuple[float, float]] = []
        self.trail_alpha = 1.0
        self.glow_intensity = 0.0
        self.eating_animation_time = 0.0
        
        # Animation manager
        self.animation_manager = AnimationManager()
        self.particle_system = ParticleSystem()
        
        # Initialize animations
        self._init_segment_animations()
        self.target_segments = self.segments.copy()
    
    def _init_segment_animations(self) -> None:
        """Initialize animation states for each segment."""
        for i in range(len(self.segments)):
            self.segment_animations[f"segment_{i}"] = {
                'scale': 1.0,
                'rotation': 0.0,
                'pulse': 0.0,
                'slide': 0.0
                'target_scale': 1.0,
                'target_rotation': 0.0
                'color_shift': (0, 0, 0)
            }
    
    def update_animations(self, dt: float) -> None:
        """Update all animations."""
        # Update animation manager
        self.animation_manager.update_all(dt)
        
        # Update each segment's animations
        for i in range(len(self.segments)):
            segment_key = f"segment_{i}"
            if segment_key in self.segment_animations:
                anim = self.segment_animations[segment_key]
                
                # Scale animation for growth
                if self.growth_pending > 0 and i >= len(self.segments) - self.growth_pending:
                    anim['target_scale'] = 1.2
                    anim['scale'] = self.animation_manager.update_interpolation(
                        f"{segment_key}_scale", anim['scale'], 1.0, 0.3
                    )
                
                # Rotation animation for movement
                if i == 0:  # Head segment
                    anim['target_rotation'] = self._get_head_rotation()
                    anim['rotation'] = self.animation_manager.update_interpolation(
                        f"{segment_key}_rotation", anim['rotation'], 
                        anim['target_rotation'], 0.2
                    )
                
                # Pulse animation for active effects
                if self.special_effects:
                    anim['pulse'] = self.animation_manager.update_interpolation(
                        f"{segment_key}_pulse", anim['pulse'], 1.0, 2.0
                    )
                
                # Update animation values
                anim['scale'] = max(0.5, anim['scale'])
                anim['pulse'] = max(0.0, min(2.0, anim['pulse']))
    
    def _get_head_rotation(self) -> float:
        """Get target rotation based on movement direction."""
        # Map direction to rotation angle
        direction_map = {
            'E': 0,
            'NE': 60,
            'NW': 120,
            'W': 180,
            'SW': 240,
            'SE': 300
        }
        
        if hasattr(self.direction, 'get_dx_dy'):
            dx, dy = self.direction.get_dx_dy()
            if dx > 0 and dy == 0:
                return direction_map['E']
            elif dx > 0 and dy < 0:
                return direction_map['SE']
            elif dx == 0 and dy < 0:
                return direction_map['SW']
            elif dx < 0 and dy < 0:
                return direction_map['W']
            elif dx < 0 and dy > 0:
                return direction_map['NW']
            elif dx == 0 and dy > 0:
                return direction_map['NE']
        
        return 0.0
    
    def update_particles(self, dt: float) -> None:
        """Update particle effects."""
        self.particle_system.update(dt)
        
        # Emit particles for special effects
        if self.special_effects and len(self.segments) > 0:
            head = self.segments[0]
            head_pos = self.grid.get_hex_center(head)
            
            # Emit particles based on current effects
            if 'trail' in self.special_effects and self.animation_manager.animation_time % 0.1 < 0.05:
                self.particle_system.emit_particles(head_pos[0], head_pos[1], 3, 
                    color=(255, 255, 100), velocity_range=(20, 50))
            
            if 'glow' in self.special_effects:
                self.glow_intensity = min(1.0, self.animation_manager.animation_time % 1.0)
        
        # Eating animation particles
        if self.eating_animation_time > 0:
            if len(self.segments) > 0:
                mouth_pos = self._get_mouth_position()
                self.particle_system.emit_particles(
                    mouth_pos[0], mouth_pos[1], 5,
                    color=(255, 255, 0), velocity_range=(100, 200)
                )
                self.eating_animation_time -= dt
                if self.eating_animation_time <= 0:
                    self.eating_animation_time = 0
    
    def _get_mouth_position(self) -> Tuple[float, float]:
        """Get approximate mouth position for particle effects."""
        if len(self.segments) < 2:
            head = self.segments[0]
        else:
            head = self.segments[0]
            neck = self.segments[1]
            
            # Calculate mouth position based on movement
            head_pos = self.grid.get_hex_center(head)
            neck_pos = self.grid.get_hex_center(neck)
            
            # Mouth is in direction of movement from head to neck
            dx = head_pos[0] - neck_pos[0]
            dy = head_pos[1] - neck_pos[1]
            
            # Normalize and extend
            length = math.sqrt(dx*dx + dy*dy) + 1
            dx = (dx / length) * 10
            dy = (dy / length) * 10
            
            return (head_pos[0] + dx, head_pos[1] + dy)
        
        return head_pos
    
    def update_trail(self, dt: float) -> None:
        """Update trail effect."""
        if not self.segments:
            return
        
        head = self.segments[0]
        head_pos = self.grid.get_hex_center(head)
        
        # Add current head position to trail
        self.trail_positions.append(head_pos)
        
        # Limit trail length
        max_trail_length = len(self.segments) + 3
        if len(self.trail_positions) > max_trail_length:
            self.trail_positions = self.trail_positions[-max_trail_length:]
        
        # Update trail alpha for fade effect
        self.trail_alpha = max(0.0, min(1.0, self.trail_alpha + dt * 2))
    
    def get_animated_render_data(self) -> Dict[str, Any]:
        """Get render data with animations and effects."""
        render_data = {}
        
        for i in range(len(self.segments)):
            segment_key = f"segment_{i}"
            anim = self.segment_animations.get(segment_key, {})
            
            # Calculate animated position
            segment = self.segments[i]
            base_pos = self.grid.get_hex_center(segment)
            
            # Apply animation transforms
            scale = anim.get('scale', 1.0)
            rotation = anim.get('rotation', 0.0)
            pulse = anim.get('pulse', 0.0)
            color_shift = anim.get('color_shift', (0, 0, 0))
            
            # Apply scale (for growth effects)
            if scale != 1.0:
                size = int(20 * scale)  # Hex size * scale
            # Would need to recalculate vertices for actual scaling
                # For now, just modify color intensity
                base_color = self._get_base_color(i)
                r, g, b = base_color
                intensity = min(255, int(255 * scale))
                render_data[f"segment_{i}_color"] = (int(r * intensity), int(g * intensity), int(b * intensity))
            else:
                render_data[f"segment_{i}_color"] = self._get_base_color(i)
            
            # Apply rotation (primarily for head)
            if rotation != 0.0 and i == 0:
                render_data[f"segment_{i}_rotation"] = math.radians(rotation)
            
            # Apply pulse (breathing effect)
            if pulse != 0.0:
                pulse_factor = (math.sin(pulse * math.pi) + 1) / 2
                render_data[f"segment_{i}_pulse"] = pulse_factor
            else:
                render_data[f"segment_{i}_pulse"] = 1.0
            
            # Store position
            render_data[f"segment_{i}_pos"] = self.grid.get_hex_center(segment)
        
        # Trail data
        render_data['trail_positions'] = self.trail_positions
        render_data['trail_alpha'] = self.trail_alpha
        
        # Glow effect
        render_data['glow_intensity'] = self.glow_intensity
        
        # Particle data
        render_data['particles'] = self.particle_system.get_particles()
        
        # Eating animation
        render_data['eating_animation'] = self.eating_animation_time > 0
        
        return render_data
    
    def _get_base_color(self, segment_index: int) -> Tuple[int, int, int]:
        """Get base color for a segment."""
        if segment_index == 0:  # Head
            base_color = (0, 255, 100)  # Green head
        else:
            # Gradient body colors
            t = segment_index / max(1, len(self.segments) - 1)
            r = int(0 + t * 50)
            g = int(200 - t * 100)
            b = int(100 + t * 50)
            base_color = (r, g, b)
        
        return base_color
    
    def start_eating_animation(self) -> None:
        """Trigger eating animation."""
        self.eating_animation_time = 0.5  # Duration in seconds
    
    def set_animation_speed(self, speed: float) -> None:
        """Set animation speed multiplier."""
        self.animation_speed = max(0.1, min(3.0, speed))
        self.animation_manager.set_time_scale(self.animation_speed)
    
    def set_special_effects(self, effects: List[str]) -> None:
        """Set special visual effects."""
        self.special_effects = effects
    
    def get_animation_state(self) -> Dict[str, Any]:
        """Get current animation state."""
        return {
            'animation_speed': self.animation_speed,
            'special_effects': self.special_effects,
            'glow_intensity': self.glow_intensity,
            'trail_alpha': self.trail_alpha,
            'particle_count': len(self.particle_system.get_particles()),
            'eating_animation': self.eating_animation_time > 0,
            'active_animations': len(self.segment_animations)
        }
    
    def add_burst_effect(self, position: HexCoord, count: int = 20, 
                        colors: List[Tuple[int, int, int]] = None) -> None:
        """Add particle burst effect."""
        if colors is None:
            colors = [(255, 100, 100), (100, 255, 100), (100, 100, 255)]
        
        pos = self.grid.get_hex_center(position)
        for color in colors:
            self.particle_system.emit_particles(pos[0], pos[1], count // len(colors), color, (50, 150))
    
    def reset_animations(self) -> None:
        """Reset all animations to initial state."""
        self.segment_animations.clear()
        self._init_segment_animations()
        self.trail_positions.clear()
        self.trail_alpha = 1.0
        self.glow_intensity = 0.0
        self.eating_animation_time = 0.0
        self.particle_system.clear()
        self.animation_manager = AnimationManager()
    
    def update(self, dt: float) -> Optional[HexCoord]:
        """Update snake with animations."""
        # Update animations
        self.update_animations(dt)
        self.update_particles(dt)
        self.update_trail(dt)
        
        # Move snake with interpolation
        if len(self.segments) > 0:
            # Calculate interpolated movement
            self.interpolation_progress += dt / 0.1  # 100ms per move
            
            if self.interpolation_progress >= 1.0:
                # Complete the move
                tail = self.move()
                self.interpolation_progress = 0.0
                self.target_segments = self.segments.copy()
                return tail
            else:
                # Interpolate between current and target positions
                for i in range(len(self.segments)):
                    if i < len(self.target_segments):
                        current = self.segments[i]
                        target = self.target_segments[i]
                        
                        # Interpolate position
                        current_pos = self.grid.get_hex_center(current)
                        target_pos = self.grid.get_hex_center(target)
                        
                        # Update segment position for rendering
                        current.q, current.r = self._interpolate_pos(
                            current_pos, target_pos, self.interpolation_progress
                        )
        
        return None