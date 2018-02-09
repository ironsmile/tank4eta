#!/usr/bin/env python
#-*- coding: utf8 -*-

import ai
import random
from stuff_on_map import *

MAP_X = 640
MAP_Y = 480
SQUARE_SIZE = 32


class MapSizeException(Exception):
    pass


class MapLogicException(Exception):
    pass


class Map (object):

    def __init__(self):
        self.unpassable = []
        self.objects = []
        self.box_size = SQUARE_SIZE
        if MAP_X % SQUARE_SIZE or MAP_Y % SQUARE_SIZE:
            raise MapSizeException("Map sizes cannot be divided by box size")
        self.x_boxes = MAP_X / SQUARE_SIZE
        self.y_boxes = MAP_Y / SQUARE_SIZE
        self.player_starts = []
        self.enemy_starts = []

    def real_coords(self, x, y):
        return (x * self.box_size - self.box_size / 2,
                y * self.box_size - self.box_size / 2)

    def load(self, map_file):
        #!TODO: add try+catch, stat of map file for 0 bytes, too large
        mapf = open(map_file, 'r')
        map_str = mapf.read()
        mapf.close()

        y = 1
        for row in map_str.splitlines():
            if y > self.y_boxes or len(row) > self.x_boxes:
                raise MapSizeException("Map size in file corrupted")
            x = 1
            for square in row:
                if square == 'w':
                    self.objects.append(Wall(self.real_coords(x, y)))
                if square == 'p':
                    self.player_starts.append(self.real_coords(x, y))
                if square == 'e':
                    self.enemy_starts.append(self.real_coords(x, y))
                if square == '~':
                    self.unpassable.append(Water(self.real_coords(x, y)))
                x += 1

            y += 1

        if len(self.player_starts) < 1:
            raise MapLogicException("No player starting positions found")
        """
        end of load
        """


class World (object):

    def __init__(self, map, players):
        self.players = players
        self.map = map
        self._drawables = []
        self.enemies = []
        self.ai = ai.AI()
        self.enemies_killed = 0
        self.enemeis_to_kill = 20

    def get_end_game_stats(self):
        return "Enemies killed: %d / %d" % (self.enemies_killed, self.enemeis_to_kill)

    def tick(self, deltat, events):
        if self.enemies_killed >= self.enemeis_to_kill:
            return GAME_WON

        players_tanks = []
        bullets = []
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
            bullet.owner.bullets.remove(bullet)
            bullet.explode_sound()
            bullets.remove(bullet)

            for collided in collided_with:
                if collided == bullet:
                    continue
                if not isinstance(collided, BasicTank):
                    continue
                if isinstance(collided, EnemyTank) and collided is not bullet.owner:
                    self.enemies.remove(collided)
                    collided.explode_sound()
                    self.enemies_killed += 1
                if isinstance(collided, Tank) and collided is not bullet.owner:
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
