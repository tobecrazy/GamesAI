import pygame
import sys
import math
import asyncio # Added for Pygbag

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

# --- Global variables that were previously inside the main loop or module level ---
# These will be managed within main_async or passed as parameters.
# For now, ensure they are accessible or re-initialized in main_async.

# Menu animation variables
menu_animation_time = 0
menu_hover = None

# Game instance and database
game = None
db = TetrisDatabase() # This might need to be web-friendly later

# Player name input variables
input_text = ""
input_active = False

# Scrolling scores variables
scroll_positions = []
scroll_speed = 1.5  # pixels per frame
scroll_paused = False

# Sound state
is_muted = False # This should ideally be part of the game object or sound manager

# Status message variables
status_message = ""
status_message_timer = 0
FPS = 120 # Define FPS for timer

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2
HIGH_SCORES = 3
NAME_INPUT = 4
START_NAME_INPUT = 5
SCROLLING_SCORES = 6

current_state = MENU # Renamed from 'state' to avoid conflict if 'state' is used elsewhere
game_over_time = 0
score_saved = False
# --- End of global-like variables ---

def draw_text(text, font_obj, color, x, y): # font_obj to avoid conflict with global font
    surface = font_obj.render(text, True, color)
    rect = surface.get_rect(center=(x, y))
    screen.blit(surface, rect)

async def main_async():
    global screen, font, large_font, small_font # Make sure these are accessible
    global menu_animation_time, menu_hover
    global game, db, input_text, input_active, scroll_positions, scroll_speed, scroll_paused
    global is_muted, status_message, status_message_timer, current_state, game_over_time, score_saved
    global FPS # ensure FPS is accessible

    # Re-initialize or ensure db is web-compatible (covered in a later step)
    # For now, db is initialized globally.

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # --- Event Handling Logic (copied and adapted from original main loop) ---
            if current_state == MENU:
                if event.type == pygame.MOUSEMOTION:
                    mouse_pos = pygame.mouse.get_pos()
                    start_button_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 3 + 30, 300, 50)
                    quit_button_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 3 + 100, 300, 50)
                    sound_button_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 3 + 170, 300, 50)
                    if start_button_rect.collidepoint(mouse_pos):
                        menu_hover = "start"
                    elif quit_button_rect.collidepoint(mouse_pos):
                        menu_hover = "quit"
                    elif sound_button_rect.collidepoint(mouse_pos):
                        menu_hover = "sound"
                    else:
                        menu_hover = None

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    start_button_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 3 + 30, 300, 50)
                    quit_button_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 3 + 100, 300, 50)
                    sound_button_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 3 + 170, 300, 50)
                    if start_button_rect.collidepoint(mouse_pos):
                        input_text = ""
                        input_active = True
                        current_state = START_NAME_INPUT
                    elif quit_button_rect.collidepoint(mouse_pos):
                        running = False
                    elif sound_button_rect.collidepoint(mouse_pos):
                        if game: # Ensure game exists before toggling mute
                           is_muted = game.toggle_mute()
                        # else: # Handle case where game is None - perhaps global mute for menu?
                        # For now, only toggle if game exists. Sound in menu might need specific handling.


                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        input_text = ""
                        input_active = True
                        current_state = START_NAME_INPUT
                    elif event.key == pygame.K_q:
                        running = False
                    elif event.key == pygame.K_m:
                        if game: # Ensure game exists
                            is_muted = game.toggle_mute()
                        # else: # Potentially a global mute for menu sounds if any were present
                            # is_muted = not is_muted # Placeholder for global mute logic
                            # print(f"Menu mute toggled: {is_muted}")


            elif current_state == PLAYING:
                if game: # Ensure game object exists
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_m:
                            is_muted = game.toggle_mute()
                        elif event.key == pygame.K_s:
                            if game.save_state():
                                status_message = "Game saved!"
                                status_message_timer = FPS * 2
                            else:
                                status_message = "Error saving game."
                                status_message_timer = FPS * 2
                        elif event.key == pygame.K_l:
                            if game.load_state():
                                status_message = "Game loaded!"
                                status_message_timer = FPS * 2
                            else:
                                status_message = "No saved game found or error loading."
                                status_message_timer = FPS * 2
                        elif event.key == pygame.K_p:
                            game.toggle_pause()
                        elif event.key == pygame.K_q:
                            game.sound.stop_background_music()
                            game = None # Properly end the game session
                            current_state = MENU


                    if not game.clearing_animation: # game might have become None
                        game.handle_event(event)

            elif current_state == GAME_OVER:
                if game and pygame.time.get_ticks() - game_over_time > 1000:  # 1 second delay
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            # Use player_name from the previous game if available
                            player_name_to_restart = game.player_name if game else "Anonymous"
                            game = Game(screen, player_name_to_restart, db_instance=db)
                            if is_muted: # Apply global mute state to new game
                                game.toggle_mute() # it will mute if is_muted is True
                            current_state = PLAYING
                            score_saved = False
                        elif event.key == pygame.K_q:
                            game = None
                            current_state = MENU
                            score_saved = False
                        elif event.key == pygame.K_h: # Show high scores
                            current_state = HIGH_SCORES
                        elif event.key == pygame.K_s: # Show scrolling scores
                            scroll_positions = []
                            scroll_paused = False
                            current_state = SCROLLING_SCORES
                        elif event.key == pygame.K_n and not score_saved:
                            input_text = ""
                            input_active = True # Activate input for name
                            current_state = NAME_INPUT

            elif current_state == HIGH_SCORES:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_b: # Back
                        if game and game.game_over:
                            current_state = GAME_OVER
                        else:
                            current_state = MENU
                    elif event.key == pygame.K_m:
                        if game: is_muted = game.toggle_mute()
                        # else: global mute logic for this screen if needed

            elif current_state == NAME_INPUT: # Post-game name input
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if game: # Ensure game context exists
                            player_name_to_save = input_text.strip() if input_text.strip() else "Anonymous"
                            game.set_player_name(player_name_to_save)
                            game.save_score()
                            score_saved = True
                        current_state = GAME_OVER
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    elif event.key == pygame.K_m:
                         if game: is_muted = game.toggle_mute()
                    elif event.unicode.isprintable() and len(input_text) < 15:
                        input_text += event.unicode

                if event.type == pygame.MOUSEBUTTONDOWN:
                    input_box_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 36)
                    if input_box_rect.collidepoint(event.pos):
                        input_active = True
                    else:
                        input_active = False


            elif current_state == START_NAME_INPUT: # Pre-game name input
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        player_name = input_text.strip() if input_text.strip() else "Anonymous"
                        game = Game(screen, player_name, db_instance=db)
                        if is_muted: # Apply global mute state if set before game started
                            game.toggle_mute() # it will mute if is_muted is True
                        current_state = PLAYING
                        input_active = False # Deactivate input box
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    # Mute toggle for this screen could be added if sounds play here
                    # elif event.key == pygame.K_m: ...
                    elif event.unicode.isprintable() and len(input_text) < 15:
                        input_text += event.unicode

                if event.type == pygame.MOUSEBUTTONDOWN:
                    input_box_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2, 300, 36)
                    if input_box_rect.collidepoint(event.pos):
                        input_active = True
                    else:
                        input_active = False

            elif current_state == SCROLLING_SCORES:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:
                        if game: is_muted = game.toggle_mute()
                        # else: global mute for this screen
                    # Any other key returns
                    elif game and game.game_over:
                        current_state = GAME_OVER
                    else:
                        current_state = MENU
            # --- End of Event Handling Logic ---

        screen.fill((0, 0, 0))  # Black background

        # --- Drawing Logic (based on current_state) ---
        if current_state == MENU:
            # draw_menu() needs access to global 'game', 'db', 'is_muted', 'menu_hover', 'WIDTH', 'HEIGHT', 'screen', 'font', 'large_font', 'small_font'
            # Make sure these are correctly scoped or passed to draw_menu
            # For simplicity of this step, we assume they are accessible via 'global' or direct use.
            # Proper refactoring would pass them as arguments.

            # Draw gradient background
            for y_grad in range(HEIGHT):
                color_value = max(0, int(40 * (1 - y_grad / HEIGHT)))
                pygame.draw.line(screen, (0, color_value, color_value * 2), (0, y_grad), (WIDTH, y_grad))

            global menu_animation_time # Modifying global
            menu_animation_time = (menu_animation_time + 0.5) % 360
            offset = int(5 * math.sin(math.radians(menu_animation_time)))

            title_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 6 - 30, 300, 120)
            block_size = 20
            for i in range(title_rect.width // block_size + 1):
                c = [(255,0,0), (0,255,0), (0,0,255), (255,255,0)][i%4]
                pygame.draw.rect(screen, c, (title_rect.left + i * block_size, title_rect.top, block_size, block_size))
                pygame.draw.rect(screen, c, (title_rect.left + i * block_size, title_rect.bottom - block_size, block_size, block_size))
            for i in range(title_rect.height // block_size):
                c = [(255,0,255), (0,255,255), (255,165,0), (255,255,255)][i%4]
                pygame.draw.rect(screen, c, (title_rect.left, title_rect.top + i * block_size, block_size, block_size))
                pygame.draw.rect(screen, c, (title_rect.right - block_size, title_rect.top + i * block_size, block_size, block_size))

            draw_text("TETRIS", large_font, (30,30,30), WIDTH // 2 + 3, HEIGHT // 6 + 3 + offset)
            draw_text("TETRIS", large_font, (0,255,0), WIDTH // 2, HEIGHT // 6 + offset)

            button_width, button_height = 300, 50
            button_x = WIDTH // 2 - button_width // 2

            start_button_rect = pygame.Rect(button_x, HEIGHT // 3 + 30, button_width, button_height)
            btn_color = (0,100,200) if menu_hover == "start" else (0,70,150)
            pygame.draw.rect(screen, btn_color, start_button_rect, border_radius=10)
            pygame.draw.rect(screen, (0,150,255), start_button_rect, 3, border_radius=10)
            draw_text("PRESS ENTER TO START", font, (255,255,255), WIDTH // 2, HEIGHT // 3 + 30 + button_height // 2 - 5)

            quit_button_rect = pygame.Rect(button_x, HEIGHT // 3 + 100, button_width, button_height)
            btn_color = (200,50,50) if menu_hover == "quit" else (150,30,30)
            pygame.draw.rect(screen, btn_color, quit_button_rect, border_radius=10)
            pygame.draw.rect(screen, (255,100,100), quit_button_rect, 3, border_radius=10)
            draw_text("PRESS Q TO QUIT", font, (255,255,255), WIDTH // 2, HEIGHT // 3 + 100 + button_height // 2 - 5)

            sound_button_rect = pygame.Rect(button_x, HEIGHT // 3 + 170, button_width, button_height)
            btn_color = (150,50,150) if menu_hover == "sound" else (100,30,100)
            pygame.draw.rect(screen, btn_color, sound_button_rect, border_radius=10)
            pygame.draw.rect(screen, (200,100,200), sound_button_rect, 3, border_radius=10)

            mute_text_menu = "SOUND: OFF (PRESS M)" if is_muted else "SOUND: ON (PRESS M)"
            if game: # if game object exists, use its mute state
                 mute_text_menu = "SOUND: OFF (PRESS M)" if game.sound.is_muted else "SOUND: ON (PRESS M)"
            draw_text(mute_text_menu, font, (255,255,255), WIDTH // 2, HEIGHT // 3 + 170 + button_height // 2 - 5)

            high_scores_list = db.get_high_scores(5)
            if high_scores_list:
                panel_y = HEIGHT // 3 + 240
                panel_height = 180
                scores_panel = pygame.Surface((WIDTH - 100, panel_height)); scores_panel.set_alpha(150); scores_panel.fill((0,0,50))
                screen.blit(scores_panel, (50, panel_y))
                pygame.draw.rect(screen, (0,150,255), pygame.Rect(50, panel_y, WIDTH - 100, panel_height), 2)
                draw_text("TOP SCORES", font, (255,215,0), WIDTH // 2, panel_y + 20)
                draw_text("RANK", small_font, (200,200,200), WIDTH//5, panel_y + 50)
                draw_text("PLAYER", small_font, (200,200,200), 2*WIDTH//5, panel_y + 50)
                draw_text("SCORE", small_font, (200,200,200), 3*WIDTH//5, panel_y + 50)
                draw_text("GRADE", small_font, (200,200,200), 4*WIDTH//5, panel_y + 50)
                pygame.draw.line(screen, (100,100,100), (70, panel_y + 65), (WIDTH - 70, panel_y + 65), 1)
                for i, (name, score, _, _, grade, _) in enumerate(high_scores_list[:5]):
                    y_pos = panel_y + 90 + i * 25
                    if i % 2 == 0: pygame.draw.rect(screen, (0,0,80), pygame.Rect(60, y_pos - 12, WIDTH - 120, 25))
                    draw_text(f"#{i+1}", small_font, (255,215,0) if i < 3 else (200,200,200), WIDTH//5, y_pos)
                    draw_text(name, small_font, (255,255,255), 2*WIDTH//5, y_pos)
                    draw_text(str(score), small_font, (0,255,0), 3*WIDTH//5, y_pos)
                    draw_text(grade, small_font, (255,215,0), 4*WIDTH//5, y_pos)
            draw_text("v1.0.0", small_font, (100,100,100), WIDTH - 40, HEIGHT - 20)

        elif current_state == PLAYING:
            if game: # Ensure game exists
                game.update()
                game.draw()

                draw_text(f"Score: {game.score}", font, (0,255,0), WIDTH - 100, 50)
                draw_text(f"Level: {game.level}", font, (0,0,255), WIDTH - 100, 100)
                draw_text(f"Lines: {game.lines_cleared}", font, (255,255,255), WIDTH - 100, 150)

                game_is_muted = game.sound.is_muted # Get mute state from game instance
                mute_text_playing = "M: Sound OFF" if game_is_muted else "M: Sound ON"
                draw_text(mute_text_playing, font, (255,255,255), WIDTH - 100, 200)

                game_status_text = "P: Pause" if not game.paused else "P: Resume"
                draw_text(game_status_text, font, (255,255,255), WIDTH - 100, 230)

                draw_text("S: Save", font, (255,255,255), WIDTH - 100, HEIGHT - 80)
                draw_text("L: Load", font, (255,255,255), WIDTH - 100, HEIGHT - 50)

                draw_text("Next:", font, (255,255,255), WIDTH - 100, 280)
                if game.next_block:
                    for y_nb, row_nb in enumerate(game.next_block.shape):
                        for x_nb, cell_nb in enumerate(row_nb):
                            if cell_nb:
                                pygame.draw.rect(screen, game.next_block.color,
                                                 (WIDTH - 150 + x_nb * 30, 330 + y_nb * 30, 30, 30))

                if status_message_timer > 0:
                    draw_text(status_message, font, (255,255,0), WIDTH // 2, 30)
                    status_message_timer -= 1
                else:
                    status_message = ""

                if game.paused:
                    # draw_pause()
                    overlay = pygame.Surface((WIDTH, HEIGHT)); overlay.set_alpha(128); overlay.fill((0,0,0))
                    screen.blit(overlay, (0,0))
                    draw_text("PAUSED", large_font, (255,255,255), WIDTH // 2, HEIGHT // 2)
                    draw_text("Press P or S to resume", font, (255,255,255), WIDTH // 2, HEIGHT // 2 + 50) # S for resume might be confusing with S for Save
                    game_is_muted_pause = game.sound.is_muted
                    mute_text_pause = "Sound: OFF (Press M to unmute)" if game_is_muted_pause else "Sound: ON (Press M to mute)"
                    draw_text(mute_text_pause, font, (255,255,255), WIDTH // 2, HEIGHT // 2 + 100)


                if game.game_over:
                    game_over_time = pygame.time.get_ticks()
                    current_state = GAME_OVER
            else: # Should not happen if state is PLAYING, but as a fallback:
                current_state = MENU


        elif current_state == GAME_OVER:
            if game: game.draw() # Draw final board state
            # draw_game_over()
            overlay = pygame.Surface((WIDTH, HEIGHT)); overlay.set_alpha(128); overlay.fill((0,0,0))
            screen.blit(overlay, (0,0))
            draw_text("GAME OVER", large_font, (255,0,0), WIDTH // 2, 80)
            if game: # Check if game instance exists
                draw_text(f"Score: {game.score}", font, (0,255,0), WIDTH // 2, 140)
                draw_text(f"Level: {game.level}", font, (0,255,0), WIDTH // 2, 180)
                draw_text(f"Grade: {db.calculate_grade(game.score, game.level)}", font, (0,255,0), WIDTH // 2, 220)
                game_is_muted_go = game.sound.is_muted
                mute_text_go = "Sound: OFF (M)" if game_is_muted_go else "Sound: ON (M)"
                draw_text(mute_text_go, font, (255,255,255), WIDTH - 100, 20)


            high_scores_list_go = db.get_high_scores(10)
            draw_text("TOP SCORES", font, (255,215,0), WIDTH // 2, 270)
            if not high_scores_list_go:
                draw_text("No scores yet!", font, (255,255,255), WIDTH // 2, 310)
            else:
                draw_text("Player", font, (255,255,255), WIDTH // 4, 310)
                draw_text("Score", font, (255,255,255), WIDTH // 2, 310)
                draw_text("Grade", font, (255,255,255), 3 * WIDTH // 4, 310)
                for i, (name, score, _, _, grade, _) in enumerate(high_scores_list_go[:5]):
                    y_pos = 350 + i * 30
                    draw_text(name, font, (255,255,255), WIDTH // 4, y_pos)
                    draw_text(str(score), font, (0,255,0), WIDTH // 2, y_pos)
                    draw_text(grade, font, (255,215,0), 3*WIDTH//4, y_pos)

            draw_text("R: Restart", font, (0,0,255), WIDTH // 2, HEIGHT - 140) # Made more concise
            draw_text("S: Scrolling Scores", font, (255,255,255), WIDTH // 2, HEIGHT - 100) # Made more concise
            draw_text("N: Enter Name", font, (255,255,255), WIDTH // 2, HEIGHT - 60) # Made more concise
            draw_text("Q: Quit to Menu", font, (255,255,0), WIDTH // 2, HEIGHT - 20) # Made more concise


        elif current_state == HIGH_SCORES:
            # draw_high_scores()
            screen.fill((0,0,0))
            draw_text("HIGH SCORES", large_font, (255,215,0), WIDTH // 2, 50)

            # Mute status - needs consistent handling (global or game instance)
            current_game_is_muted = False # Default if no game
            if game: current_game_is_muted = game.sound.is_muted
            elif is_muted: current_game_is_muted = is_muted # Fallback to global if no game
            mute_text_hs = "Sound: OFF (M)" if current_game_is_muted else "Sound: ON (M)"
            draw_text(mute_text_hs, font, (255,255,255), WIDTH - 100, 20)

            high_scores_list_hs = db.get_high_scores(10)
            if not high_scores_list_hs:
                draw_text("No scores yet!", font, (255,255,255), WIDTH // 2, HEIGHT // 2)
            else:
                draw_text("Player", font, (255,255,255), WIDTH // 4, 120)
                draw_text("Score", font, (255,255,255), WIDTH // 2, 120)
                draw_text("Grade", font, (255,255,255), 3 * WIDTH // 4, 120)
                for i, (name, score, _, _, grade, _) in enumerate(high_scores_list_hs):
                    y_pos = 170 + i * 40
                    draw_text(name, font, (255,255,255), WIDTH // 4, y_pos)
                    draw_text(str(score), font, (0,255,0), WIDTH // 2, y_pos)
                    draw_text(grade, font, (255,215,0), 3*WIDTH//4, y_pos)
            draw_text("Press B to go back", font, (255,255,255), WIDTH // 2, HEIGHT - 50)

        elif current_state == NAME_INPUT:
            # draw_name_input()
            screen.fill((0,0,0))
            draw_text("Enter Your Name:", font, (255,255,255), WIDTH // 2, HEIGHT // 3)

            current_game_is_muted_ni = False # Default if no game
            if game: current_game_is_muted_ni = game.sound.is_muted
            elif is_muted: current_game_is_muted_ni = is_muted
            mute_text_ni = "Sound: OFF (M)" if current_game_is_muted_ni else "Sound: ON (M)"
            draw_text(mute_text_ni, font, (255,255,255), WIDTH - 100, 20)

            input_box_rect_ni = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 36)
            color_ni = (0,255,0) if input_active else (100,100,100)
            pygame.draw.rect(screen, color_ni, input_box_rect_ni, 2)
            text_surface_ni = font.render(input_text, True, (255,255,255))
            screen.blit(text_surface_ni, (input_box_rect_ni.x + 5, input_box_rect_ni.y + 5))
            draw_text("Press ENTER to save", font, (255,255,255), WIDTH // 2, HEIGHT // 2 + 100)

        elif current_state == START_NAME_INPUT:
            # draw_start_name_input()
            screen.fill((0,0,0))
            draw_text("TETRIS", large_font, (0,255,0), WIDTH // 2, HEIGHT // 4)
            draw_text("Enter Your Name:", font, (255,255,255), WIDTH // 2, HEIGHT // 2 - 50)

            # Mute status only if game object exists or based on global is_muted
            current_game_is_muted_sni = is_muted # Use global for pre-game mute
            if game : current_game_is_muted_sni = game.sound.is_muted # Should not happen here though
            mute_text_sni = "Sound: OFF (M)" if current_game_is_muted_sni else "Sound: ON (M)"
            # draw_text(mute_text_sni, font, (255,255,255), WIDTH - 100, 20) # Decided not to show mute here as game not started

            input_box_rect_sni = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2, 300, 36)
            color_sni = (0,255,0) if input_active else (100,100,100)
            pygame.draw.rect(screen, color_sni, input_box_rect_sni, 2)
            text_surface_sni = font.render(input_text, True, (255,255,255))
            screen.blit(text_surface_sni, (input_box_rect_sni.x + 5, input_box_rect_sni.y + 5))
            draw_text("Press ENTER to start game", font, (255,255,255), WIDTH // 2, HEIGHT // 2 + 80)
            draw_text("(Leave empty for 'Anonymous')", small_font, (150,150,150), WIDTH // 2, HEIGHT // 2 + 120)

        elif current_state == SCROLLING_SCORES:
            # draw_scrolling_scores()
            screen.fill((0,0,0))
            draw_text("TOP PLAYERS", large_font, (255,215,0), WIDTH // 2, 50)

            current_game_is_muted_ss = False
            if game: current_game_is_muted_ss = game.sound.is_muted
            elif is_muted: current_game_is_muted_ss = is_muted
            mute_text_ss = "Sound: OFF (M)" if current_game_is_muted_ss else "Sound: ON (M)"
            draw_text(mute_text_ss, font, (255,255,255), WIDTH - 100, 20)

            high_scores_list_ss = db.get_high_scores(10)
            if not high_scores_list_ss:
                draw_text("No scores yet!", font, (255,255,255), WIDTH // 2, HEIGHT // 2)
                draw_text("Press any key to go back", font, (255,255,255), WIDTH // 2, HEIGHT - 50)
            else:
                header_y = 120
                draw_text("Rank", font, (255,255,255), WIDTH//5, header_y)
                draw_text("Player", font, (255,255,255), 2*WIDTH//5, header_y)
                draw_text("Score", font, (255,255,255), 3*WIDTH//5, header_y)
                draw_text("Grade", font, (255,255,255), 4*WIDTH//5, header_y)

                scroll_area_top = header_y + 40
                scroll_area_bottom = HEIGHT - 80

                global scroll_positions, scroll_paused, scroll_speed # Modifying globals
                if not scroll_positions: # Initialize if empty
                    for i in range(len(high_scores_list_ss)):
                        scroll_positions.append(scroll_area_bottom + i * 60)

                if not scroll_paused:
                    for i in range(len(scroll_positions)):
                        scroll_positions[i] -= scroll_speed
                        if scroll_positions[i] < scroll_area_top - 60: # Reset if scrolled off top
                            scroll_positions[i] = scroll_area_bottom + (scroll_positions[i] - (scroll_area_top - 60))


                for i, ((name, score, _, _, grade, _), y_pos) in enumerate(zip(high_scores_list_ss, scroll_positions)):
                    if scroll_area_top - 30 <= y_pos <= scroll_area_bottom + 30:
                        rank_color = (255,215,0) if i < 3 else (255,255,255)
                        draw_text(f"#{i+1}", font, rank_color, WIDTH//5, y_pos)
                        draw_text(name, font, (255,255,255), 2*WIDTH//5, y_pos)
                        draw_text(str(score), font, (0,255,0), 3*WIDTH//5, y_pos)
                        draw_text(grade, font, (255,215,0), 4*WIDTH//5, y_pos)
                draw_text("Press any key to return", font, (255,255,255), WIDTH // 2, HEIGHT - 40)

        # --- End of Drawing Logic ---

        pygame.display.flip()
        await asyncio.sleep(0)  # Yield control to the browser
        clock.tick(FPS) # Maintain FPS

    pygame.quit()
    # sys.exit() is not needed as the function will naturally exit

if __name__ == '__main__':
    # This is the standard way to run asyncio programs.
    # Pygbag might have its own way to call this, often by just running the script
    # or by calling a specific function (like 'main').
    # For now, this structure is a common pattern.
    asyncio.run(main_async())
