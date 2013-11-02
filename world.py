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
        self.objects = []
        self.resolution = (MAP_X, MAP_Y)
        self.box_size = SQUARE_SIZE
        if MAP_X % SQUARE_SIZE or MAP_Y % SQUARE_SIZE:
            raise MapSizeException("Map sizes cannot be divided by box size")
        self.x_boxes = MAP_X / SQUARE_SIZE
        self.y_boxes = MAP_Y / SQUARE_SIZE
        self.player_starts = []
        self.enemy_starts = []
    
    def real_coords(self, x, y):
        return (
                    x * self.box_size - self.box_size / 2,
                    y * self.box_size - self.box_size / 2
                )
    
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
    
    def tick(self, deltat, events):
        players_tanks = []
        bullets = []

        if len(self.enemies) < 4 and random.randint(0, 100) < 0.05:
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
        walls = pygame.sprite.RenderPlain(*self.map.objects)
        
        bullet_stoppers = players_tanks + self.map.objects + self.enemies
        bullet_stoppers = pygame.sprite.RenderPlain(bullet_stoppers)
        
        bullets_spr = pygame.sprite.RenderPlain(*bullets)
        collisions = pygame.sprite.groupcollide(bullets_spr, bullet_stoppers, False, False)
        #bullets_spr.update(deltat, collisions)
        for bullet in collisions:
            bullet.owner.bullets.remove(bullet)
            bullet.explode_sound()
            bullets.remove(bullet)
            collided_with = collisions[bullet]

            for collided in collided_with:
                if not isinstance(collided, BasicTank):
                    continue
                if isinstance(collided, EnemyTank) and collided is not bullet.owner:
                    self.enemies.remove(collided)
                if isinstance(collided, Tank):
                    tanks.remove(collided)
                    for player in self.players:
                        if player.tank is collided:
                            player.tank = None

        tanks.update(deltat)
        
        bullets_spr = pygame.sprite.RenderPlain(*bullets)
        bullets_spr.update(deltat)
        
        collisions = pygame.sprite.groupcollide(tanks, walls, False, False)
        for tank in collisions:
            tank.undo()
        
        for tank in tanks:
            collisions = pygame.sprite.spritecollide(tank, [t for t in tanks if t != tank], False)
            if len(collisions):
                tank.undo()
        
        self._drawables = [tanks, walls, bullets_spr]
        return GAME_CONTINUE

    def spawn_enemy(self):
        index = random.randint(0, len(self.map.enemy_starts)-1)
        position = self.map.enemy_starts[index]
        enemy = EnemyTank(position, self.map)
        self.enemies.append(enemy)

    def get_drawables(self):
        return self._drawables

    def objects_at(self, coords):
        return []
