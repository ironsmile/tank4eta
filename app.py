#!/usr/bin/env python
#-*- coding: utf8 -*-

from pygame.locals import *
import pygame
import pygame.mixer
import sys

import time
import math

FRAMES_PER_SECOND = 30
MOVEMENT_NONE = -1
MOVEMENT_UP = 0
MOVEMENT_DOWN = 1
MOVEMENT_LEFT = 2
MOVEMENT_RIGHT = 3

clock = pygame.time.Clock()

screen = pygame.display.set_mode((1024, 768)) # set_mode((1024, 768), FULLSCREEN)
pygame.mixer.init()
tank_sound = pygame.mixer.Sound('doycho.wav')
tank_has_sound = False

tank = pygame.image.load('tank.png')
tank_position = (50, 50)
tank_movement = MOVEMENT_NONE

current_tank = tank

tank_down = tank
tank_left = pygame.transform.rotate(tank, 270)
tank_up = pygame.transform.rotate(tank, 180)
tank_right = pygame.transform.rotate(tank, 90)


while 42:
    clock.tick(FRAMES_PER_SECOND)
    
    for event in pygame.event.get():
        if not hasattr(event, 'key'): continue
        down = event.type == KEYDOWN
        
        if down:
            if event.key == K_RIGHT: 
                tank_movement = MOVEMENT_RIGHT
                current_tank = tank_right
            elif event.key == K_LEFT: 
                tank_movement = MOVEMENT_LEFT
                current_tank = tank_left
            elif event.key == K_UP: 
                tank_movement = MOVEMENT_UP
                current_tank = tank_up
            elif event.key == K_DOWN: 
                tank_movement = MOVEMENT_DOWN
                current_tank = tank_down
            elif event.key == K_ESCAPE: sys.exit(0)
        else:
            if event.key == K_RIGHT and tank_movement == MOVEMENT_RIGHT:
                tank_movement = MOVEMENT_NONE
                tank_sound.stop()
                tank_has_sound = False
            elif event.key == K_LEFT and tank_movement == MOVEMENT_LEFT:
                tank_movement = MOVEMENT_NONE
                tank_sound.stop()
                tank_has_sound = False
            elif event.key == K_UP and tank_movement == MOVEMENT_UP:
                tank_movement = MOVEMENT_NONE
                tank_sound.stop()
                tank_has_sound = False
            elif event.key == K_DOWN and tank_movement == MOVEMENT_DOWN:
                tank_movement = MOVEMENT_NONE
                tank_sound.stop()
                tank_has_sound = False
    
    if tank_movement != MOVEMENT_NONE and not tank_has_sound:
        tank_sound.play(loops = -1)
        tank_has_sound = True
    
    tx, ty = tank_position
    
    if tank_movement == MOVEMENT_RIGHT: tank_position = (tx + 3, ty)
    elif tank_movement == MOVEMENT_LEFT: tank_position = (tx - 3, ty)
    elif tank_movement == MOVEMENT_UP: tank_position = (tx, ty - 3)
    elif tank_movement == MOVEMENT_DOWN: tank_position = (tx, ty + 3)
    
    screen.fill((0,0,0))
    
    screen.blit(current_tank, tank_position)
    pygame.display.flip()



