"""Replay system for recording and playback of snake games."""

import json
import os
import time
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from ..entities.snake import Direction, SquareCoord
from ..ai.multi_snake import GameMode, CollisionEvent


@dataclass
class InputFrame:
    """Represents a single frame of input data."""
    timestamp: float
    snake_id: str
    direction: str  # String representation of Direction enum
    frame_number: int


@dataclass
class GameStateFrame:
    """Represents a complete game state at a specific frame."""
    frame_number: int
    timestamp: float
    snake_positions: Dict[str, List[Dict]]  # snake_id -> list of segment positions
    food_positions: List[Dict]
    scores: Dict[str, int]
    active_snakes: List[str]
    eliminated_snakes: List[str]
    collision_events: List[Dict]


class ReplayRecorder:
    """Records gameplay for later replay."""
    
    def __init__(self):
        self.recording = False
        self.input_frames: List[InputFrame] = []
        self.game_state_frames: List[GameStateFrame] = []
        self.game_info: Dict[str, Any] = {}
        self.start_time = 0.0
        self.frame_counter = 0
        self.last_save_time = 0.0
    
    def start_recording(self, game_mode: GameMode, grid_size: Tuple[int, int], 
                       player_names: List[str], game_settings: Optional[Dict] = None) -> None:
        """Start recording a new game session."""
        self.recording = True
        self.input_frames.clear()
        self.game_state_frames.clear()
        self.start_time = time.time()
        self.frame_counter = 0
        self.last_save_time = self.start_time
        
        self.game_info = {
            'game_mode': game_mode.value,
            'grid_size': grid_size,
            'player_names': player_names,
            'game_settings': game_settings or {},
            'recording_start': datetime.now().isoformat(),
            'version': '1.0'
        }
    
    def stop_recording(self) -> bool:
        """Stop recording and return if recording was active."""
        was_recording = self.recording
        self.recording = False
        return was_recording
    
    def record_input(self, snake_id: str, direction: Direction) -> None:
        """Record a direction change input."""
        if not self.recording:
            return
        
        frame = InputFrame(
            timestamp=time.time() - self.start_time,
            snake_id=snake_id,
            direction=direction.name,
            frame_number=self.frame_counter
        )
        
        self.input_frames.append(frame)
    
    def record_game_state(self, snakes: Dict[str, Any], food_items: List[Any], 
                         scores: Dict[str, int], active_snakes: List[str],
                         eliminated_snakes: List[str], collision_events: List[CollisionEvent]) -> None:
        """Record a complete game state."""
        if not self.recording:
            return
        
        # Serialize snake positions
        snake_positions = {}
        for snake_id, snake in snakes.items():
            segments = snake.get_segments()
            snake_positions[snake_id] = [
                {'x': seg.x, 'y': seg.y} for seg in segments
            ]
        
        # Serialize food positions
        food_positions = [
            {'x': food.position.x, 'y': food.position.y} for food in food_items
        ]
        
        # Serialize collision events
        collision_data = []
        for event in collision_events:
            try:
                collision_data.append({
                    'snake_id': event.snake_id,
                    'collision_type': event.collision_type.value if hasattr(event.collision_type, 'value') else str(event.collision_type),
                    'position': {'x': event.position.x, 'y': event.position.y},
                    'other_snake_id': event.other_snake_id,
                    'timestamp': event.timestamp - self.start_time
                })
            except Exception as e:
                print(f"Warning: Failed to serialize collision event: {e}")
                # Skip this event if serialization fails
                continue
        
        frame = GameStateFrame(
            frame_number=self.frame_counter,
            timestamp=time.time() - self.start_time,
            snake_positions=snake_positions,
            food_positions=food_positions,
            scores=scores.copy(),
            active_snakes=active_snakes.copy(),
            eliminated_snakes=eliminated_snakes.copy(),
            collision_events=collision_data
        )
        
        self.game_state_frames.append(frame)
        self.frame_counter += 1
    
    def save_replay(self, filepath: str) -> bool:
        """Save recorded replay to file."""
        try:
            def safe_serialize(obj):
                """Safely serialize objects to JSON-compatible format."""
                if hasattr(obj, '__dict__'):
                    return obj.__dict__
                elif hasattr(obj, 'value'):
                    return obj.value
                elif isinstance(obj, set):
                    return list(obj)
                else:
                    return str(obj)
            
            replay_data = {
                'game_info': self.game_info,
                'input_frames': [safe_serialize(frame) for frame in self.input_frames],
                'game_state_frames': [safe_serialize(frame) for frame in self.game_state_frames],
                'metadata': {
                    'total_frames': self.frame_counter,
                    'duration': time.time() - self.start_time if self.recording else self.game_info.get('duration', 0),
                    'input_count': len(self.input_frames),
                    'save_time': datetime.now().isoformat()
                }
            }
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w') as f:
                json.dump(replay_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving replay: {e}")
            return False
    
    def get_recording_stats(self) -> Dict[str, Any]:
        """Get statistics about the current recording."""
        return {
            'recording': self.recording,
            'frame_count': self.frame_counter,
            'input_count': len(self.input_frames),
            'duration': time.time() - self.start_time if self.recording else 0,
            'file_size_estimate': len(json.dumps({
                'input_frames': [asdict(frame) for frame in self.input_frames],
                'game_state_frames': [asdict(frame) for frame in self.game_state_frames[:10]]  # Sample
            }))
        }


class ReplayPlayer:
    """Plays back recorded game sessions."""
    
    def __init__(self):
        self.replay_data: Optional[Dict[str, Any]] = None
        self.current_frame = 0
        self.playing = False
        self.playback_speed = 1.0
        self.last_frame_time = 0.0
        self.start_time = 0.0
        self.loop_playback = False
    
    def load_replay(self, filepath: str) -> bool:
        """Load a replay file."""
        try:
            with open(filepath, 'r') as f:
                self.replay_data = json.load(f)
            
            self.current_frame = 0
            self.playing = False
            
            return True
        except Exception as e:
            print(f"Error loading replay: {e}")
            return False
    
    def start_playback(self, speed: float = 1.0, loop: bool = False) -> bool:
        """Start playback of loaded replay."""
        if not self.replay_data:
            return False
        
        self.playing = True
        self.playback_speed = speed
        self.loop_playback = loop
        self.current_frame = 0
        self.start_time = time.time()
        self.last_frame_time = 0.0
        
        return True
    
    def stop_playback(self) -> None:
        """Stop playback."""
        self.playing = False
    
    def is_playing(self) -> bool:
        """Check if currently playing."""
        return self.playing
    
    def get_game_info(self) -> Optional[Dict[str, Any]]:
        """Get game information from replay."""
        if not self.replay_data:
            return None
        
        return self.replay_data.get('game_info')
    
    def get_next_input_frame(self) -> Optional[InputFrame]:
        """Get the next input frame for playback."""
        if not self.replay_data or not self.playing:
            return None
        
        input_frames = self.replay_data.get('input_frames', [])
        
        # Find all input frames up to current time
        current_time = (time.time() - self.start_time) * self.playback_speed
        
        next_inputs = []
        for frame_data in input_frames:
            if frame_data['timestamp'] <= current_time and frame_data['frame_number'] > self.last_frame_time:
                next_inputs.append(InputFrame(**frame_data))
        
        if next_inputs:
            self.last_frame_time = max(frame.frame_number for frame in next_inputs)
            return next_inputs
        
        return None
    
    def get_game_state_at_frame(self, frame_number: int) -> Optional[GameStateFrame]:
        """Get game state at a specific frame."""
        if not self.replay_data:
            return None
        
        state_frames = self.replay_data.get('game_state_frames', [])
        
        for frame_data in state_frames:
            if frame_data['frame_number'] == frame_number:
                return GameStateFrame(**frame_data)
        
        return None
    
    def get_current_game_state(self) -> Optional[GameStateFrame]:
        """Get the current game state based on playback time."""
        if not self.replay_data or not self.playing:
            return None
        
        # Calculate current frame based on time
        elapsed_time = (time.time() - self.start_time) * self.playback_speed
        state_frames = self.replay_data.get('game_state_frames', [])
        
        # Find the most recent frame
        current_frame = None
        for frame_data in state_frames:
            if frame_data['timestamp'] <= elapsed_time:
                current_frame = GameStateFrame(**frame_data)
            else:
                break
        
        # Check if replay is finished
        if current_frame and self.current_frame >= len(state_frames) - 1:
            if self.loop_playback:
                self.start_playback(self.playback_speed, self.loop_playback)
            else:
                self.stop_playback()
        
        self.current_frame = current_frame.frame_number if current_frame else 0
        return current_frame
    
    def seek_to_frame(self, frame_number: int) -> bool:
        """Seek to a specific frame."""
        if not self.replay_data:
            return False
        
        state_frames = self.replay_data.get('game_state_frames', [])
        max_frame = len(state_frames) - 1
        
        if frame_number < 0 or frame_number > max_frame:
            return False
        
        self.current_frame = frame_number
        return True
    
    def seek_to_time(self, timestamp: float) -> bool:
        """Seek to a specific timestamp."""
        if not self.replay_data:
            return False
        
        state_frames = self.replay_data.get('game_state_frames', [])
        
        for frame_data in state_frames:
            if frame_data['timestamp'] >= timestamp:
                self.current_frame = frame_data['frame_number']
                return True
        
        return False
    
    def get_playback_stats(self) -> Dict[str, Any]:
        """Get playback statistics."""
        if not self.replay_data:
            return {}
        
        metadata = self.replay_data.get('metadata', {})
        total_frames = metadata.get('total_frames', 0)
        duration = metadata.get('duration', 0)
        
        return {
            'current_frame': self.current_frame,
            'total_frames': total_frames,
            'progress': self.current_frame / max(total_frames, 1),
            'duration': duration,
            'playback_speed': self.playback_speed,
            'playing': self.playing,
            'loop_enabled': self.loop_playback
        }


class ReplayManager:
    """Manages replay files and operations."""
    
    def __init__(self, replay_dir: str = "data/replays"):
        self.replay_dir = replay_dir
        os.makedirs(replay_dir, exist_ok=True)
    
    def get_replay_list(self) -> List[Dict[str, Any]]:
        """Get list of available replay files."""
        replays = []
        
        if not os.path.exists(self.replay_dir):
            return replays
        
        for filename in os.listdir(self.replay_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.replay_dir, filename)
                
                try:
                    with open(filepath, 'r') as f:
                        replay_data = json.load(f)
                    
                    game_info = replay_data.get('game_info', {})
                    metadata = replay_data.get('metadata', {})
                    
                    replay_info = {
                        'filename': filename,
                        'filepath': filepath,
                        'game_mode': game_info.get('game_mode', 'unknown'),
                        'grid_size': game_info.get('grid_size', (0, 0)),
                        'player_names': game_info.get('player_names', []),
                        'duration': metadata.get('duration', 0),
                        'total_frames': metadata.get('total_frames', 0),
                        'recording_start': game_info.get('recording_start', ''),
                        'file_size': os.path.getsize(filepath)
                    }
                    
                    replays.append(replay_info)
                except Exception as e:
                    print(f"Error reading replay file {filename}: {e}")
        
        # Sort by recording date (newest first)
        replays.sort(key=lambda r: r['recording_start'], reverse=True)
        return replays
    
    def delete_replay(self, filename: str) -> bool:
        """Delete a replay file."""
        try:
            filepath = os.path.join(self.replay_dir, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
        except Exception as e:
            print(f"Error deleting replay {filename}: {e}")
        
        return False
    
    def get_replay_path(self, filename: str = None) -> str:
        """Generate a path for a new replay file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"replay_{timestamp}.json"
        
        return os.path.join(self.replay_dir, filename)
    
    def cleanup_old_replays(self, max_files: int = 50) -> int:
        """Delete old replay files to keep under max_files limit."""
        replays = self.get_replay_list()
        
        if len(replays) <= max_files:
            return 0
        
        # Sort by date and delete oldest
        replays.sort(key=lambda r: r['recording_start'])
        to_delete = replays[:-max_files]
        
        deleted_count = 0
        for replay in to_delete:
            if self.delete_replay(replay['filename']):
                deleted_count += 1
        
        return deleted_count