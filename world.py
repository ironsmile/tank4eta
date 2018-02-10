#!/usr/bin/env python
#-*- coding: utf8 -*-

import ai
import random
from stuff_on_map import *

SQUARE_SIZE = 64


class MapSizeException(Exception):
    pass


class MapLogicException(Exception):
    pass


class Map (object):

    textures = {}

    def __init__(self, map_file, render):
        self.unpassable = []
        self.objects = []
        self._unplaced_objects = []
        self.box_size = SQUARE_SIZE
        self.x_boxes = 0
        self.y_boxes = 0
        self.player_starts = []
        self.enemy_starts = []
        self.map_str = None
        self.load(map_file)
        self.render = render
        self.render.set_render_resolution(self.render_resolution)
        self.place_objects()

    def real_coords(self, x, y):
        return (x * self.box_size - self.box_size / 2,
                y * self.box_size - self.box_size / 2)

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

        self.render_resolution = (self.x_boxes * SQUARE_SIZE,
                                  self.y_boxes * SQUARE_SIZE)
        """
        end of load
        """

    def place_objects(self):
        y = 1
        for row in self.map_str.splitlines():
            x = 1
            for square in row:
                coords = self.real_coords(x, y)
                if square == 'w':
                    self.objects.append(Wall(coords, self))
                if square == 'p':
                    self.player_starts.append(coords)
                if square == 'e':
                    self.enemy_starts.append(coords)
                if square == '~':
                    self.unpassable.append(Water(coords, self))
                x += 1

            y += 1
        if len(self.player_starts) < 1:
            raise MapLogicException("No player starting positions found")

    def load_texture(self, path):
        if path in self.textures:
            return self.textures[path]
        texture = pygame.image.load(path)
        # if texture.get_width() != self.box_size or texture.get_height() != self.box_size:
        #     texture = pygame.transform.smoothscale(texture, (self.box_size, self.box_size))
        self.textures[path] = texture.convert_alpha()
        return self.textures[path]


class World (object):

    def __init__(self, map, players):
        self.players = players
        self.map = map
        self._drawables = []
        self.enemies = []
        self.ai = ai.AI()
        self.enemies_killed = 0
        self.enemeis_to_kill = 20
        self.orphaned_bullets = []

    def get_end_game_stats(self):
        return "Enemies killed: %d / %d" % (self.enemies_killed, self.enemeis_to_kill)

    def tick(self, deltat, events):
        if self.enemies_killed >= self.enemeis_to_kill:
            return GAME_WON

        players_tanks = []
        bullets = self.orphaned_bullets[:]
        alive_enemies = len(self.enemies)

        if alive_enemies < 4 and random.randint(0, 100) < 0.05 and \
                (self.enemies_killed + alive_enemies) < self.enemeis_to_kill:
            self.spawn_enemy()

        for player in self.players:
            player.process_events(events)
            if player.tank is None:
                continue
            players_tanks.append(player.tank)
            bullets += player.tank.bullets

        if len(players_tanks) < 1:
            return GAME_OVER

        self.ai.tick(self.enemies)

        for enemy in self.enemies:
            bullets += enemy.bullets

        tanks = pygame.sprite.RenderPlain(*(players_tanks + self.enemies))
        unpassable = pygame.sprite.RenderPlain(*[self.map.objects + self.map.unpassable])

        bullet_stoppers = players_tanks + self.map.objects + self.enemies + bullets
        bullet_stoppers = pygame.sprite.RenderPlain(bullet_stoppers)

        bullets_spr = pygame.sprite.RenderPlain(*bullets)
        collisions = pygame.sprite.groupcollide(bullets_spr, bullet_stoppers, False, False)
        # bullets_spr.update(deltat, collisions)

        for bullet in collisions:
            collided_with = collisions[bullet]
            if len(collided_with) == 1 and bullet in collided_with:
                continue
            if bullet.owner is None:
                self.orphaned_bullets.remove(bullet)
            else:
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
                    self.orphaned_bullets.append(orphan)

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

        bullets_spr = pygame.sprite.RenderPlain(*bullets)
        bullets_spr.update(deltat)

        collisions = pygame.sprite.groupcollide(tanks, unpassable, False, False)
        for tank in collisions:
            tank.undo()

        for tank in tanks:
            other_tanks = [t for t in tanks if t != tank]
            collisions = pygame.sprite.spritecollide(tank, other_tanks, False)
            if len(collisions):
                tank.undo()

        self._drawables = [tanks, unpassable, bullets_spr]
        return GAME_CONTINUE

    def spawn_enemy(self):
        player_objects = []
        for player in self.players:
            if player.tank is None:
                continue
            player_objects.append(player.tank)
            player_objects += player.tank.bullets

        not_spawnable_locations = self.enemies + player_objects

        for i in range(10):
            index = random.randint(0, len(self.map.enemy_starts) - 1)
            position = self.map.enemy_starts[index]
            new_enemy = EnemyTank(position, self.map)
            collisions = pygame.sprite.groupcollide(
                [new_enemy],
                not_spawnable_locations,
                False,
                False
            )
            if len(collisions):
                # we should not spawn an enemy on top of an other enemy
                continue
            self.enemies.append(new_enemy)
            break

    def get_drawables(self):
        return self._drawables

    def objects_at(self, coords):
        return []
