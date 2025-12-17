"""Main entry point for Phase 4 with enhanced hexagonal grid."""

import pygame
import sys
import os
import time

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.config import GameConfig
from src.utils.difficulty_new import Difficulty
from src.utils.customization import CustomizationManager


class Phase4GameController:
    """Enhanced game controller for Phase 4 features."""
    
    def __init__(self, config: GameConfig):
        self.config = config
        self.screen = None
        self.clock = pygame.time.Clock()

        # Phase 4 specific features
        self.hex_grid = None
        self.snake = None
        self.difficulty_manager = None
        self.scoring_system = None
        self.customization = None

        # Game state
        self.running = True
        self.paused = False
        self.game_over = False
        self.game_time = 0.0
        self.score = 0

        # Movement
        self.direction = None
        self.next_direction = None

        # Visual effects
        self.animation_time = 0.0
        self.particle_system = None

        # Food tracking
        self.food_items = []

        # Movement timing for slower snake
        self.move_timer = 0.0
        self.move_interval = 0.3  # Time between moves in seconds

        # Growth pending flag
        self.should_grow = False
        
        # Controls for hexagonal movement
        self.hex_controls = {
            'w': 'NE',      # Up/Right
            'e': 'E',       # Right
            's': 'SE',      # Down/Right
            'q': 'NW',      # Up/Left
            'a': 'W',       # Left
            'd': 'SW',      # Down/Left
            'UP': 'NE',
            'DOWN': 'SE',
            'LEFT': 'W',
            'RIGHT': 'E'
        }
        
        # Initialize systems
        self._init_phase4_systems()
    
    def _init_phase4_systems(self) -> None:
        """Initialize Phase 4 specific systems."""
        # Import and initialize hexagonal grid
        from src.grids.hex_grid import HexGrid
        self.hex_grid = HexGrid(25, 20, hex_size=25)  # Larger grid with bigger hexagons
        
        # Import and initialize difficulty system
        from src.utils.difficulty_new import DifficultyManager, DynamicScoring
        self.difficulty_manager = DifficultyManager()
        self.scoring_system = DynamicScoring()
        
        # Initialize customizations
        self.customization = CustomizationManager()
        
        # Set initial values
        self.difficulty_manager.set_difficulty(Difficulty.NORMAL)
        self.scoring_system.reset()
    
    def initialize(self, screen) -> None:
        """Initialize Phase 4 game with hexagonal grid."""
        self.screen = screen
        
        # Set custom hexagonal controls
        pygame.display.set_caption("Advanced Snake Game - Phase 4 (Hexagonal Grid)")
        
        # Initialize snake for hexagonal grid
        self._create_hex_snake()
    
    def _create_hex_snake(self) -> None:
        """Create snake adapted for hexagonal grid."""
        from src.entities.hex_snake_simple import HexSnake, HexDirection
        from src.entities.grid_new import HexCoord

        # Start at center of hex grid
        start_pos = HexCoord(0, 0)

        # Start with East direction so snake can move immediately
        initial_direction = HexDirection.E
        self.snake = HexSnake(start_pos, initial_direction)
        self.direction = initial_direction
    
    def start_new_game(self) -> None:
        """Start a new Phase 4 game."""
        # Clear hex grid
        self.hex_grid.clear()

        # Reset game state
        self.game_over = False
        self.game_time = 0.0
        self.score = 0
        self.paused = False
        self.direction = None
        self.next_direction = None
        self.move_timer = 0.0  # Reset movement timer
        self.should_grow = False  # Reset growth flag

        # Clear food items
        self.food_items.clear()

        # Reset systems
        self.difficulty_manager.reset()
        self.scoring_system.reset()

        # Create snake
        self._create_hex_snake()

        # Add snake segments to grid
        if hasattr(self.snake, 'get_segments'):
            for segment in self.snake.get_segments():
                self.hex_grid.occupy(segment)

        # Add food
        self._spawn_food()

        print("New game started successfully!")
    
    def _spawn_food(self) -> None:
        """Spawn food on hexagonal grid."""
        from src.entities.food import Food
        from src.entities.grid_new import HexCoord

        # Get random empty position
        food_pos = self.hex_grid.get_random_empty_cell()
        if food_pos:
            food = Food(food_pos)
            self.food_items.append(food)
            self.hex_grid.occupy(food.position)
            return food

        return None
    
    def update(self, dt: float) -> None:
        """Update Phase 4 game with hexagonal movement."""
        if self.game_over or self.paused:
            return
        
        # Limit update speed for hexagonal grid - much slower for better control
        max_dt = 0.25  # Much slower updates for hex
        dt = min(dt, max_dt)
        
        self.game_time += dt
        self.animation_time += dt

        # Update movement timer
        self.move_timer += dt

        # Update difficulty and scoring
        if hasattr(self.difficulty_manager, 'update_performance'):
            self.difficulty_manager.update_performance(1.0 / max(dt, 0.001))  # FPS approximation
        if hasattr(self.difficulty_manager, 'update_score'):
            self.difficulty_manager.update_score(self.score)

        # Process player input
        self._process_hex_input()

        # Move snake only at intervals
        if self.move_timer >= self.move_interval:
            self._move_hex_snake()
            self.move_timer = 0.0  # Reset timer
        
        # Check food collision
        self._check_hex_food_collision()
        
        # Update particles
        self._update_particles(dt)
        
        # Check game over
        self._check_game_over()
    
    def _process_hex_input(self) -> None:
        """Process input for hexagonal movement."""
        # Input is now handled in handle_input method
        pass
    
    def _move_hex_snake(self) -> None:
        """Move snake in hexagonal coordinates."""
        if not self.snake:
            return

        # Clear all snake positions from grid first
        if hasattr(self.snake, 'get_segments'):
            for segment in self.snake.get_segments():
                self.hex_grid.vacate(segment)

        # Update direction from next_direction
        if hasattr(self.snake, 'next_direction') and self.snake.next_direction:
            self.snake.direction = self.snake.next_direction
            self.snake.next_direction = None

        # Move snake
        if hasattr(self.snake, 'move'):
            tail = self.snake.move()

            # If we should grow, add the tail back instead of removing it
            if self.should_grow and tail:
                self.snake.segments.append(tail)
                self.should_grow = False  # Reset growth flag

            # Re-mark all snake positions in hex grid
            if hasattr(self.snake, 'get_segments'):
                for segment in self.snake.get_segments():
                    self.hex_grid.occupy(segment)

            # Re-mark food positions
            for food in self.food_items:
                self.hex_grid.occupy(food.position)
    
    def _check_hex_food_collision(self) -> None:
        """Check collision with food in hexagonal grid."""
        if not self.snake:
            return

        if hasattr(self.snake, 'get_head'):
            head = self.snake.get_head()

            # Check if snake head collides with any food
            for food in self.food_items[:]:  # Use slice to avoid modification during iteration
                if head == food.position:
                    # Remove food
                    self.food_items.remove(food)
                    self.hex_grid.vacate(food.position)

                    # Spawn new food
                    self._spawn_food()

                    # Update score
                    if hasattr(self.scoring_system, 'calculate_score') and hasattr(self.difficulty_manager, 'current_difficulty'):
                        points = self.scoring_system.calculate_score(
                            self.game_time, self.difficulty_manager.current_difficulty
                        )
                        self.score += points
                    else:
                        self.score += 10  # Default score

                    # Mark snake to grow on next move
                    self.should_grow = True

                    return
    
    def _remove_food_at(self, pos) -> None:
        """Remove food at specific position."""
        self.hex_grid.vacate(pos)
    
    def _check_game_over(self) -> None:
        """Check for game over conditions."""
        if not self.snake:
            return
        
        # Check self-collision
        if hasattr(self.snake, 'check_self_collision'):
            if self.snake.check_self_collision():
                self.game_over = True
                self._handle_game_over()
                return
        
        # Check boundary collision
        if hasattr(self.snake, 'get_head'):
            head = self.snake.get_head()
            if not self.hex_grid.is_valid_position(head):
                self.game_over = True
                self._handle_game_over()
                return
    
    def _handle_game_over(self) -> None:
        """Handle game over state."""
        pass  # Show game over screen
    
    def _update_particles(self, dt: float) -> None:
        """Update visual effects."""
        # Simple particle system placeholder
        pass
    
    def handle_input(self, event: pygame.event.Event) -> None:
        """Handle pygame events for Phase 4 game."""
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            # Handle escape and pause
            if event.key == pygame.K_ESCAPE:
                self.paused = not self.paused
            elif event.key == pygame.K_p:
                self.paused = not self.paused
            elif event.key == pygame.K_r:
                print("R key pressed - starting new game")
                self.start_new_game()
                return  # Skip other processing after restart
            else:
                # Only process movement if game is not over
                if not self.game_over:
                    from src.entities.hex_snake_simple import HexDirection
                    
                    # Map keys to hex directions (updated to match hex_main scheme)
                    key_direction_map = {
                        pygame.K_d: HexDirection.E,      # D = Right (Southeast/East)
                        pygame.K_a: HexDirection.W,      # A = Down-Left (Southwest/West)
                        pygame.K_e: HexDirection.NE,     # E = Up-Right (Northeast)
                        pygame.K_q: HexDirection.NW,     # Q = Up-Left (Northwest)
                        pygame.K_w: HexDirection.N,      # W = Up (North)
                        pygame.K_s: HexDirection.S,      # S = Down (South)
                        pygame.K_UP: HexDirection.N,      # Arrow keys
                        pygame.K_DOWN: HexDirection.S,
                        pygame.K_LEFT: HexDirection.NW,
                        pygame.K_RIGHT: HexDirection.E
                    }
                    
                    if event.key in key_direction_map:
                        new_dir = key_direction_map[event.key]
                        if self.snake and hasattr(self.snake, 'set_direction'):
                            self.snake.set_direction(new_dir)
                else:
                    # Game over - only allow R key to restart
                    if event.key == pygame.K_r:
                        print("R key pressed during game over - starting new game")
                        self.start_new_game()
    
    def get_game_data_for_rendering(self) -> dict:
        """Get game data for hexagonal rendering."""
        return {
            'snake': self.snake,
            'hex_grid': self.hex_grid,
            'food_items': self.food_items,
            'score': self.score,
            'game_time': self.game_time,
            'game_over': self.game_over,
            'paused': self.paused,
            'difficulty': self.difficulty_manager.get_difficulty_info(),
            'scoring': self.scoring_system.get_score_info(),
            'customization': self.customization.export_customization(),
            'animation_time': self.animation_time
        }
    
    def get_ui_data(self) -> dict:
        """Get UI data for Phase 4 display."""
        return {
            'phase': 4,
            'game_state': 'playing' if not self.game_over else 'game_over',
            'score': self.score,
            'high_score': self.score,  # For now, just current score
            'paused': self.paused,
            'difficulty': self.difficulty_manager.get_difficulty_info(),
            'scoring': self.scoring_system.get_score_info(),
            'controls': {
                'type': 'hexagonal_wasd',
                'mapping': self.hex_controls,
                'description': 'W: NE, E: E, S: SE, Q: NW, A: W, D: SW'
            },
            'features': [
                'Hexagonal Grid Movement',
                '6-Directional Controls',
                'Dynamic Difficulty',
                'Animated Visual Effects',
                'Custom Skins & Themes',
                'Advanced Scoring System'
            ]
        }


class SimpleHexRenderer:
    """Simple renderer for hexagonal grid."""
    
    def __init__(self, screen: pygame.Surface, config):
        self.screen = screen
        self.config = config
        self.hex_size = 25  # Larger hexagons for better visibility
        
        # Colors for hexagonal grid
        self.colors = {
            'background': (10, 10, 30),
            'grid_line': (60, 60, 80),
            'hex_fill': (20, 20, 40),
            'snake_head': (0, 255, 100),
            'snake_body': (0, 200, 80),
            'food': (255, 100, 100),
            'highlight': (100, 100, 255)
        }
    
    def render(self, game_data: dict) -> None:
        """Render hexagonal game."""
        # Store game data for use in other methods
        self.game_data = game_data

        # Clear screen
        self.screen.fill(self.colors['background'])

        hex_grid = game_data.get('hex_grid')
        snake = game_data.get('snake')
        score = game_data.get('score', 0)
        paused = game_data.get('paused', False)
        game_over = game_data.get('game_over', False)

        # Draw hexagonal grid
        if hex_grid:
            self._draw_hex_grid(hex_grid)

        # Draw snake
        if snake and hasattr(snake, 'get_segments'):
            self._draw_hex_snake(snake, hex_grid)

        # Draw food
        if hex_grid:
            self._draw_hex_food(hex_grid)

        # Draw UI
        self._draw_ui(score, paused, game_over)
    
    def _draw_hex_grid(self, hex_grid) -> None:
        """Draw hexagonal grid."""
        from src.entities.grid_new import HexCoord
        
        # Draw grid lines for hexagons
        all_cells = hex_grid.get_all_cells()
        
        for cell in all_cells:
            # Get hex vertices
            vertices = hex_grid.get_hex_vertices(cell)
            
            # Draw filled hexagon
            pygame.draw.polygon(self.screen, self.colors['hex_fill'], vertices)
            
            # Draw outline
            pygame.draw.polygon(self.screen, self.colors['grid_line'], vertices, 2)
    
    def _draw_hex_snake(self, snake, hex_grid) -> None:
        """Draw snake on hexagonal grid."""
        segments = snake.get_segments()
        
        for i, segment in enumerate(segments):
            # Get hex center position
            pos = hex_grid.get_hex_center(segment) if hex_grid else (0, 0)
            
            # Get hex vertices for this position
            vertices = hex_grid.get_hex_vertices(segment) if hex_grid else []
            
            # Color based on segment
            color = self.colors['snake_head'] if i == 0 else self.colors['snake_body']
            
            # Draw hexagon
            pygame.draw.polygon(self.screen, color, vertices)
            
            # Draw eyes on head
            if i == 0 and len(vertices) >= 6:
                self._draw_snake_eyes(vertices)
    
    def _draw_snake_eyes(self, vertices) -> None:
        """Draw eyes on snake head hexagon."""
        if len(vertices) >= 6:
            # Calculate center of hexagon
            center_x = sum(v[0] for v in vertices) // 6
            center_y = sum(v[1] for v in vertices) // 6
            
            # Eye positions (simplified)
            eye_offset = self.hex_size // 4
            left_eye = (center_x - eye_offset // 2, center_y - eye_offset // 2)
            right_eye = (center_x + eye_offset // 2, center_y - eye_offset // 2)
            
            # Draw eyes
            pygame.draw.circle(self.screen, (255, 255, 255), left_eye, 3)
            pygame.draw.circle(self.screen, (0, 0, 0), left_eye, 2)
            
            pygame.draw.circle(self.screen, (255, 255, 255), right_eye, 3)
            pygame.draw.circle(self.screen, (0, 0, 0), right_eye, 2)
    
    def _draw_hex_food(self, hex_grid) -> None:
        """Draw food on hexagonal grid."""
        # Get food items from the game controller if available
        if hasattr(self, 'game_data') and 'food_items' in self.game_data:
            food_items = self.game_data['food_items']
        else:
            # Fallback to checking occupied cells
            food_items = []
            occupied = hex_grid.get_occupied_cells() if hex_grid else []
            for pos in occupied:
                if hasattr(self, 'snake') and self.snake:
                    if hasattr(self.snake, 'get_segments'):
                        if not any(segment.q == pos.q and segment.r == pos.r for segment in self.snake.get_segments()):
                            # This is likely food
                            food_items.append(pos)

        # Draw each food item
        for food in food_items:
            if hasattr(food, 'position'):
                pos = food.position
            else:
                pos = food  # Direct HexCoord

            vertices = hex_grid.get_hex_vertices(pos) if hex_grid else []

            # Draw food as diamond in hex
            if vertices:
                center_x = sum(v[0] for v in vertices) // 6
                center_y = sum(v[1] for v in vertices) // 6

                # Draw diamond shape
                size = self.hex_size // 4
                points = [
                    (center_x, center_y - size),
                    (center_x + size, center_y),
                    (center_x, center_y + size),
                    (center_x - size, center_y)
                ]

                pygame.draw.polygon(self.screen, self.colors['food'], points)

                # Add glow effect
                pygame.draw.polygon(self.screen, (255, 200, 150), points, 2)
    
    def _draw_ui(self, score, paused, game_over) -> None:
        """Draw UI overlay."""
        # Score display
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        
        # High score
        high_score_text = font.render(f"High Score: {score}", True, (200, 200, 200))
        self.screen.blit(high_score_text, (10, 50))
        
        # Difficulty info
        font_small = pygame.font.Font(None, 24)
        diff_text = font_small.render("Difficulty: Normal", True, (150, 150, 150))
        self.screen.blit(diff_text, (10, 90))
        
        # Controls help (updated to match hex_main scheme)
        controls = [
            "D: Right (Southeast)",
            "A: Down-Left (Southwest)", 
            "E: Up-Right (Northeast)",
            "Q: Up-Left (Northwest)",
            "W: Up (North)",
            "S: Down (South)"
        ]
        
        start_y = self.config.screen_height - 120
        for i, control in enumerate(controls):
            control_text = font_small.render(control, True, (100, 100, 100))
            self.screen.blit(control_text, (10, start_y + i * 25))
        
        # Game state overlay
        if paused:
            font_large = pygame.font.Font(None, 48)
            pause_text = font_large.render("PAUSED", True, (255, 255, 100))
            pause_rect = pause_text.get_rect(center=(self.config.screen_width // 2, self.config.screen_height // 2))
            self.screen.blit(pause_text, pause_rect)
        
        if game_over:
            font_large = pygame.font.Font(None, 48)
            over_text = font_large.render("GAME OVER", True, (255, 100, 100))
            over_rect = over_text.get_rect(center=(self.config.screen_width // 2, self.config.screen_height // 2))
            
            # Draw background for text
            bg_rect = over_rect.inflate(40, 20)
            pygame.draw.rect(self.screen, (0, 0, 0, 180), bg_rect)
            
            self.screen.blit(over_text, over_rect)
            
            restart_text = font.render("Press R to Restart | ESC to Quit", True, (255, 255, 255))
            restart_rect = restart_text.get_rect(center=(self.config.screen_width // 2, self.config.screen_height // 2 + 60))
            self.screen.blit(restart_text, restart_rect)
    
    def render_ui(self, ui_data: dict) -> None:
        """Render UI overlay."""
        self._draw_ui(
            ui_data.get('score', 0),
            ui_data.get('paused', False),
            ui_data.get('game_state') == 'game_over'
        )


def main():
    """Main entry point for Phase 4."""
    # Initialize pygame
    pygame.init()
    
    # Create configuration
    config = GameConfig()
    
    # Set up display
    screen_width = config.screen_width
    screen_height = config.screen_height
    
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Advanced Snake Game - Phase 4 (Hexagonal)")
    
    # Create game controller
    game_controller = Phase4GameController(config)
    game_controller.initialize(screen)
    
    # Create renderer
    renderer = SimpleHexRenderer(screen, config)
    
    # Start the first game
    game_controller.start_new_game()
    print("Phase 4 game started. Controls: D=Right, A=Down-Left, E=Up-Right, Q=Up-Left, W=Up, S=Down")
    print("Press R to restart, ESC to pause.")
    
    # Main game loop
    clock = pygame.time.Clock()
    running = True
    last_time = time.time()
    
    while running:
        # Calculate delta time
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                game_controller.handle_input(event)
        
        # Update game
        game_controller.update(dt)
        
        # Render
        game_data = game_controller.get_game_data_for_rendering()
        ui_data = game_controller.get_ui_data()
        
        renderer.render(game_data)
        renderer.render_ui(ui_data)
        
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