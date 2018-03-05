#!/usr/bin/env python
#-*- coding: utf8 -*-

import math
from pathfinding.core.grid import Grid
from stuff_on_map import *

SQUARE_SIZE = 64


class MapSizeException(Exception):
    pass


class MapLogicException(Exception):
    pass


class Map (object):

    def __init__(self, map_file, render, texture_loader):
        self.unpassable = []
        self.objects = []
        self.limits_guard = []
        self.un_flags = []
        self.box_size = SQUARE_SIZE
        self.scaled_box_size = SQUARE_SIZE
        self.x_boxes = 0
        self.y_boxes = 0
        self.player_starts = []
        self.enemy_starts = []
        self.map_str = None
        self.texture_loader = texture_loader
        self.scale_factor = 1
        self.render = render
        self.load(map_file)
        self.render.set_render_resolution(self.scaled_resolution)
        self.texture_loader.set_dimensions(
            self.box_size,
            self.scaled_box_size,
            self.scale_factor
        )
        self.place_objects()

    def is_visible(self, source, direction, target):
        '''
        Tests wether an object at `source` can see the `target` while facing `direction`.
        Water and forest are considered as a see through objects.

        @param source pygame.Rect
        @param direction one of DIRECTION_UP, DIRECTION_DOWN, DIRECTION_RIGHT, DIRECTION_LEFT
        @param target pygame.Rect

        @returns boolean
        '''
        if direction == DIRECTION_NONE:
            return False

        targets = set()
        check_coords = self.world_to_grid_coords(source.centerx, source.centery)
        target_coords = self.world_to_grid_coords(target.centerx, target.centery)

        targets.add(target_coords)

        if direction in [DIRECTION_DOWN, DIRECTION_UP]:
            targets.add((target_coords[0] - 1, target_coords[1]))
            targets.add((target_coords[0] + 1, target_coords[1]))
        else:
            targets.add((target_coords[0], target_coords[1] - 1))
            targets.add((target_coords[0], target_coords[1] + 1))

        while 42:
            if check_coords in targets:
                return True

            if check_coords[0] < 0 or check_coords[0] >= self.x_boxes * 2 - 1:
                return False

            if check_coords[1] < 0 or check_coords[1] >= self.y_boxes * 2 - 1:
                return False

            node = self.grid.node(*check_coords)
            if not node.see_through:
                return False

            check_coords = self.direction_grid_coords(check_coords, direction)

        return False

    def direction_grid_coords(self, pos, direction):
        '''
        Returns the pathfinding grid coordinates of the neighbour square in `direction`
        relative to `pos`.
        '''
        if direction == DIRECTION_NONE:
            return pos

        if direction == DIRECTION_UP:
            return (pos[0], pos[1] - 1)
        elif direction == DIRECTION_DOWN:
            return (pos[0], pos[1] + 1)
        elif direction == DIRECTION_LEFT:
            return (pos[0] - 1, pos[1])

        return (pos[0] + 1, pos[1])

    def grid_direction(self, pos, to):
        '''
        Returns in which direction is `to` relative to `pos`.
        Does not work for diagonals. The `pos` and `to` must be next to
        each other.
        '''
        if pos == to:
            return DIRECTION_NONE

        px, py = pos
        tx, ty = to

        if tx < px:
            return DIRECTION_LEFT

        if tx > px:
            return DIRECTION_RIGHT

        if ty > py:
            return DIRECTION_DOWN

        return DIRECTION_UP

    def _axis_world_to_grid(self, axis_val, boxes_count):
        '''
        Finds at which coordinate in the pathfinding grid a particular
        axis value is.
        '''
        box_ind = math.floor(axis_val / self.scaled_box_size)
        in_box_dist = axis_val - (box_ind * self.scaled_box_size)
        in_box_coef = in_box_dist / self.scaled_box_size

        grid_ind = box_ind * 2

        if in_box_coef < 0.25 and grid_ind > 0:
            grid_ind -= 1

        if in_box_coef >= 0.75 and grid_ind < (boxes_count * 2 - 1):
            grid_ind += 1

        return grid_ind

    def world_to_grid_coords(self, x, y):
        '''
        Converts from world coordinates to the coordinates on the pathfinding grid. This
        necessarily looses precision and the wolrd coordinates are rounded to the
        nearest integer.
        '''
        gx = self._axis_world_to_grid(x, self.x_boxes)
        gy = self._axis_world_to_grid(y, self.y_boxes)

        return (gx, gy)

    def real_coords(self, x, y):
        '''
        Converts from map file coordinates to real scaled world coordinates on
        the screen.
        '''
        bs = self.scaled_box_size
        wx = ((x + 1) * bs - round(bs * 0.5))
        wy = ((y + 1) * bs - round(bs * 0.5))
        return (wx, wy)

    def load(self, map_file):
        '''
        Loads a map file and calculates the game and screen world resolutions.
        '''
        mapf = open(map_file, 'r')
        self.map_str = mapf.read(100 * 1024)
        mapf.close()

        y = 1
        for row in self.map_str.splitlines():
            row = row.strip('#')
            if len(row) < 1:
                continue
            if y > self.y_boxes:
                self.y_boxes = y
            if len(row) > self.x_boxes:
                self.x_boxes = len(row)
            y += 1

        if self.y_boxes < 5 or self.x_boxes < 5:
            raise MapSizeException("A map must be at least 5x5 boxes")

        self._matrix = [[0] * (self.x_boxes * 2 - 1) for i in range(self.y_boxes * 2 - 1)]

        self.map_resolution = (self.x_boxes * self.box_size,
                               self.y_boxes * self.box_size)
        aspect_w = self.render.aspect_resolution[0]
        map_w = self.map_resolution[0]
        self.scale_factor = aspect_w / map_w

        # Make sure the scaling always results in boxes of integer size. If not some
        # collisions would misalign.
        self.scaled_box_size = math.floor(self.box_size * self.scale_factor)
        self.scale_factor = self.scaled_box_size / self.box_size
        self.scaled_resolution = (self.x_boxes * self.scaled_box_size,
                                  self.y_boxes * self.scaled_box_size)

    def place_objects(self):
        y = 0
        for row in self.map_str.splitlines():
            row = row.strip('#')
            if len(row) < 1:
                continue
            x = 0
            for square in row:
                coords = self.real_coords(x, y)
                if square == 'w':
                    self.populate_matrix(x, y, Terrain.unpassable_no_see_through)
                    self.objects.append(Wall(coords, self.texture_loader))
                elif square == 'p':
                    self.player_starts.append(coords)
                elif square == 'e':
                    self.enemy_starts.append(coords)
                elif square == '~':
                    self.populate_matrix(x, y, Terrain.unpassable_see_through)
                    self.unpassable.append(Water(coords, self.texture_loader))
                elif square == 'f':
                    self.un_flags.append(UnFlag(coords, self.texture_loader))
                x += 1
            y += 1

        if len(self.player_starts) < 1:
            raise MapLogicException("No player starting positions found")

        limits = []

        for x in range(self.x_boxes):
            limits.append(self.real_coords(x, -1))
            limits.append(self.real_coords(x, self.y_boxes))

        for y in range(self.y_boxes):
            limits.append(self.real_coords(-1, y))
            limits.append(self.real_coords(self.x_boxes, y))

        for coords in limits:
            self.limits_guard.append(EndWorldium(coords, self.texture_loader))

    def populate_matrix(self, x, y, terrain=Terrain.unpassable_no_see_through):
        '''
        The pathfinding map is bigger than the actual map. This is because objects
        can move between world boxes. So the pathfinding gird inserts one extra
        node between every two nodes in the map.
        '''

        terrain_num = None
        if terrain == Terrain.unpassable_no_see_through:
            terrain_num = 1
        elif terrain == Terrain.unpassable_see_through:
            terrain_num = 2
        else:
            terrain_num = 0

        gx, gy = x * 2, y * 2
        self._matrix[gy][gx] = terrain_num

        if x > 0 and y > 0:
            self._matrix[gy - 1][gx - 1] = terrain_num

        if x < self.x_boxes - 1:
            self._matrix[gy][gx + 1] = terrain_num

        if y < self.y_boxes - 1:
            self._matrix[gy + 1][gx] = terrain_num

        if x < self.x_boxes - 1 and y < self.y_boxes - 1:
            self._matrix[gy + 1][gx + 1] = terrain_num

        if x > 0:
            self._matrix[gy][gx - 1] = terrain_num

        if y < self.y_boxes - 1 and x > 0:
            self._matrix[gy + 1][gx - 1] = terrain_num

        if y > 0:
            self._matrix[gy - 1][gx] = terrain_num

        if y > 0 and x < self.x_boxes - 1:
            self._matrix[gy - 1][gx + 1] = terrain_num

    def build_grid(self):
        self.grid = Grid(matrix=self._matrix)
        return self.grid
