import unittest
import os
import pygame # Required for screen surface and potentially other game components
import json # For good measure, though game.py handles json internally

from game.game import Game
from game.components.block import Block
from game.database import TetrisDatabase
from game.components.board import Board # Needed to manually modify board state

# Define a dummy screen for Game instances
# Pygame needs to be initialized to create a display or surface
pygame.init()
# Using a surface is generally safer for headless tests than pygame.display.set_mode
# However, if any part of Game explicitly relies on display features, set_mode might be needed.
# For now, a simple surface should suffice as Game.draw() won't be called in these tests.
DUMMY_SCREEN = pygame.Surface((100, 200)) # Dimensions don't matter much for these tests

class TestGameSaveLoad(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Pygame should be initialized before any pygame modules are used.
        # Moved DUMMY_SCREEN creation here to ensure pygame.init() is called first.
        # Actually, pygame.init() is already called at the module level above.
        # This is fine.
        pass

    def setUp(self):
        """Set up for each test."""
        self.test_db_path = "test_tetris_save_load.db"
        # Ensure no old test DB exists
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

        self.db_instance = TetrisDatabase(db_path=self.test_db_path)
        # player_name is important as it's the key for saving/loading states
        self.player_name = "TestPlayer123"
        self.game = Game(screen=DUMMY_SCREEN, player_name=self.player_name, db_instance=self.db_instance)
        
        # Ensure current_block and next_block are not None for saving
        if not self.game.current_block:
            self.game.current_block = Block.random()
        if not self.game.next_block:
            self.game.next_block = Block.random()


    def tearDown(self):
        """Clean up after each test."""
        if self.game and self.game.db:
            self.game.db.close() # Close the connection from the game's db instance
        elif self.db_instance: # Fallback if game.db wasn't set or game wasn't created
             self.db_instance.close()

        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_save_and_load_state_integrity(self):
        """Test saving a game state and loading it back correctly."""
        # 1. Set up a specific game scenario
        self.game.score = 1234
        self.game.level = 5
        self.game.lines_cleared = 10
        self.game.game_over = False
        self.game.paused = True # Test a non-default value
        self.game.fall_speed = 0.25
        self.game.score_saved = True # Test this flag too

        # Modify board (example: place a block manually)
        # Clear the board first for a predictable state
        self.game.board.grid = [[(0,0,0) for _ in range(self.game.board.WIDTH)] for _ in range(self.game.board.HEIGHT)]
        self.game.board.grid[5][5] = (255, 0, 0) # Put a red cell at (5,5)
        
        # Define specific current and next blocks
        # Using actual shapes and colors from Block.SHAPES and Block.COLORS
        test_current_block_shape = Block.SHAPES[0] # I-shape
        test_current_block_color = Block.COLORS[0] # Cyan
        self.game.current_block = Block(test_current_block_shape, test_current_block_color)
        self.game.current_block.x = 3
        self.game.current_block.y = 4
        
        test_next_block_shape = Block.SHAPES[1] # T-shape
        test_next_block_color = Block.COLORS[1] # Purple
        self.game.next_block = Block(test_next_block_shape, test_next_block_color)
        self.game.next_block.x = 1 # Different default x/y for next_block are not set by Block init
        self.game.next_block.y = 2 # So we don't need to set them here, default values are fine

        original_state = {
            'board_grid': [row[:] for row in self.game.board.grid], # Deep copy
            'current_block': self.game.current_block.to_dict(),
            'next_block': self.game.next_block.to_dict(),
            'score': self.game.score,
            'level': self.game.level,
            'lines_cleared': self.game.lines_cleared,
            'player_name': self.game.player_name,
            'game_over': self.game.game_over,
            'paused': self.game.paused,
            'fall_speed': self.game.fall_speed,
            'score_saved': self.game.score_saved
        }

        # 2. Call game.save_state()
        self.assertTrue(self.game.save_state(), "Failed to save game state.")

        # 3. Create a new Game instance (or reset)
        # The new game instance must use the same player_name and db_instance
        new_game = Game(screen=DUMMY_SCREEN, player_name=self.player_name, db_instance=self.db_instance)

        # 4. Call new_game.load_state()
        self.assertTrue(new_game.load_state(), "Failed to load game state.")

        # 5. Assert that the loaded game state matches the original state
        self.assertEqual(new_game.board.grid, original_state['board_grid'])
        self.assertEqual(new_game.current_block.to_dict(), original_state['current_block'])
        self.assertEqual(new_game.next_block.to_dict(), original_state['next_block'])
        self.assertEqual(new_game.score, original_state['score'])
        self.assertEqual(new_game.level, original_state['level'])
        self.assertEqual(new_game.lines_cleared, original_state['lines_cleared'])
        self.assertEqual(new_game.player_name, original_state['player_name'])
        self.assertEqual(new_game.game_over, original_state['game_over'])
        self.assertEqual(new_game.paused, original_state['paused'])
        self.assertAlmostEqual(new_game.fall_speed, original_state['fall_speed'])
        self.assertEqual(new_game.score_saved, original_state['score_saved'])


    def test_load_non_existent_state(self):
        """Test loading a state for a player that has no saved data."""
        non_existent_player_name = "PlayerDoesNotExist999"
        game_new_player = Game(screen=DUMMY_SCREEN, player_name=non_existent_player_name, db_instance=self.db_instance)
        
        self.assertFalse(game_new_player.load_state(), "Loaded a non-existent state, should return False.")

    def test_overwrite_saved_state(self):
        """Test that saving a new state overwrites an existing one for the same player."""
        # 1. Save an initial state
        self.game.score = 100
        self.game.level = 1
        self.game.current_block = Block(Block.SHAPES[0], Block.COLORS[0]) # I-shape
        self.game.current_block.x = 0; self.game.current_block.y = 0;
        self.assertTrue(self.game.save_state(), "Failed to save initial game state.")

        # 2. Modify the game state
        self.game.score = 5000 # New score
        self.game.level = 7    # New level
        new_block_shape = Block.SHAPES[4] # O-shape
        new_block_color = Block.COLORS[4] # Yellow
        self.game.current_block = Block(new_block_shape, new_block_color)
        self.game.current_block.x = 5; self.game.current_block.y = 5;


        # 3. Save the new state for the same player
        self.assertTrue(self.game.save_state(), "Failed to save overwritten game state.")

        # 4. Load the state into a new game instance
        loaded_game = Game(screen=DUMMY_SCREEN, player_name=self.player_name, db_instance=self.db_instance)
        self.assertTrue(loaded_game.load_state(), "Failed to load the overwritten game state.")

        # 5. Assert that the loaded state is the *new* state
        self.assertEqual(loaded_game.score, 5000)
        self.assertEqual(loaded_game.level, 7)
        loaded_block_dict = loaded_game.current_block.to_dict()
        self.assertEqual(loaded_block_dict['shape'], new_block_shape)
        self.assertEqual(loaded_block_dict['color'], new_block_color)
        self.assertEqual(loaded_block_dict['x'], 5)
        self.assertEqual(loaded_block_dict['y'], 5)

    def test_save_state_no_current_block(self):
        """Test that save_state handles cases where current_block is None."""
        self.game.current_block = None
        self.assertFalse(self.game.save_state(), "save_state should fail if current_block is None.")

    def test_save_state_no_next_block(self):
        """Test that save_state handles cases where next_block is None."""
        # current_block must exist, so re-initialize if setUp made it None by chance (unlikely)
        if not self.game.current_block: 
            self.game.current_block = Block.random()
        self.game.next_block = None
        self.assertFalse(self.game.save_state(), "save_state should fail if next_block is None.")


if __name__ == '__main__':
    unittest.main()
