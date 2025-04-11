import pygame

class Sound:
    def __init__(self):
        pygame.mixer.init()
        self.rotate_sound = pygame.mixer.Sound("assets/rotate.mp3")
        self.clear_sound = pygame.mixer.Sound("assets/clear.mp3")
        self.drop_sound = pygame.mixer.Sound("assets/drop.mp3")
        self.game_over_sound = pygame.mixer.Sound("assets/gameover.mp3")
        
        pygame.mixer.music.load("assets/background.mp3")
        pygame.mixer.music.set_volume(0.5)
    
    def play_rotate(self):
        self.rotate_sound.play()
    
    def play_clear(self):
        self.clear_sound.play()
    
    def play_drop(self):
        self.drop_sound.play()
    
    def play_game_over(self):
        self.game_over_sound.play()
    
    def start_background_music(self):
        pygame.mixer.music.play(-1)  # -1 means loop indefinitely
    
    def stop_background_music(self):
        pygame.mixer.music.stop()