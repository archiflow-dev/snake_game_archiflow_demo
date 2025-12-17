"""Color definitions for the game."""


class Colors:
    """Predefined color constants."""
    
    # Basic colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    
    # Game colors
    SNAKE_HEAD = (0, 255, 0)
    SNAKE_BODY = (0, 200, 0)
    FOOD = (255, 0, 0)
    GRID_LINE = (40, 40, 40)
    GRID_LINES = (40, 40, 40)
    BACKGROUND = (20, 20, 20)
    TEXT = (255, 255, 255)
    
    # UI colors
    BUTTON = (100, 100, 100)
    BUTTON_HOVER = (150, 150, 150)
    BUTTON_TEXT = (255, 255, 255)
    
    # Theme colors
    NEON_GREEN = (57, 255, 20)
    NEON_PINK = (255, 20, 147)
    NEON_BLUE = (0, 191, 255)
    NEON_YELLOW = (255, 255, 0)
    
    # Retro colors
    RETRO_GREEN = (0, 255, 0)
    RETRO_AMBER = (255, 191, 0)
    RETRO_CYAN = (0, 255, 255)
    
    @staticmethod
    def hex_to_rgb(hex_color: str) -> tuple:
        """Convert hex color string to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))