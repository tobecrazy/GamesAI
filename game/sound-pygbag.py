import pygame

class Sound:
    def __init__(self):
        pygame.mixer.init()
        self.rotate_sound = pygame.mixer.Sound("assets/rotate.ogg")
        self.clear_sound = pygame.mixer.Sound("assets/clear.ogg")
        self.drop_sound = pygame.mixer.Sound("assets/drop.ogg")
        self.game_over_sound = pygame.mixer.Sound("assets/gameover.ogg")

        pygame.mixer.music.load("assets/background.ogg")
        pygame.mixer.music.set_volume(0.5)

        # Sound state
        self.muted = False
        self.music_volume = 0.5
        self.effects_volume = 1.0

    def play_rotate(self):
        if not self.muted:
            self.rotate_sound.play()

    def play_clear(self):
        if not self.muted:
            self.clear_sound.play()

    def play_drop(self):
        if not self.muted:
            self.drop_sound.play()

    def play_game_over(self):
        if not self.muted:
            self.game_over_sound.play()

    def start_background_music(self):
        pygame.mixer.music.play(-1)  # -1 means loop indefinitely
        if self.muted:
            pygame.mixer.music.set_volume(0)
        else:
            pygame.mixer.music.set_volume(self.music_volume)

    def stop_background_music(self):
        pygame.mixer.music.stop()

    def toggle_mute(self):
        self.muted = not self.muted
        if self.muted:
            # Store current volume and set to 0
            pygame.mixer.music.set_volume(0)
        else:
            # Restore volume
            pygame.mixer.music.set_volume(self.music_volume)
        return self.muted