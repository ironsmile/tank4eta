#!/usr/bin/env python
#-*- coding: utf8 -*-

from app2 import Wall

MAP_X = 640
MAP_Y = 480
SQUARE_SIZE = 32

class MapSizeException(Exception):
    pass

class Map (object):
    
    def __init__ (self):
        self.objects = []
        self.resolution = (MAP_X, MAP_Y)
        self.box_size = SQUARE_SIZE
        if MAP_X % SQUARE_SIZE or MAP_Y % SQUARE_SIZE:
            raise MapSizeException("Map sizes cannot be divided by box size")
        self.x_boxes = MAP_X / SQUARE_SIZE
        self.y_boxes = MAP_Y / SQUARE_SIZE
        self.player_start = (0, 0)
    
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
                    self.player_start = self.real_coords(x,y)
                x += 1
            
            y += 1
        
        """
        end of load
        """        


