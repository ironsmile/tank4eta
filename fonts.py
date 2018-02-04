#!/usr/bin/env python
#-*- coding: utf8 -*-

from locals import FONT_SERIF_PATH
import pygame

pygame.font.init()

serif_normal = pygame.font.Font(FONT_SERIF_PATH, 24)
serif_big = pygame.font.Font(FONT_SERIF_PATH, 30)
