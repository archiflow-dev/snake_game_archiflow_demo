# Advanced Snake Game

A modern implementation of the classic snake game with innovative features including hexagonal grids, dynamic difficulty scaling, and extensive customization options.

## MVP Features

- **Traditional Snake Gameplay**: Classic snake mechanics on square grid with WASD controls
- **Game State Management**: Score tracking, game over detection, restart functionality
- **Food System**: Random food spawning with snake growth mechanics
- **60 FPS Performance**: Smooth, responsive gameplay

## Future Features (Post-MVP)

- **Hexagonal Grid Layout**: 6-directional movement on hexagonal cells
- **Dynamic Difficulty**: Speed increases based on score progression
- **Customization System**: Snake skins, food themes, and visual effects
- **AI Opponents**: Computer-controlled snakes with pathfinding
- **Multi-Snake Gameplay**: Competitive multiplayer modes

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the game:
   ```bash
   python main.py
   ```

## Controls

- **W/A/S/D**: Move snake (up/left/down/right)
- **R**: Restart game
- **ESC**: Pause/Resume game

## Architecture

The game follows a modular architecture with clear separation of concerns:

- **Core Systems**: Game loop, state management, event coordination
- **Entity Layer**: Snake, food, and game entities
- **System Layer**: Input, rendering, and UI systems
- **Grid System**: Support for both square and hexagonal grids

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black src/
```

### Type Checking
```bash
mypy src/
```

## License

MIT License