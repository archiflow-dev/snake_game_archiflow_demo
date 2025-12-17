"""Data persistence system for leaderboards and save games."""

import json
import os
from typing import List, Dict, Optional, Any
from datetime import datetime, timezone
import hashlib


class LeaderboardEntry:
    """Represents a single leaderboard entry."""
    
    def __init__(self, player_name: str, score: int, game_mode: str, 
                 date_played: Optional[datetime] = None, metadata: Optional[Dict] = None):
        self.player_name = player_name
        self.score = score
        self.game_mode = game_mode
        self.date_played = date_played or datetime.now(timezone.utc)
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'player_name': self.player_name,
            'score': self.score,
            'game_mode': self.game_mode,
            'date_played': self.date_played.isoformat(),
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LeaderboardEntry':
        """Create from dictionary."""
        date_played = datetime.fromisoformat(data['date_played'])
        return cls(
            player_name=data['player_name'],
            score=data['score'],
            game_mode=data['game_mode'],
            date_played=date_played,
            metadata=data.get('metadata', {})
        )


class Leaderboard:
    """Manages leaderboard data persistence."""
    
    def __init__(self, data_dir: str = "data/leaderboards"):
        self.data_dir = data_dir
        self.entries: Dict[str, List[LeaderboardEntry]] = {}  # game_mode -> entries
        self.max_entries_per_mode = 100
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Load existing leaderboards
        self.load_all()
    
    def add_entry(self, entry: LeaderboardEntry) -> bool:
        """
        Add a new entry to the leaderboard.
        
        Args:
            entry: The leaderboard entry to add
            
        Returns:
            True if entry was added successfully
        """
        game_mode = entry.game_mode
        
        if game_mode not in self.entries:
            self.entries[game_mode] = []
        
        # Check if entry qualifies for leaderboard
        if not self._qualifies_for_leaderboard(entry, game_mode):
            return False
        
        # Add entry
        self.entries[game_mode].append(entry)
        
        # Sort by score (descending) and keep only top entries
        self.entries[game_mode].sort(key=lambda e: e.score, reverse=True)
        self.entries[game_mode] = self.entries[game_mode][:self.max_entries_per_mode]
        
        # Save to file
        return self.save_game_mode(game_mode)
    
    def _qualifies_for_leaderboard(self, entry: LeaderboardEntry, game_mode: str) -> bool:
        """Check if entry qualifies for the leaderboard."""
        if game_mode not in self.entries:
            return True  # First entry always qualifies
        
        # If leaderboard is not full, entry qualifies
        if len(self.entries[game_mode]) < self.max_entries_per_mode:
            return True
        
        # Check if entry score is higher than the lowest score
        lowest_score = min(e.score for e in self.entries[game_mode])
        return entry.score > lowest_score
    
    def get_top_entries(self, game_mode: str, limit: int = 10) -> List[LeaderboardEntry]:
        """Get top entries for a specific game mode."""
        if game_mode not in self.entries:
            return []
        
        return self.entries[game_mode][:limit]
    
    def get_all_entries(self, game_mode: str) -> List[LeaderboardEntry]:
        """Get all entries for a specific game mode."""
        return self.entries.get(game_mode, []).copy()
    
    def get_player_best(self, player_name: str, game_mode: str) -> Optional[LeaderboardEntry]:
        """Get a player's best score for a specific game mode."""
        entries = self.entries.get(game_mode, [])
        player_entries = [e for e in entries if e.player_name == player_name]
        
        if not player_entries:
            return None
        
        return max(player_entries, key=lambda e: e.score)
    
    def get_player_stats(self, player_name: str) -> Dict[str, Any]:
        """Get comprehensive stats for a player."""
        stats = {
            'total_games': 0,
            'best_scores': {},
            'total_score': 0,
            'favorite_mode': None,
            'first_played': None,
            'last_played': None
        }
        
        mode_counts = {}
        
        for game_mode, entries in self.entries.items():
            player_entries = [e for e in entries if e.player_name == player_name]
            
            if player_entries:
                stats['total_games'] += len(player_entries)
                stats['best_scores'][game_mode] = max(e.score for e in player_entries)
                stats['total_score'] += sum(e.score for e in player_entries)
                mode_counts[game_mode] = len(player_entries)
                
                dates = [e.date_played for e in player_entries]
                if not stats['first_played'] or min(dates) < stats['first_played']:
                    stats['first_played'] = min(dates)
                if not stats['last_played'] or max(dates) > stats['last_played']:
                    stats['last_played'] = max(dates)
        
        if mode_counts:
            stats['favorite_mode'] = max(mode_counts, key=mode_counts.get)
        
        return stats
    
    def save_all(self) -> bool:
        """Save all leaderboard data to files."""
        success = True
        for game_mode in self.entries:
            if not self.save_game_mode(game_mode):
                success = False
        
        return success
    
    def save_game_mode(self, game_mode: str) -> bool:
        """Save leaderboard data for a specific game mode."""
        try:
            filename = os.path.join(self.data_dir, f"{game_mode}.json")
            entries_data = [entry.to_dict() for entry in self.entries[game_mode]]
            
            with open(filename, 'w') as f:
                json.dump(entries_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving leaderboard for {game_mode}: {e}")
            return False
    
    def load_all(self) -> bool:
        """Load all leaderboard data from files."""
        if not os.path.exists(self.data_dir):
            return True
        
        success = True
        
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.json'):
                game_mode = filename[:-5]  # Remove .json extension
                if not self.load_game_mode(game_mode):
                    success = False
        
        return success
    
    def load_game_mode(self, game_mode: str) -> bool:
        """Load leaderboard data for a specific game mode."""
        try:
            filename = os.path.join(self.data_dir, f"{game_mode}.json")
            
            if not os.path.exists(filename):
                return True  # No file to load is OK
            
            with open(filename, 'r') as f:
                entries_data = json.load(f)
            
            self.entries[game_mode] = [LeaderboardEntry.from_dict(data) for data in entries_data]
            return True
        except Exception as e:
            print(f"Error loading leaderboard for {game_mode}: {e}")
            return False
    
    def clear_leaderboard(self, game_mode: str) -> bool:
        """Clear all entries for a specific game mode."""
        try:
            if game_mode in self.entries:
                del self.entries[game_mode]
            
            filename = os.path.join(self.data_dir, f"{game_mode}.json")
            if os.path.exists(filename):
                os.remove(filename)
            
            return True
        except Exception as e:
            print(f"Error clearing leaderboard for {game_mode}: {e}")
            return False
    
    def clear_all_leaderboards(self) -> bool:
        """Clear all leaderboard data."""
        success = True
        for game_mode in list(self.entries.keys()):
            if not self.clear_leaderboard(game_mode):
                success = False
        
        return success
    
    def export_data(self, export_path: str) -> bool:
        """Export all leaderboard data to a single file."""
        try:
            export_data = {
                'export_date': datetime.now(timezone.utc).isoformat(),
                'game_modes': {}
            }
            
            for game_mode, entries in self.entries.items():
                export_data['game_modes'][game_mode] = [entry.to_dict() for entry in entries]
            
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error exporting leaderboard data: {e}")
            return False
    
    def import_data(self, import_path: str, merge: bool = True) -> bool:
        """Import leaderboard data from a file."""
        try:
            with open(import_path, 'r') as f:
                import_data = json.load(f)
            
            if not merge:
                self.entries.clear()
            
            for game_mode, entries_data in import_data.get('game_modes', {}).items():
                if game_mode not in self.entries:
                    self.entries[game_mode] = []
                
                new_entries = [LeaderboardEntry.from_dict(data) for data in entries_data]
                self.entries[game_mode].extend(new_entries)
                
                # Sort and trim
                self.entries[game_mode].sort(key=lambda e: e.score, reverse=True)
                self.entries[game_mode] = self.entries[game_mode][:self.max_entries_per_mode]
            
            # Save imported data
            return self.save_all()
        except Exception as e:
            print(f"Error importing leaderboard data: {e}")
            return False