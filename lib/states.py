from os import environ, path
import sys
from screens import *
import pygame
import sounds


if not pygame.mixer:
    print 'Warning, sound disabled'


class BaseState(object):
    """The base state that all other states subclass."""

    def __init__(self, window=None):
        self.music = None
        self.window = window
        self.clock = pygame.time.Clock()
        # sound setup
        if pygame.mixer:
            freq = 44100 # audio CD quality
            bitsize = -16 # unsigned 16 bit
            channels = 2 # 1 is mono, 2 is stereo
            buffer_size = 1024 # number of samples
            # initialise
            pygame.mixer.init(freq, bitsize, channels, buffer_size)
            # set volume from 0 -> 1.0
            pygame.mixer.music.set_volume(0.8)
            self.can_play_music = True
            self.can_play_sfx = True
            sounds.sounds.setup()
        else:
            self.can_play_music = False
            self.can_play_sfx = False


    def run(self):
        """The main game loop that listens for events and draws the screen."""

        while True:
            self.clock.tick(FRAME_RATE)
            self.state.show_debug(int(self.clock.get_fps()))
            self.state.check_events()
            self.state.screen.draw()

    def switch(self, state):
        self.state = state
        self.run()


    def check_base_events(self, event):
        if event.type == KEYDOWN:
            if event.key == K_m:
                self.toggle_music()
            elif event.key == K_s:
                self.toggle_sfx()

    def toggle_music(self):
        self.can_play_music = not self.can_play_music
        if self.can_play_music:
            pygame.mixer.music.play(-1)
            text = Font("menu", 24, (255,0,0), "Music Unmuted")
        else:
            pygame.mixer.music.stop()
            text = Font("menu", 24, (255,0,0), "Music Muted")
        self.screen.display_notification(text, 0)

    def toggle_sfx(self):
        """This doesn't do exactly what we want, it stops currently
        playing sounds but wont disable sfx."""
        self.can_play_sfx = not self.can_play_sfx
        if self.can_play_sfx:
            sounds.sounds.enable()
        else:
            sounds.sounds.disable()


    def show_debug(self, fps):
        """Print debugging info to console."""

        if SHOW_FRAME_RATE:
            print 'Framerate: %f/%f' % (fps, FRAME_RATE)

    def exit(self):
        pygame.quit()
        sys.exit(0)


class InitState(Screen, BaseState):
    """State used to initialize the game and switch to the title screen."""

    def __init__(self):
        environ['SDL_VIDEO_CENTERED'] = '1'
        Screen.__init__(self)
        del environ['SDL_VIDEO_CENTERED']
        BaseState.__init__(self, self.window)
        self.switch(TitleState())


class TitleState(BaseState):
    """A game state for the title screen."""

    def __init__(self, music='DarkMenu.ogg'):
        BaseState.__init__(self)
        self.screen = TitleScreen()
        self.music = path.join('data/sounds/music', music)
        pygame.mixer.music.load(self.music)
        pygame.mixer.music.play(-1)

    def check_events(self):
        """
        Title screen events:
        Esc:    exit game
        N:      new game
        """

        for event in pygame.event.get():
            if event.type == QUIT: self.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE: self.exit()
                elif event.key == K_n:
                    self.screen.destroy()
                    self.switch(WorldState(STARTING_MAP))
            elif event.type == JOYBUTTONDOWN:
                if event.button == JOY_LEFT_TOP:
                    self.exit()
                if event.button == JOY_START:
                    self.screen.destroy()
                    self.switch(WorldState(STARTING_MAP))
            self.check_base_events(event)

class WorldState(BaseState):
    """A game state for the main world screen."""

    def __init__(self, map_name, music='EpicGame.ogg'):
        BaseState.__init__(self)
        if len(sys.argv) > 1:
            filename = sys.argv[1]
        else:
            filename = None
        self.map_name = map_name
        self.screen = WorldScreen(self.map_name, filename)
        self.party = self.screen.party
        self.npcs = self.screen.npcs
        self.player = self.party.chars['hero']
        self.music = path.join('data/sounds/music', music)
        pygame.mixer.music.load(self.music)
        if self.can_play_music: 
            pygame.mixer.music.play(-1)

    def run_npcs(self):
        """
        this currently turns the NPC but to face a random direction
        but does not move it
        """
        import random
        dirs = ['up', 'down', 'left', 'right']
        for char in self.npcs.chars:
            self.npcs.chars[char].direction = random.choice(dirs)


    def check_events(self):
        """Check for user input on the world screen."""

        self.move_keys = self.player.move_keys
        for event in pygame.event.get():
            if event.type == QUIT:
                self.exit()
            # Listen for key presses
            elif event.type == KEYDOWN:
                if event.key == GAME_QUIT: self._exit()

                # press t to make the little man turn!
                elif event.key == K_t:
                    self.run_npcs()

                # Example of showing a dialog window.
                elif event.key == K_d:
                    pygame.time.set_timer(DIALOG_EVENT, 100)

                # Example of adding and removing a test character to the party.
                elif event.key == K_a:
                    self.party.add("test")
                elif event.key == K_z:
                    self.party.remove("test")

                elif event.key == K_s:
                    self.npcs.add("npc")


                # Example of changing the test character's statistics.
                elif event.key == K_s:
                    self.party.chars["test"].hp += 1

                # Move the player
                elif event.key in (
                    HERO_MOVE_DOWN,
                    HERO_MOVE_UP,
                    HERO_MOVE_LEFT,
                    HERO_MOVE_RIGHT):
                        self.player_input(True, pygame.key.name, event.key)

            # Listen for key releases
            elif event.type == KEYUP:

                # Stop moving the player
                if event.key in (
                    HERO_MOVE_DOWN,
                    HERO_MOVE_UP,
                    HERO_MOVE_LEFT,
                    HERO_MOVE_RIGHT):
                        self.player_input(False, pygame.key.name, event.key)

            elif event.type == JOYAXISMOTION and event.value:
                key = None
                if event.axis == JOY_H_AXIS:
                    key = HERO_MOVE_RIGHT if event.value > 0 else HERO_MOVE_LEFT
                elif event.axis == JOY_V_AXIS:
                    key = HERO_MOVE_DOWN if event.value > 0 else HERO_MOVE_UP
                if key:
                    self.player_input(True, pygame.key.name, key)

            elif event.type == JOYAXISMOTION:
                if event.axis in (JOY_H_AXIS, JOY_V_AXIS):
                    self.player_input(False, pygame.key.name, HERO_MOVE_UP)
                    self.player_input(False, pygame.key.name, HERO_MOVE_DOWN)
                    self.player_input(False, pygame.key.name, HERO_MOVE_RIGHT)
                    self.player_input(False, pygame.key.name, HERO_MOVE_LEFT)

            elif event.type == JOYBUTTONDOWN:
                if event.button == JOY_LEFT_TOP: self._exit()

            # Switch to the battle state when a battle event is received
            elif event.type == BATTLE_EVENT:
                self.player.move_keys = []
                self.player.stop = True
                self.switch(BattleState(self))

            # Switch to the dialog state when a dialog event is received
            elif event.type == DIALOG_EVENT:
                self.player.move_keys = []
                self.player.stop = True
                self.switch(DialogState(self))
            self.check_base_events(event)

    def player_input(self, moving, name, key):
        """Controls key input to the player character."""

        if moving:
            self.move_keys.append(name(key))
            for char in self.party.chars:
                self.party.chars[char].direction = self.move_keys[-1]
            self.player.stop = False
        else:
            if len(self.move_keys) > 0:
                if name(key) in self.move_keys:
                    keyid = self.move_keys.index(name(key))
                    del self.move_keys[keyid]
                if len(self.move_keys) != 0:
                    for char in self.party.chars:
                        self.party.chars[char].direction = self.move_keys[-1]
                else: self.player.stop = True

    def show_debug(self, fps):
        BaseState.show_debug(self, fps)
        if SHOW_RECTS:
            terrain = self.screen.map.layers['terrain']
            terrain.image.fill((0,0,0), self.player.collide_rect)
            for rect in (self.screen.map.nowalk):
                terrain.image.fill((255,255,255), rect)
        if SHOW_TERRAIN:
            print "Current terrain: %s" % self.player.current_terrain
        if SHOW_REGION:
            print "Current region: %s" % self.player.current_region

    def destroy(self):
        """Cleanup before exiting this state."""

        self.party = None
        self.player = None
        self.screen.destroy()

    def _exit(self):
        """Quit the main game screen returning to the title screen."""

        self.destroy()
        self.switch(TitleState())


class BattleState(BaseState):
    """A game state for a battle scene."""

    def __init__(self, prevstate):
        BaseState.__init__(self)
        self.screen = BattleScreen(prevstate.screen)
        self.prevstate = prevstate
        self.prev_screen = self.prevstate.screen.all_sprites

    def check_events(self):
        """Title screen events"""

        for event in pygame.event.get():
            if event.type == QUIT: self.exit()
            elif event.type == KEYDOWN:
                if event.key == GAME_QUIT: self._exit()
            elif event.type == JOYBUTTONDOWN:
                if event.button == JOY_LEFT_TOP:
                    self._exit()
            self.check_base_events(event)

    def _exit(self):
        """Quits the battle screen returning to the world screen."""

        pygame.time.set_timer(BATTLE_EVENT, 0)
        for sprite in self.prev_screen:
            sprite.dirty = 1
        self.screen.destroy()
        self.switch(self.prevstate)


class DialogState(BaseState):
    """A game state for a battle scene."""

    def __init__(self, prevstate):
        BaseState.__init__(self)
        self.prevstate = prevstate
        self.screen = prevstate.screen
        self.dialog = DialogWindow(self.screen.dialog_text)
        self.screen.layers.add(self.dialog)
        for sprite in self.screen.all_sprites:
            sprite.dirty = 1

    def check_events(self):
        """Title screen events"""

        for event in pygame.event.get():
            if event.type == QUIT: self.exit()
            elif event.type == KEYDOWN:
                if event.key == DIALOG_CLOSE: self._exit()
                elif event.key == DIALOG_SCROLL_UP:
                    self.dialog.text.scroll("up")
                elif event.key == DIALOG_SCROLL_DOWN:
                    self.dialog.text.scroll("down")
            self.check_base_events(event)

    def _exit(self):
        """Quits the battle screen returning to the world screen."""

        pygame.time.set_timer(DIALOG_EVENT, 0)
        self.dialog.destroy()
        self.switch(self.prevstate)
