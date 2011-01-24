import pygame
from constants import *
from data import *

class Spritesheet(object):
    """Load a sprite from a spritesheet."""

    def __init__(self, type, subtype, filename):
        self.sheet = load_image(type, subtype, filename)

    def image(self, rect, colorkey=None, alpha=False):
        rect = Rect(rect)
        if alpha:
            image = pygame.Surface(rect.size).convert_alpha()
        else:
            image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0,0), rect)
        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, RLEACCEL)
        return image

    def images(self, rects, colorkey=None):
        imgs = []
        for rect in rects:
            imgs.append(self.image(rect, colorkey))
        return imgs


class BasicSprite(pygame.sprite.DirtySprite):
    """The basic sprite helper for simple sprites."""

    def __init__(self, size):
        pygame.sprite.DirtySprite.__init__(self)
        self.image = pygame.Surface(size, SRCALPHA, 32)
        self.image = self.image.convert_alpha()
        self.rect = self.image.get_rect()


class MapSprite(BasicSprite):
    """A sprite to draw a layer of the map."""

    def __init__(self, w, numx, h, numy):
        size = (w * numx, h * numy)
        BasicSprite.__init__(self, size)


class CharacterSprite(pygame.sprite.DirtySprite):
    """A sprite for moving character sprites."""

    def __init__(self, screen, width, height, direction, stopped,
            start_location, spritesheet, collide_size, collide_offset,
            speed_animate, speed_walk):
        pygame.sprite.DirtySprite.__init__(self)
        self.screen = screen
        self.window = screen.window
        self.map = screen.map
        self.width = width
        self.height = height
        self.direction = direction
        self.stop = stopped
        self.sprite = Spritesheet('char', 'sprites', spritesheet)
        images = {
            'north': [
                (32, 144, CHAR_WIDTH, CHAR_HEIGHT),
                (0, 144, CHAR_WIDTH, CHAR_HEIGHT),
                (32, 144, CHAR_WIDTH, CHAR_HEIGHT),
                (64, 144, CHAR_WIDTH, CHAR_HEIGHT) ],
            'south': [
                (32, 0, CHAR_WIDTH, CHAR_HEIGHT),
                (0, 0, CHAR_WIDTH, CHAR_HEIGHT),
                (32, 0, CHAR_WIDTH, CHAR_HEIGHT),
                (64, 0, CHAR_WIDTH, CHAR_HEIGHT) ],
            'east': [
                (32, 96, CHAR_WIDTH, CHAR_HEIGHT),
                (0, 96, CHAR_WIDTH, CHAR_HEIGHT),
                (32, 96, CHAR_WIDTH, CHAR_HEIGHT),
                (64, 96, CHAR_WIDTH, CHAR_HEIGHT) ],
            'west': [
                (32, 48, CHAR_WIDTH, CHAR_HEIGHT),
                (0, 48, CHAR_WIDTH, CHAR_HEIGHT),
                (32, 48, CHAR_WIDTH, CHAR_HEIGHT),
                (64, 48, CHAR_WIDTH, CHAR_HEIGHT) ] }
        self.walking = {
            'up':       self.sprite.images(images['north'], -1),
            'down':     self.sprite.images(images['south'], -1),
            'right':    self.sprite.images(images['east'], -1),
            'left':     self.sprite.images(images['west'], -1) }
        self.speed_walk = speed_walk
        self.speed_animate = speed_animate
        self.animate_counter = 0
        self.current_space = 0
        self.frame = 0
        self.x = start_location[0]
        self.y = start_location[1]
        print "XY", type(self), self.x, self.y
        self.image = self.walking[self.direction][self.frame]
        self.rect = self.image.get_rect(left=self.x, top=self.y)
        self.rear_rect = self.rect
        self.collide = {}
        self.collide_size = collide_size
        self.collide_offset = collide_offset
        self.collide_surface = pygame.Surface(collide_size)
        self.collide_rect = self.collide_surface.get_rect(
            left=self.rect.left + collide_offset[0],
            bottom=self.rect.bottom + collide_offset[1])

    def draw(self):
        """Cycle move animation frames and redraw at the new location."""

        direction = self.walking[self.direction]
        self.animate_counter = (self.animate_counter + 1) % self.speed_animate
        if self.animate_counter == 0:
            self.frame = (self.frame + 1) % len(direction)
        self.image = direction[self.frame]

    def update(self):
        """Redraw the sprite if it moved."""

        self.movement = self.speed_walk
        if self.direction:
            self.move_check()
            if self.stop:
                self.image = self.walking[self.direction][0]
                self.dirty = 1
            else:
                self.move()
                self.draw()


class PartySprite(CharacterSprite):
    """A sprite for party characters."""

    def __init__(self, screen, hero, char):
        self.hero = hero
        self.face_small = load_image("char", "faces", char + "_small")
        direction = hero.direction
      
        position = (hero.rect[0], hero.rect[1] + 32)
        CharacterSprite.__init__(self, screen, CHAR_WIDTH, CHAR_HEIGHT,
            direction, True, position, char, PLAYER_COLLIDE_SIZE,
            PLAYER_COLLIDE_OFFSET, PLAYER_WALK_ANIMATION_SPEED,
            PLAYER_WALK_SPEED)

    def move_check(self):
        """Check if party character is near the player."""

        if pygame.Rect(self.hero.rear_rect).colliderect(self.rect):
            self.stop = True
        else:
            self.stop = False

    def move(self):
        """Move the party character."""

        self.dirty = 1
        if self.rect[0] > self.hero.rect[0]:
            self.rect.move_ip([-PLAYER_WALK_SPEED, 0])
        elif not self.rect[0] == self.hero.rect[0]:
            self.rect.move_ip([PLAYER_WALK_SPEED, 0])

        if self.rect[1] > self.hero.rect[1]:
            self.rect.move_ip([0, -PLAYER_WALK_SPEED])
        elif not self.rect[1] == self.hero.rect[1]:
            self.rect.move_ip([0, PLAYER_WALK_SPEED])


class NPCSprite(CharacterSprite):
    """A sprite for non-player characters."""

    def __init__(self, screen, char):
        self.face_small = load_image("char", "faces", char + "_small")
        CharacterSprite.__init__(self, screen, CHAR_WIDTH, CHAR_HEIGHT,
            "left", True, (128,128), char, PLAYER_COLLIDE_SIZE,
            PLAYER_COLLIDE_OFFSET, PLAYER_WALK_ANIMATION_SPEED,
            PLAYER_WALK_SPEED)
      
    # 6 methods copied from PlayerSprite
    # The idea is that NPCs with need to move and do things like check if moves are possible
    # with respect to the terrain, walls etc
    
	# copied from PlayerSprite	
    def move(self):
        """Move the NPC."""

        self.dirty = 1
        direction = self.direction
        map_rect = self.map.layers['terrain'].rect

        # If no collision, move the player.
        if not self.collide[direction]:
            if direction == "up":
                if self.rect.centery < PLAYER_SCROLL_TOP and (
                        self.scroll_pos[1] < 0):
                    self.scroll_pos[1] += self.movement
                    self.map.move([0, self.movement])
                else:
                    self.rear_rect = self.rect.move([0, -16])
                    self.rect.move_ip(0, -self.movement)
            elif direction == "down":
                if self.rect.centery > PLAYER_SCROLL_BOTTOM and (
                        map_rect.height + self.scroll_pos[1] > CAMERA_SIZE[1]):
                    self.scroll_pos[1] -= self.movement
                    self.map.move([0, -self.movement])
                else:
                    self.rear_rect = self.rect.move([0, 16])
                    self.rect.move_ip(0, self.movement)
            elif direction == "left":
                if self.rect.centerx < PLAYER_SCROLL_LEFT and (
                        self.scroll_pos[0] < 0):
                    self.scroll_pos[0] += self.movement
                    self.map.move([self.movement, 0])
                else:
                    self.rear_rect = self.rect
                    self.rect.move_ip(-self.movement, 0)
            elif direction == "right":
                if self.rect.centerx > PLAYER_SCROLL_RIGHT and (
                        map_rect.width + self.scroll_pos[0] > CAMERA_SIZE[0]):
                    self.scroll_pos[0] -= self.movement
                    self.map.move([-self.movement, 0])
                else:
                    self.rear_rect = self.rect
                    self.rect.move_ip(self.movement, 0)

            # Move the player's collision rectangle.
            self.collide_rect.left = self.rect.left - self.scroll_pos[0] + (
                self.collide_offset[0])
            self.collide_rect.bottom = self.rect.bottom - self.scroll_pos[1] + (
                self.collide_offset[1])

	# copied from PlayerSprite	
    def move_check(self):
        """Check for walls, terrain, region, and random encounters."""

        directions = {
            'up':       self.collide_rect.move(0, -self.movement),
            'down':     self.collide_rect.move(0, self.movement),
            'left':     self.collide_rect.move(-self.movement, 0),
            'right':    self.collide_rect.move(self.movement, 0) }
        for key, rect in directions.iteritems():
            self.check_walls(key, rect)
            self.check_terrain(rect)
            self.check_region(rect)
        self.check_encounter()

	# copied from PlayerSprite	
    def check_walls(self, key, rect):
        """Check if movement is blocked by a wall."""

        if pygame.Rect(rect).collidelistall(self.map.nowalk) != []:
            self.collide[key] = True
            if self.direction in self.collide and self.collide[self.direction]: 
                self.stop = True
        else: self.collide[key] = False

	# copied from PlayerSprite	
    def check_terrain(self, rect):
        """Check the type of terrain the sprite moved to."""

        for type in self.map.terrain_list:
            for subtype in type:
                if subtype in self.map.types:
                    if pygame.Rect(rect).collidelistall(
                        self.map.types[subtype]) != []:
                        self.current_terrain = type[0]

	# copied from PlayerSprite	
    def check_region(self, rect):
        """Check the region the sprite moved to."""

        for region in self.map.map_regions:
            if pygame.Rect(rect).collidelistall(
                self.map.regions[region]) != []:
                    self.current_region = region

class PlayerSprite(CharacterSprite):
    """The sprite for the character the player controls."""

    def __init__(self, screen, char):
        n = 0
        if char == "hero": n = 0
        elif char == "ando": n = 1
        start_location = [
            (screen.map.start_tile[0] -3 + n) * screen.map.tile_size[0],
            screen.map.start_tile[1] * screen.map.tile_size[1] ]
        direction = screen.map.start_direction
        self.move_keys = []
        self.scroll_pos = [0, 0]
        self.current_terrain = screen.map.map_terrains[0:1]
        self.current_region = screen.map.map_regions[0:1]
     
        self.face_small = load_image("char", "faces", char + "_small")
        CharacterSprite.__init__(self, screen, CHAR_WIDTH, CHAR_HEIGHT,
            direction, True, start_location, char, PLAYER_COLLIDE_SIZE,
            PLAYER_COLLIDE_OFFSET, PLAYER_WALK_ANIMATION_SPEED,
            PLAYER_WALK_SPEED)
    def move(self):
        """Move the player."""

        self.dirty = 1
        direction = self.direction
        map_rect = self.map.layers['terrain'].rect

        # If no collision, move the player.
        if not self.collide[direction]:
            if direction == "up":
                if self.rect.centery < PLAYER_SCROLL_TOP and (
                        self.scroll_pos[1] < 0):
                    self.scroll_pos[1] += self.movement
                    self.map.move([0, self.movement])
                else:
                    self.rear_rect = self.rect.move([0, -16])
                    self.rect.move_ip(0, -self.movement)
            elif direction == "down":
                if self.rect.centery > PLAYER_SCROLL_BOTTOM and (
                        map_rect.height + self.scroll_pos[1] > CAMERA_SIZE[1]):
                    self.scroll_pos[1] -= self.movement
                    self.map.move([0, -self.movement])
                else:
                    self.rear_rect = self.rect.move([0, 16])
                    self.rect.move_ip(0, self.movement)
            elif direction == "left":
                if self.rect.centerx < PLAYER_SCROLL_LEFT and (
                        self.scroll_pos[0] < 0):
                    self.scroll_pos[0] += self.movement
                    self.map.move([self.movement, 0])
                else:
                    self.rear_rect = self.rect
                    self.rect.move_ip(-self.movement, 0)
            elif direction == "right":
                if self.rect.centerx > PLAYER_SCROLL_RIGHT and (
                        map_rect.width + self.scroll_pos[0] > CAMERA_SIZE[0]):
                    self.scroll_pos[0] -= self.movement
                    self.map.move([-self.movement, 0])
                else:
                    self.rear_rect = self.rect
                    self.rect.move_ip(self.movement, 0)

            # Move the player's collision rectangle.
            self.collide_rect.left = self.rect.left - self.scroll_pos[0] + (
                self.collide_offset[0])
            self.collide_rect.bottom = self.rect.bottom - self.scroll_pos[1] + (
                self.collide_offset[1])

    def check_encounter(self):
        """Check for a random encounter."""

        spaces = PLAYER_MOVEMENT_NORMAL
        if self.rect.collidelistall(self.map.danger) != []:
            spaces = PLAYER_MOVEMENT_DANGER
        self.current_space += 1
        if self.current_space == spaces * self.width:
            self.current_space = 0
            if Die(PLAYER_ENCOUNTER_ROLL).roll() == 1:
                pygame.time.set_timer(BATTLE_EVENT, 100)


class PlayerSprite(CharacterSprite):
    """The sprite for the character the player controls."""

    def __init__(self, screen, char):
        start_location = [
            screen.map.start_tile[0] * screen.map.tile_size[0],
            screen.map.start_tile[1] * screen.map.tile_size[1] ]
        direction = screen.map.start_direction
        self.move_keys = []
        self.scroll_pos = [0, 0]
        self.current_terrain = screen.map.map_terrains[0:1]
        self.current_region = screen.map.map_regions[0:1]
        self.face_small = load_image("char", "faces", char + "_small")
        CharacterSprite.__init__(self, screen, CHAR_WIDTH, CHAR_HEIGHT,
            direction, True, start_location, char, PLAYER_COLLIDE_SIZE,
            PLAYER_COLLIDE_OFFSET, PLAYER_WALK_ANIMATION_SPEED,
            PLAYER_WALK_SPEED)

    def move_check(self):
        """Check for walls, terrain, region, and random encounters."""

        directions = {
            'up':       self.collide_rect.move(0, -self.movement),
            'down':     self.collide_rect.move(0, self.movement),
            'left':     self.collide_rect.move(-self.movement, 0),
            'right':    self.collide_rect.move(self.movement, 0) }
        for key, rect in directions.iteritems():
            self.check_walls(key, rect)
            self.check_terrain(rect)
            self.check_region(rect)
        self.check_encounter()

    def check_walls(self, key, rect):
        """Check if movement is blocked by a wall."""

        if pygame.Rect(rect).collidelistall(self.map.nowalk) != []:
            self.collide[key] = True
            if self.collide.get(self.direction): self.stop = True
        else: self.collide[key] = False

    def check_terrain(self, rect):
        """Check the type of terrain the sprite moved to."""

        for type in self.map.terrain_list:
            for subtype in type:
                if subtype in self.map.types:
                    if pygame.Rect(rect).collidelistall(
                        self.map.types[subtype]) != []:
                        self.current_terrain = type[0]

    def check_region(self, rect):
        """Check the region the sprite moved to."""

        for region in self.map.map_regions:
            if pygame.Rect(rect).collidelistall(
                self.map.regions[region]) != []:
                    self.current_region = region

    def move(self):
        """Move the player."""

        self.dirty = 1
        direction = self.direction
        map_rect = self.map.layers['terrain'].rect

        # If no collision, move the player.
        if not self.collide[direction]:
            if direction == "up":
                if self.rect.centery < PLAYER_SCROLL_TOP and (
                        self.scroll_pos[1] < 0):
                    self.scroll_pos[1] += self.movement
                    self.map.move([0, self.movement])
                else:
                    self.rear_rect = self.rect.move([0, -16])
                    self.rect.move_ip(0, -self.movement)
            elif direction == "down":
                if self.rect.centery > PLAYER_SCROLL_BOTTOM and (
                        map_rect.height + self.scroll_pos[1] > CAMERA_SIZE[1]):
                    self.scroll_pos[1] -= self.movement
                    self.map.move([0, -self.movement])
                else:
                    self.rear_rect = self.rect.move([0, 16])
                    self.rect.move_ip(0, self.movement)
            elif direction == "left":
                if self.rect.centerx < PLAYER_SCROLL_LEFT and (
                        self.scroll_pos[0] < 0):
                    self.scroll_pos[0] += self.movement
                    self.map.move([self.movement, 0])
                else:
                    self.rear_rect = self.rect
                    self.rect.move_ip(-self.movement, 0)
            elif direction == "right":
                if self.rect.centerx > PLAYER_SCROLL_RIGHT and (
                        map_rect.width + self.scroll_pos[0] > CAMERA_SIZE[0]):
                    self.scroll_pos[0] -= self.movement
                    self.map.move([-self.movement, 0])
                else:
                    self.rear_rect = self.rect
                    self.rect.move_ip(self.movement, 0)

            # Move the player's collision rectangle.
            self.collide_rect.left = self.rect.left - self.scroll_pos[0] + (
                self.collide_offset[0])
            self.collide_rect.bottom = self.rect.bottom - self.scroll_pos[1] + (
                self.collide_offset[1])

    def check_encounter(self):
        """Check for a random encounter."""

        spaces = PLAYER_MOVEMENT_NORMAL
        if self.rect.collidelistall(self.map.danger) != []:
            spaces = PLAYER_MOVEMENT_DANGER
        self.current_space += 1
        if self.current_space == spaces * self.width:
            self.current_space = 0
            if Die(PLAYER_ENCOUNTER_ROLL).roll() == 1:
                pygame.time.set_timer(BATTLE_EVENT, 100)


class MonsterSprite(CharacterSprite):

    def __init__(self, screen, char):
        pass
