import pygame
import sys
import random

# Constants
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400
CELL_SIZE = 20
# FPS = 10 # FPS is now level-dependent

LEVELS_CONFIG = [
    {'level': 1, 'fps': 7, 'score_to_next_level': 50},  # Score to reach level 2
    {'level': 2, 'fps': 9, 'score_to_next_level': 100}, # Score to reach level 3
    {'level': 3, 'fps': 11, 'score_to_next_level': 150},# Score to reach level 4
    {'level': 4, 'fps': 13, 'score_to_next_level': 200},# Score to reach level 5
    {'level': 5, 'fps': 15, 'score_to_next_level': 250} # Max level
]

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

class Snake:
    def __init__(self):
        self.body = [(100, 100), (80, 100), (60, 100)]
        self.direction = "RIGHT"
        self.grow_pending = False # Flag to indicate snake should grow in the next move

    def move(self):
        head_x, head_y = self.body[0]
        if self.direction == "UP":
            new_head = (head_x, head_y - CELL_SIZE)
        elif self.direction == "DOWN":
            new_head = (head_x, head_y + CELL_SIZE)
        elif self.direction == "LEFT":
            new_head = (head_x - CELL_SIZE, head_y)
        elif self.direction == "RIGHT":
            new_head = (head_x + CELL_SIZE, head_y)
        else: # Should not happen
            return

        self.body.insert(0, new_head)

        if self.grow_pending:
            self.grow_pending = False
        else:
            self.body.pop()

    def draw(self, surface):
        for segment in self.body:
            pygame.draw.rect(surface, GREEN, pygame.Rect(segment[0], segment[1], CELL_SIZE, CELL_SIZE))

    def check_collision(self):
        head = self.body[0]
        # Check wall collision
        if not (0 <= head[0] < WINDOW_WIDTH and 0 <= head[1] < WINDOW_HEIGHT):
            return True
        # Check self collision
        if head in self.body[1:]:
            return True
        return False

    def grow(self):
        self.grow_pending = True # Set flag to grow on next move

    def change_direction(self, new_direction):
        if new_direction == "UP" and self.direction != "DOWN":
            self.direction = new_direction
        elif new_direction == "DOWN" and self.direction != "UP":
            self.direction = new_direction
        elif new_direction == "LEFT" and self.direction != "RIGHT":
            self.direction = new_direction
        elif new_direction == "RIGHT" and self.direction != "LEFT":
            self.direction = new_direction

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.color = RED

    def randomize_position(self, snake_body=None):
        if snake_body is None: # Should ideally always be provided
            snake_body = []
        while True:
            self.position = (random.randint(0, (WINDOW_WIDTH - CELL_SIZE) // CELL_SIZE) * CELL_SIZE,
                             random.randint(0, (WINDOW_HEIGHT - CELL_SIZE) // CELL_SIZE) * CELL_SIZE)
            if self.position not in snake_body:
                break

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, pygame.Rect(self.position[0], self.position[1], CELL_SIZE, CELL_SIZE))

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36) # Initialize font once

        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.game_over = False

        self.current_level_index = 0
        self.fps = LEVELS_CONFIG[self.current_level_index]['fps']
        self.all_levels_complete = False
        self.level_up_message_active = False
        self.level_up_timer = 0

        self.food.randomize_position(self.snake.body)


    def restart_game(self):
        self.snake = Snake() # Re-initialize snake
        self.score = 0
        self.game_over = False
        self.current_level_index = 0
        self.fps = LEVELS_CONFIG[self.current_level_index]['fps']
        self.all_levels_complete = False
        self.level_up_message_active = False
        self.level_up_timer = 0
        self.food.randomize_position(self.snake.body)


    def run(self):
        while True: # Main loop runs indefinitely until sys.exit()
            self.check_events()

            if self.game_over:
                self.screen.fill(BLACK)
                game_over_text = self.font.render("Game Over!", True, WHITE)
                restart_text = self.font.render("Press SPACE to Play Again", True, WHITE)
                score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)

                self.screen.blit(game_over_text, (WINDOW_WIDTH // 2 - game_over_text.get_width() // 2, WINDOW_HEIGHT // 3 - game_over_text.get_height() // 2))
                self.screen.blit(score_text, (WINDOW_WIDTH // 2 - score_text.get_width() // 2, WINDOW_HEIGHT // 2 - score_text.get_height() // 2))
                self.screen.blit(restart_text, (WINDOW_WIDTH // 2 - restart_text.get_width() // 2, WINDOW_HEIGHT * 2 // 3 - restart_text.get_height() // 2))
                # Optionally display final level on game over screen
                level_on_game_over_text = f"Reached Level: {LEVELS_CONFIG[self.current_level_index]['level']}"
                if self.all_levels_complete:
                    level_on_game_over_text = "All Levels Completed!"
                final_level_text_surface = self.font.render(level_on_game_over_text, True, WHITE)
                self.screen.blit(final_level_text_surface, (WINDOW_WIDTH // 2 - final_level_text_surface.get_width() // 2, WINDOW_HEIGHT * 3 // 4 - final_level_text_surface.get_height() // 2))

            else: # Not game over
                self.update_game_state()
                self.screen.fill(BLACK)
                self.draw_elements(self.screen) # Snake and Food
                self.display_score(self.screen)
                self.display_level(self.screen)
                self.display_fps(self.screen)
                self.draw_level_progress_bar(self.screen)
                self.display_level_up_message(self.screen)


            pygame.display.flip()
        self.clock.tick(self.fps) # Use dynamic FPS

    def display_score(self, surface):
        text = self.font.render(f"Score: {self.score}", True, WHITE)
        surface.blit(text, (10, 10))

    def display_level(self, surface):
        level_num = LEVELS_CONFIG[self.current_level_index]['level']
        level_text = f"Level: {level_num}"
        if self.all_levels_complete:
            level_text = "Level: Max (Completed!)"

        text_surface = self.font.render(level_text, True, WHITE)
        surface.blit(text_surface, (10, 40))

    def display_fps(self, surface):
        fps_text = f"Speed: {self.fps} FPS"
        text_surface = self.font.render(fps_text, True, WHITE)
        surface.blit(text_surface, (10, 70)) # Display FPS below level

    def draw_level_progress_bar(self, surface):
        if self.all_levels_complete:
            return # No progress bar if all levels are done

        current_level_config = LEVELS_CONFIG[self.current_level_index]

        if self.current_level_index == 0:
            score_at_level_start = 0
        else:
            score_at_level_start = LEVELS_CONFIG[self.current_level_index - 1]['score_to_next_level']

        score_to_reach_next_level_target = current_level_config['score_to_next_level']

        # For the very last level, the "target" for progress is reaching its own score_to_next_level
        # For other levels, it's the difference to the next level's target.
        score_needed_for_this_level = score_to_reach_next_level_target - score_at_level_start
        current_score_in_level = self.score - score_at_level_start

        if score_needed_for_this_level <= 0: # Avoid division by zero if config is weird or last level
            progress_percentage = 1.0 if self.score >= score_to_reach_next_level_target else 0.0
        else:
            progress_percentage = min(1.0, max(0.0, current_score_in_level / score_needed_for_this_level))

        bar_width = WINDOW_WIDTH - 20  # Bar width with some padding
        bar_height = 10
        bar_x = 10
        bar_y = WINDOW_HEIGHT - bar_height - 10  # At the bottom

        # Draw background of progress bar
        pygame.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        # Draw progress
        pygame.draw.rect(surface, GREEN, (bar_x, bar_y, bar_width * progress_percentage, bar_height))
        # Draw outline
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)

    def display_level_up_message(self, surface):
        if self.level_up_message_active:
            elapsed_time = pygame.time.get_ticks() - self.level_up_timer
            if elapsed_time < 3000: # Display for 3 seconds
                level_up_font = pygame.font.Font(None, 72) # Larger font
                level_num = LEVELS_CONFIG[self.current_level_index]['level']
                # For "Level Up! Level 5" when level 5 is the max and just completed:
                # if self.all_levels_complete and self.current_level_index == len(LEVELS_CONFIG) -1:
                #    level_num_display = "Max" # Or keep it as the number
                text = level_up_font.render(f"Level Up! Level {level_num}", True, WHITE, GREEN)
                text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
                surface.blit(text, text_rect)
            else:
                self.level_up_message_active = False


    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_SPACE:
                        self.restart_game()
                else:
                    if event.key == pygame.K_UP:
                        self.snake.change_direction("UP")
                    elif event.key == pygame.K_DOWN:
                        self.snake.change_direction("DOWN")
                    elif event.key == pygame.K_LEFT:
                        self.snake.change_direction("LEFT")
                    elif event.key == pygame.K_RIGHT:
                        self.snake.change_direction("RIGHT")

    def update_game_state(self):
        self.snake.move()

        if self.snake.check_collision():
            self.game_over = True
            return # Stop further updates if game over

        # Check for food consumption
        if self.snake.body[0] == self.food.position:
            self.score += 10
            self.snake.grow()
            self.food.randomize_position(self.snake.body)

            # Check for level up
            if not self.all_levels_complete:
                current_level_config = LEVELS_CONFIG[self.current_level_index]
                if self.score >= current_level_config['score_to_next_level']:
                    if self.current_level_index < len(LEVELS_CONFIG) - 1:
                        self.current_level_index += 1
                        self.fps = LEVELS_CONFIG[self.current_level_index]['fps']
                        self.level_up_message_active = True
                        self.level_up_timer = pygame.time.get_ticks()
                    elif self.current_level_index == len(LEVELS_CONFIG) - 1 and not self.all_levels_complete:
                        # Just completed the score requirement for the final level
                        self.all_levels_complete = True
                        self.level_up_message_active = True # Show "Level Up!" for reaching max level too
                        self.level_up_timer = pygame.time.get_ticks()
                        # FPS for the last level is already set.


    def draw_elements(self, surface):
        # This method could be used if we want to separate game over drawing logic more cleanly
        # For now, game_over drawing is handled in run()
        if not self.game_over:
            self.snake.draw(surface)
            self.food.draw(surface)
        # If game_over is True, the run method handles drawing the game over screen.
