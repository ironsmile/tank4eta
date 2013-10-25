#!/usr/bin/env python
#-*- coding: utf8 -*-

import pygame
from locals import *


class Render (object):

    def __init__(self, world):
        self.world = world
        self.screen = pygame.display.set_mode(self.world.map.resolution)
    
    def draw(self):
        self.screen.fill(BACKGROUND_COLOUR)
        
        for obj_group in self.world.get_drawables():
            obj_group.draw(self.screen)
        
        pygame.display.flip()
