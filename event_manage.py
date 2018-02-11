#!/usr/bin/env python
#-*- coding: utf8 -*-

import pygame
from pygame.locals import *


class EventManager (object):

    def __init__(self):
        self._stopped = False
        self._toggle_full_screen = False
        self._quitted = False

    def get_events(self):
        ret = []
        self._stopped = False
        self._toggle_full_screen = False

        mods = pygame.key.get_mods()
        metaPressed = mods & pygame.KMOD_META

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quitted = True
                return

            if event.type == pygame.KEYDOWN and event.key == pygame.K_q and metaPressed:
                self._quitted = True
                return

            if hasattr(event, 'key'):
                if event.key == K_ESCAPE:
                    self._stopped = True
                    continue
            ret.append(event)
        return ret

    def game_stopped(self):
        return self._stopped

    def toggled_full_screen(self):
        return self._toggle_full_screen

    def quitted(self):
        return self._quitted
