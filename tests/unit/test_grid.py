"""Unit tests for grid functionality."""

import pytest
from src.entities.grid import SquareCoord, Grid
from src.grids.square import SquareGrid as SquareGridImpl


class TestSquareCoord:
    """Test SquareCoord functionality."""
    
    def test_coordinate_creation(self):
        """Test creating square coordinates."""
        coord = SquareCoord(5, 10)
        assert coord.x == 5
        assert coord.y == 10
    
    def test_coordinate_equality(self):
        """Test coordinate equality."""
        coord1 = SquareCoord(5, 10)
        coord2 = SquareCoord(5, 10)
        coord3 = SquareCoord(6, 10)
        
        assert coord1 == coord2
        assert coord1 != coord3
    
    def test_coordinate_hash(self):
        """Test coordinate hashing for use in sets."""
        coord1 = SquareCoord(5, 10)
        coord2 = SquareCoord(5, 10)
        coord3 = SquareCoord(6, 10)
        
        coord_set = {coord1, coord2, coord3}
        assert len(coord_set) == 2  # coord1 and coord2 are the same


class TestGrid:
    """Test Grid functionality."""
    
    def test_grid_creation(self):
        """Test creating a grid."""
        grid = Grid(20, 15)
        assert grid.width == 20
        assert grid.height == 15
        assert len(grid.get_occupied_cells()) == 0
    
    def test_valid_position(self):
        """Test position validation."""
        grid = Grid(20, 15)
        
        # Valid positions
        assert grid.is_valid_position(SquareCoord(0, 0))
        assert grid.is_valid_position(SquareCoord(19, 14))
        assert grid.is_valid_position(SquareCoord(10, 7))
        
        # Invalid positions
        assert not grid.is_valid_position(SquareCoord(-1, 0))
        assert not grid.is_valid_position(SquareCoord(20, 0))
        assert not grid.is_valid_position(SquareCoord(0, -1))
        assert not grid.is_valid_position(SquareCoord(0, 15))
    
    def test_occupancy(self):
        """Test cell occupancy management."""
        grid = Grid(20, 15)
        coord = SquareCoord(5, 5)
        
        # Initially not occupied
        assert not grid.is_occupied(coord)
        
        # Occupy the cell
        grid.occupy(coord)
        assert grid.is_occupied(coord)
        assert coord in grid.get_occupied_cells()
        
        # Vacate the cell
        grid.vacate(coord)
        assert not grid.is_occupied(coord)
        assert coord not in grid.get_occupied_cells()
    
    def test_neighbors(self):
        """Test neighbor calculation."""
        grid = Grid(20, 15)
        coord = SquareCoord(10, 7)
        
        neighbors = grid.get_neighbors(coord)
        
        # Should have 4 neighbors (up, down, left, right)
        assert len(neighbors) == 4
        
        expected = [SquareCoord(10, 6), SquareCoord(10, 8), 
                   SquareCoord(9, 7), SquareCoord(11, 7)]
        
        for neighbor in neighbors:
            assert neighbor in expected
    
    def test_edge_neighbors(self):
        """Test neighbor calculation at grid edges."""
        grid = Grid(5, 5)
        
        # Corner position
        corner = SquareCoord(0, 0)
        neighbors = grid.get_neighbors(corner)
        assert len(neighbors) == 2  # Only right and down
        
        # Edge position
        edge = SquareCoord(2, 0)
        neighbors = grid.get_neighbors(edge)
        assert len(neighbors) == 3  # Left, right, down
    
    def test_random_empty_cell(self):
        """Test getting random empty cells."""
        grid = Grid(5, 5)
        
        # Initially all cells are empty
        empty_cell = grid.get_random_empty_cell()
        assert empty_cell is not None
        assert grid.is_valid_position(empty_cell)
        assert not grid.is_occupied(empty_cell)
        
        # Occupy some cells
        grid.occupy(SquareCoord(0, 0))
        grid.occupy(SquareCoord(1, 1))
        grid.occupy(SquareCoord(2, 2))
        
        empty_cell = grid.get_random_empty_cell()
        assert empty_cell is not None
        assert not grid.is_occupied(empty_cell)
        
        # Occupy all cells
        for x in range(5):
            for y in range(5):
                grid.occupy(SquareCoord(x, y))
        
        empty_cell = grid.get_random_empty_cell()
        assert empty_cell is None
    
    def test_count_empty_cells(self):
        """Test counting empty cells."""
        grid = Grid(5, 5)
        
        # Initially all empty
        assert grid.count_empty_cells() == 25
        
        # Occupy some cells
        grid.occupy(SquareCoord(0, 0))
        grid.occupy(SquareCoord(1, 1))
        
        assert grid.count_empty_cells() == 23
        
        # Clear all
        grid.clear()
        assert grid.count_empty_cells() == 25


class TestSquareGridImpl:
    """Test SquareGrid implementation."""
    
    def test_inheritance(self):
        """Test that SquareGrid inherits from BaseGrid."""
        grid = SquareGridImpl(20, 15)
        assert hasattr(grid, 'width')
        assert hasattr(grid, 'height')
        assert hasattr(grid, 'is_valid_position')
        assert hasattr(grid, 'get_neighbors')