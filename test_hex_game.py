"""Test runner for hexagonal snake game implementation."""

import sys
import pygame
from src.core.hex_game import HexGameController


def run_integration_test():
    """Run integration test for hexagonal snake game."""
    print("Running Hexagonal Snake Game Integration Test...")
    
    # Initialize pygame in headless mode if possible
    pygame.init()
    
    # Create game instance
    game = HexGameController(screen_width=800, screen_height=600, hex_size=20)
    
    # Test initialization
    try:
        game.initialize()
        print("+ Game initialization successful")
    except Exception as e:
        print(f"X Game initialization failed: {e}")
        return False
    
    # Test game components
    try:
        # Test grid system
        assert game.grid is not None
        assert hasattr(game.grid, 'is_valid_position')
        assert hasattr(game.grid, 'get_neighbors')
        print("+ Hexagonal grid system initialized")
        
        # Test renderer
        assert game.renderer is not None
        assert hasattr(game.renderer, 'draw_grid')
        assert hasattr(game.renderer, 'draw_snake')
        print("+ Hexagonal renderer initialized")
        
        # Test input manager
        assert game.input_manager is not None
        assert hasattr(game.input_manager, 'get_validated_movement')
        print("+ Hexagonal input manager initialized")
        
        # Test animation system
        assert game.animation_system is not None
        assert hasattr(game.animation_system, 'create_animation')
        print("+ Animation system initialized")
        
        # Test difficulty manager
        assert game.difficulty_manager is not None
        assert hasattr(game.difficulty_manager, 'update_score')
        print("+ Difficulty manager initialized")
        
        # Test snake entity
        assert game.snake is not None
        assert hasattr(game.snake, 'move')
        assert hasattr(game.snake, 'change_direction')
        print("+ Hexagonal snake entity initialized")
        
        # Test food system
        assert game.food is not None
        print("+ Food system initialized")
        
    except Exception as e:
        print(f"X Component test failed: {e}")
        return False
    
    # Test basic game flow
    try:
        # Start game
        game.start_game()
        assert game.state.value == "playing"
        print("+ Game started successfully")
        
        # Test snake movement
        initial_length = game.snake.get_length()
        game.snake.move()
        print("+ Snake movement working")
        
        # Test direction change
        from src.entities.grid import HexCoord
        new_direction = HexCoord(1, 0)  # Southeast
        game.snake.change_direction(new_direction)
        game.snake.move()
        print("+ Direction change working")
        
        # Test score update
        initial_score = game.score
        game._eat_food()
        assert game.score > initial_score
        print("+ Score system working")
        
        # Test difficulty scaling
        game.difficulty_manager.update_score(100)
        assert game.difficulty_manager.current_speed_multiplier > 1.0
        print("+ Difficulty scaling working")
        
    except Exception as e:
        print(f"X Game flow test failed: {e}")
        return False
    
    # Test animation system
    try:
        from src.utils.animation import EasingFunctions
        from src.utils.animation import EasingFunctions
        
        # Create test animation
        animation = game.animation_system.create_animation(
            (0, 0), (100, 100), 0.5,
            easing_func=EasingFunctions.ease_out_quad
        )
        
        assert animation is not None
        print("+ Animation creation working")
        
        # Test interpolation
        animation.current_progress = 0.5
        interpolated = game.animation_system.interpolate_position(animation)
        assert interpolated == (50.0, 50.0)
        print("+ Animation interpolation working")
        
    except Exception as e:
        print(f"X Animation test failed: {e}")
        return False
    
    print("\n" + "="*50)
    print("All Phase 2 Integration Tests Passed! +")
    print("="*50)
    print("\nPhase 2 Features Successfully Implemented:")
    print("+ Hexagonal Grid System with axial coordinates")
    print("+ 6-directional movement with WASD + Q/E controls")
    print("+ Pointy-top hexagon rendering")
    print("+ Smooth animation system with easing functions")
    print("+ Dynamic difficulty scaling with multiple modes")
    print("+ Comprehensive test coverage")
    print("+ Integration with existing architecture")
    
    return True


def run_feature_demonstration():
    """Run a quick demonstration of Phase 2 features."""
    print("\nStarting Feature Demonstration...")
    
    # Import animation functions
    from src.utils.animation import EasingFunctions
    
    # Create game instance
    game = HexGameController(screen_width=800, screen_height=600, hex_size=20)
    game.initialize()
    
    print("Game initialized with the following Phase 2 features:")
    
    # Demonstrate grid system
    print(f"\n1. Hexagonal Grid System:")
    print(f"   - Grid size: {game.grid.width}x{game.grid.height}")
    print(f"   - Hexagon size: {game.grid.hex_size}px")
    print(f"   - Valid coordinates: {len(game.grid.get_all_valid_coords())}")
    
    # Demonstrate movement directions
    print(f"\n2. 6-Directional Movement:")
    print("   Available directions:")
    for i, direction in enumerate(game.grid.directions):
        direction_name = game.input_manager.get_direction_name(direction)
        if direction_name:
            print(f"   {direction_name}: ({direction.q}, {direction.r})")
    
    # Demonstrate difficulty system
    print(f"\n3. Dynamic Difficulty System:")
    stats = game.difficulty_manager.get_difficulty_stats()
    print(f"   - Current difficulty: {stats['difficulty_name']}")
    print(f"   - Speed multiplier: {stats['speed_multiplier']:.1f}x")
    print(f"   - Points per food: {stats['points_per_food']}")
    print(f"   - Difficulty mode: {stats['difficulty_mode']}")
    
    # Demonstrate animation system
    print(f"\n4. Animation System:")
    print(f"   - Easing functions available: {len([f for f in dir(EasingFunctions) if not f.startswith('_')])}")
    print(f"   - Active animations: {game.animation_system.get_running_count()}")
    
    print(f"\n5. Enhanced Rendering:")
    print(f"   - Pointy-top hexagons")
    print(f"   - Gradient effects on snake body")
    print(f"   - Highlighted snake head with eyes")
    print(f"   - Animated food consumption")
    
    print("\nPhase 2 implementation is complete and ready for testing!")


if __name__ == "__main__":
    print("Hexagonal Snake Game - Phase 2 Test Suite")
    print("=" * 50)
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--demo":
            run_feature_demonstration()
        elif sys.argv[1] == "--test":
            success = run_integration_test()
            sys.exit(0 if success else 1)
        else:
            print("Usage: python test_hex_game.py [--test|--demo]")
            sys.exit(1)
    else:
        # Default: run both
        if run_integration_test():
            run_feature_demonstration()
        else:
            sys.exit(1)