#!/usr/bin/env python
#-*- coding: utf8 -*-

from pygame.locals import *
import pygame
import pygame.mixer


class Object (object):
    
    def __init__ (self):
        self.passable = False
        self.movable = False
        self.coords = False
        

