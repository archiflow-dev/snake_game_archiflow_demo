"""AI behavior system for snake opponents."""

from typing import List, Optional, Dict, Any, Tuple
from enum import Enum
import random


class AIPersonality(Enum):
    """AI personality types affecting decision making."""
    AGGRESSIVE = "aggressive"  # Takes risks, goes for food quickly
    CAUTIOUS = "cautious"      # Avoids danger, prioritizes safety
    BALANCED = "balanced"       # Mix of aggression and caution
    RANDOM = "random"          # Makes some random moves


class BehaviorState(Enum):
    """Current AI behavior state."""
    SEEKING_FOOD = "seeking_food"
    AVOIDING_DANGER = "avoiding_danger"
    EXPLORING = "exploring"
    TRAPPED = "trapped"


class BehaviorNode:
    """Base class for behavior tree nodes."""
    
    def __init__(self, name: str):
        self.name = name
        self.children: List['BehaviorNode'] = []
    
    def add_child(self, child: 'BehaviorNode') -> None:
        """Add a child node."""
        self.children.append(child)
    
    def execute(self, context: Dict[str, Any]) -> bool:
        """Execute the behavior node."""
        raise NotImplementedError


class SelectorNode(BehaviorNode):
    """Selector node: executes children until one succeeds."""
    
    def execute(self, context: Dict[str, Any]) -> bool:
        """Execute children in order until one returns True."""
        for child in self.children:
            if child.execute(context):
                return True
        return False


class SequenceNode(BehaviorNode):
    """Sequence node: executes all children if all succeed."""
    
    def execute(self, context: Dict[str, Any]) -> bool:
        """Execute all children in order, stop if one fails."""
        for child in self.children:
            if not child.execute(context):
                return False
        return True


class ConditionNode(BehaviorNode):
    """Condition node: evaluates a condition."""
    
    def __init__(self, name: str, condition_func):
        super().__init__(name)
        self.condition_func = condition_func
    
    def execute(self, context: Dict[str, Any]) -> bool:
        """Evaluate the condition."""
        return self.condition_func(context)


class ActionNode(BehaviorNode):
    """Action node: performs an action."""
    
    def __init__(self, name: str, action_func):
        super().__init__(name)
        self.action_func = action_func
    
    def execute(self, context: Dict[str, Any]) -> bool:
        """Execute the action."""
        return self.action_func(context)


class BehaviorTree:
    """Behavior tree for AI decision making."""
    
    def __init__(self, root: BehaviorNode):
        self.root = root
        self.current_state = BehaviorState.EXPLORING
        self.personality = AIPersonality.BALANCED
    
    def set_personality(self, personality: AIPersonality) -> None:
        """Set the AI personality."""
        self.personality = personality
    
    def execute(self, context: Dict[str, Any]) -> bool:
        """Execute the behavior tree."""
        return self.root.execute(context)
    
    def get_current_state(self) -> BehaviorState:
        """Get the current behavior state."""
        return self.current_state
    
    def set_state(self, state: BehaviorState) -> None:
        """Set the current behavior state."""
        self.current_state = state


class BehaviorFactory:
    """Factory for creating behavior trees based on personality."""
    
    @staticmethod
    def create_aggressive_behavior() -> BehaviorTree:
        """Create behavior tree for aggressive AI."""
        root = SelectorNode("Aggressive Root")
        
        # Priority 1: Get food if nearby
        seek_food = SequenceNode("Seek Food")
        seek_food.add_child(ConditionNode("Food Nearby", lambda ctx: ctx.get("food_nearby", False)))
        seek_food.add_child(ActionNode("Move to Food", lambda ctx: ctx.get("move_to_food", lambda: False)()))
        
        # Priority 2: Avoid immediate danger
        avoid_danger = SequenceNode("Avoid Danger")
        avoid_danger.add_child(ConditionNode("Danger Ahead", lambda ctx: ctx.get("danger_ahead", False)))
        avoid_danger.add_child(ActionNode("Escape Danger", lambda ctx: ctx.get("escape_danger", lambda: False)()))
        
        # Priority 3: Explore randomly
        explore = ActionNode("Explore", lambda ctx: ctx.get("explore", lambda: False)())
        
        root.add_child(seek_food)
        root.add_child(avoid_danger)
        root.add_child(explore)
        
        tree = BehaviorTree(root)
        tree.set_personality(AIPersonality.AGGRESSIVE)
        return tree
    
    @staticmethod
    def create_cautious_behavior() -> BehaviorTree:
        """Create behavior tree for cautious AI."""
        root = SelectorNode("Cautious Root")
        
        # Priority 1: Avoid danger at all costs
        avoid_danger = SequenceNode("Avoid Danger")
        avoid_danger.add_child(ConditionNode("Any Danger", lambda ctx: ctx.get("danger_nearby", False)))
        avoid_danger.add_child(ActionNode("Escape Danger", lambda ctx: ctx.get("escape_danger", lambda: False)()))
        
        # Priority 2: Get food if safe
        seek_food = SequenceNode("Seek Food Safe")
        seek_food.add_child(ConditionNode("Food Safe", lambda ctx: ctx.get("food_safe", False)))
        seek_food.add_child(ActionNode("Move to Food", lambda ctx: ctx.get("move_to_food", lambda: False)()))
        
        # Priority 3: Stay safe and explore
        explore = ActionNode("Cautious Explore", lambda ctx: ctx.get("safe_explore", lambda: False)())
        
        root.add_child(avoid_danger)
        root.add_child(seek_food)
        root.add_child(explore)
        
        tree = BehaviorTree(root)
        tree.set_personality(AIPersonality.CAUTIOUS)
        return tree
    
    @staticmethod
    def create_balanced_behavior() -> BehaviorTree:
        """Create behavior tree for balanced AI."""
        root = SelectorNode("Balanced Root")
        
        # Equal priority for food seeking and danger avoidance
        seek_food = SequenceNode("Seek Food")
        seek_food.add_child(ConditionNode("Food Available", lambda ctx: ctx.get("food_available", False)))
        seek_food.add_child(ActionNode("Move to Food", lambda ctx: ctx.get("move_to_food", lambda: False)()))
        
        avoid_danger = SequenceNode("Avoid Danger")
        avoid_danger.add_child(ConditionNode("Danger Ahead", lambda ctx: ctx.get("danger_ahead", False)))
        avoid_danger.add_child(ActionNode("Escape Danger", lambda ctx: ctx.get("escape_danger", lambda: False)()))
        
        explore = ActionNode("Explore", lambda ctx: ctx.get("explore", lambda: False)())
        
        root.add_child(seek_food)
        root.add_child(avoid_danger)
        root.add_child(explore)
        
        tree = BehaviorTree(root)
        tree.set_personality(AIPersonality.BALANCED)
        return tree
    
    @staticmethod
    def create_random_behavior() -> BehaviorTree:
        """Create behavior tree for random AI."""
        root = SelectorNode("Random Root")
        
        # Random priorities
        behaviors = [
            ActionNode("Random Move", lambda ctx: ctx.get("random_move", lambda: False)()),
            ActionNode("Explore", lambda ctx: ctx.get("explore", lambda: False)()),
        ]
        
        # Shuffle for randomness
        random.shuffle(behaviors)
        
        for behavior in behaviors:
            root.add_child(behavior)
        
        tree = BehaviorTree(root)
        tree.set_personality(AIPersonality.RANDOM)
        return tree


class DecisionContext:
    """Context for AI decision making."""
    
    def __init__(self):
        self.food_positions: List = []
        self.danger_positions: List = []
        self.snake_position = None
        self.snake_direction = None
        self.grid = None
        self.other_snakes: List = []
        self.move_suggestions: Dict[str, callable] = {}
    
    def update_context(self, snake_pos, snake_dir, food_pos, danger_pos, grid, other_snakes):
        """Update the decision context."""
        self.snake_position = snake_pos
        self.snake_direction = snake_dir
        self.food_positions = food_pos
        self.danger_positions = danger_pos
        self.grid = grid
        self.other_snakes = other_snakes
    
    def get_nearest_food(self) -> Optional:
        """Get the nearest food position."""
        if not self.food_positions or not self.snake_position:
            return None
        
        # Simple distance calculation - would use grid-specific distance
        min_dist = float('inf')
        nearest = None
        
        for food in self.food_positions:
            dist = abs(food.x - self.snake_position.x) + abs(food.y - self.snake_position.y)
            if dist < min_dist:
                min_dist = dist
                nearest = food
        
        return nearest
    
    def is_food_safe(self, food_pos) -> bool:
        """Check if food position is safe to approach."""
        # Simple safety check - no immediate dangers nearby
        if not self.grid:
            return True
        
        # Check area around food for dangers
        for danger in self.danger_positions:
            if abs(danger.x - food_pos.x) <= 2 and abs(danger.y - food_pos.y) <= 2:
                return False
        
        return True