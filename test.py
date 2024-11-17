import pygame

def play_sound():
    pygame.mixer.init()
    pygame.mixer.music.load('assets/sound_effect/beep.mp3')
    pygame.mixer.music.play()
