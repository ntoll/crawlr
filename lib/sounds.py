import pygame.mixer

class Sounds(object):
    def __init__(self):
        pass
    
    def setup(self):
        SFX_DIR='data/sounds/sfx/'
        self.BIRD_AMBIENCE = pygame.mixer.Sound(SFX_DIR + 'birdForestAmbience.ogg')
        self.BLOOD = pygame.mixer.Sound(SFX_DIR + 'blood_splat.ogg')
        self.FEAR = pygame.mixer.Sound(SFX_DIR + 'person_screaming_with_fear.ogg')
        self.APPLAUSE = pygame.mixer.Sound(SFX_DIR + 'small_exterior_crowd_applause_with_cheering.ogg')
        self.SWORD = pygame.mixer.Sound(SFX_DIR + 'sword_hits_and_shield_hit.ogg')
        self.BABY = pygame.mixer.Sound(SFX_DIR + 'baby.ogg')
        self.BOOM = pygame.mixer.Sound('data/boom.wav')

    def enable(self):
        pygame.mixer.unpause()

    def disable(self):
        pygame.mixer.pause()

sounds = Sounds()

