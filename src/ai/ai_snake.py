"""AI Snake implementation with intelligent behavior."""

from typing import List, Optional, Set, Dict, Any
import time
import random
from ..entities.snake import Snake, Direction, SquareCoord
from ..entities.food import Food
from .behavior import BehaviorTree, BehaviorFactory, DecisionContext, AIPersonality
from .pathfinding import PathFinder


class AISnake(Snake):
    """AI-controlled snake with intelligent behavior."""
    
    def __init__(self, start_position: SquareCoord, start_direction: Direction = Direction.RIGHT,
                 personality: AIPersonality = AIPersonality.BALANCED,
                 difficulty: float = 0.5, snake_id: str = "ai_snake"):
        super().__init__(start_position, start_direction)
        self.personality = personality
        self.difficulty = max(0.1, min(1.0, difficulty))  # Clamp between 0.1 and 1.0
        self.snake_id = snake_id
        
        # AI-specific attributes
        self.behavior_tree = self._create_behavior_tree()
        self.pathfinder = None
        self.current_target: Optional[SquareCoord] = None
        self.current_path: List[SquareCoord] = []
        self.pathfinding_cooldown = 0.0
        self.last_update_time = time.time()
        self.decision_delay = 0.1  # Seconds between decisions
        self.mistake_chance = 1.0 - difficulty  # Higher difficulty = fewer mistakes
        
        # Decision context
        self.context = DecisionContext()
    
    def _create_behavior_tree(self) -> BehaviorTree:
        """Create behavior tree based on personality."""
        factory = BehaviorFactory()
        
        if self.personality == AIPersonality.AGGRESSIVE:
            return factory.create_aggressive_behavior()
        elif self.personality == AIPersonality.CAUTIOUS:
            return factory.create_cautious_behavior()
        elif self.personality == AIPersonality.RANDOM:
            return factory.create_random_behavior()
        else:  # BALANCED
            return factory.create_balanced_behavior()
    
    def set_pathfinder(self, pathfinder: PathFinder) -> None:
        """Set the pathfinder for this AI snake."""
        self.pathfinder = pathfinder
    
    def update_ai(self, food_positions: List[SquareCoord], other_snakes: List[Snake],
                  grid, current_time: float) -> None:
        """
        Update AI decision making.
        
        Args:
            food_positions: List of food positions
            other_snakes: List of other snakes on the grid
            grid: The game grid
            current_time: Current time for decision timing
        """
        # Rate limit AI decisions
        if current_time - self.last_update_time < self.decision_delay:
            return
        
        self.last_update_time = current_time
        
        if not self.pathfinder:
            return
        
        # Update pathfinding cooldown
        if self.pathfinding_cooldown > 0:
            self.pathfinding_cooldown -= self.decision_delay
        
        # Get current head position
        head = self.get_head()
        if not head:
            return
        
        # Update decision context
        obstacles = self._get_all_obstacles(other_snakes)
        dangers = self._get_danger_positions(obstacles)
        
        self.context.update_context(
            snake_pos=head,
            snake_dir=self.direction,
            food_pos=food_positions,
            danger_pos=dangers,
            grid=grid,
            other_snakes=other_snakes
        )
        
        # Set up move suggestions for behavior tree
        self._setup_move_suggestions(obstacles)
        
        # Execute behavior tree
        self.behavior_tree.execute(self.context.__dict__)
    
    def _get_all_obstacles(self, other_snakes: List[Snake]) -> Set[SquareCoord]:
        """Get all obstacle positions (other snakes and self)."""
        obstacles = set(self.get_segments())  # Self is obstacle
        
        for snake in other_snakes:
            if snake.snake_id != self.snake_id:  # Don't include self
                obstacles.update(snake.get_segments())
        
        return obstacles
    
    def _get_danger_positions(self, obstacles: Set[SquareCoord]) -> List[SquareCoord]:
        """Get positions that are dangerous to move near."""
        dangers = []
        
        for obstacle in obstacles:
            # Add nearby positions as dangers (avoid getting too close)
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    danger_pos = SquareCoord(obstacle.x + dx, obstacle.y + dy)
                    if danger_pos not in obstacles:
                        dangers.append(danger_pos)
        
        return dangers
    
    def _setup_move_suggestions(self, obstacles: Set[SquareCoord]) -> None:
        """Setup move suggestion functions for behavior tree."""
        head = self.get_head()
        
        def move_to_food():
            if not self.context.food_positions or not head:
                return False
            
            if self.pathfinding_cooldown > 0:
                return self._follow_current_path()
            
            # Find nearest food
            target = self.context.get_nearest_food()
            if not target:
                return False
            
            # Find path to food
            if self.pathfinder:
                path = self.pathfinder.find_path_astar(head, target, obstacles)
                if path and len(path) > 1:
                    self.current_path = path[1:]  # Exclude current position
                    self.current_target = target
                    self.pathfinding_cooldown = 0.5  # Prevent constant recalculation
                    return self._follow_current_path()
            
            return False
        
        def escape_danger():
            if not head or not self.pathfinder:
                return False
            
            # Find safest move
            safe_moves = self.pathfinder.get_safe_moves(head, obstacles)
            if not safe_moves:
                return False
            
            # Choose move that maximizes distance from dangers
            best_move = max(safe_moves, key=lambda pos: self._calculate_safety(pos, obstacles))
            return self._set_direction_to_position(best_move)
        
        def explore():
            if not head:
                return False
            
            # Random safe move
            safe_moves = []
            for direction in Direction:
                if self._is_direction_safe(direction, obstacles):
                    safe_moves.append(direction)
            
            if safe_moves:
                chosen_dir = random.choice(safe_moves)
                self.set_direction(chosen_dir)
                return True
            
            return False
        
        def random_move():
            if random.random() < self.mistake_chance:
                # Make a "mistake" - random direction
                directions = list(Direction)
                random.shuffle(directions)
                for direction in directions:
                    self.set_direction(direction)
                    return True
            return explore()
        
        def safe_explore():
            if not head or not self.pathfinder:
                return False
            
            # Find move with most future options
            safe_moves = self.pathfinder.get_safe_moves(head, obstacles)
            if not safe_moves:
                return False
            
            # Evaluate each move based on future options
            best_move = max(safe_moves, 
                          key=lambda pos: len(self.pathfinder.get_safe_moves(pos, obstacles)))
            return self._set_direction_to_position(best_move)
        
        # Set up context for behavior tree
        self.context.move_suggestions = {
            'move_to_food': move_to_food,
            'escape_danger': escape_danger,
            'explore': explore,
            'random_move': random_move,
            'safe_explore': safe_explore
        }
        
        # Set context flags
        self.context.__dict__.update({
            'food_nearby': len(self.context.food_positions) > 0,
            'food_available': len(self.context.food_positions) > 0,
            'food_safe': any(self.context.is_food_safe(food) for food in self.context.food_positions),
            'danger_ahead': self._danger_ahead(obstacles),
            'danger_nearby': len(self.context.danger_positions) > 0,
        })
    
    def _follow_current_path(self) -> bool:
        """Follow the current calculated path."""
        if not self.current_path:
            return False
        
        next_pos = self.current_path[0]
        return self._set_direction_to_position(next_pos)
    
    def _set_direction_to_position(self, target: SquareCoord) -> bool:
        """Set direction to move towards target position."""
        head = self.get_head()
        if not head:
            return False
        
        dx = target.x - head.x
        dy = target.y - head.y
        
        # Determine primary direction
        if abs(dx) > abs(dy):
            direction = Direction.RIGHT if dx > 0 else Direction.LEFT
        else:
            direction = Direction.DOWN if dy > 0 else Direction.UP
        
        return self.set_direction(direction)
    
    def _is_direction_safe(self, direction: Direction, obstacles: Set[SquareCoord]) -> bool:
        """Check if moving in a direction is safe."""
        head = self.get_head()
        if not head:
            return False
        
        dx, dy = direction.get_dx_dy()
        next_pos = SquareCoord(head.x + dx, head.y + dy)
        
        return (self.pathfinder.grid.is_valid_position(next_pos) and 
                next_pos not in obstacles)
    
    def _danger_ahead(self, obstacles: Set[SquareCoord]) -> bool:
        """Check if there's danger immediately ahead."""
        head = self.get_head()
        if not head:
            return False
        
        dx, dy = self.direction.get_dx_dy()
        next_pos = SquareCoord(head.x + dx, head.y + dy)
        
        return next_pos in obstacles
    
    def _calculate_safety(self, position: SquareCoord, obstacles: Set[SquareCoord]) -> float:
        """Calculate safety score for a position."""
        if not self.pathfinder:
            return 0.0
        
        # Safety based on distance from obstacles
        min_distance = float('inf')
        for obstacle in obstacles:
            dist = abs(position.x - obstacle.x) + abs(position.y - obstacle.y)
            min_distance = min(min_distance, dist)
        
        # Safety based on available future moves
        safe_moves = len(self.pathfinder.get_safe_moves(position, obstacles))
        
        return min_distance + (safe_moves * 0.5)
    
    def move(self) -> Optional[SquareCoord]:
        """Override move to handle AI-specific logic."""
        # Update current path if we've reached the next position
        if self.current_path and self.get_head() == self.current_path[0]:
            self.current_path.pop(0)
        
        # Clear target if reached
        if self.current_target and self.get_head() == self.current_target:
            self.current_target = None
        
        return super().move()
    
    def get_difficulty_level(self) -> str:
        """Get human-readable difficulty level."""
        if self.difficulty < 0.3:
            return "Easy"
        elif self.difficulty < 0.7:
            return "Medium"
        else:
            return "Hard"
    
    def set_difficulty(self, difficulty: float) -> None:
        """Set AI difficulty level."""
        self.difficulty = max(0.1, min(1.0, difficulty))
        self.mistake_chance = 1.0 - self.difficulty
        self.decision_delay = 0.2 - (self.difficulty * 0.15)  # Faster decisions at higher difficulty