#!/usr/bin/env python3
"""
Hexagonal Snake Game - Phase 2 Entry Point

This is the main entry point for the hexagonal snake game with Phase 2 features:
- Hexagonal grid system with axial coordinates
- 6-directional movement with WASD + Q/E controls
- Smooth animations and visual effects
- Dynamic difficulty scaling
- Enhanced rendering with pointy-top hexagons

Run this script to start the hexagonal snake game with all Phase 2 innovations.
"""

import sys
import argparse
import pygame
from src.core.hex_game import HexGameController
from src.utils.colors import Colors


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Hexagonal Snake Game - Phase 2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Controls:
  D: Move Right (Southeast)
  A: Move Down-Left (Southwest) 
  E: Move Up-Right (Northeast)
  Q: Move Up-Left (Northwest)
  W: Move Up (North)
  S: Move Down (South)
  Arrow Keys: Alternative movement controls
  ESC: Pause/Menu
  R: Restart game
  SPACE: Start game/Continue

Examples:
  python hex_main.py                    # Start with default settings
  python hex_main.py --size 25         # Larger hexagons
  python hex_main.py --width 1024       # Wider screen
  python hex_main.py --no-animations     # Disable animations
  python hex_main.py --test             # Run integration tests
        """
    )
    
    parser.add_argument(
        '--width', type=int, default=1400,
        help='Screen width in pixels (default: 1200)'
    )
    
    parser.add_argument(
        '--height', type=int, default=700,
        help='Screen height in pixels (default: 1000)'
    )
    
    parser.add_argument(
        '--size', type=int, default=20,
        help='Hexagon size in pixels (default: 20)'
    )
    
    parser.add_argument(
        '--fps', type=int, default=60,
        help='Target frame rate (default: 60)'
    )
    
    parser.add_argument(
        '--no-animations', action='store_true',
        help='Disable smooth animations'
    )
    
    parser.add_argument(
        '--no-grid-lines', action='store_true',
        help='Hide hexagon grid lines'
    )
    
    parser.add_argument(
        '--difficulty-mode', type=str, 
        choices=['linear', 'exponential', 'logarithmic', 'step_function', 'adaptive'],
        default='step_function',
        help='Difficulty scaling mode (default: step_function)'
    )
    
    parser.add_argument(
        '--test', action='store_true',
        help='Run integration tests and exit'
    )
    
    parser.add_argument(
        '--demo', action='store_true',
        help='Run feature demonstration and exit'
    )
    
    parser.add_argument(
        '--debug', action='store_true',
        help='Enable debug mode with additional information'
    )
    
    return parser.parse_args()


def run_game(args):
    """Run the hexagonal snake game with given arguments."""
    try:
        # Create game instance
        game = HexGameController(
            screen_width=args.width,
            screen_height=args.height,
            hex_size=args.size
        )
        
        # Apply configuration
        game.target_fps = args.fps
        game.enable_animations = not args.no_animations
        game.show_grid_lines = not args.no_grid_lines
        
        # Set difficulty mode
        from src.utils.difficulty import DifficultyMode
        mode_map = {
            'linear': DifficultyMode.LINEAR,
            'exponential': DifficultyMode.EXPONENTIAL,
            'logarithmic': DifficultyMode.LOGARITHMIC,
            'step_function': DifficultyMode.STEP_FUNCTION,
            'adaptive': DifficultyMode.ADAPTIVE
        }
        game.difficulty_manager.set_difficulty_mode(mode_map[args.difficulty_mode])
        
        # Initialize game
        game.initialize()
        
        if args.debug:
            print(f"Game initialized with settings:")
            print(f"  Screen: {args.width}x{args.height}")
            print(f"  Hex size: {args.size}px")
            print(f"  FPS: {args.fps}")
            print(f"  Animations: {game.enable_animations}")
            print(f"  Grid lines: {game.show_grid_lines}")
            print(f"  Difficulty mode: {args.difficulty_mode}")
            print(f"  Valid coordinates: {len(game.grid.get_all_valid_coords())}")
        
        # Run main game loop
        game.run()
        
    except KeyboardInterrupt:
        print("\nGame interrupted by user")
        return 1
    except Exception as e:
        print(f"Error running game: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1
    
    return 0


def run_tests():
    """Run integration tests."""
    try:
        from test_hex_game import run_integration_test
        success = run_integration_test()
        return 0 if success else 1
    except ImportError as e:
        print(f"Could not import test module: {e}")
        return 1
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1


def run_demo():
    """Run feature demonstration."""
    try:
        from test_hex_game import run_feature_demonstration
        run_feature_demonstration()
        return 0
    except ImportError as e:
        print(f"Could not import test module: {e}")
        return 1
    except Exception as e:
        print(f"Error running demo: {e}")
        return 1


def print_banner():
    """Print game banner."""
    banner = """
+==============================================================+
|                                                              |
|    SSSS    NNNN    AAAA   KK   K    EEEE     GGGG    AAAA   |
|   SS      NN  NN  AA  AA  KK  KK   EE      GG  GG  AA  AA  |
|    SSS    NN  NN  AAAAAA  KKKK    EEEE    GG      AAAAAA  |
|      SS   NN  NN  AA  AA  KK  KK  EE      GG   GG AA  AA  |
|   SSSS    NNNN    AA  AA  KK   K  EEEEE    GGGG   AA  AA  |
|                                                              |
|                    PHASE 2 IMPLEMENTATION                      |
|                 Hexagonal Grid Innovation                       |
+==============================================================+
"""
    print(banner)


def check_system_requirements():
    """Check if system meets requirements."""
    try:
        # Check Python version
        import sys
        if sys.version_info < (3, 8):
            print("Error: Python 3.8 or higher is required")
            return False
        
        # Check pygame
        import pygame
        pygame_version = pygame.version.ver
        print(f"Pygame version: {pygame_version}")
        
        # Initialize pygame for display info
        pygame.init()
        
        try:
            # Check display capabilities
            display_info = pygame.display.Info()
            print(f"Display driver: {getattr(display_info, 'driver', 'unknown')}")
            
            # Get resolution safely
            current_w = getattr(display_info, 'current_w', 'unknown')
            current_h = getattr(display_info, 'current_h', 'unknown')
            
            if current_w != 'unknown' and current_h != 'unknown':
                print(f"Current resolution: {current_w}x{current_h}")
            else:
                print("Current resolution: not available in headless mode")
                
        except Exception as e:
            print(f"Warning: Could not get display info: {e}")
            print("This is normal in headless environments")
        finally:
            # Don't quit pygame here since we'll need it for the game
            pass
        
        return True
        
    except ImportError as e:
        print(f"Missing required module: {e}")
        return False
    except Exception as e:
        print(f"Error checking requirements: {e}")
        return False


def main():
    """Main entry point."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Handle special modes
    if args.test:
        return run_tests()
    elif args.demo:
        return run_demo()
    
    # Print banner for normal execution
    print_banner()
    
    # Check system requirements
    if not check_system_requirements():
        return 1
    
    print("\nStarting Hexagonal Snake Game - Phase 2...")
    print("Use --help for command line options")
    print("\nControls: D=Right, A=Down-Left, E=Up-Right, Q=Up-Left, W=Up, S=Down | ESC: Pause | R: Restart")
    print("Press any key in game to start...")
    
    # Run the game
    return run_game(args)


if __name__ == "__main__":
    sys.exit(main())