#!/usr/bin/env python
#-*- coding: utf8 -*-

import time
import pygame
import pygame.font
import world
import fonts
from locals import *

RESOLUTION = (1024, 768)
FULLSCREEN = False


class Render (object):

    def __init__(self):
        pygame.display.init()
        pygame.display.set_caption("tank4eta")
        self.fullscreen = FULLSCREEN

        self.ndi = pygame.display.Info()
        self.debug_display(self.ndi, "native")
        self.render_resolution = (world.MAP_X, world.MAP_Y)

        self.toggle_full_screen(
            force_fullscreen_to=self.fullscreen,
            initial=True
        )

        self.render_surface = pygame.Surface(self.render_resolution, pygame.HWSURFACE)
        print("Render resolution", self.render_resolution)

    def draw(self, drawables=[]):
        self.draw_on_render_surface(drawables)
        self.draw_on_screen()

    def draw_on_render_surface(self, drawables):
        self.render_surface.fill(BACKGROUND_COLOUR)

        for obj_group in drawables:
            obj_group.draw(self.render_surface)

    def draw_on_screen(self):
        # !TODO: here should always be smoothscale but apprantly there is a bug where
        # when scaling to bigger images cuases a corruption when the target
        # is a subsurface
        scale_fnc = pygame.transform.smoothscale
        if self.fullscreen:
            scale_fnc = pygame.transform.scale

        scale_fnc(
            self.render_surface,
            self.aspect_resolution,
            self.aspect_surface
        )
        pygame.display.flip()

    def draw_end_game_screen(self, text, stats_text):
        self.screen.fill(BACKGROUND_COLOUR)
        title_text_rect = fonts.serif_big.render(text, 1, WHITE)
        title_x = (self.screen.get_width() - title_text_rect.get_width()) / 2
        title_y = (self.screen.get_height() - title_text_rect.get_height()) / 2
        self.screen.blit(title_text_rect, (title_x, title_y))

        stats_text_rect = fonts.serif_normal.render(stats_text, 1, SILVER)
        text_x = (self.screen.get_width() - stats_text_rect.get_width()) / 2
        text_y = (self.screen.get_height() - stats_text_rect.get_height()) / 2 + 50
        self.screen.blit(stats_text_rect, (text_x, text_y))
        pygame.display.flip()

    def clear_screen(self):
        self.screen.fill(BACKGROUND_COLOUR)
        pygame.display.flip()

    def debug_display(self, display, name=None):
        print("-" * 10)
        if name is None:
            print("Debugging unknown display")
        else:
            print("Debugging %s display" % name)
        print("Hardware acceleration: %d" % display.hw)
        print("Can be windowed: %d" % display.wm)
        print("Video memory: %d" % display.video_mem)
        print("Width, Height: %dx%d" % (display.current_w, display.current_h))
        print("-" * 10)

    def get_aspect_surface(self):
        render_w, render_h = self.render_resolution
        display_w, display_h = self.resolution

        render_ratio = float(render_w) / render_h
        display_ratio = float(display_w) / display_h

        if abs(render_ratio - display_ratio) < 0.00001:
            return self.screen
        else:
            aspect_w = int(render_ratio * display_h)
            aspect_h = display_h
            aspect = (aspect_w, aspect_h)

        sub_x = int((display_w - aspect_w) / 2)
        sub_y = int((display_h - aspect_h) / 2)
        pos = (sub_x, sub_y)

        print("Aspect surface is %dx%d" % aspect)
        print("Aspect surface is on coords (%d, %d)" % pos)

        return self.screen.subsurface(
            pygame.Rect(pos, aspect)
        )

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
            print("Going into fullscreen")
            self.fullscreen = True
        else:
            print("Going into windowed mode")
            self.fullscreen = False

        if self.fullscreen:
            self.resolution = (self.ndi.current_w, self.ndi.current_h)
            self.screen = pygame.display.set_mode(
                self.resolution,
                pygame.DOUBLEBUF | pygame.FULLSCREEN | pygame.HWSURFACE
            )
        else:
            self.resolution = RESOLUTION
            self.screen = pygame.display.set_mode(
                self.resolution,
                pygame.DOUBLEBUF | pygame.HWSURFACE
            )

        self.display_info = pygame.display.Info()
        self.debug_display(self.display_info, "game")

        aserf = self.get_aspect_surface()
        self.aspect_surface = aserf
        self.aspect_resolution = (aserf.get_width(), aserf.get_height())
