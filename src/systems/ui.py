"""UI system for the snake game."""

import pygame
from typing import Optional, List, Dict, Any


class UIManager:
    """Manages user interface elements."""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        self.colors = {
            'text': (255, 255, 255),
            'background': (0, 0, 0),
            'button': (100, 100, 100),
            'button_hover': (150, 150, 150),
            'button_text': (255, 255, 255)
        }
    
    def draw_text(self, text: str, position: tuple, font_size: str = 'medium', 
                  color: tuple = None, centered: bool = False) -> None:
        """Draw text on the screen."""
        if color is None:
            color = self.colors['text']
        
        font = self._get_font(font_size)
        text_surface = font.render(text, True, color)
        
        if centered:
            text_rect = text_surface.get_rect(center=position)
            self.screen.blit(text_surface, text_rect)
        else:
            self.screen.blit(text_surface, position)
    
    def draw_button(self, text: str, rect: pygame.Rect, 
                   is_hovered: bool = False) -> None:
        """Draw a button."""
        color = self.colors['button_hover'] if is_hovered else self.colors['button']
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, self.colors['text'], rect, 2)  # Border
        
        # Center text in button
        text_surface = self.font_medium.render(text, True, self.colors['button_text'])
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)
    
    def _get_font(self, size: str):
        """Get font by size identifier."""
        font_map = {
            'small': self.font_small,
            'medium': self.font_medium,
            'large': self.font_large
        }
        return font_map.get(size, self.font_medium)