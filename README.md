# Hexagonal Snake Game - An Archiflow Demo

A revolutionary snake game implementation featuring innovative hexagonal grid mechanics, developed as a demonstration of **Archiflow** - a vibe engineering agent for complete software life cycles.

Hexagonal Snake Game Demo:
https://www.youtube.com/watch?v=0f-cT5X-gvg


## 🎮 Game Features

### Core Gameplay
- **Hexagonal Grid System**: Break from tradition with 6-directional movement on a hexagonal grid
- **Smooth Controls**: Intuitive WASD + Q/E control scheme for natural hexagonal navigation
- **Dynamic Difficulty**: Adaptive difficulty scaling that responds to player performance
- **Visual Polish**: Smooth animations and particle effects for engaging gameplay

### Technical Innovations
- **Axial Coordinate System**: Efficient hexagonal grid implementation using axial coordinates
- **Pointy-Top Hexagons**: Optimized rendering for better visual appeal
- **Performance Optimized**: Consistent 60 FPS gameplay with efficient collision detection
- **Modular Architecture**: Clean separation of game logic, rendering, and state management

## 🚀 About Archiflow

This game is a product of **[Archiflow](https://github.com/archiflow-dev/ArchiFlow)**, an AI-powered vibe engineering agent that transforms software development through intelligent collaboration. Archiflow demonstrates the complete software development lifecycle:

### 1. Product Ideation & Brainstorming
- Creative concept generation for game mechanics
- Feature prioritization and MVP definition
- User experience design philosophy

### 2. System Design & Architecture
- Modular component architecture design
- Technology stack selection and optimization
- Scalability and performance considerations

### 3. Pair Programming with AI
- Real-time code generation and refactoring
- Intelligent debugging and problem-solving
- Best practices implementation and code review

### 4. Automated Code Review
- Comprehensive code quality analysis
- Performance optimization suggestions
- Security vulnerability detection
- Maintainability and readability improvements

## 🎯 Quick Start

### Prerequisites
- Python 3.8 or higher
- Pygame library

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/hexagonal-snake-game.git
   cd hexagonal-snake-game
   ```

2. Install dependencies:
   ```bash
   pip install pygame
   ```

3. Run the game:
   ```bash
   # Main hexagonal game experience
   python hex_main.py

   # Alternative implementation
   python main_final.py
   ```

## 🕹️ Controls

### Hexagonal Movement
- **D**: Move Right (Southeast)
- **A**: Move Down-Left (Southwest)
- **E**: Move Up-Right (Northeast)
- **Q**: Move Up-Left (Northwest)
- **W**: Move Up (North)
- **S**: Move Down (South)

### Game Controls
- **Arrow Keys**: Alternative movement controls
- **ESC**: Pause/Menu
- **R**: Restart game
- **SPACE**: Start game/Continue

## 🏗️ Architecture Highlights

The codebase showcases modern software engineering principles:

### Core Systems
```python
src/
├── core/
│   ├── hex_game.py      # Main game controller
│   └── config.py        # Game configuration
├── entities/
│   ├── hex_snake_simple.py  # Snake entity for hex grid
│   └── grid_new.py           # Hexagonal grid system
├── grids/
│   └── hex_grid.py      # Hexagonal grid implementation
└── utils/
    ├── difficulty.py    # Dynamic difficulty system
    └── colors.py        # Color management
```

### Key Design Patterns
- **Entity Component System**: Flexible game entity management
- **Observer Pattern**: Event-driven game state updates
- **Strategy Pattern**: Pluggable difficulty scaling algorithms
- **Factory Pattern**: Efficient game object creation

## 🔧 Advanced Features

### Dynamic Difficulty Modes
- **Linear**: Steady difficulty progression
- **Exponential**: Rapidly increasing challenge
- **Logarithmic**: Smooth early game, challenging late game
- **Step Function**: Discrete difficulty jumps
- **Adaptive**: AI-driven difficulty based on performance

### Customization Options
```bash
# Custom game configurations
python hex_main.py --size 25         # Larger hexagons
python hex_main.py --width 1024      # Wider screen
python hex_main.py --no-animations   # Disable animations
python hex_main.py --difficulty-mode adaptive  # Adaptive difficulty
```

## 📊 Performance Metrics

- **Frame Rate**: 60 FPS target with frame limiting
- **Grid Size**: Scalable from 15x15 to 50x50 hexagons
- **Memory Usage**: Optimized entity pooling system
- **Load Times**: Sub-second game initialization

## 🧪 Testing

### Built-in Tests
```bash
# Run integration tests
python hex_main.py --test

# Run feature demonstration
python hex_main.py --demo
```

### Test Coverage
- Grid coordinate transformations
- Snake movement validation
- Collision detection accuracy
- Performance benchmarking

## 🎨 Visual Design

The game features a carefully crafted visual experience:

- **Color Palette**: High-contrast colors for accessibility
- **Hexagonal Aesthetics**: Pointy-top hexagons for optimal grid visibility
- **Smooth Animations**: Interpolated movement for visual continuity
- **Particle Effects**: Visual feedback for player actions

## 🔮 Future Roadmap

### Enhanced Features
- **Multiplayer Support**: Real-time competitive gameplay
- **AI Opponents**: Intelligent snake AI with pathfinding
- **Level Editor**: Custom hexagonal grid creation
- **Sound System**: Dynamic audio feedback
- **Leaderboards**: Global scoring integration

### Technical Improvements
- **WebGL Rendering**: Hardware acceleration for better performance
- **Network Play**: WebSocket-based multiplayer architecture
- **Mobile Support**: Touch controls and responsive design
- **Save System**: Game state persistence and replay functionality

## 🤝 Contributing

This project serves as a reference implementation for AI-assisted development. While contributions are welcome, the primary goal is to showcase the capabilities of Archiflow in production-quality software development.

## 📄 License

MIT License - feel free to use this project as a reference for your own AI-assisted development endeavors.

---

**Built with ❤️ by [Archiflow](https://github.com/archiflow-dev/ArchiFlow)** - Where AI meets creativity in software engineering

*Archiflow: Transforming ideas into elegant code through intelligent collaboration*