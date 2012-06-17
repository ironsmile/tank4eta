#!/usr/bin/env python
#-*- coding: utf8 -*-

from pygame.locals import *
from locals import *
import pygame
import pygame.mixer
import sys

import time
import math

import world

from object import Object, MovableObject, NonMovableObject


class Tank (MovableObject):
    
    def __init__ (self, image, position, game_map):
        MovableObject.__init__(self, image, position, game_map)
        self.engine_working = False
        self.engine = pygame.mixer.Sound('doycho.wav')
        self.move(DIRECTION_UP)
        self.stop()
        self.bullets = []
    
    def stop (self):
        MovableObject.stop(self)
        self.engine.stop()
        self.engine_working = False
        
    def process_event(self, event):
        if not hasattr(event, 'key'): return
        down = event.type == KEYDOWN
        
        if down:
            if event.key == K_RIGHT: 
                self.change_axis(AXIS_X)
                self.move(DIRECTION_RIGHT)
            elif event.key == K_LEFT: 
                self.change_axis(AXIS_X)
                self.move(DIRECTION_LEFT)
            elif event.key == K_UP: 
                self.change_axis(AXIS_Y)
                self.move(DIRECTION_UP)
            elif event.key == K_DOWN: 
                self.change_axis(AXIS_Y)
                self.move(DIRECTION_DOWN)
        else:
            if event.key == K_RIGHT and self.direction == DIRECTION_RIGHT:
                self.stop()
            elif event.key == K_LEFT and self.direction == DIRECTION_LEFT:
                self.stop()
            elif event.key == K_UP and self.direction == DIRECTION_UP:
                self.stop()
            elif event.key == K_DOWN and self.direction == DIRECTION_DOWN:
                self.stop()
            elif event.key == K_SPACE:
                self.fire()
    
    def update(self, delta = None):
        if self.direction != DIRECTION_NONE and not self.engine_working:
            self.engine.play(loops = -1)
            self.engine_working = True
        
        MovableObject.update(self, delta)
    
    def fire (self):
        if len(self.bullets) > 0: return
        bullet = Bullet(self)
        self.bullets.append(bullet)
    
class Bullet (MovableObject):
    
    bullet_img = 'bullet.png'
    
    def __init__ (self, owner):
        self.owner = owner
        MovableObject.__init__(self, self.bullet_img, owner.rect.center, owner.map)
        self.set_movement_speed(BULLET_SPEED)
        self.direction = owner.facing
        self.move(self.direction)
        self.rect = self.image.get_rect()
        self.rect.center = owner.rect.center
    
    # a bullet does not stop!
    def stop (self): pass
    
    # a bullet does not care for your "events" !
    def process_event (self, event): pass
    
    def update (self, delta = None, collisions = []):
        if self in collisions:
            self.owner.bullets.remove(self)
        x, y = self.rect.center
        dx, dy = self.movements[self.direction]
        self.rect.center = (x+dx, y+dy)
    
    
class Wall (NonMovableObject):
    image = pygame.image.load('wall.png')
    def __init__ (self, position):
        NonMovableObject.__init__(self, position)


if __name__ == '__main__':
    
    game_map = world.Map()
    game_map.load('first_map.map')
    
    screen = pygame.display.set_mode(game_map.resolution)
    pygame.mixer.init()
    clock = pygame.time.Clock()
    
    tank = Tank('tank.png', game_map.player_start, game_map)
    tanks = pygame.sprite.RenderPlain(tank)
    
    walls = pygame.sprite.RenderPlain(*game_map.objects)
    
    while 42:
        deltat = clock.tick(FRAMES)
        for event in pygame.event.get():
            if not hasattr(event, 'key'): continue
            if event.key == K_ESCAPE: sys.exit(0)
            tank.process_event(event)
        
        screen.fill((0,0,0))
        tanks.update(deltat)
        
        if len(tank.bullets) > 0:
            bullets = pygame.sprite.RenderPlain(*tank.bullets)
            collisions = pygame.sprite.groupcollide(bullets, walls, False, False)
            bullets.update(deltat, collisions)
        else:
            bullets = pygame.sprite.RenderPlain()
        
        collisions = pygame.sprite.spritecollide(tank, walls, False)
        if len(collisions):
            tank.undo()
                    
        tanks.draw(screen)
        walls.draw(screen)
        bullets.draw(screen)
        pygame.display.flip()



