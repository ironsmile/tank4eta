#!/usr/bin/env python
#-*- coding: utf8 -*-

from stuff_on_map import *

MAP_X = 640
MAP_Y = 480
SQUARE_SIZE = 32

class MapSizeException(Exception): pass

class MapLogicException(Exception): pass

class Map (object):
    
    def __init__ (self):
        self.objects = []
        self.resolution = (MAP_X, MAP_Y)
        self.box_size = SQUARE_SIZE
        if MAP_X % SQUARE_SIZE or MAP_Y % SQUARE_SIZE:
            raise MapSizeException("Map sizes cannot be divided by box size")
        self.x_boxes = MAP_X / SQUARE_SIZE
        self.y_boxes = MAP_Y / SQUARE_SIZE
        self.player_starts = []
    
    def real_coords (self, x, y):
        return (
                    x * self.box_size - self.box_size / 2,
                    y * self.box_size - self.box_size / 2
                ) 
    
    def load (self, map_file):
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
                    self.objects.append( Wall(self.real_coords(x,y)) )
                if square == 'p':
                    self.player_starts.append(self.real_coords(x,y))
                x += 1
            
            y += 1
        
        if len(self.player_starts) < 1:
            raise MapLogicException("No player starting positions found")
        """
        end of load
        """

class World (object):
    
    def __init__ (self, map, players):
        self.players = players
        self.map = map
        self.drawables = []
    
    def tick (self, deltat, events):
        players_tanks = []
        bullets = []
        for player in self.players:
            player.process_events(events)
            players_tanks.append(player.tank)
            bullets += player.tank.bullets
        
        tanks = pygame.sprite.RenderPlain(*players_tanks)
        walls = pygame.sprite.RenderPlain(*self.map.objects)
        
        bullet_stoppers = pygame.sprite.RenderPlain(players_tanks + self.map.objects)
        
        bullets_spr = pygame.sprite.RenderPlain(*bullets)
        collisions = pygame.sprite.groupcollide(bullets_spr, bullet_stoppers, False, False)
        #bullets_spr.update(deltat, collisions)
        for bullet in collisions:
            bullet.owner.bullets.remove(bullet)
            bullets.remove(bullet)
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
        
        self.drawables = [tanks, walls, bullets_spr]




