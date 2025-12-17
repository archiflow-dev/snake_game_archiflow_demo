"""Main game loop and coordination."""

import pygame
import sys
from typing import Optional

from .config import Config
from .state import StateManager, GameState
from .events import EventManager, Event, EventType
from ..systems.input import InputManager
from ..systems.render import RenderEngine
from ..entities.grid import Grid, SquareCoord
from ..entities.snake import Snake, Direction
from ..entities.food import Food


class Game:
    """Main game class that coordinates all game systems."""
    
    def __init__(self):
        pygame.init()
        
        # Initialize core systems
        self.config = Config()
        self.state_manager = StateManager()
        self.event_manager = EventManager()
        
        # Display setup
        self._setup_display()
        
        # Game timing
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0.0
        self.move_timer = 0.0
        self.move_interval = 0.2  # Start with slow speed (5 moves per second)
        
        # Game data
        self.score = 0
        self.high_score = 0
        
        # Initialize game systems
        self._initialize_systems()
        
        # Register event listeners
        self._register_event_listeners()
        
        # Register state handlers
        self._register_state_handlers()
    
    def _initialize_systems(self) -> None:
        """Initialize all game systems."""
        # Create grid
        grid_width = self.config.get("game.grid_size[0]", 20)
        grid_height = self.config.get("game.grid_size[1]", 15)
        self.grid = Grid(grid_width, grid_height)
        
        # Create input manager
        self.input_manager = InputManager()
        
        # Create renderer
        self.renderer = RenderEngine(self.screen, self.grid)
        
        # Set up input handlers
        self._setup_input_handlers()
    
    def _setup_display(self) -> None:
        """Initialize the display window."""
        width = self.config.get("window.width", 800)
        height = self.config.get("window.height", 600)
        title = self.config.get("window.title", "Snake Game")
        
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
    
    def _register_event_listeners(self) -> None:
        """Register event listeners for game events."""
        self.event_manager.subscribe(EventType.QUIT, self._handle_quit)
        self.event_manager.subscribe(EventType.GAME_OVER, self._handle_game_over)
    
    def _register_state_handlers(self) -> None:
        """Register state transition handlers."""
        self.state_manager.register_state_handler(GameState.PLAYING, self._start_playing)
        self.state_manager.register_state_handler(GameState.GAME_OVER, self._handle_game_over_state)
    
    def _handle_quit(self, event: Event) -> None:
        """Handle quit event."""
        self.running = False
    
    def _handle_game_over(self, event: Event) -> None:
        """Handle game over event."""
        self.state_manager.set_state(GameState.GAME_OVER)
        if self.score > self.high_score:
            self.high_score = self.score
    
    def _start_playing(self) -> None:
        """Initialize gameplay when entering PLAYING state."""
        self.score = 0
        # Systems will be initialized in the full implementation
    
    def _start_playing(self) -> None:
        """Initialize gameplay when entering PLAYING state."""
        self.score = 0
        self.move_timer = 0.0
        self._update_difficulty()  # Reset to starting speed
        
        # Clear grid
        self.grid.clear()
        
        # Create snake at center
        start_x = self.grid.width // 2
        start_y = self.grid.height // 2
        start_pos = SquareCoord(start_x, start_y)
        start_length = self.config.get("snake.starting_length", 3)
        self.snake = Snake(start_pos, Direction.RIGHT, start_length)
        
        # Mark initial snake positions as occupied
        for segment in self.snake.get_segments():
            self.grid.occupy(segment)
        
        # Spawn initial food
        self.food = Food.spawn_food(self.grid)
    
    def _update_snake_movement(self) -> None:
        """Update snake movement and check collisions."""
        if not self.snake:
            return
        
        # Move snake
        removed_tail = self.snake.move()
        
        # Check wall collision
        head = self.snake.get_head()
        if not self.grid.is_valid_position(head):
            self.event_manager.dispatch(Event(EventType.GAME_OVER))
            return
        
        # Check self collision
        if self.snake.check_self_collision():
            self.event_manager.dispatch(Event(EventType.GAME_OVER))
            return
        
        # Update grid occupancy
        if removed_tail:
            self.grid.vacate(removed_tail)
        
        # Mark new head position as occupied
        self.grid.occupy(head)
        
        # Check food collision
        if self.food and head == self.food.get_position():
            self._handle_food_eaten()
    
    def _handle_food_eaten(self) -> None:
        """Handle when snake eats food."""
        if not self.food:
            return
        
        # Increase score
        self.score += self.food.get_point_value()
        self.event_manager.dispatch(Event(EventType.SCORE_CHANGED, {'score': self.score}))
        
        # Grow snake
        self.snake.grow(self.config.get("snake.growth_per_food", 1))
        
        # Spawn new food
        self.food = Food.spawn_food(self.grid)
        
        # Dispatch food eaten event
        self.event_manager.dispatch(Event(EventType.FOOD_EATEN))
    
    def _update_difficulty(self) -> None:
        """Update game difficulty based on score."""
        # Simple difficulty scaling - decrease move interval (increase speed)
        if self.score < 50:
            self.move_interval = 0.2  # 5 moves per second
        elif self.score < 150:
            self.move_interval = 0.15  # ~6.7 moves per second
        elif self.score < 300:
            self.move_interval = 0.1  # 10 moves per second
        else:
            # Gradually increase speed beyond 300 points
            self.move_interval = max(0.05, 0.1 - (self.score - 300) / 1000)
    
    def _handle_game_over_state(self) -> None:
        """Handle transition to game over state."""
        pass  # UI updates would go here
    
    def run(self) -> None:
        """Main game loop."""
        while self.running:
            self.dt = self.clock.tick(self.config.get("game.fps", 60)) / 1000.0
            
            # Handle events
            self._handle_events()
            
            # Update game logic
            self._update()
            
            # Render
            self._render()
        
        pygame.quit()
        sys.exit()
    
    def _handle_events(self) -> None:
        """Process pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.event_manager.dispatch(Event(EventType.QUIT))
            elif event.type == pygame.KEYDOWN:
                self._handle_key_input(event.key)
            else:
                # Pass other events to input manager
                self.input_manager.handle_event(event)
    
    def _setup_input_handlers(self) -> None:
        """Set up input handlers."""
        self.input_manager.register_action_handler('start', self._handle_start)
        self.input_manager.register_action_handler('pause', self._handle_pause)
        self.input_manager.register_action_handler('restart', self._handle_restart)
        self.input_manager.register_action_handler('move_up', self._handle_move_up)
        self.input_manager.register_action_handler('move_down', self._handle_move_down)
        self.input_manager.register_action_handler('move_left', self._handle_move_left)
        self.input_manager.register_action_handler('move_right', self._handle_move_right)
    
    def _handle_start(self) -> None:
        """Handle start game action."""
        if self.state_manager.get_current_state() == GameState.MENU:
            self.state_manager.set_state(GameState.PLAYING)
    
    def _handle_pause(self) -> None:
        """Handle pause action."""
        if self.state_manager.is_in_gameplay():
            if self.state_manager.get_current_state() == GameState.PLAYING:
                self.state_manager.set_state(GameState.PAUSED)
            else:
                self.state_manager.set_state(GameState.PLAYING)
        else:
            self.event_manager.dispatch(Event(EventType.QUIT))
    
    def _handle_restart(self) -> None:
        """Handle restart action."""
        if self.state_manager.get_current_state() == GameState.GAME_OVER:
            self.state_manager.restart_gameplay()
    
    def _handle_move_up(self) -> None:
        """Handle move up input."""
        if self.state_manager.get_current_state() == GameState.PLAYING and self.snake:
            self.snake.set_direction(Direction.UP)
    
    def _handle_move_down(self) -> None:
        """Handle move down input."""
        if self.state_manager.get_current_state() == GameState.PLAYING and self.snake:
            self.snake.set_direction(Direction.DOWN)
    
    def _handle_move_left(self) -> None:
        """Handle move left input."""
        if self.state_manager.get_current_state() == GameState.PLAYING and self.snake:
            self.snake.set_direction(Direction.LEFT)
    
    def _handle_move_right(self) -> None:
        """Handle move right input."""
        if self.state_manager.get_current_state() == GameState.PLAYING and self.snake:
            self.snake.set_direction(Direction.RIGHT)
    
    def _handle_key_input(self, key: int) -> None:
        """Handle keyboard input."""
        # Pass event to input manager
        event = pygame.event.Event(pygame.KEYDOWN, {'key': key})
        self.input_manager.handle_event(event)
    
    def _update(self) -> None:
        """Update game logic."""
        current_state = self.state_manager.get_current_state()
        
        if current_state == GameState.PLAYING:
            # Update input manager
            self.input_manager.update()
            
            # Update snake movement (timer-based)
            self.move_timer += self.dt
            if self.move_timer >= self.move_interval:
                self.move_timer = 0.0
                self._update_snake_movement()
            
            # Update game speed based on score
            self._update_difficulty()
    
    def _render(self) -> None:
        """Render the game."""
        # Render based on current state
        current_state = self.state_manager.get_current_state()
        
        if current_state == GameState.MENU:
            self._render_menu()
        elif current_state == GameState.PLAYING:
            self._render_game()
        elif current_state == GameState.PAUSED:
            self._render_game()
            self._render_pause_overlay()
        elif current_state == GameState.GAME_OVER:
            self._render_game()
            self._render_game_over_overlay()
        
        pygame.display.flip()
    
    def _render_menu(self) -> None:
        """Render main menu."""
        if self.renderer:
            self.renderer.clear_screen()
            self.renderer.draw_start_menu()
    
    def _render_game(self) -> None:
        """Render gameplay elements."""
        if self.renderer:
            # Clear screen
            self.renderer.clear_screen()
            
            # Draw grid
            self.renderer.draw_grid()
            
            # Draw food
            if self.food:
                self.renderer.draw_food(self.food)
            
            # Draw snake
            if self.snake:
                self.renderer.draw_snake(self.snake)
            
            # Draw score
            self.renderer.draw_score(self.score, self.high_score)
    
    def _render_pause_overlay(self) -> None:
        """Render pause overlay."""
        if self.renderer:
            self.renderer.draw_pause_overlay()
    
    def _render_game_over_overlay(self) -> None:
        """Render game over overlay."""
        if self.renderer:
            self.renderer.draw_game_over(self.score)