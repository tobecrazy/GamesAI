# Pygame Tetris

This is a Tetris game implemented in Python using the Pygame library.

![Tetris Game Demo](https://github.com/tobecrazy/GamesAI/blob/main/assets/Game%20demo.gif "Snapshot")

*Note: Replace the above placeholder image with your actual game screenshot or GIF when available.*

## Features

- Classic Tetris gameplay
- Seven standard Tetromino shapes
- Next block preview
- Ghost piece preview for easier placement
- Score, level, and lines cleared display
- Increasing difficulty (speed) with levels
- Smooth animations
- Sound effects and background music
- Start menu
- Pause functionality
- Game over screen
- Multiple game states (menu, playing, paused, game over)

## Requirements

- Python 3.x
- Pygame 2.3.0

## Installation

1. Make sure you have Python 3.x installed on your system.
2. Clone this repository or download the source code.
3. Navigate to the project directory in your terminal.
4. Install the required dependencies using pip:
   ```
   pip install -r requirements.txt
   ```

## How to Run

1. Navigate to the project directory in your terminal.
2. Run the following command:
   ```
   python tetris.py
   ```

## Controls

- Left Arrow: Move block left
- Right Arrow: Move block right
- Down Arrow: Soft drop
- Up Arrow: Rotate block clockwise
- Spacebar: Hard drop
- P: Pause/Resume game
- R: Restart game (when game over)
- Q: Quit to main menu (during gameplay or game over)

## Game Mechanics

- The game speed increases with each level
- Every 10 lines cleared increases the level
- Scoring system:
  * 1 line: 40 points × level
  * 2 lines: 100 points × level
  * 3 lines: 300 points × level
  * 4 lines: 1200 points × level

## Project Structure

- `tetris.py`: Main game file with game loop and state management
- `requirements.txt`: List of project dependencies
- `game/`
  - `__init__.py`
  - `game.py`: Game class (main game logic)
  - `sound.py`: Sound class (handles sound effects and music)
  - `components/`
    - `block.py`: Block class (Tetromino implementation)
    - `board.py`: Board class (game board and collision detection)

### Tree

```
tetris/
│
├── assets/
│   ├── background_music.mp3
│   ├── clear.wav
│   ├── drop.wav
│   ├── gameover.wav
│   └── rotate.wav
│
├── game/
│   ├── components/
│   │   ├── __init__.py
│   │   ├── block.py
│   │   └── board.py
│   │
│   ├── __init__.py
│   ├── game.py
│   └── sound.py
│
├── README.md
├── requirements.txt
└── tetris.py
```


## Assets

Make sure to place your sound files in an `assets` folder:

- `assets/rotate.wav`
- `assets/clear.wav`
- `assets/drop.wav`
- `assets/gameover.wav`
- `assets/background_music.mp3`

## Customization

You can easily customize various aspects of the game by modifying the constants in the respective files:

- Block colors and shapes: `game/components/block.py`
- Board size: `game/components/board.py`
- Game speed and scoring: `game/game.py`

## Game States

1. Menu: The initial state where players can start a new game or quit
2. Playing: The main gameplay state
3. Paused: When the game is paused (music stops, overlay displayed)
4. Game Over: Displays the final score and allows restarting or quitting

Enjoy playing Tetris!