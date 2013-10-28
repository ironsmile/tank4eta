#!/usr/bin/env python
#-*- coding: utf8 -*-

import pygame
import pygame.font
from locals import *

RESOLUTION = (1024, 768)

class Render (object):

    def __init__(self, world):
        self.world = world
        self.screen = pygame.display.set_mode(RESOLUTION, pygame.DOUBLEBUF)
        self.render_surface = pygame.Surface(self.world.map.resolution)
    
    def draw(self):
        self.draw_on_render_surface()
        self.draw_on_screen()

    def draw_on_render_surface(self):
        self.render_surface.fill(BACKGROUND_COLOUR)
        
        for obj_group in self.world.get_drawables():
            obj_group.draw(self.render_surface)

    def draw_on_screen(self):
        pygame.transform.smoothscale(self.render_surface, RESOLUTION, self.screen)
        pygame.display.flip()

    def draw_end_screen(self):
        self.screen.fill(BACKGROUND_COLOUR)
        pygame.font.init()
        font = pygame.font.SysFont("Sans Serif", 30)
        msg = "GAME OVER"
        self.screen.blit(font.render(msg, 1, (255,255,255)), 
                            ((self.screen.get_width() / 2) - 100,
                            (self.screen.get_height() / 2) - 10))
        pygame.display.flip()
