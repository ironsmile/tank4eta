#!/usr/bin/env python
#-*- coding: utf8 -*-

from objects import *
from pygame.locals import *
from locals import *
from utils import *

class BasicTank (MovableObject):

    image = ""
    max_bullets = 1

    def __init__ (self, position, game_map):
        MovableObject.__init__(self, self.image, position, game_map)
        self.move(DIRECTION_DOWN)
        self.stop()
        self.bullets = []

    def fire (self):
        if len(self.bullets) >= self.max_bullets: return
        bullet = Bullet(self)
        self.bullets.append(bullet)

    def process_events (self, events):
        pass
    
    def _move_left (self):
        self.change_axis(AXIS_X)
        self.move(DIRECTION_LEFT)
    
    def _move_right (self):
        self.change_axis(AXIS_X)
        self.move(DIRECTION_RIGHT)
    
    def _move_up (self):
        self.change_axis(AXIS_Y)
        self.move(DIRECTION_UP)
            
    def _move_down (self):
        self.change_axis(AXIS_Y)
        self.move(DIRECTION_DOWN)
    
    def _stop (self):
        self.stop()
    
    def _fire (self):
        self.fire()

class EnemyTank (BasicTank):

    image = texture_path("enemy-1.png")
    max_bullets = 1

    def __init__ (self, position, game_map):
        MovableObject.__init__(self, self.image, position, game_map)
        self.move(DIRECTION_DOWN)
        self.stop()
        self.bullets = []

    def process_events (self, events):
        print "EnemyTank processing event. If you see me do something."

class Tank (BasicTank):
    
    image = texture_path('tank.png')
    max_bullets = 2
    
    def __init__ (self, position, game_map):
        MovableObject.__init__(self, self.image, position, game_map)
        self.engine_working = False
        self.engine = pygame.mixer.Sound( sound_path('didi_engine_01.wav') )
        self.move(DIRECTION_UP)
        self.stop()
        self.bullets = []
        self.event_map = {
            EVENT_FIRE : self._fire,
            EVENT_MOVE_LEFT : self._move_left,
            EVENT_MOVE_RIGHT: self._move_right,
            EVENT_MOVE_UP   : self._move_up,
            EVENT_MOVE_DOWN : self._move_down,
            EVENT_STOP : self._stop,
        }
    
    def process_events (self, events):
        for event in events:
            self.event_map[event]()
    
    def stop (self):
        MovableObject.stop(self)
        self.engine.stop()
        self.engine_working = False
    
    def update(self, delta = None):
        if self.direction != DIRECTION_NONE and not self.engine_working:
            self.engine.play(loops = -1)
            self.engine_working = True
        
        MovableObject.update(self, delta)


class Bullet (MovableObject):
    
    bullet_img = texture_path('bullet.png')
    
    def __init__ (self, owner):
        self.owner = owner
        MovableObject.__init__(self, self.bullet_img, owner.rect.center, owner.map)
        self.set_movement_speed(BULLET_SPEED)
        self.direction = owner.facing
        self.move(self.direction)
        self.rect = self.image.get_rect()
        self.rect.center = owner.rect.center
        self.position_front_of_owner()
        self.fire_sound = pygame.mixer.Sound( sound_path('didi_gunfire_01.wav') )
        self.explosion_sound = pygame.mixer.Sound( sound_path('didi_explode_01.wav') )
        self.fire_sound.play(loops=0, maxtime=0, fade_ms=0)
    
    def position_front_of_owner (self):
        dx, dy = self.owner.movements[self.owner.facing]
        if dx:
            dx = dx / abs(dx)
            diff = self.owner.rect.width / 2 + self.rect.width / 2 + 1
        if dy:
            dy = dy / abs(dy)
            diff = self.owner.rect.height / 2 + self.rect.height / 2 + 1
        
        rx, ry = self.rect.center
        self.rect.center = (rx + diff * dx, ry + diff * dy)
        
    def explode_sound (self):
        self.explosion_sound.play()

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
    image = pygame.image.load( texture_path('wall.png') )
    def __init__ (self, position):
        NonMovableObject.__init__(self, position)

