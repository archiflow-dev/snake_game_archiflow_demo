"""Rendering engine for the snake game."""

import pygame
from typing import Tuple, Optional, List
from ..entities.grid import Grid, SquareCoord
from ..entities.snake import Snake
from ..entities.food import Food


class RenderEngine:
    """Handles all rendering operations for the game."""
    
    def __init__(self, screen: pygame.Surface, grid: Grid):
        self.screen = screen
        self.grid = grid
        self.cell_size = 20  # Size of each grid cell in pixels
        
        # Colors
        self.colors = {
            'background': (20, 20, 20),
            'grid_line': (40, 40, 40),
            'snake_head': (0, 255, 0),
            'snake_body': (0, 200, 0),
            'food': (255, 0, 0),
            'text': (255, 255, 255),
            'score_bg': (0, 0, 0, 128)
        }
        
        # Fonts
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # Calculate grid offset to center it
        self._calculate_grid_offset()
    
    def _calculate_grid_offset(self) -> None:
        """Calculate offset to center the grid on screen."""
        grid_width = self.grid.width * self.cell_size
        grid_height = self.grid.height * self.cell_size
        
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        self.grid_offset_x = (screen_width - grid_width) // 2
        self.grid_offset_y = (screen_height - grid_height) // 2
    
    def clear_screen(self) -> None:
        """Clear the screen with background color."""
        self.screen.fill(self.colors['background'])
    
    def draw_grid(self) -> None:
        """Draw the game grid."""
        # Draw grid lines
        for x in range(self.grid.width + 1):
            start_x = self.grid_offset_x + x * self.cell_size
            start_y = self.grid_offset_y
            end_x = start_x
            end_y = start_y + self.grid.height * self.cell_size
            pygame.draw.line(self.screen, self.colors['grid_line'], 
                           (start_x, start_y), (end_x, end_y), 1)
        
        for y in range(self.grid.height + 1):
            start_x = self.grid_offset_x
            start_y = self.grid_offset_y + y * self.cell_size
            end_x = start_x + self.grid.width * self.cell_size
            end_y = start_y
            pygame.draw.line(self.screen, self.colors['grid_line'], 
                           (start_x, start_y), (end_x, end_y), 1)
    
    def draw_snake(self, snake: Snake) -> None:
        """Draw the snake."""
        segments = snake.get_segments()
        
        for i, segment in enumerate(segments):
            # Choose color based on segment position
            if i == 0:  # Head
                color = self.colors['snake_head']
            else:  # Body
                color = self.colors['snake_body']
            
            # Draw segment
            self._draw_cell(segment, color)
    
    def draw_food(self, food: Food) -> None:
        """Draw food on the grid."""
        self._draw_cell(food.get_position(), self.colors['food'])
    
    def _draw_cell(self, coord: SquareCoord, color: Tuple[int, int, int]) -> None:
        """Draw a single cell with the given color."""
        x = self.grid_offset_x + coord.x * self.cell_size
        y = self.grid_offset_y + coord.y * self.cell_size
        
        # Draw filled rectangle with small margin
        margin = 2
        pygame.draw.rect(self.screen, color,
                        (x + margin, y + margin, 
                         self.cell_size - 2 * margin, self.cell_size - 2 * margin))
    
    def draw_score(self, score: int, high_score: int = 0) -> None:
        """Draw the score display."""
        # Score text
        score_text = self.font_medium.render(f"Score: {score}", True, self.colors['text'])
        self.screen.blit(score_text, (10, 10))
        
        # High score text
        high_score_text = self.font_small.render(f"High: {high_score}", True, self.colors['text'])
        self.screen.blit(high_score_text, (10, 50))
    
    def draw_game_over(self, score: int) -> None:
        """Draw game over overlay."""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        game_over_text = self.font_large.render("GAME OVER", True, (255, 0, 0))
        game_over_rect = game_over_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 50))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Score text
        score_text = self.font_medium.render(f"Final Score: {score}", True, self.colors['text'])
        score_rect = score_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 20))
        self.screen.blit(score_text, score_rect)
        
        # Restart text
        restart_text = self.font_small.render("Press R to Restart", True, self.colors['text'])
        restart_rect = restart_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 70))
        self.screen.blit(restart_text, restart_rect)
    
    def draw_pause_overlay(self) -> None:
        """Draw pause overlay."""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Pause text
        pause_text = self.font_large.render("PAUSED", True, (255, 255, 0))
        pause_rect = pause_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
        self.screen.blit(pause_text, pause_rect)
        
        # Resume text
        resume_text = self.font_small.render("Press ESC to Resume", True, self.colors['text'])
        resume_rect = resume_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 50))
        self.screen.blit(resume_text, resume_rect)
    
    def draw_start_menu(self) -> None:
        """Draw the start menu."""
        # Title
        title_text = self.font_large.render("SNAKE GAME", True, self.colors['text'])
        title_rect = title_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 50))
        self.screen.blit(title_text, title_rect)
        
        # Start instruction
        start_text = self.font_medium.render("Press SPACE to Start", True, self.colors['text'])
        start_rect = start_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 20))
        self.screen.blit(start_text, start_rect)
        
        # Controls
        controls_text = self.font_small.render("Use WASD to Move", True, self.colors['text'])
        controls_rect = controls_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 70))
        self.screen.blit(controls_text, controls_rect)
    
    def set_cell_size(self, size: int) -> None:
        """Set the size of grid cells."""
        self.cell_size = size
        self._calculate_grid_offset()
    
    def set_color(self, element: str, color: Tuple[int, int, int]) -> None:
        """Set a color scheme element."""
        if element in self.colors:
            self.colors[element] = color
    
    def grid_to_screen_coords(self, coord: SquareCoord) -> Tuple[int, int]:
        """Convert grid coordinates to screen coordinates."""
        x = self.grid_offset_x + coord.x * self.cell_size
        y = self.grid_offset_y + coord.y * self.cell_size
        return (x, y)