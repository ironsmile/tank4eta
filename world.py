#!/usr/bin/env python
#-*- coding: utf8 -*-

import ai
import math
import random
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

    def real_coords(self, x, y):
        bs = self.scaled_box_size
        return ((x * bs - bs / 2),
                (y * bs - bs / 2))

    def load(self, map_file):
        #!TODO: add try+catch, stat of map file for 0 bytes, too large
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
        y = 1
        for row in self.map_str.splitlines():
            x = 1
            for square in row:
                coords = self.real_coords(x, y)
                if square == 'w':
                    self.objects.append(Wall(coords, self.texture_loader))
                if square == 'p':
                    self.player_starts.append(coords)
                if square == 'e':
                    self.enemy_starts.append(coords)
                if square == '~':
                    self.unpassable.append(Water(coords, self.texture_loader))
                x += 1

            y += 1
        if len(self.player_starts) < 1:
            raise MapLogicException("No player starting positions found")

    def scale_to_screen(self, val):
        return val * self.scale_factor


class World (object):

    def __init__(self, game_map, players, texture_loader):
        self.players = players
        self.map = game_map
        self.texture_loader = texture_loader
        self._drawables = []
        self.enemies = []
        self.ai = ai.Random(self)
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

        if alive_enemies < 4 and random.randint(0, 100) < 0.05 and \
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

        self.ai.tick(self.enemies)

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

        tanks.update(deltat)
        bullets.update(deltat)

        collisions = pygame.sprite.groupcollide(tanks, unpassable, False, False)
        for tank in collisions:
            tank.undo()

        for tank in tanks:
            other_tanks = [t for t in tanks if t != tank]
            collisions = pygame.sprite.spritecollide(tank, other_tanks, False)
            if len(collisions):
                tank.undo()

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
