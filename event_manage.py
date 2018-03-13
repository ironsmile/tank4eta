#!/usr/bin/env python
#-*- coding: utf8 -*-

from pygame.locals import *
import pygame
import sys


class EventManager (object):

    def __init__(self):
        self._stopped = False
        self._toggle_full_screen = False

    def get_events(self):
        ret = []
        self._stopped = False
        self._toggle_full_screen = False

        mods = pygame.key.get_mods()
        metaPressed = mods & pygame.KMOD_META

        for event in pygame.event.get():
            if self._is_quit(event, metaPressed):
                pygame.quit()
                sys.exit(0)

            if event.type == pygame.KEYDOWN and event.key in [K_ESCAPE, K_PAUSE] or \
                event.type == pygame.JOYBUTTONDOWN and event.button == 5:
                self._stopped = True
                continue

            ret.append(event)
        return ret

    def game_stopped(self):
        return self._stopped

    def toggled_full_screen(self):
        return self._toggle_full_screen

    def wait(self):
        event = pygame.event.wait()
        if self._is_quit(event):
            pygame.quit()
            sys.exit(0)
        return event

    def _is_quit(self, event, metaPressed = None):
        if event.type == pygame.QUIT:
            return True

        if metaPressed is None:
            mods = pygame.key.get_mods()
            metaPressed = mods & pygame.KMOD_META

        if event.type == pygame.KEYDOWN and event.key == pygame.K_q and metaPressed:
            return True

        return False
