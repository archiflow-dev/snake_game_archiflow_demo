"""Enhanced game controller with Phase 3 AI and multiplayer features."""

import pygame
import time
from typing import Dict, List, Optional, Tuple
from ..entities.snake import Snake, Direction, SquareCoord
from ..entities.food import Food
from ..entities.grid import Grid
from ..ai.multi_snake import MultiSnakeGame, GameMode, MultiSnakeGameFactory
from ..ai.ai_snake import AIPersonality
from ..data.leaderboard import Leaderboard, LeaderboardEntry
from ..data.replay import ReplayRecorder, ReplayPlayer, ReplayManager
from ..core.config import GameConfig
from ..core.state import GameState


class Phase3GameController:
    """Enhanced game controller with AI and multiplayer features."""
    
    def __init__(self, config: GameConfig):
        self.config = config
        self.screen = None
        self.clock = pygame.time.Clock()
        
        # Core game components
        self.grid = Grid(config.grid_width, config.grid_height)
        self.multi_snake_game: Optional[MultiSnakeGame] = None
        self.game_mode = GameMode.FREE_FOR_ALL
        
        # Player management
        self.player_name = "Player"
        self.ai_snake_count = 2
        self.ai_difficulty = 0.5
        
        # Data systems
        self.leaderboard = Leaderboard()
        self.replay_recorder = ReplayRecorder()
        self.replay_player = ReplayPlayer()
        self.replay_manager = ReplayManager()
        self.current_replay_path: Optional[str] = None
        
        # Game state
        self.game_state = GameState.MENU
        self.running = True
        self.paused = False
        self.game_time = 0.0
        self.score = 0
        self.high_score = 0
        
        # Input handling
        self.keys_pressed = set()
        self.input_buffer: List[Direction] = []
        
        # UI state
        self.show_leaderboard = False
        self.show_replay_list = False
        self.selected_menu_item = 0
        self.menu_items = ["Start Game", "AI Settings", "Game Mode", "Leaderboards", "Replays", "Quit"]
        self.game_mode_items = ["Free For All", "Survival", "Score Race", "Cooperative"]
        self.ai_settings_items = ["AI Count", "AI Difficulty", "AI Personalities", "Back"]
        self.selected_ai_count = self.ai_snake_count
        self.selected_ai_difficulty = self.ai_difficulty
        self.ai_personalities = [AIPersonality.BALANCED, AIPersonality.AGGRESSIVE, 
                                AIPersonality.CAUTIOUS, AIPersonality.RANDOM]
    
    def initialize(self, screen) -> None:
        """Initialize the game controller with a display surface."""
        self.screen = screen
        self.high_score = self._load_high_score()
    
    def start_new_game(self) -> None:
        """Start a new game with current settings."""
        # Reset grid
        self.grid.clear()
        
        # Create multi-snake game based on mode
        if self.game_mode == GameMode.SURVIVAL:
            self.multi_snake_game = MultiSnakeGameFactory.create_survival_game(
                self.grid, self.ai_snake_count, self.ai_difficulty
            )
        elif self.game_mode == GameMode.SCORE_RACE:
            self.multi_snake_game = MultiSnakeGameFactory.create_score_race_game(
                self.grid, time_limit=120.0, num_ai=self.ai_snake_count, 
                ai_difficulty=self.ai_difficulty
            )
        elif self.game_mode == GameMode.COOPERATIVE:
            self.multi_snake_game = MultiSnakeGameFactory.create_score_race_game(
                self.grid, time_limit=180.0, num_ai=self.ai_snake_count,
                ai_difficulty=self.ai_difficulty
            )
        else:  # FREE_FOR_ALL
            self.multi_snake_game = MultiSnakeGameFactory.create_free_for_all_game(
                self.grid, self.ai_snake_count, self.ai_difficulty
            )
        
        # Add player snake
        player_start = SquareCoord(self.grid.width // 2, self.grid.height // 2)
        self.multi_snake_game.add_player_snake("player", player_start, Direction.RIGHT)
        
        # Start recording
        player_names = [self.player_name] + [f"AI_{i}" for i in range(self.ai_snake_count)]
        game_settings = {
            'ai_difficulty': self.ai_difficulty,
            'ai_count': self.ai_snake_count,
            'game_mode': self.game_mode.value
        }
        
        self.replay_recorder.start_recording(
            self.game_mode, (self.grid.width, self.grid.height), 
            player_names, game_settings
        )
        
        # Reset game state
        self.game_state = GameState.PLAYING
        self.game_time = 0.0
        self.score = 0
        self.paused = False
        self.current_replay_path = self.replay_manager.get_replay_path()
    
    def start_replay(self, replay_file: str) -> bool:
        """Start playing a replay."""
        if self.replay_player.load_replay(replay_file):
            self.game_state = GameState.REPLAY
            self.replay_player.start_playback()
            return True
        return False
    
    def update(self, dt: float) -> None:
        """Update game state."""
        if self.paused:
            return
        
        if self.game_state == GameState.PLAYING:
            self._update_gameplay(dt)
        elif self.game_state == GameState.REPLAY:
            self._update_replay(dt)
    
    def _update_gameplay(self, dt: float) -> None:
        """Update active gameplay."""
        if not self.multi_snake_game:
            return
        
        # Limit update speed to prevent game from being too fast
        max_dt = 0.1  # Max 100ms per update (10 updates per second for slower gameplay)
        dt = min(dt, max_dt)
        
        self.game_time += dt
        
        # Process player input
        self._process_player_input()
        
        # Update multi-snake game
        collision_events = self.multi_snake_game.update(dt)
        
        # Record game state
        self._record_game_state()
        
        # Check if player is still active
        if "player" not in self.multi_snake_game.active_snakes:
            self._handle_game_over()
        
        # Check win conditions
        if self.multi_snake_game.is_game_over():
            self._handle_game_over()
        
        # Update score
        if "player" in self.multi_snake_game.scores:
            self.score = self.multi_snake_game.scores["player"]
    
    def _update_replay(self, dt: float) -> None:
        """Update replay playback."""
        if not self.replay_player.is_playing():
            self.game_state = GameState.MENU
            return
        
        # Get current replay state for rendering
        current_state = self.replay_player.get_current_game_state()
        # This would be used by the renderer to draw the replay
    
    def _process_player_input(self) -> None:
        """Process buffered player input."""
        if not self.multi_snake_game or "player" not in self.multi_snake_game.snakes:
            return
        
        player_snake = self.multi_snake_game.snakes["player"]
        
        # Process input buffer
        for direction in self.input_buffer:
            if player_snake.set_direction(direction):
                self.replay_recorder.record_input("player", direction)
        
        self.input_buffer.clear()
    
    def _record_game_state(self) -> None:
        """Record current game state for replay."""
        if not self.multi_snake_game or not self.replay_recorder.recording:
            return
        
        snakes = self.multi_snake_game.snakes
        food_items = self.multi_snake_game.food_items
        scores = self.multi_snake_game.scores
        active_snakes = self.multi_snake_game.active_snakes
        eliminated_snakes = self.multi_snake_game.eliminated_snakes
        collision_events = self.multi_snake_game.collision_events
        
        try:
            self.replay_recorder.record_game_state(
                snakes, food_items, scores, active_snakes, 
                eliminated_snakes, collision_events
            )
        except Exception as e:
            print(f"Warning: Failed to record game state: {e}")
            # Stop recording if there's an error
            self.replay_recorder.stop_recording()
    
    def _handle_game_over(self) -> None:
        """Handle game over conditions."""
        self.game_state = GameState.GAME_OVER
        
        # Stop recording
        if self.replay_recorder.stop_recording():
            self.replay_recorder.save_replay(self.current_replay_path)
        
        # Update leaderboard
        if self.score > 0:
            entry = LeaderboardEntry(
                player_name=self.player_name,
                score=self.score,
                game_mode=self.game_mode.value
            )
            self.leaderboard.add_entry(entry)
        
        # Update high score
        if self.score > self.high_score:
            self.high_score = self.score
            self._save_high_score()
    
    def handle_input(self, event: pygame.event.Event) -> None:
        """Handle pygame events."""
        if event.type == pygame.KEYDOWN:
            self.keys_pressed.add(event.key)
            self._handle_key_down(event.key)
        elif event.type == pygame.KEYUP:
            self.keys_pressed.discard(event.key)
    
    def _handle_key_down(self, key: int) -> None:
        """Handle key press events."""
        if self.game_state == GameState.MENU:
            self._handle_menu_input(key)
        elif self.game_state == GameState.PLAYING:
            self._handle_game_input(key)
        elif self.game_state == GameState.GAME_OVER:
            self._handle_game_over_input(key)
        elif self.game_state == GameState.REPLAY:
            self._handle_replay_input(key)
    
    def _handle_menu_input(self, key: int) -> None:
        """Handle input in menu state."""
        if key == pygame.K_UP:
            self.selected_menu_item = (self.selected_menu_item - 1) % len(self.menu_items)
        elif key == pygame.K_DOWN:
            self.selected_menu_item = (self.selected_menu_item + 1) % len(self.menu_items)
        elif key == pygame.K_RETURN:
            self._execute_menu_action()
    
    def _handle_game_input(self, key: int) -> None:
        """Handle input during gameplay."""
        if key == pygame.K_ESCAPE:
            self.paused = not self.paused
        elif key == pygame.K_p:
            self.paused = not self.paused
        else:
            # Map keys to directions
            direction_map = {
                pygame.K_w: Direction.UP,
                pygame.K_s: Direction.DOWN,
                pygame.K_a: Direction.LEFT,
                pygame.K_d: Direction.RIGHT
            }
            
            if key in direction_map:
                self.input_buffer.append(direction_map[key])
    
    def _handle_game_over_input(self, key: int) -> None:
        """Handle input in game over state."""
        if key == pygame.K_RETURN:
            self.start_new_game()
        elif key == pygame.K_ESCAPE:
            self.game_state = GameState.MENU
    
    def _handle_replay_input(self, key: int) -> None:
        """Handle input during replay playback."""
        if key == pygame.K_ESCAPE:
            self.replay_player.stop_playback()
            self.game_state = GameState.MENU
        elif key == pygame.K_SPACE:
            if self.replay_player.is_playing():
                self.replay_player.stop_playback()
            else:
                self.replay_player.start_playback()
    
    def _execute_menu_action(self) -> None:
        """Execute the selected menu action."""
        item = self.menu_items[self.selected_menu_item]
        
        if item == "Start Game":
            self.start_new_game()
        elif item == "AI Settings":
            # TODO: Show AI settings screen
            pass
        elif item == "Game Mode":
            # TODO: Show game mode selection
            pass
        elif item == "Leaderboards":
            self.show_leaderboard = True
        elif item == "Replays":
            self.show_replay_list = True
        elif item == "Quit":
            self.running = False
    
    def _load_high_score(self) -> int:
        """Load high score from file."""
        try:
            # Get best score from any mode
            best_entry = self.leaderboard.get_player_best(self.player_name, "free_for_all")
            if best_entry:
                return best_entry.score
        except:
            pass
        return 0
    
    def _save_high_score(self) -> None:
        """Save high score to file."""
        # Handled by leaderboard system
        pass
    
    def get_game_data_for_rendering(self) -> Dict:
        """Get current game data for the renderer."""
        if self.game_state == GameState.PLAYING and self.multi_snake_game:
            return {
                'snakes': self.multi_snake_game.get_active_snakes(),
                'food_items': self.multi_snake_game.food_items,
                'scores': self.multi_snake_game.scores,
                'game_time': self.game_time,
                'game_mode': self.game_mode,
                'is_paused': self.paused
            }
        elif self.game_state == GameState.REPLAY:
            current_state = self.replay_player.get_current_game_state()
            if current_state:
                # Convert replay state to renderable format
                # This is a simplified version - full implementation would reconstruct snake objects
                return {
                    'replay_data': current_state,
                    'playback_stats': self.replay_player.get_playback_stats()
                }
        
        return {}
    
    def get_ui_data(self) -> Dict:
        """Get UI data for menus and overlays."""
        return {
            'game_state': self.game_state,
            'score': self.score,
            'high_score': self.high_score,
            'selected_menu_item': self.selected_menu_item,
            'menu_items': self.menu_items,
            'show_leaderboard': self.show_leaderboard,
            'show_replay_list': self.show_replay_list,
            'leaderboard_entries': self.leaderboard.get_top_entries(self.game_mode.value, 10),
            'replay_list': self.replay_manager.get_replay_list(),
            'is_paused': self.paused
        }