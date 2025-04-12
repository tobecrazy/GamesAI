import pygame
from .components.block import Block
from .components.board import Board
from .sound import Sound

class Game:
    def __init__(self, screen):
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
        self.__init__(self.screen)
        self.sound.start_background_music()  # Ensure music starts on restart
    
    def toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            self.sound.stop_background_music()
        else:
            self.sound.start_background_music()