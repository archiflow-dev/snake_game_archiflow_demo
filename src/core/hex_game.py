"""Main game controller for hexagonal snake game."""

import pygame
import time
from typing import Optional, Dict, Any
from .game import Game
from .state import GameState
from ..entities.hex_snake import HexSnake
from ..entities.food import Food
from ..entities.grid import HexCoord
from ..grids.hexagonal import HexagonalGrid
from ..renderers.hex_renderer import HexagonalRenderer
from ..systems.hex_input import HexInputManager
from ..utils.animation import AnimationSystem, EntityAnimator, EasingFunctions
from ..utils.difficulty import DifficultyManager, DifficultyMode
from ..utils.colors import Colors


class HexGameController:
    """Game controller specifically for hexagonal snake game."""
    
    def __init__(self, screen_width: int = 800, screen_height: int = 600, hex_size: int = 20):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.hex_size = hex_size
        
        # Core systems
        self.screen = None  # Will be initialized in start()
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game components
        self.grid = None
        self.snake = None
        self.food = None
        self.renderer = None
        self.input_manager = None
        
        # Enhanced systems for Phase 2
        self.animation_system = AnimationSystem()
        self.entity_animator = None
        self.difficulty_manager = DifficultyManager()
        
        # Game state
        self.state = GameState.MENU
        self.game_mode = "NORMAL"
        self.score = 0
        self.high_score = 0
        self.frame_count = 0
        self.last_update_time = time.time()
        
        # Performance settings
        self.target_fps = 60
        self.enable_animations = True
        self.show_grid_lines = True
        
        # UI state
        self.menu_selection = 0
        self.paused_menu_selection = 0
    
    def initialize(self) -> None:
        """Initialize all game components."""
        # Create pygame screen if not exists
        if self.screen is None:
            pygame.init()
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
            pygame.display.set_caption("Hexagonal Snake Game - Phase 2")
        
        # Initialize hexagonal grid
        self.grid = HexagonalGrid(self.screen_width, self.screen_height, self.hex_size)
        
        # Initialize renderer
        self.renderer = HexagonalRenderer(self.screen, self.grid)
        self.renderer.set_grid_visibility(self.show_grid_lines)
        
        # Initialize input manager
        self.input_manager = HexInputManager()
        self._setup_input_handlers()
        
        # Initialize animation system
        self.entity_animator = EntityAnimator(self.animation_system)
        
        # Initialize difficulty manager
        self.difficulty_manager.set_difficulty_mode(DifficultyMode.STEP_FUNCTION)
        
        # Set up initial game state
        self._setup_new_game()
    
    def _setup_input_handlers(self) -> None:
        """Setup input handlers for game actions."""
        # Menu navigation
        self.input_manager.register_action_handler('start', self.start_game)
        self.input_manager.register_action_handler('pause', self.toggle_pause)
        self.input_manager.register_action_handler('restart', self.restart_game)
        
        # Direction changes will be handled in update loop
    
    def _setup_new_game(self) -> None:
        """Set up a new game."""
        # Get a valid starting position
        start_coord = self.grid.get_random_empty_cell()
        if start_coord is None:
            start_coord = HexCoord(0, 0)  # Fallback to center
        
        # Start with a random valid direction
        directions = self.grid.directions
        import random
        start_direction = random.choice(directions)
        
        # Create snake
        self.snake = HexSnake(start_coord, start_direction, self.grid)
        
        # Create initial food
        self.food = self._spawn_food()
        
        # Reset game state
        self.score = 0
        self.difficulty_manager.reset_difficulty()
        self.animation_system.stop_all_animations()
    
    def _spawn_food(self) -> Food:
        """Spawn food at a random empty location."""
        empty_coord = self.grid.get_random_empty_cell()
        if empty_coord is None:
            return None  # No empty cells available
        
        # Convert to square coordinate for Food entity (temporary compatibility)
        # TODO: Update Food entity to use HexCoord directly
        from ..entities.grid import SquareCoord
        square_coord = SquareCoord(empty_coord.q, empty_coord.r)
        
        food = Food(square_coord)
        food.points = self.difficulty_manager.current_food_points
        return food
    
    def start_game(self) -> None:
        """Start a new game."""
        if self.state in [GameState.MENU, GameState.GAME_OVER]:
            self._setup_new_game()
            self.state = GameState.PLAYING
    
    def toggle_pause(self) -> None:
        """Toggle pause state."""
        if self.state == GameState.PLAYING:
            self.state = GameState.PAUSED
            self.paused_menu_selection = 0
        elif self.state == GameState.PAUSED:
            self.state = GameState.PLAYING
    
    def restart_game(self) -> None:
        """Restart the current game."""
        if self.state in [GameState.PLAYING, GameState.PAUSED, GameState.GAME_OVER]:
            self._setup_new_game()
            self.state = GameState.PLAYING
    
    def update(self, dt: float) -> None:
        """Update game logic."""
        if self.state == GameState.PLAYING:
            self._update_gameplay(dt)
        elif self.state == GameState.PAUSED:
            self._update_paused()
        elif self.state == GameState.MENU:
            self._update_menu()
        elif self.state == GameState.GAME_OVER:
            self._update_game_over()
        
        # Update animation system
        if self.enable_animations:
            self.animation_system.update()
    
    def _update_gameplay(self, dt: float) -> None:
        """Update gameplay logic."""
        # Process input
        direction = self.input_manager.get_validated_movement(
            self.snake.get_direction_name()
        )
        
        if direction:
            self.snake.change_direction(direction)
        
        # Update difficulty based on score
        if self.score != self.difficulty_manager.current_score:
            self.difficulty_manager.update_score(self.score)
        
        # Move snake based on difficulty-adjusted speed
        move_interval = 1.0 / (10 * self.difficulty_manager.current_speed_multiplier)
        
        current_time = time.time()
        if current_time - self.last_update_time >= move_interval:
            if self.snake.move():
                # Check food collision
                if self.food and self._check_food_collision():
                    self._eat_food()
                
                # Update animations for smooth movement
                if self.enable_animations:
                    self._update_snake_animations()
                
                self.last_update_time = current_time
            else:
                # Snake died
                self._game_over()
    
    def _update_paused(self) -> None:
        """Update paused state."""
        # Handle pause menu navigation
        pass  # TODO: Implement pause menu
    
    def _update_menu(self) -> None:
        """Update main menu state."""
        # Handle menu navigation
        pass  # TODO: Implement main menu
    
    def _update_game_over(self) -> None:
        """Update game over state."""
        # Handle game over menu
        pass  # TODO: Implement game over menu
    
    def _check_food_collision(self) -> bool:
        """Check if snake head collided with food."""
        if not self.food:
            return False
        
        head_pos = self.snake.get_head_position()
        # Convert food position to hex coordinate for comparison
        food_hex = HexCoord(self.food.position.x, self.food.position.y)
        
        return head_pos == food_hex
    
    def _eat_food(self) -> None:
        """Handle food consumption."""
        if not self.food:
            return
        
        # Update score
        self.score += self.food.points
        if self.score > self.high_score:
            self.high_score = self.score
        
        # Record food consumption for adaptive difficulty
        current_time = time.time()
        time_since_last = current_time - getattr(self, '_last_food_time', current_time)
        self.difficulty_manager.record_food_eaten(time_since_last)
        self._last_food_time = current_time
        
        # Make snake grow
        self.snake.grow()
        
        # Spawn new food
        self.food = self._spawn_food()
        
        # Play eating animation
        if self.enable_animations:
            self._play_eat_animation()
    
    def _update_snake_animations(self) -> None:
        """Update smooth movement animations for snake."""
        if not self.entity_animator:
            return
        
        # Animate each segment
        for i, segment in enumerate(self.snake.segments):
            entity_id = f"snake_segment_{i}"
            
            # Simple scale animation for movement feedback
            if i == len(self.snake.segments) - 1:  # Head
                current_scale = self.entity_animator.get_current_scale(entity_id) or 1.0
                if current_scale >= 1.0:
                    self.entity_animator.animate_scale(
                        entity_id, 1.0, 1.2, 0.1,
                        EasingFunctions.ease_out_elastic
                    )
    
    def _play_eat_animation(self) -> None:
        """Play animation when food is eaten."""
        if not self.food:
            return
        
        # Animate food consumption
        food_id = "food"
        self.entity_animator.animate_scale(
            food_id, 1.0, 1.5, 0.2,
            EasingFunctions.ease_out_back
        )
    
    def _game_over(self) -> None:
        """Handle game over."""
        self.state = GameState.GAME_OVER
        
        # Record death for adaptive difficulty
        self.difficulty_manager.record_death(self.score)
        
        # Play death animation
        if self.enable_animations:
            self._play_death_animation()
    
    def _play_death_animation(self) -> None:
        """Play snake death animation."""
        if not self.entity_animator:
            return
        
        # Flash red and scale down
        for i, segment in enumerate(self.snake.segments):
            entity_id = f"snake_segment_{i}"
            
            # Animate to red color
            self.entity_animator.animate_color(
                entity_id, Colors.SNAKE_BODY, Colors.RED, 0.5
            )
            
            # Scale down animation
            self.entity_animator.animate_scale(
                entity_id, 1.0, 0.1, 0.5,
                EasingFunctions.ease_in_cubic
            )
    
    def render(self) -> None:
        """Render the game."""
        if not self.screen:
            return
        
        # Clear screen
        self.renderer.clear_screen(Colors.BACKGROUND)
        
        if self.state == GameState.PLAYING or self.state == GameState.PAUSED:
            self._render_game()
        elif self.state == GameState.MENU:
            self._render_menu()
        elif self.state == GameState.GAME_OVER:
            self._render_game_over()
        
        # Update display
        pygame.display.flip()
        self.frame_count += 1
    
    def _render_game(self) -> None:
        """Render the main game view."""
        # Draw grid
        self.renderer.draw_grid()
        
        # Draw food
        if self.food:
            self.renderer.draw_food(self.food)
        
        # Draw snake
        if self.snake:
            self.renderer.draw_snake(self.snake)
        
        # Draw UI overlay
        self._render_game_ui()
    
    def _render_game_ui(self) -> None:
        """Render game UI elements."""
        font = pygame.font.Font(None, 36)
        
        # Score
        score_text = font.render(f"Score: {self.score}", True, Colors.TEXT)
        self.screen.blit(score_text, (10, 10))
        
        # High score
        high_score_text = font.render(f"High Score: {self.high_score}", True, Colors.TEXT)
        self.screen.blit(high_score_text, (10, 50))
        
        # Difficulty level
        diff_name = self.difficulty_manager.get_current_difficulty_name()
        diff_text = font.render(f"Difficulty: {diff_name}", True, Colors.TEXT)
        self.screen.blit(diff_text, (10, 90))
        
        # Speed multiplier
        speed = self.difficulty_manager.current_speed_multiplier
        speed_text = font.render(f"Speed: {speed:.1f}x", True, Colors.TEXT)
        self.screen.blit(speed_text, (10, 130))
        
        # Progress bar to next difficulty
        if self.difficulty_manager.get_difficulty_progress() < 1.0:
            progress = self.difficulty_manager.get_difficulty_progress()
            bar_width = 200
            bar_height = 10
            bar_x = 10
            bar_y = 170
            
            # Background
            pygame.draw.rect(self.screen, Colors.GRID_LINES, 
                           (bar_x, bar_y, bar_width, bar_height))
            
            # Progress
            pygame.draw.rect(self.screen, Colors.GREEN, 
                           (bar_x, bar_y, int(bar_width * progress), bar_height))
        
        # Pause indicator
        if self.state == GameState.PAUSED:
            pause_font = pygame.font.Font(None, 72)
            pause_text = pause_font.render("PAUSED", True, Colors.YELLOW)
            text_rect = pause_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(pause_text, text_rect)
    
    def _render_menu(self) -> None:
        """Render main menu."""
        font = pygame.font.Font(None, 72)
        option_font = pygame.font.Font(None, 48)
        
        # Title
        title = font.render("HEXAGONAL SNAKE", True, Colors.NEON_GREEN)
        title_rect = title.get_rect(center=(self.screen_width // 2, 150))
        self.screen.blit(title, title_rect)
        
        subtitle = option_font.render("Phase 2 Implementation", True, Colors.NEON_BLUE)
        subtitle_rect = subtitle.get_rect(center=(self.screen_width // 2, 220))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Menu options
        options = ["Start Game", "Controls", "Quit"]
        for i, option in enumerate(options):
            color = Colors.NEON_YELLOW if i == self.menu_selection else Colors.TEXT
            text = option_font.render(option, True, color)
            text_rect = text.get_rect(center=(self.screen_width // 2, 350 + i * 60))
            self.screen.blit(text, text_rect)
        
        # Controls info
        controls_font = pygame.font.Font(None, 24)
        controls = [
            "Controls: D=Right, A=Down-Left, E=Up-Right, Q=Up-Left",
            "W=Up, S=Down | Arrow keys also supported",
            "ESC: Pause | R: Restart"
        ]
        
        for i, control in enumerate(controls):
            text = controls_font.render(control, True, Colors.GRID_LINES)
            text_rect = text.get_rect(center=(self.screen_width // 2, 550 + i * 25))
            self.screen.blit(text, text_rect)
    
    def _render_game_over(self) -> None:
        """Render game over screen."""
        font = pygame.font.Font(None, 72)
        score_font = pygame.font.Font(None, 48)
        option_font = pygame.font.Font(None, 36)
        
        # Game over text
        game_over_text = font.render("GAME OVER", True, Colors.RED)
        text_rect = game_over_text.get_rect(center=(self.screen_width // 2, 150))
        self.screen.blit(game_over_text, text_rect)
        
        # Final score
        score_text = score_font.render(f"Final Score: {self.score}", True, Colors.TEXT)
        score_rect = score_text.get_rect(center=(self.screen_width // 2, 250))
        self.screen.blit(score_text, score_rect)
        
        # High score
        if self.score >= self.high_score:
            high_score_text = score_font.render("NEW HIGH SCORE!", True, Colors.NEON_YELLOW)
        else:
            high_score_text = score_font.render(f"High Score: {self.high_score}", True, Colors.TEXT)
        
        high_score_rect = high_score_text.get_rect(center=(self.screen_width // 2, 320))
        self.screen.blit(high_score_text, high_score_rect)
        
        # Options
        options = ["Press SPACE to Play Again", "Press ESC for Main Menu"]
        for i, option in enumerate(options):
            text = option_font.render(option, True, Colors.TEXT)
            text_rect = text.get_rect(center=(self.screen_width // 2, 450 + i * 40))
            self.screen.blit(text, text_rect)
    
    def handle_events(self) -> None:
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                # Handle menu navigation
                if self.state == GameState.MENU:
                    if event.key == pygame.K_UP:
                        self.menu_selection = (self.menu_selection - 1) % 3
                    elif event.key == pygame.K_DOWN:
                        self.menu_selection = (self.menu_selection + 1) % 3
                    elif event.key == pygame.K_RETURN:
                        if self.menu_selection == 0:  # Start Game
                            self.start_game()
                        elif self.menu_selection == 2:  # Quit
                            self.running = False
                elif self.state == GameState.GAME_OVER:
                    if event.key == pygame.K_SPACE:
                        self.restart_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.state = GameState.MENU
                        self.menu_selection = 0
            
            # Pass to input manager for game controls
            self.input_manager.handle_event(event)
    
    def run(self) -> None:
        """Main game loop."""
        self.initialize()
        
        while self.running:
            dt = self.clock.tick(self.target_fps) / 1000.0  # Convert to seconds
            
            self.handle_events()
            self.update(dt)
            self.render()
        
        pygame.quit()
    
    def get_game_stats(self) -> Dict[str, Any]:
        """Get current game statistics."""
        return {
            "score": self.score,
            "high_score": self.high_score,
            "snake_length": self.snake.get_length() if self.snake else 0,
            "difficulty_stats": self.difficulty_manager.get_difficulty_stats(),
            "fps": self.clock.get_fps(),
            "frame_count": self.frame_count,
            "state": self.state.value,
            "game_mode": self.game_mode
        }