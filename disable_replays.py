"""Disable replay system to prevent corruption errors."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def disable_replay_system():
    """Temporarily disable replay system to prevent corruption."""
    print("Disabling replay system to prevent JSON errors...")
    
    # Create a dummy replay directory
    replay_dir = "data/replays"
    os.makedirs(replay_dir, exist_ok=True)
    
    # Create a .disabled file to indicate replay is disabled
    with open(os.path.join(replay_dir, ".disabled"), "w") as f:
        f.write("Replay system temporarily disabled due to JSON serialization issues")
    
    print("+ Replay system disabled")
    return True

def create_simple_phase3_main():
    """Create a simpler version of phase3_main without replay errors."""
    content = '''"""Simplified Phase 3 Main - Without Replay System."""

import pygame
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.phase3_game import Phase3GameController
from src.core.config import GameConfig
from src.renderers.phase3_ui import Phase3UIRenderer


class SimpleRenderer:
    """Simple renderer without replay dependencies."""
    
    def __init__(self, screen, config):
        self.screen = screen
        self.config = config
        self.cell_size = 20
        self.colors = {
            'background': (10, 10, 30),
            'grid_line': (40, 40, 40),
            'snake_head': (0, 255, 0),
            'snake_body': (0, 200, 0),
            'food': (255, 0, 0),
        }
    
    def render_game(self, game_data):
        """Render the game state."""
        if not game_data:
            return
        
        # Clear screen
        self.screen.fill(self.colors['background'])
        
        snakes = game_data.get('snakes', [])
        food_items = game_data.get('food_items', [])
        
        # Calculate cell size based on grid dimensions
        grid_width = 40  # From config
        grid_height = 30  # From config
        
        # Dynamic cell size to fit screen
        max_cell_width = self.screen.get_width() // (grid_width + 4)
        max_cell_height = self.screen.get_height() // (grid_height + 4)
        self.cell_size = min(max_cell_width, max_cell_height, 20)
        
        # Draw grid
        total_grid_width = grid_width * self.cell_size
        total_grid_height = grid_height * self.cell_size
        offset_x = (self.screen.get_width() - total_grid_width) // 2
        offset_y = (self.screen.get_height() - total_grid_height) // 2
        
        # Draw grid lines
        for x in range(grid_width + 1):
            pygame.draw.line(self.screen, self.colors['grid_line'],
                           (offset_x + x * self.cell_size, offset_y),
                           (offset_x + x * self.cell_size, offset_y + total_grid_height))
        
        for y in range(grid_height + 1):
            pygame.draw.line(self.screen, self.colors['grid_line'],
                           (offset_x, offset_y + y * self.cell_size),
                           (offset_x + total_grid_width, offset_y + y * self.cell_size))
        
        # Draw snakes
        for snake in snakes:
            if hasattr(snake, 'get_segments'):
                segments = snake.get_segments()
                for i, segment in enumerate(segments):
                    color = self.colors['snake_head'] if i == 0 else self.colors['snake_body']
                    x = offset_x + segment.x * self.cell_size + 2
                    y = offset_y + segment.y * self.cell_size + 2
                    size = self.cell_size - 4
                    pygame.draw.rect(self.screen, color, (x, y, size, size))
        
        # Draw food
        for food in food_items:
            if hasattr(food, 'position'):
                x = offset_x + food.position.x * self.cell_size + self.cell_size // 2
                y = offset_y + food.position.y * self.cell_size + self.cell_size // 2
                radius = max(3, self.cell_size // 4)
                pygame.draw.circle(self.screen, self.colors['food'], (x, y), radius)
    
    def render_replay(self, game_data):
        """Render replay data."""
        self.render_game(game_data)


def main():
    """Main entry point for Phase 3 game without replays."""
    # Initialize pygame
    pygame.init()
    
    # Create configuration
    config = GameConfig()
    
    # Set up display
    screen_width = config.screen_width
    screen_height = config.screen_height
    
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Advanced Snake Game - Phase 3 (No Replays)")
    
    # Create game controller
    game_controller = Phase3GameController(config)
    game_controller.initialize(screen)
    
    # Disable replay system
    game_controller.replay_recorder.recording = False
    
    # Create renderers
    game_renderer = SimpleRenderer(screen, config)
    ui_renderer = Phase3UIRenderer(screen, config)
    
    # Main game loop
    clock = pygame.time.Clock()
    running = True
    
    while running:
        dt = clock.tick(60) / 1000.0  # Convert to seconds
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                game_controller.handle_input(event)
        
        # Update game
        game_controller.update(dt)
        
        # Clear screen
        screen.fill(config.background_color)
        
        # Render based on game state
        game_state = game_controller.game_state
        
        if game_state.value == "playing":
            # Render game
            game_data = game_controller.get_game_data_for_rendering()
            if game_data:
                game_renderer.render_game(game_data)
            
            # Render UI overlay
            ui_data = game_controller.get_ui_data()
            ui_renderer.render_game_ui(ui_data)
            
        elif game_state.value == "menu":
            # Render main menu
            ui_data = game_controller.get_ui_data()
            ui_renderer.render_main_menu(ui_data)
            
        elif game_state.value == "game_over":
            # Render game over screen
            ui_data = game_controller.get_ui_data()
            ui_renderer.render_game_over(ui_data)
        
        # Update display
        pygame.display.flip()
        
        # Check if controller wants to quit
        if not game_controller.running:
            running = False
    
    # Cleanup
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
'''
    
    with open("phase3_main_stable.py", "w") as f:
        f.write(content)
    
    print("+ Created stable Phase 3 main file without replays")
    return True

if __name__ == "__main__":
    disable_replay_system()
    create_simple_phase3_main()
    print("\\n+ Phase 3 stable version ready!")
    print("Run: python phase3_main_stable.py")