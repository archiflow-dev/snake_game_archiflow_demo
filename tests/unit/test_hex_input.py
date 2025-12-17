"""Unit tests for hexagonal input system."""

import pytest
from src.systems.hex_input import HexInputManager
from src.entities.grid import HexCoord


class TestHexInputManager:
    """Test the HexInputManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.input_manager = HexInputManager()
    
    def test_initialization(self):
        """Test input manager initialization."""
        assert len(self.input_manager._key_mappings) > 0
        assert len(self.input_manager._hex_directions) == 6
        assert len(self.input_manager._opposite_directions) == 8
    
    def test_hex_direction_mappings(self):
        """Test that all hex directions are properly mapped."""
        expected_directions = [
            'move_north', 'move_northeast', 'move_southeast', 
            'move_south', 'move_southwest', 'move_northwest',
            'move_west', 'move_east'
        ]
        
        for direction in expected_directions:
            assert direction in self.input_manager._hex_directions
            assert isinstance(self.input_manager._hex_directions[direction], HexCoord)
    
    def test_wasd_mappings(self):
        """Test WASD key mappings."""
        assert self.input_manager._key_mappings[pygame.K_w] == 'move_northwest'
        assert self.input_manager._key_mappings[pygame.K_a] == 'move_west'
        assert self.input_manager._key_mappings[pygame.K_s] == 'move_southwest'
        assert self.input_manager._key_mappings[pygame.K_d] == 'move_southeast'
    
    def test_qe_mappings(self):
        """Test Q and E key mappings for diagonal directions."""
        assert self.input_manager._key_mappings[pygame.K_q] == 'move_northeast'
        assert self.input_manager._key_mappings[pygame.K_e] == 'move_south'
    
    def test_get_hex_direction_vector(self):
        """Test getting direction vectors."""
        north_vector = self.input_manager.get_hex_direction_vector('move_north')
        assert north_vector is not None
        assert north_vector.q == 0
        assert north_vector.r == -1
        
        northeast_vector = self.input_manager.get_hex_direction_vector('move_northeast')
        assert northeast_vector is not None
        assert northeast_vector.q == 1
        assert northeast_vector.r == -1
        
        invalid_vector = self.input_manager.get_hex_direction_vector('invalid_move')
        assert invalid_vector is None
    
    def test_opposite_directions(self):
        """Test opposite direction detection."""
        assert self.input_manager.is_opposite_direction('move_north', 'move_south')
        assert self.input_manager.is_opposite_direction('move_northeast', 'move_southwest')
        assert self.input_manager.is_opposite_direction('move_southeast', 'move_northwest')
        assert self.input_manager.is_opposite_direction('move_west', 'move_east')
        
        # Non-opposite directions
        assert not self.input_manager.is_opposite_direction('move_north', 'move_northeast')
        assert not self.input_manager.is_opposite_direction('move_west', 'move_north')
    
    def test_movement_validation_no_current_direction(self):
        """Test movement validation when no current direction is set."""
        # Simulate pressing 'W' key
        self.input_manager._handle_key_down(pygame.K_w)
        
        direction = self.input_manager.get_validated_movement()
        assert direction is not None
        assert isinstance(direction, HexCoord)
    
    def test_movement_validation_with_opposite_direction(self):
        """Test that opposite directions are filtered out."""
        # Simulate current direction being north
        current_direction = 'move_north'
        
        # Add movement to buffer
        self.input_manager._input_buffer.put('move_south')  # Opposite
        self.input_manager._input_buffer.put('move_northeast')  # Valid
        
        direction = self.input_manager.get_validated_movement(current_direction)
        
        # Should return the valid direction, not the opposite one
        assert direction is not None
        valid_dir = self.input_manager.get_hex_direction_vector('move_northeast')
        assert direction.q == valid_dir.q
        assert direction.r == valid_dir.r
    
    def test_movement_validation_all_opposite(self):
        """Test when all buffered movements are opposite."""
        current_direction = 'move_north'
        
        # Add only opposite directions
        self.input_manager._input_buffer.put('move_south')
        self.input_manager._input_buffer.put('move_south')
        
        direction = self.input_manager.get_validated_movement(current_direction)
        assert direction is None
    
    def test_get_direction_name(self):
        """Test getting direction name from coordinate."""
        coord = HexCoord(0, -1)  # North
        name = self.input_manager.get_direction_name(coord)
        assert name == 'move_north'
        
        coord = HexCoord(1, -1)  # Northeast
        name = self.input_manager.get_direction_name(coord)
        assert name == 'move_northeast'
        
        coord = HexCoord(5, 5)  # Invalid direction
        name = self.input_manager.get_direction_name(coord)
        assert name is None
    
    def test_get_all_direction_names(self):
        """Test getting all available direction names."""
        names = self.input_manager.get_all_direction_names()
        
        expected = [
            'move_north', 'move_northeast', 'move_southeast', 
            'move_south', 'move_southwest', 'move_northwest',
            'move_west', 'move_east'
        ]
        
        for name in expected:
            assert name in names
    
    def test_set_hex_key_mapping(self):
        """Test setting custom hexagonal key mappings."""
        # Valid mapping
        success = self.input_manager.set_hex_key_mapping(pygame.K_z, 'north')
        assert success
        assert self.input_manager._key_mappings[pygame.K_z] == 'move_north'
        
        # Invalid mapping
        success = self.input_manager.set_hex_key_mapping(pygame.K_x, 'invalid_dir')
        assert not success
        assert pygame.K_x not in self.input_manager._key_mappings
    
    def test_key_press_tracking(self):
        """Test tracking of currently pressed keys."""
        assert not self.input_manager.is_key_pressed(pygame.K_w)
        
        self.input_manager._handle_key_down(pygame.K_w)
        assert self.input_manager.is_key_pressed(pygame.K_w)
        
        self.input_manager._handle_key_up(pygame.K_w)
        assert not self.input_manager.is_key_pressed(pygame.K_w)
    
    def test_movement_key_pressed_detection(self):
        """Test detection of any movement key being pressed."""
        assert not self.input_manager.is_movement_key_pressed()
        
        self.input_manager._handle_key_down(pygame.K_w)
        assert self.input_manager.is_movement_key_pressed()
        
        self.input_manager._handle_key_up(pygame.K_w)
        assert not self.input_manager.is_movement_key_pressed()
        
        # Test with control key
        self.input_manager._handle_key_down(pygame.K_ESCAPE)
        assert not self.input_manager.is_movement_key_pressed()
    
    def test_active_movement_directions(self):
        """Test getting all currently active movement directions."""
        assert len(self.input_manager.get_active_movement_directions()) == 0
        
        self.input_manager._handle_key_down(pygame.K_w)
        self.input_manager._handle_key_down(pygame.K_q)
        
        active = self.input_manager.get_active_movement_directions()
        assert len(active) == 2
        assert 'move_northwest' in active
        assert 'move_northeast' in active
        
        self.input_manager._handle_key_up(pygame.K_w)
        active = self.input_manager.get_active_movement_directions()
        assert len(active) == 1
        assert 'move_northeast' in active
    
    def test_buffer_management(self):
        """Test input buffer management."""
        # Add some actions
        self.input_manager._input_buffer.put('move_north')
        self.input_manager._input_buffer.put('pause')
        self.input_manager._input_buffer.put('move_southeast')
        
        # Get movement direction should return latest movement
        direction = self.input_manager.get_movement_direction()
        assert direction == 'move_southeast'
        
        # Buffer should have preserved non-movement action
        action = self.input_manager.get_buffered_action()
        assert action == 'pause'
        
        # Clear buffer
        self.input_manager.clear_buffer()
        assert self.input_manager.get_buffered_action() is None
    
    def test_complex_movement_sequence(self):
        """Test a complex sequence of movement inputs."""
        current_direction = None
        
        # Press W (northwest)
        self.input_manager._handle_key_down(pygame.K_w)
        direction = self.input_manager.get_validated_movement(current_direction)
        assert direction is not None
        
        # Update current direction
        current_direction = 'move_northwest'
        
        # Try opposite direction (southeast) - should be blocked
        self.input_manager._handle_key_down(pygame.K_d)
        direction = self.input_manager.get_validated_movement(current_direction)
        assert direction is None
        
        # Try valid direction (north)
        self.input_manager._handle_key_down(pygame.K_q)  # northeast
        direction = self.input_manager.get_validated_movement(current_direction)
        assert direction is not None
        north_coord = HexCoord(0, -1)
        assert direction.q == north_coord.q
        assert direction.r == north_coord.r
    
    def test_arrow_key_mappings(self):
        """Test arrow key alternative mappings."""
        assert self.input_manager._key_mappings[pygame.K_UP] == 'move_northwest'
        assert self.input_manager._key_mappings[pygame.K_DOWN] == 'move_southeast'
        assert self.input_manager._key_mappings[pygame.K_LEFT] == 'move_west'
        
        # Test that they work with validation
        self.input_manager._handle_key_down(pygame.K_UP)
        direction = self.input_manager.get_validated_movement()
        assert direction is not None
        assert direction.q == -1 and direction.r == 0  # northwest vector


if __name__ == "__main__":
    pytest.main([__file__])