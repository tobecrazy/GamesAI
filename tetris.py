import pygame
import sys
import math
from game.game import Game
from game.database import TetrisDatabase

# Initialize Pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris")

# Set up fonts
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)
small_font = pygame.font.Font(None, 24)

# Menu animation variables
menu_animation_time = 0
menu_hover = None

def draw_text(text, font, color, x, y):
    surface = font.render(text, True, color)
    rect = surface.get_rect(center=(x, y))
    screen.blit(surface, rect)

def draw_menu():
    # Draw gradient background
    for y in range(HEIGHT):
        # Create a gradient from dark blue to black
        color_value = max(0, int(40 * (1 - y / HEIGHT)))
        pygame.draw.line(screen, (0, color_value, color_value * 2), (0, y), (WIDTH, y))

    # Calculate animation offset based on time
    global menu_animation_time
    menu_animation_time = (menu_animation_time + 0.5) % 360
    offset = int(5 * math.sin(math.radians(menu_animation_time)))

    # Draw tetris blocks border around title - moved higher
    title_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 6 - 30, 300, 120)
    block_size = 20

    # Draw tetromino-like border
    for i in range(title_rect.width // block_size + 1):
        # Top and bottom borders with different colors
        if i % 4 == 0:
            color = (255, 0, 0)  # Red
        elif i % 4 == 1:
            color = (0, 255, 0)  # Green
        elif i % 4 == 2:
            color = (0, 0, 255)  # Blue
        else:
            color = (255, 255, 0)  # Yellow

        # Top border
        pygame.draw.rect(screen, color,
                        (title_rect.left + i * block_size, title_rect.top, block_size, block_size))
        # Bottom border
        pygame.draw.rect(screen, color,
                        (title_rect.left + i * block_size, title_rect.bottom - block_size, block_size, block_size))

    for i in range(title_rect.height // block_size):
        # Left and right borders with different colors
        if i % 4 == 0:
            color = (255, 0, 255)  # Purple
        elif i % 4 == 1:
            color = (0, 255, 255)  # Cyan
        elif i % 4 == 2:
            color = (255, 165, 0)  # Orange
        else:
            color = (255, 255, 255)  # White

        # Left border
        pygame.draw.rect(screen, color,
                        (title_rect.left, title_rect.top + i * block_size, block_size, block_size))
        # Right border
        pygame.draw.rect(screen, color,
                        (title_rect.right - block_size, title_rect.top + i * block_size, block_size, block_size))

    # Draw title with shadow effect - moved higher
    draw_text("TETRIS", large_font, (30, 30, 30), WIDTH // 2 + 3, HEIGHT // 6 + 3 + offset)  # Shadow
    draw_text("TETRIS", large_font, (0, 255, 0), WIDTH // 2, HEIGHT // 6 + offset)  # Green

    # Draw menu options as buttons
    button_width, button_height = 300, 50
    button_x = WIDTH // 2 - button_width // 2

    # Start button - positioned with more space from title
    start_button = pygame.Rect(button_x, HEIGHT // 3 + 30, button_width, button_height)
    button_color = (0, 100, 200) if menu_hover == "start" else (0, 70, 150)
    pygame.draw.rect(screen, button_color, start_button, border_radius=10)
    pygame.draw.rect(screen, (0, 150, 255), start_button, 3, border_radius=10)
    draw_text("PRESS ENTER TO START", font, (255, 255, 255), WIDTH // 2, HEIGHT // 3 + 30 + button_height // 2 - 5)

    # Quit button
    quit_button = pygame.Rect(button_x, HEIGHT // 3 + 100, button_width, button_height)
    button_color = (200, 50, 50) if menu_hover == "quit" else (150, 30, 30)
    pygame.draw.rect(screen, button_color, quit_button, border_radius=10)
    pygame.draw.rect(screen, (255, 100, 100), quit_button, 3, border_radius=10)
    draw_text("PRESS Q TO QUIT", font, (255, 255, 255), WIDTH // 2, HEIGHT // 3 + 100 + button_height // 2 - 5)

    # Sound button
    sound_button = pygame.Rect(button_x, HEIGHT // 3 + 170, button_width, button_height)
    button_color = (150, 50, 150) if menu_hover == "sound" else (100, 30, 100)
    pygame.draw.rect(screen, button_color, sound_button, border_radius=10)
    pygame.draw.rect(screen, (200, 100, 200), sound_button, 3, border_radius=10)

    # Show mute status
    if game:
        mute_status = "SOUND: OFF (PRESS M)" if is_muted else "SOUND: ON (PRESS M)"
    else:
        mute_status = "PRESS M TO SET SOUND"
    draw_text(mute_status, font, (255, 255, 255), WIDTH // 2, HEIGHT // 3 + 170 + button_height // 2 - 5)

    # Display top scores in a table format
    high_scores = db.get_high_scores(5)  # Get top 5 for the menu
    if high_scores:
        # Calculate panel position to avoid overlap with buttons
        panel_y = HEIGHT // 3 + 240  # Position after the sound button
        panel_height = 180  # Reduced height

        # Draw a semi-transparent panel for scores
        scores_panel = pygame.Surface((WIDTH - 100, panel_height))
        scores_panel.set_alpha(150)
        scores_panel.fill((0, 0, 50))
        screen.blit(scores_panel, (50, panel_y))

        # Draw border for the panel
        pygame.draw.rect(screen, (0, 150, 255), pygame.Rect(50, panel_y, WIDTH - 100, panel_height), 2)

        # Draw header
        draw_text("TOP SCORES", font, (255, 215, 0), WIDTH // 2, panel_y + 20)  # Gold

        # Draw table headers
        draw_text("RANK", small_font, (200, 200, 200), WIDTH // 5, panel_y + 50)
        draw_text("PLAYER", small_font, (200, 200, 200), 2 * WIDTH // 5, panel_y + 50)
        draw_text("SCORE", small_font, (200, 200, 200), 3 * WIDTH // 5, panel_y + 50)
        draw_text("GRADE", small_font, (200, 200, 200), 4 * WIDTH // 5, panel_y + 50)

        # Draw horizontal line under headers
        pygame.draw.line(screen, (100, 100, 100), (70, panel_y + 65), (WIDTH - 70, panel_y + 65), 1)

        for i, (name, score, _, _, grade, _) in enumerate(high_scores[:5]):
            y_pos = panel_y + 90 + i * 25  # Reduced spacing between rows
            rank_color = (255, 215, 0) if i < 3 else (200, 200, 200)  # Gold for top 3

            # Alternate row colors for better readability
            if i % 2 == 0:
                pygame.draw.rect(screen, (0, 0, 80), pygame.Rect(60, y_pos - 12, WIDTH - 120, 25))

            draw_text(f"#{i+1}", small_font, rank_color, WIDTH // 5, y_pos)
            draw_text(name, small_font, (255, 255, 255), 2 * WIDTH // 5, y_pos)
            draw_text(str(score), small_font, (0, 255, 0), 3 * WIDTH // 5, y_pos)
            draw_text(grade, small_font, (255, 215, 0), 4 * WIDTH // 5, y_pos)

    # Draw version info
    draw_text("v1.0.0", small_font, (100, 100, 100), WIDTH - 40, HEIGHT - 20)

def draw_game_over():
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(128)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    draw_text("GAME OVER", large_font, (255, 0, 0), WIDTH // 2, 80)  # Red
    draw_text(f"Score: {game.score}", font, (0, 255, 0), WIDTH // 2, 140)  # Green
    draw_text(f"Level: {game.level}", font, (0, 255, 0), WIDTH // 2, 180)  # Green
    draw_text(f"Grade: {db.calculate_grade(game.score, game.level)}", font, (0, 255, 0), WIDTH // 2, 220)  # Green

    # Show mute status
    mute_status = "Sound: OFF (M)" if is_muted else "Sound: ON (M)"
    draw_text(mute_status, font, (255, 255, 255), WIDTH - 100, 20)

    # Display top 10 scores
    draw_text("TOP SCORES", font, (255, 215, 0), WIDTH // 2, 270)  # Gold
    high_scores = db.get_high_scores(10)
    if not high_scores:
        draw_text("No scores yet!", font, (255, 255, 255), WIDTH // 2, 310)
    else:
        # Display column headers
        draw_text("Player", font, (255, 255, 255), WIDTH // 4, 310)
        draw_text("Score", font, (255, 255, 255), WIDTH // 2, 310)
        draw_text("Grade", font, (255, 255, 255), 3 * WIDTH // 4, 310)

        # Display scores (up to 5 to fit on screen)
        for i, (name, score, _, _, grade, _) in enumerate(high_scores[:5]):
            y_pos = 350 + i * 30
            draw_text(name, font, (255, 255, 255), WIDTH // 4, y_pos)
            draw_text(str(score), font, (0, 255, 0), WIDTH // 2, y_pos)
            draw_text(grade, font, (255, 215, 0), 3 * WIDTH // 4, y_pos)

    # Controls at the bottom
    draw_text("Press R to restart", font, (0, 0, 255), WIDTH // 2, HEIGHT - 140)  # Blue
    draw_text("Press S for scrolling scores", font, (255, 255, 255), WIDTH // 2, HEIGHT - 100)  # White
    draw_text("Press N to enter name", font, (255, 255, 255), WIDTH // 2, HEIGHT - 60)  # White
    draw_text("Press Q to quit", font, (255, 255, 0), WIDTH // 2, HEIGHT - 20)  # Yellow

def draw_pause():
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(128)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    draw_text("PAUSED", large_font, (255, 255, 255), WIDTH // 2, HEIGHT // 2)
    draw_text("Press P or S to resume", font, (255, 255, 255), WIDTH // 2, HEIGHT // 2 + 50)

    # Show mute status
    mute_text = "Sound: OFF (Press M to unmute)" if is_muted else "Sound: ON (Press M to mute)"
    draw_text(mute_text, font, (255, 255, 255), WIDTH // 2, HEIGHT // 2 + 100)

# Create game instance and database
game = None
db = TetrisDatabase()

# Player name input variables
input_text = ""
input_active = False

# Scrolling scores variables
scroll_positions = []
scroll_speed = 1.5  # pixels per frame
scroll_paused = False

# Sound state
is_muted = False

def draw_high_scores():
    screen.fill((0, 0, 0))
    draw_text("HIGH SCORES", large_font, (255, 215, 0), WIDTH // 2, 50)  # Gold

    # Show mute status
    mute_status = "Sound: OFF (M)" if is_muted else "Sound: ON (M)"
    draw_text(mute_status, font, (255, 255, 255), WIDTH - 100, 20)

    high_scores = db.get_high_scores(10)
    if not high_scores:
        draw_text("No scores yet!", font, (255, 255, 255), WIDTH // 2, HEIGHT // 2)
    else:
        draw_text("Player", font, (255, 255, 255), WIDTH // 4, 120)
        draw_text("Score", font, (255, 255, 255), WIDTH // 2, 120)
        draw_text("Grade", font, (255, 255, 255), 3 * WIDTH // 4, 120)

        for i, (name, score, _, _, grade, _) in enumerate(high_scores):
            y_pos = 170 + i * 40
            draw_text(name, font, (255, 255, 255), WIDTH // 4, y_pos)
            draw_text(str(score), font, (0, 255, 0), WIDTH // 2, y_pos)
            draw_text(grade, font, (255, 215, 0), 3 * WIDTH // 4, y_pos)

    draw_text("Press B to go back", font, (255, 255, 255), WIDTH // 2, HEIGHT - 50)

def draw_name_input():
    screen.fill((0, 0, 0))
    draw_text("Enter Your Name:", font, (255, 255, 255), WIDTH // 2, HEIGHT // 3)

    # Show mute status
    mute_status = "Sound: OFF (M)" if is_muted else "Sound: ON (M)"
    draw_text(mute_status, font, (255, 255, 255), WIDTH - 100, 20)

    # Draw input box
    input_box = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 36)
    color = (0, 255, 0) if input_active else (100, 100, 100)
    pygame.draw.rect(screen, color, input_box, 2)

    # Render the input text
    text_surface = font.render(input_text, True, (255, 255, 255))
    screen.blit(text_surface, (input_box.x + 5, input_box.y + 5))

    draw_text("Press ENTER to save", font, (255, 255, 255), WIDTH // 2, HEIGHT // 2 + 100)

def draw_start_name_input():
    screen.fill((0, 0, 0))
    draw_text("TETRIS", large_font, (0, 255, 0), WIDTH // 2, HEIGHT // 4)  # Green
    draw_text("Enter Your Name:", font, (255, 255, 255), WIDTH // 2, HEIGHT // 2 - 50)

    # Show mute status if a game exists
    if game:
        mute_status = "Sound: OFF (M)" if is_muted else "Sound: ON (M)"
        draw_text(mute_status, font, (255, 255, 255), WIDTH - 100, 20)

    # Draw input box
    input_box = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2, 300, 36)
    color = (0, 255, 0) if input_active else (100, 100, 100)
    pygame.draw.rect(screen, color, input_box, 2)

    # Render the input text
    text_surface = font.render(input_text, True, (255, 255, 255))
    screen.blit(text_surface, (input_box.x + 5, input_box.y + 5))

    draw_text("Press ENTER to start game", font, (255, 255, 255), WIDTH // 2, HEIGHT // 2 + 80)
    draw_text("(Leave empty for 'Anonymous')", font, (150, 150, 150), WIDTH // 2, HEIGHT // 2 + 120)

def draw_scrolling_scores():
    screen.fill((0, 0, 0))
    draw_text("TOP PLAYERS", large_font, (255, 215, 0), WIDTH // 2, 50)  # Gold

    # Show mute status
    mute_status = "Sound: OFF (M)" if is_muted else "Sound: ON (M)"
    draw_text(mute_status, font, (255, 255, 255), WIDTH - 100, 20)

    high_scores = db.get_high_scores(10)
    if not high_scores:
        draw_text("No scores yet!", font, (255, 255, 255), WIDTH // 2, HEIGHT // 2)
        draw_text("Press any key to go back", font, (255, 255, 255), WIDTH // 2, HEIGHT - 50)
        return

    # Draw column headers
    header_y = 120
    draw_text("Rank", font, (255, 255, 255), WIDTH // 5, header_y)
    draw_text("Player", font, (255, 255, 255), 2 * WIDTH // 5, header_y)
    draw_text("Score", font, (255, 255, 255), 3 * WIDTH // 5, header_y)
    draw_text("Grade", font, (255, 255, 255), 4 * WIDTH // 5, header_y)

    # Draw scrolling scores
    scroll_area_top = header_y + 40
    scroll_area_bottom = HEIGHT - 80

    # Initialize scroll positions if needed
    if not scroll_positions:
        for i in range(len(high_scores)):
            scroll_positions.append(scroll_area_bottom + i * 60)  # Start below the screen

    # Update scroll positions if not paused
    if not scroll_paused:
        for i in range(len(scroll_positions)):
            scroll_positions[i] -= scroll_speed
            # If a score scrolls off the top, move it to the bottom
            if scroll_positions[i] < scroll_area_top - 60:
                scroll_positions[i] = scroll_area_bottom

    # Draw scores
    for i, ((name, score, _, _, grade, _), y_pos) in enumerate(zip(high_scores, scroll_positions)):
        # Only draw if within visible area
        if scroll_area_top - 30 <= y_pos <= scroll_area_bottom + 30:
            rank_color = (255, 215, 0) if i < 3 else (255, 255, 255)  # Gold for top 3
            draw_text(f"#{i+1}", font, rank_color, WIDTH // 5, y_pos)
            draw_text(name, font, (255, 255, 255), 2 * WIDTH // 5, y_pos)
            draw_text(str(score), font, (0, 255, 0), 3 * WIDTH // 5, y_pos)
            draw_text(grade, font, (255, 215, 0), 4 * WIDTH // 5, y_pos)

    # Draw instructions
    draw_text("Press any key to return", font, (255, 255, 255), WIDTH // 2, HEIGHT - 40)

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2
HIGH_SCORES = 3
NAME_INPUT = 4
START_NAME_INPUT = 5
SCROLLING_SCORES = 6

state = MENU
game_over_time = 0
score_saved = False

# Main game loop
clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if state == MENU:
            # Handle mouse hover for buttons
            if event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                # Start button
                start_button = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 3 + 30, 300, 50)
                if start_button.collidepoint(mouse_pos):
                    menu_hover = "start"
                # Quit button
                elif pygame.Rect(WIDTH // 2 - 150, HEIGHT // 3 + 100, 300, 50).collidepoint(mouse_pos):
                    menu_hover = "quit"
                # Sound button
                elif pygame.Rect(WIDTH // 2 - 150, HEIGHT // 3 + 170, 300, 50).collidepoint(mouse_pos):
                    menu_hover = "sound"
                else:
                    menu_hover = None

            # Handle mouse clicks
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                # Start button
                if pygame.Rect(WIDTH // 2 - 150, HEIGHT // 3 + 30, 300, 50).collidepoint(mouse_pos):
                    input_text = ""
                    input_active = True
                    state = START_NAME_INPUT
                # Quit button
                elif pygame.Rect(WIDTH // 2 - 150, HEIGHT // 3 + 100, 300, 50).collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()
                # Sound button
                elif pygame.Rect(WIDTH // 2 - 150, HEIGHT // 3 + 170, 300, 50).collidepoint(mouse_pos) and game:
                    is_muted = game.toggle_mute()

            # Handle keyboard input
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    input_text = ""
                    input_active = True
                    state = START_NAME_INPUT
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_m and game:
                    is_muted = game.toggle_mute()
        elif state == PLAYING:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    is_muted = game.toggle_mute()
                elif event.key == pygame.K_s:
                    # Add S key as an alternative to pause/resume
                    game.toggle_pause()
                elif event.key == pygame.K_q:
                    game.sound.stop_background_music()
                    game = None
                    state = MENU

            if not game.clearing_animation:
                game.handle_event(event)
        elif state == GAME_OVER:
            if pygame.time.get_ticks() - game_over_time > 1000:  # 1 second delay
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        game = Game(screen, game.player_name)
                        # Apply mute state to new game
                        if is_muted:
                            game.toggle_mute()
                        state = PLAYING
                        score_saved = False
                    elif event.key == pygame.K_q:
                        game = None
                        state = MENU
                        score_saved = False
                    elif event.key == pygame.K_h:
                        state = HIGH_SCORES
                    elif event.key == pygame.K_s:
                        # Reset scroll positions for a fresh start
                        scroll_positions = []
                        scroll_paused = False
                        state = SCROLLING_SCORES
                    elif event.key == pygame.K_n and not score_saved:
                        input_text = ""
                        state = NAME_INPUT

        elif state == HIGH_SCORES:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:
                    if game and game.game_over:
                        state = GAME_OVER
                    else:
                        state = MENU
                elif event.key == pygame.K_m and game:
                    is_muted = game.toggle_mute()

        elif state == NAME_INPUT:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if input_text.strip():
                        game.set_player_name(input_text.strip())
                    game.save_score()
                    score_saved = True
                    state = GAME_OVER
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.key == pygame.K_m and game:
                    is_muted = game.toggle_mute()
                else:
                    # Only add printable characters and limit length
                    if event.unicode.isprintable() and len(input_text) < 15:
                        input_text += event.unicode

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check if the input box is clicked
                input_box = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 36)
                input_active = input_box.collidepoint(event.pos)

        elif state == START_NAME_INPUT:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    player_name = input_text.strip() if input_text.strip() else "Anonymous"
                    game = Game(screen, player_name)
                    # Apply mute state if it was set before game started
                    if is_muted:
                        game.toggle_mute()
                    state = PLAYING
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.key == pygame.K_m and game:
                    is_muted = game.toggle_mute()
                else:
                    # Only add printable characters and limit length
                    if event.unicode.isprintable() and len(input_text) < 15:
                        input_text += event.unicode

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check if the input box is clicked
                input_box = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2, 300, 36)
                input_active = input_box.collidepoint(event.pos)

        elif state == SCROLLING_SCORES:
            # Any key press returns to game over screen
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m and game:
                    is_muted = game.toggle_mute()
                elif game and game.game_over:
                    state = GAME_OVER
                else:
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
        draw_text(f"Lines: {game.lines_cleared}", font, (255, 255, 255), WIDTH - 100, 150)  # White

        # Draw mute status and game status
        mute_status = "M: Sound OFF" if is_muted else "M: Sound ON"
        draw_text(mute_status, font, (255, 255, 255), WIDTH - 100, 200)

        # Draw game status (P/S: Pause)
        game_status = "P/S: Pause" if not game.paused else "P/S: Resume"
        draw_text(game_status, font, (255, 255, 255), WIDTH - 100, 230)

        # Draw next block preview
        draw_text("Next:", font, (255, 255, 255), WIDTH - 100, 280)
        if game.next_block:
            for y, row in enumerate(game.next_block.shape):
                for x, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(
                            screen,
                            game.next_block.color,
                            (WIDTH - 150 + x * 30, 330 + y * 30, 30, 30)
                        )

        if game.paused:
            draw_pause()

        if game.game_over:
            game_over_time = pygame.time.get_ticks()
            state = GAME_OVER

    elif state == GAME_OVER:
        game.draw()
        draw_game_over()

    elif state == HIGH_SCORES:
        draw_high_scores()

    elif state == NAME_INPUT:
        draw_name_input()

    elif state == START_NAME_INPUT:
        draw_start_name_input()

    elif state == SCROLLING_SCORES:
        draw_scrolling_scores()

    pygame.display.flip()
    clock.tick(120)  # 120 FPS for smoother animation