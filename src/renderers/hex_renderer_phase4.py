"""Enhanced hexagonal renderer with Phase 4 effects."""

import pygame
import math
import time
from typing import List, Tuple, Optional, Dict, Any
from ..grids.hex_grid import HexGrid
from ..grids.grid_new import HexCoord
from ..core.config import GameConfig
from ..utils.animation_new import AnimationManager, ParticleSystem, ScreenShake
from ..entities.hex_snake_animated import HexSnakeAnimated


class Phase4HexRenderer:
    """Enhanced renderer for Phase 4 hexagonal grid."""
    
    def __init__(self, screen: pygame.Surface, hex_grid: HexGrid, config: GameConfig):
        self.screen = screen
        self.hex_grid = hex_grid
        self.config = config
        
        # Visual effects systems
        self.animation_manager = AnimationManager()
        self.particle_system = ParticleSystem(max_particles=200)
        self.screen_shake = ScreenShake(intensity=5.0, duration=0.2)
        
        # Enhanced color schemes with gradients and effects
        self.colors = {
            'background': (10, 10, 30),
            'grid_line': (60, 60, 80),
            'hex_fill': (20, 20, 40),
            'hex_fill_alternate': (15, 15, 35),
            'hex_border': (100, 100, 120),
            'snake_head': (0, 255, 100),
            'snake_head_alt': (0, 200, 80),
            'snake_body': (0, 200, 80),
            'snake_body_alt': (0, 150, 60),
            'snake_glow': (100, 255, 150),
            'food_normal': (255, 100, 100),
            'food_special': (255, 215, 0),
            'food_glow': (255, 200, 150),
            'particle_default': (255, 255, 255),
            'particle_collect': (100, 255, 100),
            'particle_explosion': (255, 200, 100),
            'particle_trail': (150, 200, 255)
            'highlight': (255, 255, 100),
            'shadow': (0, 0, 0, 80)
        }
        
        # Animation timing
        self.hex_pulse_phase = 0.0
        self.food_rotation = 0.0
        self.food_scale = 1.0
        self.glow_effect_phase = 0.0
        
        # Particle effects for different events
        self.event_particles: Dict[str, Any] = {}
        
        # Visual quality settings
        self.render_quality = "high"  # "low", "medium", "high"
        self.enable_shadows = True
        self.enable_glow = True
        self.enable_particles = True
        self.enable_animations = True
        
        # Performance metrics
        self.frame_count = 0
        self.last_frame_time = time.time()
    
    def draw_grid(self) -> None:
        """Draw enhanced hexagonal grid with animations."""
        all_cells = self.hex_grid.get_all_cells()
        
        for i, cell in enumerate(all_cells):
            # Animated grid fill
            fill_color = self._get_animated_grid_color(cell, i)
            
            vertices = self.hex_grid.get_hex_vertices(cell)
            
            # Draw filled hex
            pygame.draw.polygon(self.screen, fill_color, vertices)
            
            # Draw border with glow effect
            if self.enable_glow:
                glow_vertices = self._get_glow_vertices(vertices, 3)
                pygame.draw.polygon(self.screen, (50, 50, 100), glow_vertices)
            
            # Draw outline
            pygame.draw.polygon(self.screen, self.colors['hex_border'], vertices, 2)
    
    def _get_animated_grid_color(self, cell: HexCoord, index: int) -> Tuple[int, int, int]:
        """Get animated color for grid cells."""
        # Subtle pulsing effect
        self.hex_pulse_phase += 0.05
        pulse = (math.sin(self.hex_pulse_phase) + 1.0) / 2.0
        
        # Base colors with alternating pattern
        base_colors = [self.colors['hex_fill'], self.colors['hex_fill_alternate']]
        base_color = base_colors[index % 2]
        
        # Apply pulse effect
        r, g, b = base_color
        pulse_modulation = int(pulse * 30)
        
        return (
            min(255, r + pulse_modulation),
            min(255, g + pulse_modulation),
            min(255, b + pulse_modulation)
        )
    
    def _get_glow_vertices(self, vertices: List[Tuple[int, int]], size: int) -> List[Tuple[int, int]]:
        """Get glow vertices for a polygon."""
        glow_vertices = []
        center_x = sum(v[0] for v in vertices) // len(vertices)
        center_y = sum(v[1] for v in vertices) // len(vertices)
        
        for vx, vy in vertices:
            # Expand vertices outward
            dx = vx - center_x
            dy = vy - center_y
            length = math.sqrt(dx*dx + dy*dy)
            
            if length > 0:
                expand_x = dx * (1 + size / length)
                expand_y = dy * (1 + size / length)
                
                glow_vertices.append((int(center_x + expand_x), int(center_y + expand_y)))
        
        return glow_vertices
    
    def draw_snake(self, snake: Any, interpolation: float = 0.0, 
                 theme_data: Optional[Dict] = None) -> None:
        """Draw enhanced snake with multiple rendering options."""
        if hasattr(snake, 'get_animated_render_data'):
            # Use animated snake data if available
            render_data = snake.get_animated_render_data()
            self._draw_animated_snake(render_data, theme_data)
        elif hasattr(snake, 'get_segments'):
            # Fallback to regular snake
            self._draw_regular_snake(snake, theme_data)
    
    def _draw_animated_snake(self, render_data: Dict[str, Any], 
                           theme_data: Optional[Dict] = None) -> None:
        """Draw snake with advanced animations."""
        segments = render_data.get('segments', [])
        animation_state = render_data.get('animation_state', {})
        particle_positions = render_data.get('trail_positions', [])
        
        # Draw trail effect
        if self.enable_particles and particle_positions:
            self._draw_snake_trail(particle_positions)
        
        # Draw segments with animations
        for i, segment in enumerate(segments):
            segment_data = self._get_segment_animation_data(i, len(segments), animation_state)
            
            # Get render position
            if i < len(segment_data['render_positions']):
                render_pos = self.hex_grid.hex_to_pixel(segment_data['render_positions'][i])
            else:
                render_pos = self.hex_grid.hex_to_pixel(segment)
            
            # Apply screen shake
            shake_offset = self.screen_shake.update(1/60) if self.screen_shake.is_active else (0, 0)
            actual_pos = (render_pos[0] + shake_offset[0], render_pos[1] + shake_offset[1])
            
            # Draw hexagon
            self._draw_animated_hexagon(actual_pos, segment_data, i == 0, theme_data)
            
            # Draw special effects
            self._draw_segment_effects(actual_pos, segment_data, i == 0)
    
    def _draw_regular_snake(self, snake: Any, theme_data: Optional[Dict] = None) -> None:
        """Draw regular snake without animations."""
        segments = snake.get_segments()
        
        for i, segment in enumerate(segments):
            # Get render position
            render_pos = self.hex_grid.hex_to_pixel(segment)
            
            # Apply theme colors if available
            if theme_data and theme_data.get('snake_colors'):
                colors = theme_data['snake_colors']
            else:
                colors = self._get_default_snake_colors(i)
            
            # Draw hexagon
            vertices = self.hex_grid.get_hex_vertices(segment)
            pygame.draw.polygon(self.screen, colors['fill'], vertices)
            
            # Draw outline
            pygame.draw.polygon(self.screen, colors['outline'], vertices, 2)
            
            # Draw eyes on head
            if i == 0:
                self._draw_enhanced_eyes(vertices, colors['outline'])
            
            # Draw shadow effect
            if self.enable_shadows and i > 0:
                self._draw_segment_shadow(vertices, colors)
    
    def _get_segment_animation_data(self, segment_index: int, total_segments: int, 
                                   animation_state: Dict[str, Any]) -> Dict[str, Any]:
        """Get animation data for a snake segment."""
        # Scale based on segment position (tail segments smaller)
        base_scale = 1.0
        if segment_index > total_segments // 2:
            base_scale = 0.7 - (segment_index / total_segments) * 0.3
        
        # Animation modifiers
        scale = base_scale * animation_state.get('scale', 1.0)
        rotation = animation_state.get('rotation', 0.0)
        pulse = animation_state.get('pulse', 1.0)
        
        return {
            'scale': scale,
            'rotation': rotation,
            'pulse': pulse,
            'color_shift': animation_state.get('color_shift', (0, 0, 0)),
            'render_positions': animation_state.get('render_positions', [])
        }
    
    def _get_default_snake_colors(self, segment_index: int) -> Dict[str, Tuple[int, int, int]]:
        """Get default colors for snake segments."""
        if segment_index == 0:  # Head
            return {
                'fill': self.colors['snake_head'],
                'outline': self.colors['snake_head_alt']
            }
        else:  # Body
            body_colors = [self.colors['snake_body'], self.colors['snake_body_alt']]
            return {
                'fill': body_colors[segment_index % 2],
                'outline': self.colors['snake_body_alt']
            }
    
    def _draw_animated_hexagon(self, pos: Tuple[int, int], segment_data: Dict[str, Any], 
                            is_head: bool, theme_data: Optional[Dict] = None) -> None:
        """Draw animated hexagon with effects."""
        # Get vertices
        temp_coord = self.hex_grid._pixel_to_hex(pos)
        if temp_coord:
            vertices = self.hex_grid.get_hex_vertices(temp_coord)
        else:
            return
        
        # Apply transformations
        scale = segment_data.get('scale', 1.0)
        rotation = segment_data.get('rotation', 0.0)
        pulse = segment_data.get('pulse', 1.0)
        color_shift = segment_data.get('color_shift', (0, 0, 0))
        
        # Transform vertices
        center_x = sum(v[0] for v in vertices) // len(vertices)
        center_y = sum(v[1] for v in vertices) // len(vertices)
        
        transformed_vertices = []
        for vx, vy in vertices:
            # Scale
            sx = vx - center_x
            sy = vy - center_y
            
            # Rotate
            cos_r = math.cos(rotation)
            sin_r = math.sin(rotation)
            rx = sx * cos_r - sy * sin_r
            ry = sx * sin_r + sy * cos_r
            
            # Scale back
            tx = rx * scale + center_x
            ty = ry * scale + center_y
            
            transformed_vertices.append((int(tx), int(ty)))
        
        # Apply color modifications
        base_color = segment_data.get('fill_color', self.colors['snake_body'])
        
        # Apply color shift
        r, g, b = base_color
        r = min(255, max(0, r + color_shift[0]))
        g = min(255, max(0, g + color_shift[1]))
        b = min(255, max(0, b + color_shift[2]))
        final_color = (int(r), int(g), int(b))
        
        # Apply pulse effect
        if pulse != 1.0:
            brightness = (math.sin(pulse * math.pi) + 1.0) / 2.0
            final_color = tuple(int(c * brightness) for c in final_color)
        
        # Apply theme colors if available
        if theme_data and theme_data.get('snake_colors'):
            theme_colors = theme_data['snake_colors']
            if is_head and 'snake_head' in theme_colors:
                base_color = theme_colors['snake_head']
            elif not is_head and 'snake_body' in theme_colors:
                base_color = theme_colors['snake_body']
        
            r, g, b = base_color
            final_color = (int(r), int(g), int(b))
        
        # Draw with glow effect
        if self.enable_glow:
            glow_vertices = self._get_glow_vertices(transformed_vertices, 2)
            glow_color = tuple(c // 2 for c in final_color)
            pygame.draw.polygon(self.screen, glow_color, glow_vertices)
        
        # Draw main hexagon
        pygame.draw.polygon(self.screen, final_color, transformed_vertices)
        
        # Draw outline
        outline_color = tuple(min(255, c + 50) for c in final_color)
        pygame.draw.polygon(self.screen, outline_color, transformed_vertices, 2)
        
        # Store for particle emission
        segment_data['last_vertices'] = transformed_vertices
        segment_data['last_color'] = final_color
    
    def _draw_enhanced_eyes(self, vertices: List[Tuple[int, int]], outline_color: Tuple[int, int, int]) -> None:
        """Draw enhanced eyes with animations."""
        if len(vertices) >= 6:
            # Calculate eye positions (more detailed)
            center_x = sum(v[0] for v in vertices) // 6
            center_y = sum(v[1] for v in vertices) // 6
            
            # Enhanced eye positions with multiple components
            eye_offset = self.hex_grid.hex_size // 4
            
            # Left eye components
            left_eye_center = (center_x - eye_offset, center_y - eye_offset // 2)
            left_pupil_pos = (left_eye_center[0] + 1, left_eye_center[1] + 1)
            
            # Right eye components
            right_eye_center = (center_x + eye_offset, center_y - eye_offset // 2)
            right_pupil_pos = (right_eye_center[0] - 1, right_eye_center[1] + 1)
            
            # Animated eye blinking
            blink_factor = (math.sin(time.time() * 3) + 1.0) / 2.0
            pupil_size = int(2 + blink_factor * 2)
            
            # Draw eye whites
            pygame.draw.circle(self.screen, (255, 255, 255), left_eye_center, 4)
            pygame.draw.circle(self.screen, (255, 255, 255), right_eye_center, 4)
            
            # Draw pupils
            pygame.draw.circle(self.screen, (0, 0, 0), left_pupil_pos, pupil_size)
            pygame.draw.circle(self.screen, (0, 0, 0), right_pupil_pos, pupil_size)
            
            # Draw eye highlights
            highlight_offset = 1
            pygame.draw.circle(self.screen, (255, 255, 255), 
                         (left_pupil_pos[0] - highlight_offset, left_pupil_pos[1] - highlight_offset), 
                         1)
            pygame.draw.circle(self.screen, (255, 255, 255), 
                         (right_pupil_pos[0] + highlight_offset, right_pupil_pos[1] - highlight_offset), 
                         1)
    
    def _draw_segment_shadow(self, vertices: List[Tuple[int, int]], colors: Dict[str, Tuple[int, int, int]]) -> None:
        """Draw shadow effect for snake segment."""
        shadow_offset = 3
        shadow_color = self.colors['shadow']
        
        # Offset vertices for shadow
        shadow_vertices = []
        for vx, vy in vertices:
            shadow_vertices.append((vx + shadow_offset, vy + shadow_offset))
        
        # Draw shadow with transparency
        shadow_surface = pygame.Surface((max(v[0] for v in vertices) + shadow_offset * 2, 
                                       max(v[1] for v in vertices) + shadow_offset * 2), 
                                       pygame.SRCALPHA)
        shadow_surface.set_alpha(100)
        
        for vx, vy in shadow_vertices:
            pygame.draw.circle(shadow_surface, shadow_color, (vx, vy), self.hex_grid.hex_size // 2)
        
        self.screen.blit(shadow_surface, (vertices[0][0] - shadow_offset, vertices[0][1] - shadow_offset))
    
    def _draw_segment_effects(self, pos: Tuple[int, int], segment_data: Dict[str, Any], is_head: bool) -> None:
        """Draw special effects for snake segment."""
        if not self.enable_particles:
            return
        
        # Emit particles for head movement
        if is_head:
            if segment_data.get('scale', 1.0) > 1.0:  # Growing
                self.particle_system.emit_particles(pos[0], pos[1], 3, 
                                              color=(100, 255, 100), velocity_range=(30, 60))
            
            if self.frame_count % 10 == 0:  # Periodic trail effect
                self.particle_system.emit_particles(pos[0], pos[1], 2, 
                                              color=(150, 200, 255), velocity_range=(20, 40))
    
    def _draw_snake_trail(self, particle_positions: List[Tuple[float, float]]) -> None:
        """Draw trailing particle effect."""
        if not self.enable_particles:
            return
        
        # Emit particles along trail
        for i in range(0, len(particle_positions), 5):
            if i % 2 == 0:  # Every other position
                pos = particle_positions[min(i, len(particle_positions) - 1)]
                self.particle_system.emit_particles(pos[0], pos[1], 1, 
                                              color=(100, 150, 255), velocity_range=(10, 20))
    
    def draw_food(self, food: Any, theme_data: Optional[Dict] = None) -> None:
        """Draw enhanced food with animations."""
        if hasattr(food, 'position'):
            pos = self.hex_grid.hex_to_pixel(food.position)
            
            # Apply theme colors if available
            if theme_data and theme_data.get('food_colors'):
                colors = theme_data['food_colors']
                base_color = colors.get('food_normal', self.colors['food_normal'])
                glow_color = colors.get('food_glow', self.colors['food_glow'])
            else:
                base_color = self.colors['food_normal']
                glow_color = self.colors['food_glow']
            
            # Animated rotation
            self.food_rotation += 0.05
            self.food_scale = 1.0 + math.sin(self.food_rotation) * 0.1
            
            # Draw rotating food
            self._draw_rotating_food(pos, base_color, glow_color)
            
            # Draw particle effects
            if self.enable_particles and self.frame_count % 30 == 0:
                self.particle_system.emit_particles(pos[0], pos[1], 5, 
                                              color=base_color, velocity_range=(20, 40))
    
    def _draw_rotating_food(self, pos: Tuple[int, int], base_color: Tuple[int, int, int], 
                          glow_color: Tuple[int, int, int]) -> None:
        """Draw rotating food with multiple components."""
        # Main food shape (diamond/star)
        size = int(self.hex_grid.hex_size * self.food_scale * 0.6)
        
        # Create rotating shape
        points = []
        num_points = 6  # Star shape
        for i in range(num_points):
            angle = (i * 2 * math.pi) / num_points + self.food_rotation
            px = pos[0] + size * math.cos(angle)
            py = pos[1] + size * math.sin(angle)
            points.append((int(px), int(py)))
        
        # Draw glow effect
        if self.enable_glow:
            glow_points = []
            for px, py in points:
                glow_size = size + 3
                gx = pos[0] + (px - pos[0]) * 1.5
                gy = pos[1] + (py - pos[1]) * 1.5
                glow_points.append((int(gx), int(gy)))
            
            pygame.draw.polygon(self.screen, glow_color, glow_points)
        
        # Draw main shape
        pygame.draw.polygon(self.screen, base_color, points)
        
        # Draw sparkles
        if self.enable_particles and self.frame_count % 15 == 0:
            for px, py in points:
                self.particle_system.emit_particles(px, py, 1, 
                                              color=(255, 255, 200), velocity_range=(5, 15))
    
    def draw_highlighted_hex(self, coord: HexCoord, color: Tuple[int, int, int] = None, 
                          intensity: float = 1.0) -> None:
        """Draw highlighted hex with enhanced effects."""
        if color is None:
            color = self.colors['highlight']
        
        vertices = self.hex_grid.get_hex_vertices(coord)
        
        # Pulsing highlight effect
        self.glow_effect_phase += 0.1
        glow_size = int(3 + math.sin(self.glow_effect_phase) * 2)
        
        # Draw multiple highlight layers
        for i in range(glow_size):
            alpha = max(50, 255 - i * 30)
            layer_color = (*color, alpha)
            pygame.draw.polygon(self.screen, layer_color, vertices, 3 - i)
    
    def set_animation_speed(self, speed: float) -> None:
        """Set animation speed multiplier."""
        self.animation_manager.set_time_scale(speed)
    
    def set_render_quality(self, quality: str) -> None:
        """Set render quality (low/medium/high)."""
        self.render_quality = quality
        
        # Adjust visual effects based on quality
        if quality == "low":
            self.enable_particles = False
            self.enable_glow = False
            self.enable_shadows = False
        elif quality == "medium":
            self.enable_particles = True
            self.enable_glow = True
            self.enable_shadows = False
        else:  # high
            self.enable_particles = True
            self.enable_glow = True
            self.enable_shadows = True
    
    def update(self, dt: float) -> None:
        """Update all visual effects."""
        # Update animation systems
        self.animation_manager.update_all(dt)
        self.particle_system.update(dt)
        self.screen_shake.update(dt)
        
        # Update frame counter
        self.frame_count += 1
        self.last_frame_time = time.time()
    
    def get_performance_info(self) -> Dict[str, Any]:
        """Get performance metrics."""
        current_time = time.time()
        if self.last_frame_time > 0:
            fps = 1.0 / (current_time - self.last_frame_time)
        else:
            fps = 60.0
        
        return {
            'fps': fps,
            'particle_count': self.particle_system.get_particle_count(),
            'animation_count': len(self.animation_manager.animations),
            'render_quality': self.render_quality,
            'effects_enabled': {
                'particles': self.enable_particles,
                'glow': self.enable_glow,
                'shadows': self.enable_shadows,
                'animations': self.enable_animations
            }
        }
    
    def set_screen_shake(self, intensity: float, duration: float) -> None:
        """Trigger screen shake effect."""
        self.screen_shake.start(intensity, duration)
    
    def emit_burst_particles(self, position: HexCoord, count: int = 20) -> None:
        """Emit particle burst at position."""
        pos = self.hex_grid.hex_to_pixel(position)
        self.particle_system.emit_particles(pos[0], pos[1], count, 
                                          color=(255, 255, 100), velocity_range=(50, 150))
    
    def start_food_collect_animation(self, food_pos: HexCoord) -> None:
        """Start animation for food collection."""
        pos = self.hex_grid.hex_to_pixel(food_pos)
        self.particle_system.emit_particles(pos[0], pos[1], 15, 
                                          color=(255, 215, 0), velocity_range=(100, 200))
        self.screen_shake.start(10, 0.15)
        
        # Create burst effect at food position
        self.emit_burst_particles(food_pos, 10)