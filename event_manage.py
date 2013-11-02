#!/usr/bin/env python
#-*- coding: utf8 -*-

import pygame
from pygame.locals import *


class EventManager (object):
    
    def __init__(self):
        self._stopped = False
        self._toggle_full_screen = False

    def get_events(self):
        ret = []
        self._stopped = False
        self._toggle_full_screen = False

        for event in pygame.event.get():
            if hasattr(event, 'key'):
                if event.key == K_ESCAPE:
                    self._stopped = True
                    continue
                elif event.key == K_F11 and event.type == KEYUP:
                    self._toggle_full_screen = True
                    continue
            ret.append(event)
        return ret

    def game_stopped(self):
        return self._stopped

    def toggled_full_screen(self):
        return self._toggle_full_screen
