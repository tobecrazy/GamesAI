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
- Sound effects and background music with mute option (press 'M' to toggle)
- Start menu with top scores display
- Player name input at game start (defaults to "Anonymous" if empty)
- Pause functionality
- Game over screen with top scores display
- Scrolling top 10 players leaderboard (continuous animation until any key is pressed)
- Simultaneous line clearing animation for multiple rows
- Multiple game states (menu, playing, paused, game over)
- SQLite database for storing and retrieving game scores
- Performance grading system (S, A, B, C, D, F)
- High score leaderboard

## Requirements

- Python 3.x
- Pygame 2.3.0
- SQLite3 (included in Python standard library)

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
- M: Toggle mute for all sounds and music
- R: Restart game (when game over)
- Q: Quit to main menu (during gameplay or game over)
- S: View scrolling top 10 players (when game over)
- N: Enter name to save score (when game over)
- H: View high scores (when game over)
- B: Go back from high scores screen
- Any key: Return from scrolling scores screen

## Game Mechanics

- The game speed increases with each level
- Every 10 lines cleared increases the level
- Scoring system:
  * 1 line: 40 points × level
  * 2 lines: 100 points × level
  * 3 lines: 300 points × level
  * 4 lines: 1200 points × level
- Grading system:
  * S: 10,000+ points
  * A: 7,500-9,999 points
  * B: 5,000-7,499 points
  * C: 2,500-4,999 points
  * D: 1,000-2,499 points
  * F: 0-999 points

## Project Structure

- `tetris.py`: Main game file with game loop and state management
- `requirements.txt`: List of project dependencies
- `tetris_scores.db`: SQLite database file (created on first run)
- `game/`
  - `__init__.py`
  - `game.py`: Game class (main game logic)
  - `sound.py`: Sound class (handles sound effects and music)
  - `database.py`: Database class (handles score storage and retrieval)
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
│   ├── database.py
│   ├── game.py
│   └── sound.py
│
├── README.md
├── requirements.txt
├── tetris_scores.db
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
2. Start Name Input: Allows the player to enter their name before starting the game
3. Playing: The main gameplay state
4. Paused: When the game is paused (music stops, overlay displayed)
5. Game Over: Displays the final score, top scores, and allows restarting or quitting
6. High Scores: Displays the top scores from the database
7. Name Input: Allows the player to enter their name before saving their score
8. Scrolling Scores: Displays top 10 players scrolling from bottom to top continuously until any key is pressed

## Recent Updates

### Sound System Enhancements
- Added mute functionality (press 'M' to toggle all sounds and music)
- Mute status is displayed on all game screens
- Mute state persists between game states and when restarting

### User Interface Improvements
- Added scrolling animation for top 10 players display
- Scores continuously scroll from bottom to top until any key is pressed
- Fixed UI elements positioning to ensure all text is fully visible

### Gameplay Enhancements
- Fixed bug where multiple completed rows wouldn't disappear simultaneously
- Improved line clearing animation to handle multiple rows at once
- Enhanced player name input with clearer instructions

Enjoy playing Tetris!