#!/usr/bin/env python
#-*- coding: utf8 -*-

import sys
import pygame
from pygame.locals import *

class EventManager (object):
    
    def get_events (self):
        ret = []
        for event in pygame.event.get():
            if hasattr(event, 'key') and event.key == K_ESCAPE: sys.exit(0)
            ret.append(event)
        return ret
