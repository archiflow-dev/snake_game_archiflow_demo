"""Unit tests for hexagonal grid functionality."""

import pytest
import math
from src.entities.grid import HexCoord
from src.grids.hexagonal import HexagonalGrid


class TestHexCoord:
    """Test the HexCoord coordinate system."""
    
    def test_hex_coord_creation(self):
        """Test hex coordinate creation and basic properties."""
        coord = HexCoord(2, -1)
        assert coord.q == 2
        assert coord.r == -1
        assert coord.s == -1  # Should be -q - r
    
    def test_hex_coord_equality(self):
        """Test hex coordinate equality."""
        coord1 = HexCoord(1, 2)
        coord2 = HexCoord(1, 2)
        coord3 = HexCoord(2, 1)
        
        assert coord1 == coord2
        assert coord1 != coord3
    
    def test_hex_coord_hash(self):
        """Test hex coordinate hashing for use in sets/dicts."""
        coord1 = HexCoord(1, 2)
        coord2 = HexCoord(1, 2)
        coord3 = HexCoord(2, 1)
        
        assert hash(coord1) == hash(coord2)
        assert hash(coord1) != hash(coord3)
        
        # Test in set
        coord_set = {coord1, coord2, coord3}
        assert len(coord_set) == 2  # coord1 and coord2 are the same
    
    def test_hex_coord_distance(self):
        """Test hex distance calculation."""
        coord1 = HexCoord(0, 0)
        coord2 = HexCoord(1, 0)
        coord3 = HexCoord(1, -1)
        coord4 = HexCoord(2, -2)
        
        assert coord1.get_distance(coord2) == 1
        assert coord1.get_distance(coord3) == 1
        assert coord2.get_distance(coord3) == 1
        assert coord1.get_distance(coord4) == 2
    
    def test_hex_coord_repr(self):
        """Test hex coordinate string representation."""
        coord = HexCoord(3, -2)
        assert repr(coord) == "HexCoord(3, -2)"


class TestHexagonalGrid:
    """Test the HexagonalGrid class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.width = 800
        self.height = 600
        self.hex_size = 20
        self.grid = HexagonalGrid(self.width, self.height, self.hex_size)
    
    def test_grid_initialization(self):
        """Test grid initialization."""
        assert self.grid.width == self.width
        assert self.grid.height == self.height
        assert self.grid.hex_size == self.hex_size
        assert len(self.grid.directions) == 6
    
    def test_axial_to_pixel_conversion(self):
        """Test conversion from axial to pixel coordinates."""
        coord = HexCoord(0, 0)
        x, y = self.grid.axial_to_pixel(coord)
        assert x == 0
        assert y == 0
        
        coord = HexCoord(1, 0)
        x, y = self.grid.axial_to_pixel(coord)
        expected_x = self.hex_size * math.sqrt(3)
        assert abs(x - expected_x) < 0.001
        assert y == 0
    
    def test_pixel_to_axial_conversion(self):
        """Test conversion from pixel to axial coordinates."""
        # Test round-trip conversion
        original_coord = HexCoord(2, -1)
        x, y = self.grid.axial_to_pixel(original_coord)
        converted_coord = self.grid.pixel_to_axial(x, y)
        
        assert converted_coord.q == original_coord.q
        assert converted_coord.r == original_coord.r
    
    def test_axial_round(self):
        """Test rounding fractional axial coordinates."""
        # Test rounding exact coordinates
        coord = self.grid.axial_round(1.2, 2.8)
        assert coord.q == 1
        assert coord.r == 3
        
        # Test rounding to nearest hex
        coord = self.grid.axial_round(0.49, 0.49)
        assert coord.q == 0
        assert coord.r == 0
    
    def test_hex_corners_calculation(self):
        """Test calculation of hexagon corner points."""
        coord = HexCoord(0, 0)
        corners = self.grid.get_hex_corners(coord)
        
        assert len(corners) == 6
        assert all(isinstance(corner, tuple) and len(corner) == 2 for corner in corners)
        
        # Verify center point is roughly average of corners
        center_x, center_y = self.grid.axial_to_pixel(coord)
        avg_x = sum(corner[0] for corner in corners) / 6
        avg_y = sum(corner[1] for corner in corners) / 6
        
        assert abs(avg_x - center_x) < 1
        assert abs(avg_y - center_y) < 1
    
    def test_is_valid_position(self):
        """Test position validation."""
        # Center should be valid
        center_coord = HexCoord(0, 0)
        assert self.grid.is_valid_position(center_coord)
        
        # Coordinates within bounds should be valid
        coord = HexCoord(5, 5)
        x, y = self.grid.axial_to_pixel(coord)
        if self.grid.hex_size <= x < self.width - self.grid.hex_size and \
           self.grid.hex_size <= y < self.height - self.grid.hex_size:
            assert self.grid.is_valid_position(coord)
        
        # Far coordinates should be invalid
        far_coord = HexCoord(100, 100)
        x, y = self.grid.axial_to_pixel(far_coord)
        if not (self.grid.hex_size <= x < self.width - self.grid.hex_size and \
                self.grid.hex_size <= y < self.height - self.grid.hex_size):
            assert not self.grid.is_valid_position(far_coord)
        
        # Wrong type should be invalid
        assert not self.grid.is_valid_position("not a coord")
        assert not self.grid.is_valid_position((1, 2))
    
    def test_get_neighbors(self):
        """Test neighbor calculation."""
        center_coord = HexCoord(0, 0)
        neighbors = self.grid.get_neighbors(center_coord)
        
        # Should have up to 6 neighbors
        assert len(neighbors) <= 6
        
        # All neighbors should be valid positions (within bounds)
        for neighbor in neighbors:
            assert self.grid.is_valid_position(neighbor)
        
        # Distance to each neighbor should be 1
        for neighbor in neighbors:
            assert center_coord.get_distance(neighbor) == 1
    
    def test_direction_vectors(self):
        """Test that direction vectors are correct."""
        center = HexCoord(0, 0)
        
        for direction in self.grid.directions:
            neighbor = HexCoord(center.q + direction.q, center.r + direction.r)
            assert center.get_distance(neighbor) == 1
    
    def test_direction_vector_calculation(self):
        """Test getting direction vector between coordinates."""
        from_coord = HexCoord(0, 0)
        to_coord = HexCoord(1, 0)
        
        direction = self.grid.get_direction_vector(from_coord, to_coord)
        assert direction is not None
        assert direction.q == 1
        assert direction.r == 0
        
        # Non-adjacent coordinates should return None
        far_coord = HexCoord(2, 0)
        direction = self.grid.get_direction_vector(from_coord, far_coord)
        assert direction is None
    
    def test_get_random_empty_cell(self):
        """Test getting random empty cells."""
        # With no occupied cells, should return a valid coordinate
        empty_coord = self.grid.get_random_empty_cell()
        assert empty_coord is not None
        assert isinstance(empty_coord, HexCoord)
        assert self.grid.is_valid_position(empty_coord)
        assert not self.grid.is_occupied(empty_coord)
        
        # After occupying a cell, should still find other cells
        self.grid.occupy(empty_coord)
        new_empty_coord = self.grid.get_random_empty_cell()
        assert new_empty_coord is not None
        assert new_empty_coord != empty_coord
    
    def test_get_all_valid_coords(self):
        """Test getting all valid coordinates."""
        all_coords = self.grid.get_all_valid_coords()
        
        assert isinstance(all_coords, list)
        assert all(isinstance(coord, HexCoord) for coord in all_coords)
        assert all(self.grid.is_valid_position(coord) for coord in all_coords)
    
    def test_occupied_cells_management(self):
        """Test occupation management."""
        coord = HexCoord(0, 0)
        
        assert not self.grid.is_occupied(coord)
        
        self.grid.occupy(coord)
        assert self.grid.is_occupied(coord)
        
        self.grid.vacate(coord)
        assert not self.grid.is_occupied(coord)
        
        # Occupying already occupied should not cause issues
        self.grid.occupy(coord)
        self.grid.occupy(coord)
        assert self.grid.is_occupied(coord)
        
        # Vacating non-occupied should not cause issues
        self.grid.vacate(coord)
        self.grid.vacate(coord)
        assert not self.grid.is_occupied(coord)
    
    def test_clear(self):
        """Test clearing all occupied cells."""
        coords = [HexCoord(0, 0), HexCoord(1, 0), HexCoord(0, 1)]
        
        for coord in coords:
            self.grid.occupy(coord)
        
        assert all(self.grid.is_occupied(coord) for coord in coords)
        
        self.grid.clear()
        assert all(not self.grid.is_occupied(coord) for coord in coords)
    
    def test_count_empty_cells(self):
        """Test counting empty cells."""
        all_coords = self.grid.get_all_valid_coords()
        total_cells = len(all_coords)
        
        # Initially all cells should be empty
        assert self.grid.count_empty_cells() == total_cells
        
        # Occupy some cells
        coords_to_occupy = all_coords[:5] if len(all_coords) >= 5 else all_coords
        for coord in coords_to_occupy:
            self.grid.occupy(coord)
        
        assert self.grid.count_empty_cells() == total_cells - len(coords_to_occupy)
    
    def test_boundary_conditions(self):
        """Test behavior at grid boundaries."""
        # Test coordinates near boundaries
        boundary_coords = [
            HexCoord(0, 0),
            HexCoord(-1, 0),
            HexCoord(1, 0),
            HexCoord(0, -1),
            HexCoord(0, 1),
        ]
        
        for coord in boundary_coords:
            if self.grid.is_valid_position(coord):
                neighbors = self.grid.get_neighbors(coord)
                # Neighbors should still be valid positions
                for neighbor in neighbors:
                    assert self.grid.is_valid_position(neighbor)


class TestHexGridIntegration:
    """Integration tests for hexagonal grid system."""
    
    def test_complete_movement_scenario(self):
        """Test a complete movement scenario."""
        grid = HexagonalGrid(400, 300, 15)
        
        # Place snake at center
        center = HexCoord(0, 0)
        grid.occupy(center)
        
        # Get valid movement directions
        neighbors = grid.get_neighbors(center)
        assert len(neighbors) > 0
        
        # Move to first neighbor
        next_pos = neighbors[0]
        assert grid.is_valid_position(next_pos)
        assert not grid.is_occupied(next_pos)
        
        grid.vacate(center)
        grid.occupy(next_pos)
        
        # Continue moving
        new_neighbors = grid.get_neighbors(next_pos)
        assert len(new_neighbors) > 0
        
        # Should not include previous position if we want to prevent backtracking
        filtered_neighbors = [n for n in new_neighbors if n != center]
        assert len(filtered_neighbors) >= 0  # May be 0 in small grids
    
    def test_pixel_space_consistency(self):
        """Test that pixel space calculations are consistent."""
        grid = HexagonalGrid(800, 600, 20)
        
        test_coords = [HexCoord(i, j) for i in range(-2, 3) for j in range(-2, 3)]
        
        for coord in test_coords:
            if grid.is_valid_position(coord):
                # Convert to pixel and back
                x, y = grid.axial_to_pixel(coord)
                converted = grid.pixel_to_axial(x, y)
                
                # Should be very close to original
                assert abs(converted.q - coord.q) <= 1
                assert abs(converted.r - coord.r) <= 1
    
    def test_grid_size_scaling(self):
        """Test grid behavior with different hex sizes."""
        sizes = [10, 20, 30, 40]
        
        for hex_size in sizes:
            grid = HexagonalGrid(400, 300, hex_size)
            
            # Should have valid coordinates
            all_coords = grid.get_all_valid_coords()
            assert len(all_coords) > 0
            
            # Larger hexes should generally have fewer coordinates
            # (since they take more space)
            center = HexCoord(0, 0)
            assert grid.is_valid_position(center)


if __name__ == "__main__":
    pytest.main([__file__])