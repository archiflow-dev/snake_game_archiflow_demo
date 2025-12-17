"""Phase 3 UI renderer for advanced game features."""

import pygame
from typing import Dict, Any, List, Optional
from ..core.config import GameConfig
from ..core.state import GameState
from ..ai.multi_snake import GameMode


class Phase3UIRenderer:
    """UI renderer for Phase 3 game features."""
    
    def __init__(self, screen: pygame.Surface, config: GameConfig):
        self.screen = screen
        self.config = config
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # UI colors
        self.text_color = (255, 255, 255)
        self.selected_color = (255, 255, 0)
        self.dimmed_color = (128, 128, 128)
        self.bg_color = (0, 0, 0, 180)  # Semi-transparent
        
        # UI positions
        self.screen_center_x = config.screen_width // 2
        self.screen_center_y = config.screen_height // 2
        self.screen_width = config.screen_width
        self.screen_height = config.screen_height
    
    def render_main_menu(self, ui_data: Dict[str, Any]) -> None:
        """Render the main menu."""
        menu_items = ui_data.get('menu_items', [])
        selected_item = ui_data.get('selected_menu_item', 0)
        
        # Title
        title_text = self.font_large.render("Advanced Snake Game", True, self.text_color)
        title_rect = title_text.get_rect(center=(self.screen_center_x, 100))
        self.screen.blit(title_text, title_rect)
        
        subtitle_text = self.font_medium.render("Phase 3 - AI & Multiplayer", True, self.dimmed_color)
        subtitle_rect = subtitle_text.get_rect(center=(self.screen_center_x, 150))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Menu items
        start_y = 250
        item_height = 50
        
        for i, item in enumerate(menu_items):
            color = self.selected_color if i == selected_item else self.text_color
            item_text = self.font_medium.render(item, True, color)
            item_rect = item_text.get_rect(center=(self.screen_center_x, start_y + i * item_height))
            self.screen.blit(item_text, item_rect)
        
        # Instructions
        instructions = [
            "Use Arrow Keys to Navigate",
            "Press ENTER to Select"
        ]
        
        start_y = self.screen_height - 100
        for i, instruction in enumerate(instructions):
            inst_text = self.font_small.render(instruction, True, self.dimmed_color)
            inst_rect = inst_text.get_rect(center=(self.screen_center_x, start_y + i * 25))
            self.screen.blit(inst_text, inst_rect)
    
    def render_game_ui(self, ui_data: Dict[str, Any]) -> None:
        """Render in-game UI overlay."""
        score = ui_data.get('score', 0)
        high_score = ui_data.get('high_score', 0)
        is_paused = ui_data.get('is_paused', False)
        
        # Score display
        score_text = self.font_medium.render(f"Score: {score}", True, self.text_color)
        self.screen.blit(score_text, (10, 10))
        
        high_score_text = self.font_small.render(f"High Score: {high_score}", True, self.dimmed_color)
        self.screen.blit(high_score_text, (10, 50))
        
        # Controls help
        controls = [
            "WASD: Move",
            "ESC/P: Pause"
        ]
        
        start_x = self.screen_width - 150
        for i, control in enumerate(controls):
            control_text = self.font_small.render(control, True, self.dimmed_color)
            self.screen.blit(control_text, (start_x, 10 + i * 25))
        
        # Pause overlay
        if is_paused:
            self._render_pause_overlay()
    
    def render_game_over(self, ui_data: Dict[str, Any]) -> None:
        """Render game over screen."""
        score = ui_data.get('score', 0)
        high_score = ui_data.get('high_score', 0)
        
        # Darken background
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Game Over text
        game_over_text = self.font_large.render("GAME OVER", True, (255, 0, 0))
        game_over_rect = game_over_text.get_rect(center=(self.screen_center_x, self.screen_center_y - 100))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Score
        score_text = self.font_medium.render(f"Final Score: {score}", True, self.text_color)
        score_rect = score_text.get_rect(center=(self.screen_center_x, self.screen_center_y))
        self.screen.blit(score_text, score_rect)
        
        # High score
        if score >= high_score:
            new_high_text = self.font_medium.render("NEW HIGH SCORE!", True, (255, 255, 0))
            new_high_rect = new_high_text.get_rect(center=(self.screen_center_x, self.screen_center_y + 50))
            self.screen.blit(new_high_text, new_high_rect)
        
        # Instructions
        instructions = [
            "Press ENTER to Play Again",
            "Press ESC for Main Menu"
        ]
        
        start_y = self.screen_center_y + 120
        for i, instruction in enumerate(instructions):
            inst_text = self.font_small.render(instruction, True, self.text_color)
            inst_rect = inst_text.get_rect(center=(self.screen_center_x, start_y + i * 30))
            self.screen.blit(inst_text, inst_rect)
    
    def render_replay_ui(self, ui_data: Dict[str, Any]) -> None:
        """Render replay UI overlay."""
        playback_stats = ui_data.get('playback_stats', {})
        
        if not playback_stats:
            return
        
        # Replay info background
        info_bg = pygame.Surface((300, 120))
        info_bg.set_alpha(200)
        info_bg.fill((0, 0, 0))
        self.screen.blit(info_bg, (10, 10))
        
        # Playback info
        is_playing = playback_stats.get('playing', False)
        current_frame = playback_stats.get('current_frame', 0)
        total_frames = playback_stats.get('total_frames', 0)
        progress = playback_stats.get('progress', 0)
        
        # Title
        title_text = self.font_small.render("REPLAY", True, self.text_color)
        self.screen.blit(title_text, (20, 20))
        
        # Status
        status = "PLAYING" if is_playing else "PAUSED"
        status_color = (0, 255, 0) if is_playing else (255, 255, 0)
        status_text = self.font_small.render(status, True, status_color)
        self.screen.blit(status_text, (20, 45))
        
        # Progress
        progress_text = self.font_small.render(f"Frame: {current_frame}/{total_frames}", True, self.text_color)
        self.screen.blit(progress_text, (20, 70))
        
        # Progress bar
        bar_width = 280
        bar_height = 10
        bar_x = 20
        bar_y = 95
        
        # Background
        pygame.draw.rect(self.screen, self.dimmed_color, (bar_x, bar_y, bar_width, bar_height))
        
        # Progress
        if total_frames > 0:
            progress_width = int(bar_width * progress)
            pygame.draw.rect(self.screen, (0, 255, 0), (bar_x, bar_y, progress_width, bar_height))
        
        # Controls
        controls = [
            "SPACE: Play/Pause",
            "ESC: Stop Replay"
        ]
        
        start_x = self.screen_width - 200
        for i, control in enumerate(controls):
            control_text = self.font_small.render(control, True, self.text_color)
            self.screen.blit(control_text, (start_x, 10 + i * 25))
    
    def render_leaderboard(self, entries: List[Dict[str, Any]], game_mode: str) -> None:
        """Render leaderboard screen."""
        # Darken background
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Title
        title_text = self.font_large.render(f"LEADERBOARD - {game_mode.upper()}", True, self.text_color)
        title_rect = title_text.get_rect(center=(self.screen_center_x, 80))
        self.screen.blit(title_text, title_rect)
        
        # Headers
        headers = ["Rank", "Player", "Score", "Date"]
        header_x_positions = [self.screen_center_x - 200, self.screen_center_x - 100, self.screen_center_x, self.screen_center_x + 100]
        
        for i, header in enumerate(headers):
            header_text = self.font_small.render(header, True, self.dimmed_color)
            self.screen.blit(header_text, (header_x_positions[i], 150))
        
        # Entries
        start_y = 190
        entry_height = 35
        
        for i, entry in enumerate(entries[:10]):  # Top 10 entries
            y = start_y + i * entry_height
            
            rank_text = self.font_small.render(f"#{i+1}", True, self.text_color)
            self.screen.blit(rank_text, (header_x_positions[0], y))
            
            name_text = self.font_small.render(entry.get('player_name', 'Unknown'), True, self.text_color)
            self.screen.blit(name_text, (header_x_positions[1], y))
            
            score_text = self.font_small.render(str(entry.get('score', 0)), True, self.text_color)
            self.screen.blit(score_text, (header_x_positions[2], y))
            
            # Format date
            date_str = entry.get('date_played', '')
            if len(date_str) > 10:
                date_str = date_str[:10]  # Just the date part
            date_text = self.font_small.render(date_str, True, self.dimmed_color)
            self.screen.blit(date_text, (header_x_positions[3], y))
        
        # Instructions
        inst_text = self.font_small.render("Press ESC to return to menu", True, self.dimmed_color)
        inst_rect = inst_text.get_rect(center=(self.screen_center_x, self.screen_height - 50))
        self.screen.blit(inst_text, inst_rect)
    
    def render_ai_settings(self, ui_data: Dict[str, Any]) -> None:
        """Render AI settings screen."""
        # Darken background
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Title
        title_text = self.font_large.render("AI SETTINGS", True, self.text_color)
        title_rect = title_text.get_rect(center=(self.screen_center_x, 80))
        self.screen.blit(title_text, title_rect)
        
        # Settings (simplified for this example)
        settings = [
            f"AI Count: {ui_data.get('ai_count', 2)}",
            f"AI Difficulty: {ui_data.get('ai_difficulty', 0.5):.1f}",
            "AI Personalities: Mixed"
        ]
        
        start_y = 200
        for i, setting in enumerate(settings):
            setting_text = self.font_medium.render(setting, True, self.text_color)
            setting_rect = setting_text.get_rect(center=(self.screen_center_x, start_y + i * 50))
            self.screen.blit(setting_text, setting_rect)
        
        # Instructions
        inst_text = self.font_small.render("Press ESC to return to menu", True, self.dimmed_color)
        inst_rect = inst_text.get_rect(center=(self.screen_center_x, self.screen_height - 50))
        self.screen.blit(inst_text, inst_rect)
    
    def render_game_mode_selection(self, current_mode: GameMode) -> None:
        """Render game mode selection screen."""
        # Darken background
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Title
        title_text = self.font_large.render("SELECT GAME MODE", True, self.text_color)
        title_rect = title_text.get_rect(center=(self.screen_center_x, 80))
        self.screen.blit(title_text, title_rect)
        
        # Game modes
        modes = [
            (GameMode.FREE_FOR_ALL, "Free For All", "Compete against AI snakes"),
            (GameMode.SURVIVAL, "Survival", "Last snake alive wins"),
            (GameMode.SCORE_RACE, "Score Race", "Most points in time limit"),
            (GameMode.COOPERATIVE, "Cooperative", "Work together")
        ]
        
        start_y = 200
        mode_height = 80
        
        for i, (mode, name, description) in enumerate(modes):
            y = start_y + i * mode_height
            
            # Highlight current mode
            if mode == current_mode:
                highlight_bg = pygame.Surface((self.screen_width - 100, 70))
                highlight_bg.set_alpha(50)
                highlight_bg.fill((255, 255, 0))
                highlight_rect = highlight_bg.get_rect(center=(self.screen_center_x, y))
                self.screen.blit(highlight_bg, highlight_rect)
            
            # Mode name
            name_text = self.font_medium.render(name, True, self.selected_color if mode == current_mode else self.text_color)
            name_rect = name_text.get_rect(center=(self.screen_center_x, y - 15))
            self.screen.blit(name_text, name_rect)
            
            # Description
            desc_text = self.font_small.render(description, True, self.dimmed_color)
            desc_rect = desc_text.get_rect(center=(self.screen_center_x, y + 15))
            self.screen.blit(desc_text, desc_rect)
        
        # Instructions
        inst_text = self.font_small.render("Press 1-4 to select mode, ESC to return", True, self.dimmed_color)
        inst_rect = inst_text.get_rect(center=(self.screen_center_x, self.screen_height - 50))
        self.screen.blit(inst_text, inst_rect)
    
    def _render_pause_overlay(self) -> None:
        """Render pause overlay."""
        # Darken background
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Pause text
        pause_text = self.font_large.render("PAUSED", True, self.text_color)
        pause_rect = pause_text.get_rect(center=(self.screen_center_x, self.screen_center_y))
        self.screen.blit(pause_text, pause_rect)
        
        # Instructions
        inst_text = self.font_small.render("Press P or ESC to resume", True, self.dimmed_color)
        inst_rect = inst_text.get_rect(center=(self.screen_center_x, self.screen_center_y + 50))
        self.screen.blit(inst_text, inst_rect)