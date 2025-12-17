# Quick Start Guide - Hexagonal Snake Game (Phase 2)

## 🚀 Run the Game

### Method 1: Simple Entry Point (Recommended)
```bash
python run_hex_game.py
```

### Method 2: Full Entry Point
```bash
python hex_main.py
```

### Method 3: With Options
```bash
# Larger hexagons for better visibility
python hex_main.py --size 25

# Adaptive difficulty that responds to your performance
python hex_main.py --difficulty-mode adaptive

# Higher frame rate for smoother gameplay
python hex_main.py --fps 120

# Wider screen for more hexagons
python hex_main.py --width 1024 --height 768
```

## 🎮 Controls

### Movement (6-Directional)
- **W**: Northwest ↑↖
- **Q**: Northeast ↑↗  
- **A**: West ←
- **S**: Southwest ↓↙
- **E**: South ↓↘
- **D**: Southeast →↘

### Alternative Controls
- **Arrow Keys**: Movement (limited to 4 directions)
- **Page Up/Down**: Diagonal directions

### Game Controls
- **ESC**: Pause/Resume
- **R**: Restart game
- **SPACE**: Start game/Continue from menu
- **Enter**: Select menu option

## 🧪 Testing

### Run Integration Tests
```bash
python hex_main.py --test
```

### Show Feature Demo
```bash
python hex_main.py --demo
```

## 📁 What's Included

- **Hexagonal Grid**: Innovative 6-directional movement
- **Smooth Animations**: Fluid movement with easing functions
- **Dynamic Difficulty**: Adapts to player skill level
- **Visual Effects**: Gradient snake, animated food
- **Full Controls**: WASD + Q/E for all 6 directions

## 🔧 Requirements

- Python 3.8 or higher
- Pygame library: `pip install pygame`

## 🎯 Game Objective

Control your snake on a hexagonal grid to eat food and grow. The game features:
- **6-directional movement** instead of traditional 4
- **Dynamic difficulty** that increases as you score
- **Smooth animations** for better gameplay feel
- **Progressive challenges** with speed and point scaling

Enjoy the innovative hexagonal twist on classic snake gameplay!