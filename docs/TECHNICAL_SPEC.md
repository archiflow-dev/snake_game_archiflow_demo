# Technical Specification: Advanced Snake Game

## 1. System Architecture

### High-Level Architecture
The game follows a modular architecture with clear separation of concerns:
- **Game Engine**: Core game loop and state management
- **Rendering System**: Graphics rendering and visual effects
- **Input System**: Keyboard input handling and mapping
- **Entity System**: Snake, food, and other game entities
- **UI System**: Menu system and in-game HUD
- **Audio System**: Sound effect management
- **Data System**: Configuration and save data management

### Core Components

**GameController**
- Main game loop coordination
- State machine management (menu, playing, game over)
- Frame rate control and timing
- Event coordination between systems

**GridManager**
- Grid coordinate system (square → hexagonal)
- Cell validation and collision detection
- Coordinate transformation between different grid types

**EntityManager**
- Snake segment tracking and management
- Food spawning and lifecycle
- Multi-entity collision detection

**RenderEngine**
- Drawing primitives and sprite management
- Animation interpolation
- Visual effects coordination

### Technology Stack
- **Primary**: Python 3.8+
- **Graphics**: Pygame 2.0+ for 2D rendering and input
- **Math**: NumPy for coordinate calculations (hexagonal grid)
- **Data**: JSON for configuration and save files
- **Audio**: Pygame mixer for sound effects
- **Testing**: Pytest for unit tests

## 2. Data Model

### Core Entities

**Snake**
```python
class Snake:
    segments: List[Coordinate]  # Head to tail ordering
    direction: Direction        # Current heading
    next_direction: Direction   # Buffered next input
    growth_pending: int         # Segments to add on next move
    skin_id: str               # Selected skin identifier
```

**Coordinate Systems**
```python
# Square Grid (MVP)
class SquareCoord:
    x: int
    y: int

# Hexagonal Grid (Phase 1)
class HexCoord:
    q: int  # Axial coordinate Q
    r: int  # Axial coordinate R
    
    def to_pixel(self, size: int) -> Tuple[int, int]:
        # Convert hex to screen coordinates
        pass
```

**Food**
```python
class Food:
    position: Coordinate
    food_type: str           # Visual variant
    point_value: int
    visual_effects: List[str]
```

**Game State**
```python
class GameState:
    score: int
    high_score: int
    speed: float              # Current game speed
    difficulty_level: int
    play_time: float
    settings: GameSettings
```

### Configuration Data
```python
class GameSettings:
    grid_type: str           # "square" or "hexagonal"
    grid_size: Tuple[int, int]
    starting_speed: float
    difficulty_curve: Dict[int, float]  # score -> speed multiplier
    selected_skin: str
    selected_food_theme: str
    selected_background: str
```

## 3. Grid Systems

### Square Grid (MVP)
- Simple Cartesian coordinate system
- 4-directional movement (up, down, left, right)
- Easy collision detection and boundary checking
- Perfect for initial implementation and testing

### Hexagonal Grid (Phase 1)
- **Coordinate System**: Axial coordinates (q, r)
- **Movement**: 6 directions using neighbor calculations
- **Neighbor Calculation**:
```python
HEX_DIRECTIONS = {
    'NE': (+1, 0),   'NW': (0, +1),   'N': (-1, +1),
    'SE': (+1, -1),  'SW': (0, -1),   'S': (-1, 0)
}
```

- **Pixel Conversion**:
```python
def hex_to_pixel(q: int, r: int, size: int) -> Tuple[int, int]:
    x = size * (3/2 * q)
    y = size * (sqrt(3)/2 * q + sqrt(3) * r)
    return (int(x), int(y))
```

## 4. Input System

### Key Mapping
```python
KEY_MAPPINGS = {
    pygame.K_w: 'UP',
    pygame.K_a: 'LEFT', 
    pygame.K_s: 'DOWN',
    pygame.K_d: 'RIGHT',
    pygame.K_ESCAPE: 'PAUSE',
    pygame.K_r: 'RESTART'
}
```

### Input Buffering
- Queue system for responsive controls
- Prevents invalid reverse directions
- Smooth input handling at high speeds

## 5. Rendering System

### Architecture
**Renderer Base Class**
- Abstract interface for different renderers
- SquareRenderer and HexRenderer implementations

### Hexagonal Rendering
- **Drawing Hexagons**: Pointy-top hexagons with calculated vertices
- **Segment Interpolation**: Smooth movement between hex centers
- **Visual Effects**: Rotation and scaling for food consumption

### Animation System
```python
class Animation:
    duration: float
    start_time: float
    easing_function: Callable[[float], float]
    
    def update(self, dt: float) -> float:
        # Return interpolation value (0.0 to 1.0)
        pass
```

## 6. Dynamic Difficulty System

### Speed Scaling Algorithm
```python
def calculate_speed(score: int, base_speed: float) -> float:
    # Exponential scaling with score thresholds
    if score < 50:
        return base_speed
    elif score < 150:
        return base_speed * 1.2
    elif score < 300:
        return base_speed * 1.5
    else:
        return base_speed * (1.0 + score / 1000)
```

### Difficulty Events
- Speed increases at score thresholds
- Visual feedback for difficulty changes
- Smooth transitions between speed levels

## 7. Customization System

### Asset Management
```python
class ThemeManager:
    skins: Dict[str, SkinAsset]
    food_themes: Dict[str, FoodTheme]
    backgrounds: Dict[str, BackgroundAsset]
    
    def load_theme(self, theme_name: str) -> Theme:
        pass
```

### Skin System
- **Snake Skins**: Color gradients, patterns, animated effects
- **Configuration**: JSON files defining color schemes
- **Runtime Switching**: Apply skins without game restart

### Food Variants
- **Visual Types**: Different shapes and animations
- **Themed Sets**: Consistent visual language per theme
- **Particle Effects**: Custom effects per food type

## 8. Multi-Snake System (Phase 3)

### Entity Management
```python
class MultiSnakeGame:
    player_snake: Snake
    ai_snakes: List[AISnake]
    food_entities: List[Food]
    
    def update_collisions(self) -> None:
        # Handle snake-snake and snake-food collisions
        pass
```

### AI Architecture
**Behavior Tree System**
- **Decision Making**: Food seeking, obstacle avoidance
- **Pathfinding**: A* algorithm for optimal routes
- **Difficulty Levels**: Different decision-making parameters

```python
class AISnake(Snake):
    personality: AIPersonality
    target_food: Optional[Food]
    pathfinding_cooldown: float
    
    def calculate_next_direction(self) -> Direction:
        # AI decision logic
        pass
```

## 9. Performance Requirements

### Frame Rate Optimization
- **Target**: Consistent 60 FPS
- **Optimization Techniques**:
  - Dirty rectangle rendering for partial screen updates
  - Sprite batching for similar objects
  - Efficient collision detection with spatial partitioning

### Memory Management
- **Object Pooling**: Reuse food and effect objects
- **Segment Management**: Efficient snake segment data structure
- **Asset Loading**: Lazy loading for customization assets

## 10. Error Handling

### Game State Validation
- Grid boundary checking
- Snake self-collision prevention
- Valid move validation

### Exception Handling
```python
class GameError(Exception):
    pass

class InvalidMoveError(GameError):
    pass

class GridError(GameError):
    pass
```

### Debug Systems
- Collision visualization mode
- Performance monitoring overlay
- Debug console for runtime inspection

## 11. File Structure

```
snake_game/
├── main.py                 # Game entry point
├── src/
│   ├── core/
│   │   ├── game.py         # Main game loop
│   │   ├── state.py        # Game state management
│   │   └── events.py       # Event system
│   ├── entities/
│   │   ├── snake.py        # Snake entity logic
│   │   ├── food.py         # Food entity logic
│   │   └── grid.py         # Grid management
│   ├── systems/
│   │   ├── input.py        # Input handling
│   │   ├── render.py       # Rendering engine
│   │   ├── audio.py        # Sound management
│   │   └── ui.py           # User interface
│   ├── ai/
│   │   ├── behavior.py     # AI decision logic
│   │   └── pathfinding.py  # Pathfinding algorithms
│   └── utils/
│       ├── math.py         # Coordinate calculations
│       ├── animation.py    # Animation utilities
│       └── assets.py       # Asset management
├── assets/
│   ├── skins/              # Snake skin assets
│   ├── food/               # Food visual assets
│   ├── backgrounds/        # Background images
│   └── sounds/             # Sound effects
├── data/
│   ├── themes/             # Theme configurations
│   └── saves/              # Save files
├── tests/                  # Unit tests
└── docs/                   # Documentation
```

## 12. Testing Strategy

### Unit Tests
- Grid coordinate calculations
- Snake movement logic
- Collision detection
- Difficulty scaling

### Integration Tests
- Game state transitions
- Multi-system coordination
- Asset loading and management

### Performance Tests
- Frame rate consistency
- Memory usage profiling
- Load testing for complex scenarios

---

*Document Version: 1.0*  
*Last Updated: 2025-06-17*  
*Status: Technical Design Complete*