import pygame
import sys
from game.game import Game

# Initialize Pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris")

# Set up fonts
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)

def draw_text(text, font, color, x, y):
    surface = font.render(text, True, color)
    rect = surface.get_rect(center=(x, y))
    screen.blit(surface, rect)

def draw_menu():
    screen.fill((0, 0, 0))
    draw_text("TETRIS", large_font, (0, 255, 0), WIDTH // 2, HEIGHT // 4)  # Green
    draw_text("Press ENTER to start", font, (0, 0, 255), WIDTH // 2, HEIGHT // 2)  # Blue
    draw_text("Press Q to quit", font, (255, 255, 0), WIDTH // 2, HEIGHT // 2 + 50)  # Yellow

def draw_game_over():
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(128)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    draw_text("GAME OVER", large_font, (255, 0, 0), WIDTH // 2, HEIGHT // 3)  # Red
    draw_text(f"Score: {game.score}", font, (0, 255, 0), WIDTH // 2, HEIGHT // 2)  # Green
    draw_text("Press R to restart", font, (0, 0, 255), WIDTH // 2, HEIGHT // 2 + 50)  # Blue
    draw_text("Press Q to quit", font, (255, 255, 0), WIDTH // 2, HEIGHT // 2 + 100)  # Yellow

def draw_pause():
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(128)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    draw_text("PAUSED", large_font, (255, 255, 255), WIDTH // 2, HEIGHT // 2)
    draw_text("Press P to resume", font, (255, 255, 255), WIDTH // 2, HEIGHT // 2 + 50)

# Create game instance
game = None

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2

state = MENU
game_over_time = 0

# Main game loop
clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if state == MENU:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game = Game(screen)
                    state = PLAYING
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
        elif state == PLAYING:
            if not game.clearing_animation:
                game.handle_event(event)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                game.sound.stop_background_music()
                game = None
                state = MENU
        elif state == GAME_OVER:
            if pygame.time.get_ticks() - game_over_time > 1000:  # 1 second delay
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        game = Game(screen)
                        state = PLAYING
                    elif event.key == pygame.K_q:
                        game = None
                        state = MENU
    
    screen.fill((0, 0, 0))  # Black background
    
    if state == MENU:
        draw_menu()
    elif state == PLAYING:
        game.update()
        game.draw()
        
        # Draw score, level, and lines cleared
        draw_text(f"Score: {game.score}", font, (0, 255, 0), WIDTH - 100, 50)  # Green
        draw_text(f"Level: {game.level}", font, (0, 0, 255), WIDTH - 100, 100)  # Blue
        draw_text(f"Lines: {game.lines_cleared}", font, (255, 255, 255), WIDTH - 100, 150)
        
        # Draw next block preview
        draw_text("Next:", font, (255, 255, 255), WIDTH - 100, 200)
        if game.next_block:
            for y, row in enumerate(game.next_block.shape):
                for x, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(
                            screen,
                            game.next_block.color,
                            (WIDTH - 150 + x * 30, 250 + y * 30, 30, 30)
                        )
        
        if game.paused:
            draw_pause()
        
        if game.game_over:
            game_over_time = pygame.time.get_ticks()
            state = GAME_OVER
    
    elif state == GAME_OVER:
        game.draw()
        draw_game_over()
    
    pygame.display.flip()
    clock.tick(120)  # 120 FPS for smoother animation