"""Customization system for snake skins and themes."""

import json
import os
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum


class SkinType(Enum):
    """Types of snake skins."""
    CLASSIC = "classic"
    NEON = "neon"
    METALLIC = "metallic"
    FIRE = "fire"
    ICE = "ice"
    EARTH = "earth"
    SPACE = "space"
    GOLD = "gold"
    SHADOW = "shadow"
    RAINBOW = "rainbow"


class ThemeType(Enum):
    """Types of themes."""
    DEFAULT = "default"
    DARK = "dark"
    NEON_CYBERPUNK = "neon_cyberpunk"
    PASTEL = "pastel"
    RETRO_8BIT = "retro_8bit"
    MINIMALIST = "minimalist"
    NATURE = "nature"
    OCEAN = "ocean"
    SUNSET = "sunset"
    GALAXY = "galaxy"


class ColorScheme:
    """Represents a color scheme for skins."""
    
    def __init__(self, primary: Tuple[int, int, int], 
                 secondary: Tuple[int, int, int],
                 accent: Tuple[int, int, int],
                 outline: Tuple[int, int, int]):
        self.primary = primary
        self.secondary = secondary
        self.accent = accent
        self.outline = outline


class Skin:
    """Represents a snake skin."""
    
    def __init__(self, name: str, skin_type: SkinType, 
                 color_scheme: ColorScheme,
                 pattern: str = "solid",
                 animated: bool = False):
        self.name = name
        self.skin_type = skin_type
        self.color_scheme = color_scheme
        self.pattern = pattern
        self.animated = animated
        self.custom_data: Dict[str, Any] = {}
    
    def get_colors(self) -> List[Tuple[int, int, int]]:
        """Get list of colors for this skin."""
        if self.pattern == "gradient":
            return [self.color_scheme.primary, self.color_scheme.secondary, self.color_scheme.accent]
        elif self.pattern == "striped":
            return [self.color_scheme.primary, self.color_scheme.secondary, self.color_scheme.accent]
        else:  # solid
            return [self.color_scheme.primary]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert skin to dictionary for JSON serialization."""
        return {
            'name': self.name,
            'skin_type': self.skin_type.value,
            'color_scheme': {
                'primary': self.color_scheme.primary,
                'secondary': self.color_scheme.secondary,
                'accent': self.color_scheme.accent,
                'outline': self.color_scheme.outline
            },
            'pattern': self.pattern,
            'animated': self.animated,
            'custom_data': self.custom_data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Skin':
        """Create skin from dictionary."""
        color_data = data.get('color_scheme', {})
        color_scheme = ColorScheme(
            tuple(color_data.get('primary', (0, 255, 0))),
            tuple(color_data.get('secondary', (0, 200, 0))),
            tuple(color_data.get('accent', (255, 255, 0))),
            tuple(color_data.get('outline', (0, 150, 0)))
        )
        
        return cls(
            name=data.get('name', 'Unknown'),
            skin_type=SkinType(data.get('skin_type', 'classic')),
            color_scheme=color_scheme,
            pattern=data.get('pattern', 'solid'),
            animated=data.get('animated', False),
            custom_data=data.get('custom_data', {})
        )


class Theme:
    """Represents a visual theme."""
    
    def __init__(self, name: str, theme_type: ThemeType,
                 background: Tuple[int, int, int],
                 grid_colors: Dict[str, Tuple[int, int, int]],
                 food_colors: Dict[str, Tuple[int, int, int]],
                 ui_colors: Dict[str, Tuple[int, int, int]]):
        self.name = name
        self.theme_type = theme_type
        self.background = background
        self.grid_colors = grid_colors
        self.food_colors = food_colors
        self.ui_colors = ui_colors
        self.particle_colors = {
            'default': (255, 255, 255),
            'explosion': (255, 200, 100),
            'collect': (100, 255, 100),
            'trail': (150, 150, 255)
        }
        self.custom_effects: Dict[str, Any] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert theme to dictionary for JSON serialization."""
        return {
            'name': self.name,
            'theme_type': self.theme_type.value,
            'background': self.background,
            'grid_colors': self.grid_colors,
            'food_colors': self.food_colors,
            'ui_colors': self.ui_colors,
            'particle_colors': self.particle_colors,
            'custom_effects': self.custom_effects
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Theme':
        """Create theme from dictionary."""
        return cls(
            name=data.get('name', 'Unknown'),
            theme_type=ThemeType(data.get('theme_type', 'default')),
            background=tuple(data.get('background', (10, 10, 30))),
            grid_colors=data.get('grid_colors', {}),
            food_colors=data.get('food_colors', {}),
            ui_colors=data.get('ui_colors', {}),
            particle_colors=data.get('particle_colors', {}),
            custom_effects=data.get('custom_effects', {})
        )


class CustomizationManager:
    """Manages snake skins and visual themes."""
    
    def __init__(self, data_dir: str = "data/customization"):
        self.data_dir = data_dir
        self.skins: Dict[str, Skin] = {}
        self.themes: Dict[str, Theme] = {}
        self.current_skin = "classic"
        self.current_theme = "default"
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(os.path.join(data_dir, "skins"), exist_ok=True)
        os.makedirs(os.path.join(data_dir, "themes"), exist_ok=True)
        
        # Load default assets
        self._create_default_skins()
        self._create_default_themes()
        
        # Load custom assets
        self.load_skins()
        self.load_themes()
    
    def _create_default_skins(self) -> None:
        """Create default built-in skins."""
        default_skins = {
            "classic": Skin("Classic", SkinType.CLASSIC, 
                         ColorScheme((0, 255, 0), (0, 200, 0), (255, 255, 0), (0, 150, 0)),
                         "solid", False),
            
            "neon": Skin("Neon", SkinType.NEON,
                       ColorScheme((255, 0, 255), (0, 255, 255), (255, 255, 100), (200, 100, 255)),
                       "gradient", True),
            
            "metallic": Skin("Metallic", SkinType.METALLIC,
                           ColorScheme((192, 192, 192), (128, 128, 128), (255, 215, 0), (100, 100, 100)),
                           "striped", False),
            
            "fire": Skin("Fire", SkinType.FIRE,
                      ColorScheme((255, 0, 0), (255, 165, 0), (255, 255, 0), (255, 100, 100)),
                      "animated", True),
            
            "ice": Skin("Ice", SkinType.ICE,
                     ColorScheme((100, 200, 255), (200, 255, 255), (255, 255, 255), (100, 100, 200)),
                     "gradient", True),
            
            "rainbow": Skin("Rainbow", SkinType.RAINBOW,
                         ColorScheme((255, 0, 0), (255, 255, 0), (0, 255, 0), (255, 255, 255), (100, 100, 100)),
                         "gradient", True),
        }
        
        for name, skin in default_skins.items():
            self.skins[name] = skin
    
    def _create_default_themes(self) -> None:
        """Create default built-in themes."""
        default_themes = {
            "default": Theme("Default", ThemeType.DEFAULT,
                           (10, 10, 30),
                           {
                               'line': (60, 60, 80),
                               'fill': (20, 20, 40)
                           },
                           {
                               'apple': (255, 0, 0),
                               'special': (255, 215, 0)
                           },
                           {
                               'text': (255, 255, 255),
                               'button': (100, 100, 200),
                               'background': (50, 50, 100)
                           }),
                           custom_effects={'particle_count': 50}),
            
            "dark": Theme("Dark", ThemeType.DARK,
                       (20, 20, 40),
                       {
                           'line': (80, 80, 100),
                           'fill': (40, 40, 60)
                       },
                       {
                           'apple': (200, 0, 0),
                           'special': (255, 100, 0)
                       },
                       {
                           'text': (200, 200, 200),
                           'button': (80, 80, 160),
                           'background': (30, 30, 50)
                       },
                       custom_effects={'particle_glow': True}),
            
            "neon_cyberpunk": Theme("Neon Cyberpunk", ThemeType.NEON_CYBERPUNK,
                                 (0, 0, 20),
                                 {
                                     'line': (255, 0, 255),
                                     'fill': (50, 0, 50)
                                 },
                                 {
                                     'apple': (255, 100, 100),
                                     'special': (255, 255, 0)
                                 },
                                 {
                                     'text': (0, 255, 255),
                                     'button': (100, 100, 255),
                                     'background': (0, 50, 100)
                                 },
                                 custom_effects={
                                     'particle_trail': True,
                                     'grid_glow': True
                                 }),
            
            "retro_8bit": Theme("Retro 8-Bit", ThemeType.RETRO_8BIT,
                              (100, 100, 150),
                              {
                                  'line': (200, 200, 200),
                                  'fill': (150, 150, 200)
                              },
                              {
                                  'apple': (255, 0, 0),
                                  'special': (255, 255, 0)
                              },
                              {
                                  'text': (255, 255, 255),
                                  'button': (150, 150, 150),
                                  'background': (100, 100, 150)
                              },
                              custom_effects={'pixelated': True}),
        }
        
        for name, theme in default_themes.items():
            self.themes[name] = theme
    
    def load_skins(self) -> None:
        """Load custom skins from files."""
        skins_dir = os.path.join(self.data_dir, "skins")
        
        for filename in os.listdir(skins_dir):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(skins_dir, filename), 'r') as f:
                        data = json.load(f)
                    
                    skin = Skin.from_dict(data)
                    self.skins[skin.name] = skin
                    
                except Exception as e:
                    print(f"Warning: Failed to load skin {filename}: {e}")
    
    def load_themes(self) -> None:
        """Load custom themes from files."""
        themes_dir = os.path.join(self.data_dir, "themes")
        
        for filename in os.listdir(themes_dir):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(themes_dir, filename), 'r') as f:
                        data = json.load(f)
                    
                    theme = Theme.from_dict(data)
                    self.themes[theme.name] = theme
                    
                except Exception as e:
                    print(f"Warning: Failed to load theme {filename}: {e}")
    
    def save_skin(self, skin_name: str) -> bool:
        """Save a skin to file."""
        if skin_name not in self.skins:
            return False
        
        try:
            skin_data = self.skins[skin_name].to_dict()
            filepath = os.path.join(self.data_dir, "skins", f"{skin_name}.json")
            
            with open(filepath, 'w') as f:
                json.dump(skin_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving skin {skin_name}: {e}")
            return False
    
    def save_theme(self, theme_name: str) -> bool:
        """Save a theme to file."""
        if theme_name not in self.themes:
            return False
        
        try:
            theme_data = self.themes[theme_name].to_dict()
            filepath = os.path.join(self.data_dir, "themes", f"{theme_name}.json")
            
            with open(filepath, 'w') as f:
                json.dump(theme_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving theme {theme_name}: {e}")
            return False
    
    def get_available_skins(self) -> List[str]:
        """Get list of available skin names."""
        return list(self.skins.keys())
    
    def get_available_themes(self) -> List[str]:
        """Get list of available theme names."""
        return list(self.themes.keys())
    
    def get_skin(self, skin_name: str) -> Optional[Skin]:
        """Get a skin by name."""
        return self.skins.get(skin_name)
    
    def get_theme(self, theme_name: str) -> Optional[Theme]:
        """Get a theme by name."""
        return self.themes.get(theme_name)
    
    def set_current_skin(self, skin_name: str) -> bool:
        """Set the current active skin."""
        if skin_name in self.skins:
            self.current_skin = skin_name
            return True
        return False
    
    def set_current_theme(self, theme_name: str) -> bool:
        """Set the current active theme."""
        if theme_name in self.themes:
            self.current_theme = theme_name
            return True
        return False
    
    def get_current_skin(self) -> Skin:
        """Get the currently active skin."""
        return self.skins.get(self.current_skin, self.skins["classic"])
    
    def get_current_theme(self) -> Theme:
        """Get the currently active theme."""
        return self.themes.get(self.current_theme, self.themes["default"])
    
    def create_custom_skin(self, name: str, primary_color: Tuple[int, int, int],
                         secondary_color: Tuple[int, int, int] = None,
                         pattern: str = "solid") -> Skin:
        """Create a custom skin."""
        if secondary_color is None:
            # Create complementary secondary color
            secondary_color = tuple(min(255, c + 50) for c in primary_color)
        
        accent_color = tuple(min(255, c + 100) for c in primary_color)
        outline_color = tuple(max(0, c - 50) for c in primary_color)
        
        color_scheme = ColorScheme(primary_color, secondary_color, accent_color, outline_color)
        
        return Skin(name, SkinType.CUSTOM, color_scheme, pattern, False, {})
    
    def create_animated_skin(self, name: str, color_sequence: List[Tuple[int, int, int]],
                          animation_speed: float = 1.0) -> Skin:
        """Create an animated skin."""
        if not color_sequence:
            return None
        
        # Use first color as primary
        primary_color = color_sequence[0]
        secondary_color = tuple(min(255, c + 50) for c in primary_color)
        accent_color = tuple(min(255, c + 100) for c in primary_color)
        outline_color = tuple(max(0, c - 50) for c in primary_color)
        
        color_scheme = ColorScheme(primary_color, secondary_color, accent_color, outline_color)
        custom_data = {
            'color_sequence': color_sequence,
            'animation_speed': animation_speed,
            'current_color_index': 0
        }
        
        return Skin(name, SkinType.ANIMATED, color_scheme, "animated", True, custom_data)
    
    def create_custom_theme(self, name: str, background: Tuple[int, int, int],
                        grid_colors: Dict[str, Tuple[int, int, int]],
                        food_colors: Dict[str, Tuple[int, int, int]],
                        ui_colors: Dict[str, Tuple[int, int, int]]) -> Theme:
        """Create a custom theme."""
        return Theme(name, ThemeType.CUSTOM, background, grid_colors, 
                  food_colors, ui_colors)
    
    def get_skin_preview_colors(self, skin_name: str) -> List[Tuple[int, int, int]]:
        """Get colors for skin preview rendering."""
        skin = self.get_skin(skin_name)
        if not skin:
            return [(100, 100, 100)]
        
        return skin.get_colors()
    
    def apply_skin_to_render_context(self, skin: Skin, render_context: Dict[str, Any]) -> None:
        """Apply skin colors to rendering context."""
        colors = skin.get_colors()
        render_context['snake_colors'] = colors
        render_context['snake_outline'] = skin.color_scheme.outline
        render_context['snake_pattern'] = skin.pattern
        render_context['snake_animated'] = skin.animated
        render_context['snake_custom_data'] = skin.custom_data
    
    def apply_theme_to_render_context(self, theme: Theme, render_context: Dict[str, Any]) -> None:
        """Apply theme colors to rendering context."""
        render_context['background_color'] = theme.background
        render_context['grid_colors'] = theme.grid_colors
        render_context['food_colors'] = theme.food_colors
        render_context['ui_colors'] = theme.ui_colors
        render_context['particle_colors'] = theme.particle_colors
        render_context['theme_effects'] = theme.custom_effects
    
    def export_customization(self) -> Dict[str, Any]:
        """Export all customization data."""
        return {
            'skins': {name: skin.to_dict() for name, skin in self.skins.items()},
            'themes': {name: theme.to_dict() for name, theme in self.themes.items()},
            'current_skin': self.current_skin,
            'current_theme': self.current_theme
        }
    
    def import_customization(self, data: Dict[str, Any]) -> bool:
        """Import customization data."""
        try:
            # Import skins
            skins_data = data.get('skins', {})
            for skin_name, skin_data in skins_data.items():
                self.skins[skin_name] = Skin.from_dict(skin_data)
            
            # Import themes
            themes_data = data.get('themes', {})
            for theme_name, theme_data in themes_data.items():
                self.themes[theme_name] = Theme.from_dict(theme_data)
            
            # Set current selections
            self.current_skin = data.get('current_skin', 'classic')
            self.current_theme = data.get('current_theme', 'default')
            
            return True
        except Exception as e:
            print(f"Error importing customization: {e}")
            return False