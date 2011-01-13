import pygame
from random import choice
from constants import *
from data import load_map
from sprite import *
from terrain import *

class Map(object):
    """The game world."""

    def __init__(self, level):
        self.nowalk = []
        self.danger = []
        self.types = {}
        self.regions = {}
        self.position = {}
        self.tile_dict = {}
        self.terrain = {
            TERRAIN_GRASS[0]:   TerrainGrass(0),
            TERRAIN_GRASS[1]:   TerrainGrass(1),
            TERRAIN_GRASS[2]:   TerrainGrass(2),
            TERRAIN_FOREST[0]:  TerrainForest(0) }
        self.layer_list = []
        self.layers = {}
        self.config = load_map(level)
        self.create_map()

    def configure(self):
        """Reads and stores keys from the map config."""

        self.config_options = self.config['Options']
        self.config_tiles = self.config['Tiles']
        self.config_monsters = self.config['Monsters']
        tile_set = self.config_options['tile_set']
        self.map_objects = {}
        if tile_set == 'world':
            self.terrain_list = TERRAIN_ALL_WORLD
            self.map_objects['g'] = self.config_tiles['objects_grass']
            self.map_objects['f'] = self.config_tiles['objects_forest']
        self.start_tile = [
            int(self.config_options['start_tile'][0]),
            int(self.config_options['start_tile'][1]) ]
        self.tile_size = [
            int(self.config_options['tile_size'][0]),
            int(self.config_options['tile_size'][1]) ]
        self.num_tiles = [
            int(self.config_options['num_tiles'][0]),
            int(self.config_options['num_tiles'][1]) ]
        self.start_direction = self.config_options['start_direction']
        self.map_regions = self.config_tiles['regions']
        self.map_terrains = self.config_tiles['terrains']
        self.region_monsters = {}
        for i in set(self.map_regions):
            self.region_monsters[i] = self.config_monsters[i]

    def create_map(self):
        """Reads and creates the map from the config."""

        self.configure()
        self.create_layers()
        self.draw_map()

    def create_layers(self):
        """Create the map's layers."""

        # Create the map's layer sprites, 'terrain' and 'foreground'.
        self.layers['terrain'] = MapSprite(self.tile_size[0],
            self.num_tiles[0], self.tile_size[1], self.num_tiles[1])
        self.layers['foreground'] = MapSprite(self.tile_size[0],
            self.num_tiles[0], self.tile_size[1], self.num_tiles[1])

        # Generate each layer and their tiles.
        temp_layer = []
        line = ""
        for layer in range(0, LAYERS_NUM):
            row_num = 0
            tile_num = 0
            for row in range(0, self.num_tiles[1]):
                for tile in range(0, self.num_tiles[0]):

                    # Add the 'X' tile to the edges to block the player from
                    # walking off of the map."
                    if layer == LAYER_DATA and (
                        row == 0 or row == self.num_tiles[1] - 1 or (
                        tile == 0 or tile == self.num_tiles[0] - 1)):
                            line = line + 'X'

                    # Add a random tile from map configuration file.
                    else:
                        offset = (tile_num * self.tile_size[0],
                            row_num * self.tile_size[1])
                        if layer == LAYER_DATA:
                            line = line + choice(self.map_regions)
                        elif layer == LAYER_TERRAIN:
                            line = line + choice(self.map_terrains)
                            self.tile_dict[offset] = line[-1]
                            self.set_terrain(offset)
                        elif layer == LAYER_OBJECTS:
                            type = self.tile_dict[offset]
                            chance = int(self.map_objects[type][0])
                            if Die(chance).roll() == 1:
                                line = line + choice(self.map_objects[type][1])
                            else:
                                line = line + "."

                    tile_num += 1
                row_num += 1
                tile_num = 0

            # Add all map layers to a list.
                temp_layer.append(line)
                line = ""
            self.layer_list.append(temp_layer)
            temp_layer = []
            # import pdb; pdb.set_trace()

    def get_size(self):
        """Get the size of the map."""

        w = self.num_tiles[0] * self.tile_size[0]
        h = self.num_tiles[1] * self.tile_size[1]
        return (w, h)

    def set_terrain(self, offset):
        """Sets the terrain type of the tile."""

        tile = self.tile_dict[offset]
        rect = Rect(offset[0], offset[1],
            self.tile_size[0], self.tile_size[1])

        # Make each terrain more natural by mixing in another similar type.
        check = Die(TERRAIN_RANDOMNESS).roll()
        if check == 1:
            for terrain in self.terrain_list:
                if tile == terrain[0]:
                    choice = Die(len(terrain)).roll()-1
                    tile = terrain[choice]

        self.terrain[tile].collide.append(rect)
        self.types[tile] = self.terrain[tile].collide
        self.position[offset] = [ self.terrain[tile], {} ]

    def draw_map(self):
        """Draws the layers to the map."""

        for layer in range(0, len(self.layer_list)):
            row_num = 0
            tile_num = 0
            for row in self.layer_list[layer]:
                for tile in row:
                    offset = (tile_num * self.tile_size[0],
                        row_num * self.tile_size[1])
                    self.draw_tile(layer, tile, offset)
                    tile_num+=1
                row_num+=1
                tile_num = 0

    def draw_tile(self, layer, tile, offset):
        """Draws a tile to the correct layer."""

        terrain = self.position[offset]
        blit = self.layers['terrain'].image.blit

        if tile != ".":
            if layer == LAYER_DATA:
                if tile == "X":
                    self.set_nowalk(offset)
                elif tile.isdigit():
                    self.set_region(tile, offset)

            elif layer == LAYER_TERRAIN:
                blit(terrain[0].image, offset)
                self.set_edges(offset)
                self.draw_transitions(terrain, offset)
                terrain[0].draw_details(self.layers['terrain'], offset)
                if not terrain[0].walkable:
                    self.set_nowalk(offset)

            elif layer == LAYER_OBJECTS:
                tiles = terrain[0].objects[tile]
                w = tiles[TILE_IMAGE].get_width()
                h = tiles[TILE_IMAGE].get_height()
                offset = self.align_objects(w, h, offset)
                blit(tiles[TILE_IMAGE], offset)
                if not tiles[TILE_WALKABLE]:
                    self.set_nowalk(offset, tiles[TILE_SIZE], tiles[TILE_POS])
                self.set_above(w, h, tiles[TILE_IMAGE], offset,
                    tiles[TILE_SLICE])

    def draw_transitions(self, terrain, offset):
        """Draws edges to transition cleanly with unlike terrain types."""

        order = terrain[0].order
        edges = terrain[0].edges
        corners = terrain[0].corners
        sides = ('n', 'e', 's', 'w')
        diags = ('ne', 'se', 'sw', 'nw')
        blit = self.layers['terrain'].image.blit
        dict = terrain[1]

        if offset in self.position:
            for depth in range(3):
                if depth > order:
                    for type in TERRAIN_TRANSITIONS:

                        # Draw side transitions
                        for key in sides:
                            if type in edges and (dict.get(key) == type):
                                blit(edges[type][key], offset)

                        # Draw corner transitions
                        for key in diags:
                            if type in corners and (dict.get(key) == type):
                                blit(corners[type][key], offset)

                        if type in TERRAIN_UNWALKABLE:
                            self.set_nowalk(offset)

    def set_edges(self, offset):
        """Loops through all adjacent tiles and stores their terrain types."""

        rect = Rect((offset[0], offset[1],
            self.tile_size[0], self.tile_size[1]))
        w, h = self.tile_size[0], self.tile_size[1]
        edges = {
            'n':  rect.move(0,-h),
            'ne': rect.move(w,-h),
            'e':  rect.move(w,0),
            'se': rect.move(w,h),
            's':  rect.move(0,h),
            'sw': rect.move(-w,h),
            'w':  rect.move(-w,0),
            'nw': rect.move(-w,-h) }
        for edge in edges:
            cursor = (edges[edge][0], edges[edge][1])
            cur_x, cur_y = cursor
            map_w, map_h = self.get_size()
            if (0 <= cur_x <= map_w and 0 <= cur_y <= map_h and
                cursor in self.position and offset in self.position):
                self.position[offset][1][edge] = self.position[cursor][0].type

    def align_objects(self, w, h, offset):
        """Re-align bigger tiles to fit the rest."""

        object_offset = [0, 0]
        offset = [offset[0], offset[1]]
        if not self.tile_size[0] == w:
            object_offset[0] = self.tile_size[0] - w / 2
            offset[0] += object_offset[0]
        if not self.tile_size[1] == h:
            object_offset[1] = self.tile_size[1] - h
            offset[1] += object_offset[1]
        return offset

    def move(self, offset):
        """Scroll the map when when the player needs it to move."""

        self.layers['terrain'].dirty = 1
        for layer in self.layers:
            self.layers[layer].rect.move_ip(offset)

    def set_nowalk(self, offset, size=[32,32], pos=[0,0]):
        """Sets the parts of the tile that are unwalkable."""

        rect = Rect(offset[0] + pos[0], offset[1] + pos[1], size[0], size[1])
        self.nowalk.append(rect)

    def set_above(self, width, height, tile, offset, section):
        """Draws the correct piece of the tile to the foreground."""

        if (width > self.tile_size[0]) or (height > self.tile_size[1]):
            self.layers['foreground'].image.blit(tile, offset, section)

    def set_region(self, tile, offset):
        """Sets the region number for the tile."""

        rect = Rect(offset[0], offset[1], self.tile_size[0], self.tile_size[1])
        if tile in self.regions:
            self.regions[tile].append(rect)
        else:
            self.regions[tile] = []

    def scroll(self, camera, player):
        """Scroll the map to keep the player visible."""

        b_x, b_y = player.rect.center
        camera.center = (b_x, b_y)
        b_x, b_y = camera.topleft
        camera_w, camera_h = (camera.width, camera.height)
        map_w, map_h = self.get_size()
        if b_x < 0:
            b_x = 0
        if b_x > map_w - camera_w:
            b_x = map_w - camera_w
        if b_y < 0:
            b_y = 0
        if b_y > map_h - camera_h:
            b_y = map_h - camera_h
        if map_h < camera_h:
            b_y = (map_h - camera_h) / 2
        if map_w < camera_w:
            b_x - (map_w - camera_w) / 2
        camera.topleft = [ -b_x, -b_y ]
        self.move([ camera[0], camera[1] ])
        player.rect.move_ip([ camera[0], camera[1] ])
        player.scroll_pos = [ camera[0], camera[1] ]
