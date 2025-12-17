"""Multi-snake gameplay system for advanced competitive modes."""

from typing import List, Dict, Optional, Set, Tuple
import time
from enum import Enum
from ..entities.snake import Snake, Direction, SquareCoord
from ..entities.food import Food
from ..entities.grid import Grid
from ..ai.ai_snake import AISnake, AIPersonality
from .pathfinding import PathFinder


class GameMode(Enum):
    """Different game modes for multi-snake gameplay."""
    SURVIVAL = "survival"      # Last snake alive wins
    SCORE_RACE = "score_race"  # Most points in time limit wins
    FREE_FOR_ALL = "free_for_all"  # No rules, just compete
    COOPERATIVE = "cooperative"  # Work together against AI


class CollisionType(Enum):
    """Types of collisions in multi-snake games."""
    WALL = "wall"
    SELF = "self"
    SNAKE = "snake"
    FOOD = "food"


class CollisionEvent:
    """Represents a collision event."""
    
    def __init__(self, snake_id: str, collision_type: CollisionType, 
                 position: SquareCoord, other_snake_id: Optional[str] = None):
        self.snake_id = snake_id
        self.collision_type = collision_type
        self.position = position
        self.other_snake_id = other_snake_id
        self.timestamp = time.time()
        self.name = f"collision_{snake_id}_{collision_type.value}_{int(self.timestamp)}"


class MultiSnakeGame:
    """Manages multiple snakes in a single game session."""
    
    def __init__(self, grid: Grid, game_mode: GameMode = GameMode.FREE_FOR_ALL):
        self.grid = grid
        self.game_mode = game_mode
        self.snakes: Dict[str, Snake] = {}
        self.food_items: List[Food] = []
        self.pathfinder = PathFinder(grid)
        self.collision_events: List[CollisionEvent] = []
        self.game_time = 0.0
        self.time_limit = None  # For timed modes
        self.scores: Dict[str, int] = {}
        self.active_snakes: Set[str] = set()
        self.eliminated_snakes: Set[str] = set()
        
        # Game mode specific settings
        self.max_food_items = 5
        self.food_spawn_rate = 0.1  # Probability per frame
        self.respawn_enabled = False
        self.respawn_delay = 3.0  # Seconds
        
    def add_player_snake(self, snake_id: str, start_position: SquareCoord, 
                         start_direction: Direction = Direction.RIGHT) -> bool:
        """
        Add a player-controlled snake to the game.
        
        Args:
            snake_id: Unique identifier for the snake
            start_position: Starting position
            start_direction: Starting direction
            
        Returns:
            True if snake was added successfully
        """
        if snake_id in self.snakes:
            return False
        
        if not self.grid.is_valid_position(start_position):
            return False
        
        # Create player snake
        snake = Snake(start_position, start_direction)
        snake.snake_id = snake_id
        
        self.snakes[snake_id] = snake
        self.scores[snake_id] = 0
        self.active_snakes.add(snake_id)
        
        return True
    
    def add_ai_snake(self, snake_id: str, start_position: SquareCoord,
                    personality: AIPersonality = AIPersonality.BALANCED,
                    difficulty: float = 0.5) -> bool:
        """
        Add an AI-controlled snake to the game.
        
        Args:
            snake_id: Unique identifier for the snake
            start_position: Starting position
            personality: AI personality
            difficulty: AI difficulty level
            
        Returns:
            True if snake was added successfully
        """
        if snake_id in self.snakes:
            return False
        
        if not self.grid.is_valid_position(start_position):
            return False
        
        # Create AI snake
        ai_snake = AISnake(start_position, personality=personality, 
                          difficulty=difficulty, snake_id=snake_id)
        ai_snake.set_pathfinder(self.pathfinder)
        
        self.snakes[snake_id] = ai_snake
        self.scores[snake_id] = 0
        self.active_snakes.add(snake_id)
        
        return True
    
    def remove_snake(self, snake_id: str) -> bool:
        """
        Remove a snake from the game.
        
        Args:
            snake_id: Snake to remove
            
        Returns:
            True if snake was removed
        """
        if snake_id not in self.snakes:
            return False
        
        self.active_snakes.discard(snake_id)
        self.eliminated_snakes.add(snake_id)
        return True
    
    def update(self, dt: float) -> List[CollisionEvent]:
        """
        Update the game state for one frame.
        
        Args:
            dt: Time delta in seconds
            
        Returns:
            List of collision events that occurred
        """
        self.game_time += dt
        events = []
        
        # Update AI snakes
        current_time = time.time()
        food_positions = [food.position for food in self.food_items]
        other_snakes = [snake for snake in self.snakes.values() 
                       if snake.snake_id not in self.eliminated_snakes]
        
        for snake_id, snake in self.snakes.items():
            if snake_id in self.active_snakes and isinstance(snake, AISnake):
                snake.update_ai(food_positions, other_snakes, self.grid, current_time)
        
        # Move all active snakes
        for snake_id in list(self.active_snakes):
            snake = self.snakes[snake_id]
            tail_position = snake.move()
            
            # Handle movement and collisions
            snake_events = self._handle_snake_movement(snake_id, snake, tail_position)
            events.extend(snake_events)
        
        # Update food
        self._update_food()
        
        # Check food collisions
        food_events = self._check_food_collisions()
        events.extend(food_events)
        
        # Check win/lose conditions
        self._check_game_conditions()
        
        self.collision_events.extend(events)
        return events
    
    def _handle_snake_movement(self, snake_id: str, snake: Snake, 
                              tail_position: Optional[SquareCoord]) -> List[CollisionEvent]:
        """Handle snake movement and detect collisions."""
        events = []
        head = snake.get_head()
        
        if not head:
            return events
        
        # Check wall collision
        if not self.grid.is_valid_position(head):
            event = CollisionEvent(snake_id, CollisionType.WALL, head)
            events.append(event)
            self._handle_snake_elimination(snake_id)
            return events
        
        # Check self collision
        if snake.check_self_collision():
            event = CollisionEvent(snake_id, CollisionType.SELF, head)
            events.append(event)
            self._handle_snake_elimination(snake_id)
            return events
        
        # Check snake-to-snake collisions
        for other_id, other_snake in self.snakes.items():
            if other_id != snake_id and other_snake.occupies_position(head):
                collision_type = CollisionType.SNAKE
                event = CollisionEvent(snake_id, collision_type, head, other_id)
                events.append(event)
                
                # Handle collision based on game mode
                self._handle_snake_collision(snake_id, other_id, head)
        
        # Update grid occupancy
        if tail_position:
            self.grid.vacate(tail_position)
        self.grid.occupy(head)
        
        return events
    
    def _check_food_collisions(self) -> List[CollisionEvent]:
        """Check for snake-food collisions."""
        events = []
        food_to_remove = []
        
        for food in self.food_items:
            for snake_id, snake in self.snakes.items():
                if snake_id in self.active_snakes and snake.get_head() == food.position:
                    # Snake ate food
                    snake.grow()
                    self.scores[snake_id] += food.point_value
                    
                    event = CollisionEvent(snake_id, CollisionType.FOOD, food.position)
                    events.append(event)
                    
                    food_to_remove.append(food)
                    break
        
        # Remove eaten food
        for food in food_to_remove:
            self.food_items.remove(food)
            self.grid.vacate(food.position)
        
        return events
    
    def _handle_snake_collision(self, snake1_id: str, snake2_id: str, 
                               collision_pos: SquareCoord) -> None:
        """Handle collision between two snakes."""
        if self.game_mode == GameMode.SURVIVAL:
            # In survival, both snakes are eliminated on collision
            self._handle_snake_elimination(snake1_id)
            self._handle_snake_elimination(snake2_id)
        elif self.game_mode == GameMode.FREE_FOR_ALL:
            # In free for all, the snake whose head hit the other is eliminated
            if self.snakes[snake1_id].get_head() == collision_pos:
                self._handle_snake_elimination(snake1_id)
        elif self.game_mode == GameMode.COOPERATIVE:
            # In cooperative, collisions don't eliminate snakes
            pass
    
    def _handle_snake_elimination(self, snake_id: str) -> None:
        """Handle snake elimination."""
        self.active_snakes.discard(snake_id)
        self.eliminated_snakes.add(snake_id)
        
        # Clear snake from grid
        snake = self.snakes[snake_id]
        for segment in snake.get_segments():
            self.grid.vacate(segment)
    
    def _update_food(self) -> None:
        """Spawn food items as needed."""
        # Spawn new food if below maximum
        while len(self.food_items) < self.max_food_items:
            if random.random() < self.food_spawn_rate:
                new_food = Food.spawn_food(self.grid)
                if new_food:
                    self.food_items.append(new_food)
                    self.grid.occupy(new_food.position)
    
    def _check_game_conditions(self) -> None:
        """Check if game should end based on mode-specific conditions."""
        if self.game_mode == GameMode.SURVIVAL:
            # Check if only one snake remains
            if len(self.active_snakes) <= 1:
                return  # Game over
        
        elif self.game_mode == GameMode.SCORE_RACE:
            # Check time limit
            if self.time_limit and self.game_time >= self.time_limit:
                return  # Game over
    
    def get_active_snakes(self) -> List[Snake]:
        """Get all currently active snakes."""
        return [self.snakes[snake_id] for snake_id in self.active_snakes]
    
    def get_eliminated_snakes(self) -> List[Snake]:
        """Get all eliminated snakes."""
        return [self.snakes[snake_id] for snake_id in self.eliminated_snakes]
    
    def get_leaderboard(self) -> List[Tuple[str, int]]:
        """Get current scores sorted by highest first."""
        return sorted(self.scores.items(), key=lambda x: x[1], reverse=True)
    
    def get_winner(self) -> Optional[str]:
        """Get the winner based on game mode."""
        if self.game_mode == GameMode.SURVIVAL:
            if len(self.active_snakes) == 1:
                return list(self.active_snakes)[0]
        elif self.game_mode == GameMode.SCORE_RACE:
            if self.time_limit and self.game_time >= self.time_limit:
                leaderboard = self.get_leaderboard()
                return leaderboard[0][0] if leaderboard else None
        elif self.game_mode == GameMode.FREE_FOR_ALL:
            if len(self.active_snakes) == 1:
                return list(self.active_snakes)[0]
        
        return None
    
    def is_game_over(self) -> bool:
        """Check if the game is over."""
        if self.game_mode in [GameMode.SURVIVAL, GameMode.FREE_FOR_ALL]:
            return len(self.active_snakes) <= 1
        elif self.game_mode == GameMode.SCORE_RACE:
            return self.time_limit and self.game_time >= self.time_limit
        return False
    
    def set_time_limit(self, time_limit: float) -> None:
        """Set time limit for timed game modes."""
        self.time_limit = time_limit
    
    def set_max_food(self, max_food: int) -> None:
        """Set maximum number of food items."""
        self.max_food_items = max(1, max_food)
    
    def set_food_spawn_rate(self, spawn_rate: float) -> None:
        """Set food spawn rate (0.0 to 1.0)."""
        self.food_spawn_rate = max(0.0, min(1.0, spawn_rate))
    
    def reset_game(self) -> None:
        """Reset the game to initial state."""
        # Clear all snakes and food
        self.snakes.clear()
        self.food_items.clear()
        self.collision_events.clear()
        
        # Reset state
        self.grid.clear()
        self.game_time = 0.0
        self.scores.clear()
        self.active_snakes.clear()
        self.eliminated_snakes.clear()


class MultiSnakeGameFactory:
    """Factory for creating configured multi-snake games."""
    
    @staticmethod
    def create_survival_game(grid: Grid, num_ai: int = 3, ai_difficulty: float = 0.5) -> MultiSnakeGame:
        """Create a survival mode game."""
        game = MultiSnakeGame(grid, GameMode.SURVIVAL)
        
        # Add AI snakes
        start_positions = MultiSnakeGameFactory._get_spaced_start_positions(grid, num_ai + 1)
        
        for i in range(num_ai):
            if i < len(start_positions):
                personality = random.choice(list(AIPersonality))
                game.add_ai_snake(f"ai_{i}", start_positions[i], personality, ai_difficulty)
        
        return game
    
    @staticmethod
    def create_score_race_game(grid: Grid, time_limit: float = 120.0, 
                              num_ai: int = 2, ai_difficulty: float = 0.5) -> MultiSnakeGame:
        """Create a score race mode game."""
        game = MultiSnakeGame(grid, GameMode.SCORE_RACE)
        game.set_time_limit(time_limit)
        
        # Add AI snakes
        start_positions = MultiSnakeGameFactory._get_spaced_start_positions(grid, num_ai + 1)
        
        for i in range(num_ai):
            if i < len(start_positions):
                personality = random.choice(list(AIPersonality))
                game.add_ai_snake(f"ai_{i}", start_positions[i], personality, ai_difficulty)
        
        return game
    
    @staticmethod
    def create_free_for_all_game(grid: Grid, num_ai: int = 2, ai_difficulty: float = 0.5) -> MultiSnakeGame:
        """Create a free-for-all mode game."""
        game = MultiSnakeGame(grid, GameMode.FREE_FOR_ALL)
        
        # Add AI snakes
        start_positions = MultiSnakeGameFactory._get_spaced_start_positions(grid, num_ai + 1)
        
        for i in range(num_ai):
            if i < len(start_positions):
                personality = random.choice(list(AIPersonality))
                game.add_ai_snake(f"ai_{i}", start_positions[i], personality, ai_difficulty)
        
        return game
    
    @staticmethod
    def _get_spaced_start_positions(grid: Grid, num_snakes: int) -> List[SquareCoord]:
        """Get well-spaced starting positions for snakes."""
        positions = []
        grid_width = grid.width
        grid_height = grid.height
        
        # Divide grid into regions
        cols = int((num_snakes + 1) ** 0.5)
        rows = (num_snakes + cols - 1) // cols
        
        cell_width = grid_width // cols
        cell_height = grid_height // rows
        
        for i in range(num_snakes):
            row = i // cols
            col = i % cols
            
            # Center position in each cell
            x = col * cell_width + cell_width // 2
            y = row * cell_height + cell_height // 2
            
            # Ensure position is valid
            x = max(2, min(x, grid_width - 3))
            y = max(2, min(y, grid_height - 3))
            
            positions.append(SquareCoord(x, y))
        
        return positions


# Import random for start position generation
import random