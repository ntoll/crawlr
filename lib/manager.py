import pygame
from characters import *

class PartyManager(object):
    """A manager that can add and remove characters to/from the party."""

    def __init__(self, screen):
        self.screen = screen
        self.hero = CharHero(screen)
        self.ando = CharHero(screen, "ando")
        self.all_chars = {
            'hero': self.hero,
            # 'test': CharParty(screen, self.hero), 
            'ando' : self.ando}
        self.chars = {}  #  'name' -> pygame.Sprite, added to PartyManager & initialised
        self.sprites = pygame.sprite.Group()

    def add(self, char):
        """Add a new party character to the party."""

        if not self.all_chars[char] in self.sprites:
            print "Adding %s" % char
            self.chars[char] = self.all_chars[char]
            """
            if not char is "hero":
                self.chars[char].__init__(self.screen, self.hero)
            else:
                self.chars[char].__init__(self.screen)
                self.sprites.add(self.chars[char])
            """
            # Adrian: removed because __init__ already called at CharHero init
            # if char == "hero":
            #     self.chars[char].__init__(self.screen, "hero")
            # elif char == "ando":
            #     self.chars[char].__init__(self.screen, "ando")
            # else:
            #     self.chars[char].__init__(self.screen)
            
            # Adrian: removed because this should be called once only, in Screen init
            ##self.screen.add_sprites()

    def remove(self, char):
        """Remove a character from the party."""

        if self.all_chars[char] in self.sprites:
            self.chars[char].kill()
            del self.chars[char]


class NPCManager(object):
    """A manager that can add and remove characters to/from the party."""

    def __init__(self, screen):
        self.screen = screen
        self.all_chars = {
            'npc': CharNPC(screen) }
        self.chars = {}
        self.sprites = pygame.sprite.Group()

    def add(self, char):
        """Add a new party character to the party."""

        if not self.all_chars[char] in self.sprites:
            self.chars[char] = self.all_chars[char]
            self.chars[char].__init__(self.screen)
            self.sprites.add(self.chars[char])
            ##self.screen.add_sprites()

    def remove(self, char):
        """Remove a character from the party."""

        if self.all_chars[char] in self.sprites:
            self.chars[char].kill()
            del self.chars[char]
