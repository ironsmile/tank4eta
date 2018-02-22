#!/usr/bin/env python
#-*- coding: utf8 -*-

import ai
import math
import random

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
        Water and forest are considered as a see through obojects.
        !TODO: actually implement it.
        '''
        return True

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

        if in_box_coef > 0.75 and grid_ind < (boxes_count * 2 - 1):
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
        return (((x + 1) * bs - bs / 2),
                ((y + 1) * bs - bs / 2))

    def load(self, map_file):
        '''
        Loads a map file and calculates the game and screen world resolutions.
        !TODO: add try+catch, stat of map file for 0 bytes, too large
        '''
        mapf = open(map_file, 'r')
        self.map_str = mapf.read()
        mapf.close()

        y = 1
        for row in self.map_str.splitlines():
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
            x = 0
            for square in row:
                coords = self.real_coords(x, y)
                if square == 'w':
                    self.populate_matrix(x, y)
                    self.objects.append(Wall(coords, self.texture_loader))
                elif square == 'p':
                    self.player_starts.append(coords)
                elif square == 'e':
                    self.enemy_starts.append(coords)
                elif square == '~':
                    self.populate_matrix(x, y)
                    self.unpassable.append(Water(coords, self.texture_loader))
                x += 1

            y += 1
        if len(self.player_starts) < 1:
            raise MapLogicException("No player starting positions found")

    def populate_matrix(self, x, y):
        '''
        The pathfinding map is bigger than the actual map. This is because objects
        can move between world boxes. So the pathfinding gird inserts one extra
        node between every two nodes in the map.
        '''
        gx, gy = x * 2, y * 2
        self._matrix[gy][gx] = 1

        if x > 0 and y > 0:
            self._matrix[gy - 1][gx - 1] = 1

        if x < self.x_boxes - 1:
            self._matrix[gy][gx + 1] = 1

        if y < self.y_boxes - 1:
            self._matrix[gy + 1][gx] = 1

        if x < self.x_boxes - 1 and y < self.y_boxes - 1:
            self._matrix[gy + 1][gx + 1] = 1

        if x > 0:
            self._matrix[gy][gx - 1] = 1

        if y < self.y_boxes - 1 and x > 0:
            self._matrix[gy + 1][gx - 1] = 1

        if y > 0:
            self._matrix[gy - 1][gx] = 1

        if y > 0 and x < self.x_boxes - 1:
            self._matrix[gy - 1][gx + 1] = 1

    def build_grid(self):
        self.grid = Grid(matrix=self._matrix)
        return self.grid


class World (object):

    def __init__(self, game_map, players, texture_loader):
        self.players = players
        self.map = game_map
        self.texture_loader = texture_loader
        self._drawables = []
        self.enemies = []
        self.ai = ai.ZombieDriver(self)
        self.enemies_killed = 0
        self.enemeis_to_kill = 20

        self._bullets = pygame.sprite.RenderUpdates()
        self._unpassable = pygame.sprite.RenderUpdates()
        self._movable = pygame.sprite.RenderUpdates()

    def init(self):
        for player in self.players:
            self._movable.add(player.tank)
        self._unpassable.add(*[self.map.objects + self.map.unpassable])
        self.map.render.set_background(self._unpassable)

    def get_end_game_stats(self):
        return "Enemies killed: %d / %d" % (self.enemies_killed, self.enemeis_to_kill)

    def tick(self, deltat, events):
        if self.enemies_killed >= self.enemeis_to_kill:
            return GAME_WON

        bullets = self._bullets
        unpassable = self._unpassable

        self.map.render.clear([bullets, self._movable])

        players_tanks = []
        alive_enemies = len(self.enemies)

        if alive_enemies < 6 and random.randint(0, 100) < 0.05 and \
                (self.enemies_killed + alive_enemies) < self.enemeis_to_kill:
            self.spawn_enemy()

        for player in self.players:
            player.process_events(events)
            if player.tank is None:
                continue
            players_tanks.append(player.tank)
            bullets.add(*player.tank.bullets)

        if len(players_tanks) < 1:
            return GAME_OVER

        self.ai.tick(deltat, self.enemies)

        for enemy in self.enemies:
            bullets.add(*enemy.bullets)

        tanks = pygame.sprite.RenderUpdates(*(players_tanks + self.enemies))

        bullet_stoppers = players_tanks + self.map.objects + self.enemies + bullets.sprites()
        bullet_stoppers = pygame.sprite.Group(bullet_stoppers)

        collisions = pygame.sprite.groupcollide(bullets, bullet_stoppers, False, False)

        for bullet in collisions:
            collided_with = collisions[bullet]
            if len(collided_with) == 1 and bullet in collided_with:
                continue
            if bullet.owner is not None:
                bullet.owner.bullets.remove(bullet)
            bullet.explode_sound()
            bullets.remove(bullet)

            for collided in collided_with:
                if collided == bullet:
                    continue
                if not isinstance(collided, BasicTank):
                    continue
                if collided is bullet.owner:
                    continue

                if not collided.is_player and not bullet.is_player_bullet:
                    continue

                for orphan in collided.bullets:
                    orphan.owner = None

                self._movable.remove(collided)

                if isinstance(collided, EnemyTank):
                    self.enemies.remove(collided)
                    collided.explode_sound()
                    self.enemies_killed += 1
                if isinstance(collided, Tank):
                    tanks.remove(collided)
                    for player in self.players:
                        if player.tank is collided:
                            player.tank.explode_sound()
                            player.tank = None

        bullets.update(deltat)

        for tank in tanks:
            other_tanks = [t for t in tanks if t != tank]
            previously_collided = pygame.sprite.spritecollide(tank, other_tanks, False, False)

            tank.update(deltat)

            collision = pygame.sprite.spritecollideany(tank, unpassable)

            if collision is not None:
                tank.undo()
                continue

            others = pygame.sprite.spritecollide(tank, other_tanks, False, False)
            if len(others) < 1:
                continue

            for other in others:
                if other not in previously_collided:
                    tank.undo()
                    break

                dist = math.sqrt(
                    abs(tank.rect.centerx - other.rect.centerx) ** 2 +
                    abs(tank.rect.centery - other.rect.centery) ** 2
                )

                if dist < self.map.scaled_box_size * 0.75:
                    tank.undo()
                    break


        self._drawables = [self._movable, bullets]
        return GAME_CONTINUE

    def spawn_enemy(self):
        player_objects = []
        for player in self.players:
            if player.tank is None:
                continue
            player_objects.append(player.tank)
            player_objects += player.tank.bullets

        for i in range(10):
            index = random.randint(0, len(self.map.enemy_starts) - 1)
            position = self.map.enemy_starts[index]
            new_enemy = EnemyTank(position, self.texture_loader)
            collisions = pygame.sprite.groupcollide(
                [new_enemy],
                self._movable,
                False,
                False
            )
            if len(collisions):
                # we should not spawn an enemy on top of an other enemy
                continue
            self._movable.add(new_enemy)
            self.enemies.append(new_enemy)
            break

    def get_drawables(self):
        return self._drawables

    def objects_at(self, coords):
        return []
