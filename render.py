#!/usr/bin/env python
#-*- coding: utf8 -*-

import sys
import time
import pygame
import logging
import pygame.font
import fonts
from locals import *

RESOLUTION = (1024, 768)


class Render (object):

    def __init__(self, fullscreen=False):
        pygame.display.init()
        pygame.display.set_caption("tank4eta")
        self.fullscreen = fullscreen
        self.should_flip = False
        self.show_fps = False
        self.fps = 0
        self.ndi = pygame.display.Info()
        self.debug_display(self.ndi, "native")
        self.render_resolution = None
        self.screen = None
        self.background = None
        self.toggle_full_screen(
            force_fullscreen_to=self.fullscreen,
            initial=True
        )
        self.set_render_resolution(RESOLUTION)
        if sys.platform.startswith('win') or sys.platform.startswith('linux'):
            self.should_flip = True

    def set_render_resolution(self, resolution):
        if self.render_resolution == resolution:
            return
        self.render_resolution = resolution
        self.create_aspect_surface()

    def set_background(self, sprite):
        self.background.fill(BACKGROUND_COLOUR)
        sprite.draw(self.background)
        self.draw_background()

    def draw_background(self):
        self.aspect_surface.blit(self.background, (0, 0))

    def clear(self, sprites=[]):
        for obj_group in sprites:
            obj_group.clear(self.aspect_surface, self.background)

    def draw(self, sprites=[]):
        changed = []
        for obj_group in sprites:
            changed += obj_group.draw(self.aspect_surface)
        self.update(changed)

    def update(self, changed):
        self.draw_fps()
        pygame.display.update(changed)
        if self.should_flip:
            pygame.display.flip()

    def draw_fps(self):
        if not self.show_fps:
            return
        fps_text = "{0}".format(int(self.fps))
        fps_sprite = fonts.serif_normal.render(fps_text, 1, YELLOW)
        fps_rect = fps_sprite.get_rect()
        self.aspect_surface.blit(self.background, (0, 0), fps_rect)
        self.aspect_surface.blit(fps_sprite, (0, 0))
        return fps_rect

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
        self.screen.fill(BLACK)
        pygame.display.flip()

    def debug_display(self, display, name=None):
        logging.debug("-" * 10)
        if name is None:
            logging.debug("Debugging unknown display")
        else:
            logging.debug("Debugging %s display" % name)
        logging.debug("Hardware acceleration: %d" % display.hw)
        logging.debug("Can be windowed: %d" % display.wm)
        logging.debug("Video memory: %d" % display.video_mem)
        logging.debug("Width, Height: %dx%d" % (display.current_w, display.current_h))
        logging.debug("-" * 10)

    def create_aspect_surface(self):
        render_w, render_h = self.render_resolution
        display_w, display_h = self.resolution

        render_ratio = float(render_w) / render_h

        aspect_w = int(render_ratio * display_h)
        aspect_h = display_h
        aspect = (aspect_w, aspect_h)

        sub_x = int((display_w - aspect_w) / 2)
        sub_y = int((display_h - aspect_h) / 2)
        pos = (sub_x, sub_y)

        logging.debug("Aspect surface is %dx%d" % aspect)
        logging.debug("Aspect surface is on coords (%d, %d)" % pos)

        aserf = self.screen.subsurface(
            pygame.Rect(pos, aspect)
        )
        self.aspect_surface = aserf
        self.aspect_resolution = aspect
        self.background = self.aspect_surface.copy()

        if self.render_resolution == aspect:
            return

        # Since the render resolution is always floored it is guaranteed to be
        # less or equal to the aspect resolution. We the following we are centering
        # the picture in the aspect surface
        ox = int((aspect_w - render_w) / 2)
        oy = int((aspect_h - render_h) / 2)

        self.aspect_surface = self.aspect_surface.subsurface(
            pygame.Rect((ox, oy), self.render_resolution)
        )

    def update_fps(self, clock):
        self.fps = clock.get_fps()

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
            logging.debug("Going into fullscreen")
            self.fullscreen = True
        else:
            logging.debug("Going into windowed mode")
            self.fullscreen = False

        if self.fullscreen:
            self.resolution = (self.ndi.current_w, self.ndi.current_h)
            self.screen = pygame.display.set_mode(
                self.resolution,
                pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE
            )
        else:
            self.resolution = RESOLUTION
            self.screen = pygame.display.set_mode(
                self.resolution,
                pygame.DOUBLEBUF | pygame.HWSURFACE
            )

        self.display_info = pygame.display.Info()
        self.debug_display(self.display_info, "game")

        if not initial:
            self.create_aspect_surface()

    def show_menu_instruction(self, instruction):
        text_obj = fonts.serif_normal.render(instruction, True, SILVER)
        text_x = (self.screen.get_width() - text_obj.get_width()) / 2
        text_y = 40
        self.screen.blit(text_obj, (text_x, text_y))
