#!/usr/bin/env python3
"""
Simple runner script for hexagonal snake game.
This handles common initialization errors gracefully.
"""

import sys
import os

def main():
    """Run the hexagonal snake game with error handling."""
    
    # Add current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    try:
        # Import and run the main game
        from hex_main import main as hex_main
        return hex_main()
    
    except ImportError as e:
        print(f"Import error: {e}")
        print("\nMake sure you're in the correct directory and all dependencies are installed.")
        print("Try: pip install pygame")
        return 1
    
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())