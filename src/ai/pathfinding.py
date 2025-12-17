"""Pathfinding algorithms for AI snake navigation."""

from typing import List, Optional, Set, Tuple, Dict
import heapq
from ..entities.grid import SquareCoord, HexCoord


class PathNode:
    """Node for pathfinding algorithms."""
    
    def __init__(self, position, g_cost: float = 0, h_cost: float = 0, parent=None):
        self.position = position
        self.g_cost = g_cost  # Cost from start
        self.h_cost = h_cost  # Heuristic cost to goal
        self.f_cost = g_cost + h_cost  # Total cost
        self.parent = parent
    
    def __lt__(self, other):
        return self.f_cost < other.f_cost
    
    def __eq__(self, other):
        return self.position == other.position
    
    def __hash__(self):
        return hash(self.position)


class PathFinder:
    """Pathfinding system for AI snake navigation."""
    
    def __init__(self, grid):
        self.grid = grid
    
    def find_path_astar(self, start: SquareCoord, goal: SquareCoord, 
                       obstacles: Set[SquareCoord] = None) -> Optional[List[SquareCoord]]:
        """
        Find path using A* algorithm.
        
        Args:
            start: Starting position
            goal: Goal position  
            obstacles: Set of positions to avoid
            
        Returns:
            List of coordinates from start to goal, or None if no path
        """
        if obstacles is None:
            obstacles = set()
        
        # Check if start or goal are invalid
        if not self.grid.is_valid_position(start) or not self.grid.is_valid_position(goal):
            return None
        
        if start in obstacles or goal in obstacles:
            return None
        
        # Priority queue for open nodes
        open_set = []
        closed_set = set()
        
        # Create start node
        start_node = PathNode(start, 0, self._heuristic(start, goal))
        heapq.heappush(open_set, start_node)
        
        # Track nodes for quick lookup
        all_nodes = {start: start_node}
        
        while open_set:
            current = heapq.heappop(open_set)
            
            # Check if we reached the goal
            if current.position == goal:
                return self._reconstruct_path(current)
            
            closed_set.add(current.position)
            
            # Explore neighbors
            neighbors = self.grid.get_neighbors(current.position)
            
            for neighbor in neighbors:
                if neighbor in closed_set or neighbor in obstacles:
                    continue
                
                g_cost = current.g_cost + 1
                h_cost = self._heuristic(neighbor, goal)
                
                if neighbor not in all_nodes:
                    neighbor_node = PathNode(neighbor, g_cost, h_cost, current)
                    all_nodes[neighbor] = neighbor_node
                    heapq.heappush(open_set, neighbor_node)
                else:
                    neighbor_node = all_nodes[neighbor]
                    if g_cost < neighbor_node.g_cost:
                        neighbor_node.g_cost = g_cost
                        neighbor_node.f_cost = g_cost + h_cost
                        neighbor_node.parent = current
                        heapq.heappush(open_set, neighbor_node)
        
        # No path found
        return None
    
    def find_path_greedy(self, start: SquareCoord, goal: SquareCoord,
                        obstacles: Set[SquareCoord] = None) -> Optional[List[SquareCoord]]:
        """
        Find path using greedy best-first search (faster but less optimal).
        
        Args:
            start: Starting position
            goal: Goal position
            obstacles: Set of positions to avoid
            
        Returns:
            List of coordinates from start to goal, or None if no path
        """
        if obstacles is None:
            obstacles = set()
        
        if not self.grid.is_valid_position(start) or not self.grid.is_valid_position(goal):
            return None
        
        if start in obstacles or goal in obstacles:
            return None
        
        current = start
        path = [current]
        visited = {current}
        max_iterations = 100  # Prevent infinite loops
        iterations = 0
        
        while current != goal and iterations < max_iterations:
            iterations += 1
            
            # Get all valid neighbors
            neighbors = self.grid.get_neighbors(current)
            
            # Filter out obstacles and visited nodes
            valid_neighbors = [
                n for n in neighbors 
                if n not in obstacles and n not in visited
            ]
            
            if not valid_neighbors:
                return None  # No valid moves
            
            # Choose neighbor closest to goal
            best_neighbor = min(valid_neighbors, 
                              key=lambda n: self._heuristic(n, goal))
            
            current = best_neighbor
            path.append(current)
            visited.add(current)
        
        return path if current == goal else None
    
    def get_safe_moves(self, position: SquareCoord, obstacles: Set[SquareCoord] = None) -> List[SquareCoord]:
        """
        Get all safe moves from a position.
        
        Args:
            position: Current position
            obstacles: Set of positions to avoid
            
        Returns:
            List of safe neighboring positions
        """
        if obstacles is None:
            obstacles = set()
        
        neighbors = self.grid.get_neighbors(position)
        safe_moves = []
        
        for neighbor in neighbors:
            if (self.grid.is_valid_position(neighbor) and 
                neighbor not in obstacles):
                safe_moves.append(neighbor)
        
        return safe_moves
    
    def get_dead_end_ahead(self, position: SquareCoord, obstacles: Set[SquareCoord] = None,
                          look_ahead: int = 3) -> bool:
        """
        Check if there's a dead end ahead.
        
        Args:
            position: Current position
            obstacles: Set of positions to avoid
            look_ahead: How many moves to look ahead
            
        Returns:
            True if dead end detected
        """
        if obstacles is None:
            obstacles = set()
        
        safe_moves = self.get_safe_moves(position, obstacles)
        
        # If only one move available, check if it leads to a dead end
        if len(safe_moves) == 1:
            next_pos = safe_moves[0]
            next_safe = self.get_safe_moves(next_pos, obstacles | {position})
            
            if len(next_safe) == 0:
                return True
        
        return False
    
    def _heuristic(self, pos1: SquareCoord, pos2: SquareCoord) -> float:
        """
        Calculate heuristic distance between two positions.
        Uses Manhattan distance for square grids.
        """
        return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)
    
    def _reconstruct_path(self, node: PathNode) -> List[SquareCoord]:
        """Reconstruct path from start to goal."""
        path = []
        current = node
        
        while current:
            path.append(current.position)
            current = current.parent
        
        return list(reversed(path))


class HexPathFinder(PathFinder):
    """Pathfinding for hexagonal grids."""
    
    def __init__(self, hex_grid):
        self.hex_grid = hex_grid
    
    def get_hex_neighbors(self, position: HexCoord) -> List[HexCoord]:
        """Get all valid hex neighbors."""
        # Hex directions in axial coordinates
        directions = [
            HexCoord(1, 0),   # East
            HexCoord(1, -1),  # Southeast
            HexCoord(0, -1),  # Southwest
            HexCoord(-1, 0),  # West
            HexCoord(-1, 1),  # Northwest
            HexCoord(0, 1),   # Northeast
        ]
        
        neighbors = []
        for direction in directions:
            neighbor = HexCoord(position.q + direction.q, position.r + direction.r)
            if self._is_valid_hex(neighbor):
                neighbors.append(neighbor)
        
        return neighbors
    
    def _is_valid_hex(self, position: HexCoord) -> bool:
        """Check if hex position is valid within grid bounds."""
        # This would need to be implemented based on hex grid dimensions
        # For now, assume all hex positions are valid
        return True
    
    def _heuristic(self, pos1: HexCoord, pos2: HexCoord) -> float:
        """Calculate hex distance using axial coordinates."""
        return pos1.get_distance(pos2)
    
    def find_path_astar(self, start: HexCoord, goal: HexCoord,
                       obstacles: Set[HexCoord] = None) -> Optional[List[HexCoord]]:
        """A* pathfinding for hex grids."""
        if obstacles is None:
            obstacles = set()
        
        if not self._is_valid_hex(start) or not self._is_valid_hex(goal):
            return None
        
        if start in obstacles or goal in obstacles:
            return None
        
        open_set = []
        closed_set = set()
        
        start_node = PathNode(start, 0, self._heuristic(start, goal))
        heapq.heappush(open_set, start_node)
        
        all_nodes = {start: start_node}
        
        while open_set:
            current = heapq.heappop(open_set)
            
            if current.position == goal:
                return self._reconstruct_path(current)
            
            closed_set.add(current.position)
            
            neighbors = self.get_hex_neighbors(current.position)
            
            for neighbor in neighbors:
                if neighbor in closed_set or neighbor in obstacles:
                    continue
                
                g_cost = current.g_cost + 1
                h_cost = self._heuristic(neighbor, goal)
                
                if neighbor not in all_nodes:
                    neighbor_node = PathNode(neighbor, g_cost, h_cost, current)
                    all_nodes[neighbor] = neighbor_node
                    heapq.heappush(open_set, neighbor_node)
                else:
                    neighbor_node = all_nodes[neighbor]
                    if g_cost < neighbor_node.g_cost:
                        neighbor_node.g_cost = g_cost
                        neighbor_node.f_cost = g_cost + h_cost
                        neighbor_node.parent = current
                        heapq.heappush(open_set, neighbor_node)
        
        return None