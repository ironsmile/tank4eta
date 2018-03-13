#!/usr/bin/env python
#-*- coding: utf8 -*-

import enum
import os

FRAMES = 120
MOVE_SPEED = 6
ENEMY_MOVE_SPEED = 3.5
BULLET_SPEED = 18

DIRECTION_NONE = -1
DIRECTION_DOWN = 1
DIRECTION_LEFT = 2
DIRECTION_UP = 4
DIRECTION_RIGHT = 8

AXIS_X = 0
AXIS_Y = 1

BACKGROUND_COLOUR = (46, 52, 54)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
SILVER = (160, 160, 160)
YELLOW = (255, 255, 0)
ORANGE = (252, 158, 27)
BLUE = (30, 50, 107)

MAPS_DIR = os.path.join('data', 'maps')
SOUNDS_DIR = os.path.join('data', 'sounds')
TEXTURES_DIR = os.path.join('data', 'textures')

JOY_CENTERED = (0, 0)
JOY_UP = (0, 1)
JOY_DOWN = (0, -1)
JOY_RIGHT = (1, 0)
JOY_LEFT = (-1, 0)

EVENT_FIRE = 0
EVENT_MOVE_LEFT = 1
EVENT_MOVE_RIGHT = 2
EVENT_MOVE_UP = 3
EVENT_MOVE_DOWN = 4
EVENT_STOP = 5

GAME_CONTINUE = 0
GAME_WON = 1
GAME_OVER = -1

FONT_SERIF_PATH = os.path.join('data', 'fonts', 'ubuntu', 'Ubuntu-R.ttf')
FONT_EASTERN_PATH = os.path.join('data', 'fonts', 'noto', 'NotoSerifCJKjp-Regular.otf')


class Terrain(enum.Enum):
    '''
    This class is used while populating the pathfinding matrix
    '''
    passable_see_through = 0
    unpassable_no_see_through = 1
    unpassable_see_through = 2


class ScreenSetting(enum.Enum):
    windowed = 0
    fullscreen = 1
