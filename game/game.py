import pygame
import json # Added import
from .components.block import Block
from .components.board import Board
from .sound import Sound
from .database import TetrisDatabase

class Game:
    def __init__(self, screen, player_name="Anonymous", db_instance=None):
        self.screen = screen
        self.board = Board()
        self.current_block = None
        self.next_block = None
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        self.fall_time = 0
        self.fall_speed = 0.5  # Initial fall speed
        self.paused = False
        self.clearing_animation = False
        self.player_name = player_name
        self.score_saved = False

        # Initialize database
        if db_instance:
            self.db = db_instance
        else:
            self.db = TetrisDatabase() # Default behavior

        self.sound = Sound()
        self.sound.start_background_music()

        self.generate_new_block()

    def generate_new_block(self):
        if not self.next_block:
            self.next_block = Block.random()
        self.current_block = self.next_block
        self.next_block = Block.random()
        self.current_block.x = self.board.WIDTH // 2 - len(self.current_block.shape[0]) // 2
        self.current_block.y = 0

        if not self.board.is_valid_position(self.current_block):
            self.game_over = True
            self.sound.play_game_over()
            self.sound.stop_background_music()

            # Save score to database when game ends
            if not self.score_saved and self.score > 0:
                self.save_score()
                self.score_saved = True

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if not self.game_over and not self.paused and not self.clearing_animation:
                if event.key == pygame.K_LEFT:
                    self.move_block(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    self.move_block(1, 0)
                elif event.key == pygame.K_DOWN:
                    self.move_block(0, 1)
                elif event.key == pygame.K_UP:
                    self.rotate_block()
                elif event.key == pygame.K_SPACE:
                    self.drop_block()
            if event.key == pygame.K_r:
                self.restart_game()
            elif event.key == pygame.K_p:
                self.toggle_pause()
            # M key is now handled in the main game loop

    def move_block(self, dx, dy):
        self.current_block.move(dx, dy)
        if not self.board.is_valid_position(self.current_block):
            self.current_block.move(-dx, -dy)
            if dy > 0:
                self.place_block()

    def rotate_block(self):
        self.current_block.rotate()
        if self.board.is_valid_position(self.current_block):
            self.sound.play_rotate()
        else:
            self.current_block.rotate(-1)

    def drop_block(self):
        while self.board.is_valid_position(self.current_block):
            self.current_block.move(0, 1)
        self.current_block.move(0, -1)
        self.place_block()
        self.sound.play_drop()

    def place_block(self):
        self.board.place_block(self.current_block)
        lines_cleared = self.board.clear_lines()
        if lines_cleared > 0:
            self.clearing_animation = True
            self.sound.play_clear()
        else:
            self.generate_new_block()

    def update_score(self, lines_cleared):
        self.lines_cleared += lines_cleared
        self.score += [0, 40, 100, 300, 1200][lines_cleared] * self.level
        self.level = min(20, 1 + self.lines_cleared // 10)
        self.fall_speed = max(0.05, 0.5 - (self.level - 1) * 0.02)  # Increase speed with level

    def update(self):
        if not self.game_over and not self.paused:
            if self.clearing_animation:
                self.board.update_clearing_animation()
                if self.board.is_animation_complete():
                    self.finish_line_clear()
            else:
                now = pygame.time.get_ticks()
                if now - self.fall_time > self.fall_speed * 1000:
                    self.fall_time = now
                    self.move_block(0, 1)

    def finish_line_clear(self):
        self.clearing_animation = False
        lines_cleared = self.board.lines_cleared
        self.update_score(lines_cleared)
        self.generate_new_block()

    def draw(self):
        self.board.draw(self.screen)
        if self.current_block and not self.clearing_animation:
            self.current_block.draw(self.screen)
            self.board.draw_ghost(self.screen, self.current_block)

    def restart_game(self):
        player_name = self.player_name  # Keep the player name
        # Pass the current db instance if it exists, otherwise it will create a new one.
        db_instance = getattr(self, 'db', None)
        self.__init__(self.screen, player_name, db_instance=db_instance)
        self.sound.start_background_music()  # Ensure music starts on restart

    def toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            self.sound.stop_background_music()
        else:
            self.sound.start_background_music()

    def toggle_mute(self):
        """Toggle mute state for all game sounds."""
        is_muted = self.sound.toggle_mute()
        return is_muted

    def save_score(self):
        """Save the current game score to the database."""
        return self.db.save_score(self.player_name, self.score, self.level, self.lines_cleared)

    def get_high_scores(self, limit=10):
        """Get the top scores from the database."""
        return self.db.get_high_scores(limit)

    def set_player_name(self, name):
        """Set the player name."""
        self.player_name = name if name else "Anonymous"

    def save_state(self):
        """Save the current game state to the database."""
        if not self.current_block or not self.next_block:
            # Cannot save if blocks are not initialized (e.g., very start or end of game)
            return False

        game_state = {
            'board': self.board.grid,
            'current_block': self.current_block.to_dict(),
            'next_block': self.next_block.to_dict(),
            'score': self.score,
            'level': self.level,
            'lines_cleared': self.lines_cleared,
            'fall_speed': self.fall_speed,
            'player_name': self.player_name, # player_name is part of the key in DB
            'game_over': self.game_over,
            'paused': self.paused,
            'fall_time': self.fall_time,
            'score_saved': self.score_saved # Important to restore this
        }
        try:
            serialized_state = json.dumps(game_state)
            return self.db.save_game_state(self.player_name, serialized_state)
        except TypeError as e:
            print(f"Error serializing game state: {e}")
            return False

    def load_state(self):
        """Load the game state from the database."""
        serialized_state = self.db.load_game_state(self.player_name)
        if serialized_state:
            try:
                game_state = json.loads(serialized_state)

                self.board.grid = game_state['board']
                self.current_block = Block.from_dict(game_state['current_block'])
                self.next_block = Block.from_dict(game_state['next_block'])
                self.score = game_state['score']
                self.level = game_state['level']
                self.lines_cleared = game_state['lines_cleared']
                self.fall_speed = game_state['fall_speed']
                # self.player_name is already correct as it's used for loading
                self.game_over = game_state['game_over']
                self.paused = game_state['paused']
                self.fall_time = game_state['fall_time']
                self.score_saved = game_state.get('score_saved', False) # For compatibility with older saves

                # Ensure sound state is consistent with loaded game state
                if self.paused:
                    self.sound.stop_background_music()
                else:
                    self.sound.start_background_music()
                
                # Reset fall_time to avoid immediate drop after loading if game was paused a long time
                if not self.game_over and not self.paused:
                     self.fall_time = pygame.time.get_ticks()


                return True
            except (TypeError, KeyError, json.JSONDecodeError) as e:
                print(f"Error loading or parsing game state: {e}")
                return False
        return False