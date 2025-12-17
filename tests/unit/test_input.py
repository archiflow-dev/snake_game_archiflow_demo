"""Unit tests for input functionality."""

import pytest
import pygame
from src.systems.input import InputManager


class TestInputManager:
    """Test InputManager functionality."""
    
    def test_input_manager_creation(self):
        """Test creating an input manager."""
        input_manager = InputManager()
        
        assert len(input_manager._key_mappings) > 0
        assert 'move_up' in input_manager._key_mappings.values()
        assert 'move_down' in input_manager._key_mappings.values()
        assert 'move_left' in input_manager._key_mappings.values()
        assert 'move_right' in input_manager._key_mappings.values()
    
    def test_key_mapping(self):
        """Test key mapping functionality."""
        input_manager = InputManager()
        
        # Test default mappings
        assert input_manager.get_action_from_key(pygame.K_w) == 'move_up'
        assert input_manager.get_action_from_key(pygame.K_s) == 'move_down'
        assert input_manager.get_action_from_key(pygame.K_a) == 'move_left'
        assert input_manager.get_action_from_key(pygame.K_d) == 'move_right'
        
        # Test custom mapping
        input_manager.set_key_mapping(pygame.K_UP, 'move_up')
        assert input_manager.get_action_from_key(pygame.K_UP) == 'move_up'
    
    def test_action_handler_registration(self):
        """Test registering action handlers."""
        input_manager = InputManager()
        
        handler_called = False
        
        def test_handler():
            nonlocal handler_called
            handler_called = True
        
        input_manager.register_action_handler('move_up', test_handler)
        assert 'move_up' in input_manager._action_handlers
    
    def test_event_handling_key_down(self):
        """Test handling key down events."""
        input_manager = InputManager()
        
        handler_called = False
        
        def test_handler():
            nonlocal handler_called
            handler_called = True
        
        input_manager.register_action_handler('pause', test_handler)
        
        # Simulate ESC key press
        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_ESCAPE})
        input_manager.handle_event(event)
        
        assert handler_called
        assert pygame.K_ESCAPE in input_manager._active_keys
        assert input_manager.get_buffered_action() is None  # pause is not a movement action
    
    def test_movement_action_buffering(self):
        """Test movement action buffering."""
        input_manager = InputManager()
        
        # Simulate movement key presses
        events = [
            pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_w}),
            pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_d}),
            pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_s})
        ]
        
        for event in events:
            input_manager.handle_event(event)
        
        # Should get the latest movement action
        assert input_manager.get_movement_direction() == 'move_down'
        
        # Buffer should be empty of movement actions
        assert input_manager.get_movement_direction() is None
    
    def test_key_up_handling(self):
        """Test key up event handling."""
        input_manager = InputManager()
        
        # Press key
        event_down = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_w})
        input_manager.handle_event(event_down)
        assert input_manager.is_key_pressed(pygame.K_w)
        
        # Release key
        event_up = pygame.event.Event(pygame.KEYUP, {'key': pygame.K_w})
        input_manager.handle_event(event_up)
        assert not input_manager.is_key_pressed(pygame.K_w)
    
    def test_clear_buffer(self):
        """Test clearing the input buffer."""
        input_manager = InputManager()
        
        # Add some movement actions
        events = [
            pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_w}),
            pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_d}),
        ]
        
        for event in events:
            input_manager.handle_event(event)
        
        assert input_manager.get_buffered_action() is not None
        
        # Clear buffer
        input_manager.clear_buffer()
        assert input_manager.get_buffered_action() is None
    
    def test_get_buffered_action(self):
        """Test getting buffered actions FIFO."""
        input_manager = InputManager()
        
        # Add actions in order
        actions = ['move_up', 'move_right', 'move_down']
        for action in actions:
            # Simulate key press
            key = None
            if action == 'move_up':
                key = pygame.K_w
            elif action == 'move_right':
                key = pygame.K_d
            elif action == 'move_down':
                key = pygame.K_s
            
            if key:
                event = pygame.event.Event(pygame.KEYDOWN, {'key': key})
                input_manager.handle_event(event)
        
        # Get actions in FIFO order
        retrieved_actions = []
        action = input_manager.get_buffered_action()
        while action is not None:
            retrieved_actions.append(action)
            action = input_manager.get_buffered_action()
        
        assert retrieved_actions == actions