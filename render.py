#!/usr/bin/env python
#-*- coding: utf8 -*-

import time
import pygame
import pygame.font
import world
from locals import *

RESOLUTION = (1024, 768)
FULLSCREEN = False

class Render (object):

    def __init__(self):
        pygame.display.init()
        self.fullscreen = FULLSCREEN

        self.ndi = pygame.display.Info()
        self.debug_display(self.ndi, "native")

        self.render_resolution = (world.MAP_X, world.MAP_Y)
        self.render_surface = pygame.Surface(self.render_resolution)
        print "Render resolution", self.render_resolution

        self.toggle_full_screen(force_fullscreen_to=self.fullscreen, initial=True)

    def draw(self, drawables):
        self.draw_on_render_surface(drawables)
        self.draw_on_aspect_surface()
        self.draw_on_screen()

    def draw_on_render_surface(self, drawables):
        self.render_surface.fill(BACKGROUND_COLOUR)

        for obj_group in drawables:
            obj_group.draw(self.render_surface)

    def draw_on_aspect_surface(self):
        dst_x = (self.aspect_resolution[0] - self.render_resolution[0]) / 2
        dst_y = (self.aspect_resolution[1] - self.render_resolution[1]) / 2
        self.aspect_surface.blit(self.render_surface, (dst_x, dst_y))

    def draw_on_screen(self):
        pygame.transform.smoothscale(self.aspect_surface, self.resolution, self.screen)
        pygame.display.flip()

    def draw_end_screen(self):
        self.screen.fill(BACKGROUND_COLOUR)
        pygame.font.init()
        font = pygame.font.SysFont("Sans Serif", 30)
        msg = "GAME OVER"
        self.screen.blit(font.render(msg, 1, (255, 255, 255)),
                            ((self.screen.get_width() / 2) - 100,
                            (self.screen.get_height() / 2) - 10))
        pygame.display.flip()

    def debug_display(self, display, name=None):
        print "-" * 10
        if name is None:
            print "Debugging unknown display"
        else:
            print "Debugging %s display" % name
        print "Hardware acceleration: %d" % display.hw
        print "Can be windowed: %d" % display.wm
        print "Video memory: %d" % display.video_mem
        print "Width, Height: %dx%d" % (display.current_w, display.current_h)
        print "-" * 10

    def get_aspect_surface(self):
        render_w, render_h = self.render_resolution
        display_w, display_h = self.resolution

        render_ration = float(render_w) / render_h
        display_ratio = float(display_w) / display_h

        if render_ration == display_ratio:
            aspect = (render_w, render_h)
        else:
            aspect_w = int(display_ratio * render_h)
            aspect_h = render_h
            aspect = (aspect_w, aspect_h)

        print "Aspect surface is %dx%d" % aspect
        self.aspect_resolution = aspect
        return pygame.Surface(aspect)

    def quit(self):
        pygame.display.quit()

    def toggle_full_screen(self, force_fullscreen_to=None, initial=False):

        if not initial:
            pygame.display.quit()
            time.sleep(1)
            pygame.display.init()

        if force_fullscreen_to is not None:
            self.fullscreen = not force_fullscreen_to

        if not self.fullscreen:
            print "Going into fullscreen"
            self.fullscreen = True
        else:
            print "Going into windowed mode"
            self.fullscreen = False

        if self.fullscreen:
            self.resolution = (self.ndi.current_w, self.ndi.current_h)
            self.screen = pygame.display.set_mode(self.resolution,
                    pygame.DOUBLEBUF | pygame.FULLSCREEN | pygame.HWSURFACE)
        else:
            self.resolution = RESOLUTION
            self.screen = pygame.display.set_mode(self.resolution, pygame.DOUBLEBUF)

        self.display_info = pygame.display.Info()
        self.debug_display(self.display_info, "game")

        self.aspect_surface = self.get_aspect_surface()
