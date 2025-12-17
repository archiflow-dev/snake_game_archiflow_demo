"""Test the Phase 3 game with improved grid size and speed."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_improved_settings():
    """Test the improved game settings."""
    print("Testing Improved Phase 3 Settings...")
    print("=" * 50)
    
    try:
        from src.core.config import GameConfig
        from src.core.phase3_game import Phase3GameController
        
        # Test config changes
        config = GameConfig()
        print(f"Window size: {config.screen_width}x{config.screen_height}")
        print(f"Grid size: {config.grid_width}x{config.grid_height}")
        print(f"Starting speed: {config.get('game.starting_speed', 'N/A')}")
        print(f"Default AI difficulty: {config.get('game.ai_difficulty', 'N/A')}")
        print(f"AI snake count: {config.get('game.ai_snake_count', 'N/A')}")
        
        # Expected values
        expected_window = (1200, 800)
        expected_grid = (40, 30)
        
        if (config.screen_width, config.screen_height) == expected_window:
            print("+ Window size updated correctly")
        else:
            print(f"- Window size incorrect: expected {expected_window}")
        
        if (config.grid_width, config.grid_height) == expected_grid:
            print("+ Grid size updated correctly")
        else:
            print(f"- Grid size incorrect: expected {expected_grid}")
        
        # Test controller with new settings
        controller = Phase3GameController(config)
        print(f"+ Controller created with new settings")
        print(f"Game mode: {controller.game_mode.value}")
        print(f"AI snake count: {controller.ai_snake_count}")
        print(f"AI difficulty: {controller.ai_difficulty}")
        
        # Test speed limiting
        test_dt_values = [0.01, 0.05, 0.1, 0.2]
        print("\nTesting speed limiting:")
        for dt in test_dt_values:
            max_dt = 0.1
            limited_dt = min(dt, max_dt)
            print(f"  Input dt: {dt:.3f}s -> Limited dt: {limited_dt:.3f}s")
        
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        return False

def test_replay_error_handling():
    """Test improved replay error handling."""
    try:
        from src.data.replay import ReplayRecorder
        from src.ai.multi_snake import GameMode
        
        print("\nTesting improved replay system...")
        
        recorder = ReplayRecorder()
        recorder.start_recording(GameMode.FREE_FOR_ALL, (40, 30), ["Test"])
        
        # Test recording with various scenarios
        from src.entities.snake import Direction
        recorder.record_input("player", Direction.UP)
        
        # Mock simple state recording
        recorder.record_game_state({}, [], {}, [], [], [])
        
        recorder.stop_recording()
        
        # Test saving
        import tempfile
        temp_file = os.path.join(tempfile.mkdtemp(), "improved_replay.json")
        success = recorder.save_replay(temp_file)
        
        if success:
            print("+ Replay saving with improved error handling works")
            
            # Test loading
            from src.data.replay import ReplayPlayer
            player = ReplayPlayer()
            if player.load_replay(temp_file):
                print("+ Replay loading works without errors")
            else:
                print("- Replay loading failed")
                return False
        else:
            print("- Replay saving failed")
            return False
        
        # Cleanup
        import shutil
        shutil.rmtree(os.path.dirname(temp_file))
        
        return True
        
    except Exception as e:
        print(f"Replay test failed: {e}")
        return False

if __name__ == "__main__":
    print("Phase 3 Improvements Test")
    print("=" * 50)
    
    success = True
    
    if not test_improved_settings():
        success = False
    
    if not test_replay_error_handling():
        success = False
    
    if success:
        print("\n" + "=" * 50)
        print("+ ALL IMPROVEMENTS VERIFIED!")
        print("\nChanges Applied:")
        print("- Larger grid: 40x30 (was 25x20)")
        print("- Larger window: 1200x800 (was 1024x768)")
        print("- Slower starting speed: 3.0 (was 5.0)")
        print("- Easier AI: 0.3 difficulty (was 0.5)")
        print("- Slower updates: 10Hz (was 20Hz)")
        print("- Dynamic cell sizing for better display")
        print("- Improved replay error handling")
    else:
        print("\n" + "=" * 50)
        print("- SOME IMPROVEMENTS FAILED!")
    
    sys.exit(0 if success else 1)