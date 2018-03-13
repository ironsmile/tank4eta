#!/usr/bin/env python
#-*- coding: utf8 -*-

from locals import FONT_SERIF_PATH, FONT_EASTERN_PATH
import pygame

pygame.font.init()

_serif_western_normal = pygame.font.Font(FONT_SERIF_PATH, 24)
_serif_western_big = pygame.font.Font(FONT_SERIF_PATH, 30)

_serif_japanese_normal = pygame.font.Font(FONT_EASTERN_PATH, 24)
_serif_japanese_big = pygame.font.Font(FONT_EASTERN_PATH, 30)

_serif_path = FONT_SERIF_PATH
_serif_normal = _serif_western_normal
_serif_big = _serif_western_big


def get_serif_path():
    return _serif_path


def get_serif_normal():
    return _serif_normal


def get_serif_big():
    return _serif_big


def switch_to_japanese():
    global _serif_path, _serif_normal, _serif_big
    _serif_path = FONT_EASTERN_PATH
    _serif_normal = _serif_japanese_normal
    _serif_big = _serif_japanese_big


def switch_to_western():
    global _serif_path, _serif_normal, _serif_big
    _serif_path = FONT_SERIF_PATH
    _serif_normal = _serif_western_normal
    _serif_big = _serif_western_big
