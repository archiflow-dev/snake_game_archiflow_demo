"""Hexagonal renderer for Phase 4."""

import pygame
import math
from typing import List, Tuple, Optional
from ..grids.hex_grid import HexGrid
from ..entities.snake import Snake
from ..entities.food import Food
from ..core.config import GameConfig


class HexRenderer:
    """Renderer for hexagonal grid layout."""
    
    def __init__(self, screen: pygame.Surface, hex_grid: HexGrid, config: GameConfig):
        self.screen = screen
        self.hex_grid = hex_grid
        self.config = config
        
        # Colors
        self.colors = {
            'background': (10, 10, 30),
            'grid_line': (60, 60, 80),
            'hex_fill': (20, 20, 40),
            'snake_head': (0, 255, 100),
            'snake_body': (0, 200, 80),
            'food': (255, 100, 100),
            'highlight': (100, 100, 255)
        }
        
        # Animation state
        self.animation_time = 0.0
        self.interpolation_factor = 0.0
    
    def draw_grid(self) -> None:
        """Draw hexagonal grid."""
        all_cells = self.hex_grid.get_all_cells()
        
        for cell in all_cells:
            vertices = self.hex_grid.get_hex_vertices(cell)
            
            # Fill hex background
            pygame.draw.polygon(self.screen, self.colors['hex_fill'], vertices)
            
            # Draw hex outline
            pygame.draw.polygon(self.screen, self.colors['grid_line'], vertices, 2)
    
    def draw_snake(self, snake: Snake, interpolation: float = 0.0) -> None:
        """Draw snake with smooth interpolation between hex centers."""
        segments = snake.get_segments()
        
        for i in range(len(segments) - 1):
            start_pos = self.hex_grid.get_hex_center(segments[i])
            end_pos = self.hex_grid.get_hex_center(segments[i + 1])
            
            # Interpolate position
            if interpolation > 0 and i == 0:  # Only interpolate head movement
                current_pos = self.hex_grid.hex_lerp(
                    segments[i], segments[i + 1], interpolation
                )
                start_pos = current_pos
            
            color = self.colors['snake_head'] if i == 0 else self.colors['snake_body']
            
            # Draw hexagon at position
            self._draw_hex_at_position(start_pos, color, i == 0)
    
    def draw_food(self, food: Food) -> None:
        """Draw food on hexagonal grid."""
        if hasattr(food, 'position'):
            pos = self.hex_grid.get_hex_center(food.position)
            
            # Draw food as diamond shape in hex
            size = self.hex_grid.hex_size // 3
            vertices = [
                (pos[0], pos[1] - size),
                (pos[0] + size, pos[1]),
                (pos[0], pos[1] + size),
                (pos[0] - size, pos[1])
            ]
            
            pygame.draw.polygon(self.screen, self.colors['food'], vertices)
            
            # Add glow effect
            pygame.draw.polygon(self.screen, (255, 150, 150), vertices, 2)
    
    def _draw_hex_at_position(self, pos: Tuple[int, int], color: Tuple[int, int, int], is_head: bool = False) -> None:
        """Draw a hexagon at a given position."""
        # Create a temporary HexCoord to get vertices
        temp_coord = self._pixel_to_hex(pos)
        if temp_coord:
            vertices = self.hex_grid.get_hex_vertices(temp_coord)
            
            # Draw filled hexagon
            pygame.draw.polygon(self.screen, color, vertices)
            
            # Draw outline
            outline_color = tuple(min(255, c + 50) for c in color)
            pygame.draw.polygon(self.screen, outline_color, vertices, 2)
            
            # Draw eyes on head
            if is_head:
                self._draw_snake_eyes(vertices)
    
    def _draw_snake_eyes(self, vertices: List[Tuple[int, int]]) -> None:
        """Draw eyes on snake head."""
        if len(vertices) >= 6:
            # Calculate eye positions (simple approximation)
            center_x = sum(v[0] for v in vertices) // 6
            center_y = sum(v[1] for v in vertices) // 6
            
            eye_offset = self.hex_grid.hex_size // 4
            
            left_eye = (center_x - eye_offset // 2, center_y - eye_offset // 2)
            right_eye = (center_x + eye_offset // 2, center_y - eye_offset // 2)
            
            # Draw eyes
            pygame.draw.circle(self.screen, (255, 255, 255), left_eye, 3)
            pygame.draw.circle(self.screen, (0, 0, 0), left_eye, 2)
            
            pygame.draw.circle(self.screen, (255, 255, 255), right_eye, 3)
            pygame.draw.circle(self.screen, (0, 0, 0), right_eye, 2)
    
    def _pixel_to_hex(self, pos: Tuple[int, int]) -> Optional['HexCoord']:
        """Convert pixel position back to hex coordinate."""
        # Simplified reverse conversion
        screen_center_x = self.config.screen_width // 2
        screen_center_y = self.config.screen_height // 2
        
        # Offset from center
        offset_x = pos[0] - screen_center_x
        offset_y = pos[1] - screen_center_y
        
        # Convert to axial coordinates (approximate)
        size = self.hex_grid.hex_size
        q = (2/3 * offset_x) / size
        r = (-1/3 * offset_x + math.sqrt(3)/3 * offset_y) / size
        
        # Round to nearest hex
        q = round(q)
        r = round(r)
        
        from ..grids.hex_grid import HexCoord
        return HexCoord(q, r)
    
    def draw_grid_coordinates(self) -> None:
        """Draw coordinate labels for debugging."""
        all_cells = self.hex_grid.get_all_cells()
        font = pygame.font.Font(None, 12)
        
        for cell in all_cells:
            pos = self.hex_grid.get_hex_center(cell)
            coord_text = f"{cell.q},{cell.r}"
            
            text_surface = font.render(coord_text, True, (100, 100, 100))
            text_rect = text_surface.get_rect(center=pos)
            
            self.screen.blit(text_surface, text_rect)
    
    def draw_direction_indicator(self, coord: 'HexCoord', direction: str) -> None:
        """Draw directional indicator at hex position."""
        center = self.hex_grid.get_hex_center(coord)
        
        # Draw arrow based on direction
        arrow_length = self.hex_grid.hex_size // 2
        
        if direction == 'E':
            end_pos = (center[0] + arrow_length, center[1])
        elif direction == 'SE':
            end_pos = (center[0] + arrow_length//2, center[1] + arrow_length//2)
        elif direction == 'SW':
            end_pos = (center[0] - arrow_length//2, center[1] + arrow_length//2)
        elif direction == 'W':
            end_pos = (center[0] - arrow_length, center[1])
        elif direction == 'NW':
            end_pos = (center[0] - arrow_length//2, center[1] - arrow_length//2)
        elif direction == 'NE':
            end_pos = (center[0] + arrow_length//2, center[1] - arrow_length//2)
        else:
            end_pos = center
        
        pygame.draw.line(self.screen, self.colors['highlight'], center, end_pos, 3)
    
    def set_animation_time(self, time: float) -> None:
        """Set animation time for smooth movement."""
        self.animation_time = time
    
    def set_interpolation(self, factor: float) -> None:
        """Set interpolation factor for smooth movement."""
        self.interpolation_factor = max(0.0, min(1.0, factor))
    
    def get_hex_color(self, coord: 'HexCoord', base_color: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Get hex color with coordinate-based variation."""
        # Create subtle color variation based on coordinates
        r, g, b = base_color
        variation = (coord.q + coord.r) % 3
        
        if variation == 0:
            return (r, g, b)
        elif variation == 1:
            return (min(255, r + 20), min(255, g + 20), b)
        else:
            return (r, min(255, g + 20), min(255, b + 20))
    
    def draw_highlighted_hex(self, coord: 'HexCoord', color: Tuple[int, int, int] = None) -> None:
        """Draw a highlighted hex at the given coordinate."""
        if color is None:
            color = self.colors['highlight']
        
        vertices = self.hex_grid.get_hex_vertices(coord)
        
        # Draw with thicker outline for highlight
        pygame.draw.polygon(self.screen, color, vertices)
        pygame.draw.polygon(self.screen, (255, 255, 255), vertices, 3)