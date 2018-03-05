#!/usr/bin/env python
#-*- coding: utf8 -*-

import random
import logging

from objects import *
from pygame.locals import *
from locals import *
from utils import *


class BasicTank(MovableObject):

    image = ""
    max_bullets = 1
    is_player = False

    def __init__(self, position, texture_loader):
        MovableObject.__init__(self, self.image, position, texture_loader)
        self.move(DIRECTION_DOWN)
        self.stop()
        self.bullets = []
        self.fire_timeout = 0

    def fire(self):
        if len(self.bullets) >= self.max_bullets:
            return
        self.fire_timeout = 0
        bullet = Bullet(self)
        self.bullets.append(bullet)

    def update(self, deltat):
        self.fire_timeout += deltat
        MovableObject.update(self, deltat)

    def is_facing(self, world_map, obj):
        '''
        @param world_map Map object
        @param obj pygame.Rect
        '''
        return world_map.is_visible(self.rect, self.facing, obj)

    def process_events(self, events):
        pass

    def _move_left(self):
        self.move(DIRECTION_LEFT)

    def _move_right(self):
        self.move(DIRECTION_RIGHT)

    def _move_up(self):
        self.move(DIRECTION_UP)

    def _move_down(self):
        self.move(DIRECTION_DOWN)

    def _stop(self):
        self.stop()

    def _fire(self):
        self.fire()


class EnemyTank(BasicTank):

    max_bullets = 1
    explosion_sound = None

    def __init__(self, position, texture_loader):
        num = random.randint(1, 2)
        self.image = texture_path("enemy-%d.png" % num)
        BasicTank.__init__(self, position, texture_loader)
        if EnemyTank.explosion_sound is None:
            path = sound_path('explosion_enemy.wav')
            EnemyTank.explosion_sound = pygame.mixer.Sound(path)
        self.set_movement_speed(ENEMY_MOVE_SPEED)
        self.current_target = None
        self.current_path = []
        self.path_duration = 0
        self.next_shot_timeout = random.randint(600, 1300)

    def fire(self):
        if self.fire_timeout <= self.next_shot_timeout:
            return
        bullets_count = len(self.bullets)
        BasicTank.fire(self)
        if len(self.bullets) > bullets_count:
            self.next_shot_timeout = random.randint(600, 1300)

    def explode_sound(self):
        self.explosion_sound.play()

    def process_events(self, events):
        logging.error("EnemyTank processing event. If you see me do something.")

    def has_target(self):
        return self.current_target is not None

    def set_current_path(self, path):
        self.current_path = path
        self.reset_path_duration()
        if len(path):
            self.current_target = path[-1]
        else:
            self.current_target = None

    def update_path_duration(self, deltat):
        self.path_duration += deltat

    def reset_path_duration(self):
        self.path_duration = 0

    def get_path_next(self, grid_pos):
        while 42:
            if len(self.current_path) == 0:
                return None
            next_node = self.current_path[0]
            if next_node == grid_pos:
                self.current_path.remove(next_node)
                continue
            return next_node


_player_tank_number = 0


class Tank(BasicTank):

    is_player = True
    max_bullets = 2

    def __init__(self, position, texture_loader):
        global _player_tank_number
        num = (_player_tank_number % 3) + 1
        _player_tank_number += 1

        sounds = {
            1: 'didi_engine_01.wav',
            2: 'doycho.wav',
            3: 'didi_engine_01.wav',
        }

        textures = {
            1: 'panzer.png',
            2: 'tank-of-love.png',
            3: 'tank.png',
        }

        texture_image = textures[num]
        self.image = texture_path(texture_image)
        self.engine = pygame.mixer.Sound(sound_path(sounds[num]))
        self.engine_working = False
        BasicTank.__init__(self, position, texture_loader)
        self.move(DIRECTION_UP)
        self.stop()
        self.explosion_sound = pygame.mixer.Sound(sound_path('player_death.wav'))
        self.event_map = {
            EVENT_FIRE: self._fire,
            EVENT_MOVE_LEFT: self._move_left,
            EVENT_MOVE_RIGHT: self._move_right,
            EVENT_MOVE_UP: self._move_up,
            EVENT_MOVE_DOWN: self._move_down,
            EVENT_STOP: self._stop,
        }

    def explode_sound(self):
        self.explosion_sound.play()

    def process_events(self, events):
        for event in events:
            self.event_map[event]()

    def stop(self):
        MovableObject.stop(self)
        self.engine.stop()
        self.engine_working = False

    def update(self, delta=None):
        if self.direction != DIRECTION_NONE and not self.engine_working:
            self.engine.play(loops=-1)
            self.engine_working = True

        MovableObject.update(self, delta)


class Bullet(MovableObject):

    bullet_img = texture_path('bullet.png')
    fire_sound = None
    explosion_sound = None

    def __init__(self, owner):
        self.owner = owner
        self.is_player_bullet = owner.is_player
        MovableObject.__init__(self, self.bullet_img, owner.rect.center, owner.texture_loader)
        self.set_movement_speed(BULLET_SPEED)
        self.direction = owner.facing
        self.move(self.direction)
        self.rect = self.image.get_rect()
        self.rect.center = owner.rect.center
        self.position_front_of_owner()

        if Bullet.fire_sound is None:
            Bullet.fire_sound = pygame.mixer.Sound(sound_path('didi_gunfire_01.wav'))

        if Bullet.explosion_sound is None:
            Bullet.explosion_sound = pygame.mixer.Sound(sound_path('didi_explode_01.wav'))

        self.fire_sound.play(loops=0, maxtime=0, fade_ms=0)

    def position_front_of_owner(self):
        dx, dy = self.owner.movements[self.owner.facing]
        if dx:
            dx = dx / abs(dx)
            diff = self.owner.rect.width / 2 + self.rect.width / 2 + 1
        if dy:
            dy = dy / abs(dy)
            diff = self.owner.rect.height / 2 + self.rect.height / 2 + 1

        rx, ry = self.rect.center
        self.rect.center = (rx + diff * dx, ry + diff * dy)
        self.real_center = self.rect.center

    def explode_sound(self):
        self.explosion_sound.play()

    # a bullet does not stop!
    def stop(self):
        pass

    # a bullet does not care for your "events" !
    def process_event(self, event):
        pass

    def update(self, delta, collisions=[]):
        if self in collisions and self.owner is not None:
            self.owner.bullets.remove(self)
        MovableObject.update(self, delta)


class Wall (NonMovableObject):

    def __init__(self, position, texture_loader):
        path = texture_path('wall.png')
        Wall.image = texture_loader.load_texture(path)
        NonMovableObject.__init__(self, position, texture_loader)


class Water (NonMovableObject):

    def __init__(self, position, texture_loader):
        path = texture_path('water.png')
        Water.image = texture_loader.load_texture(path)
        NonMovableObject.__init__(self, position, texture_loader)


class UnFlag (NonMovableObject):

    def __init__(self, position, texture_loader):
        path = texture_path('un_flag.png')
        UnFlag.image = texture_loader.load_texture(path)
        NonMovableObject.__init__(self, position, texture_loader)


class EndWorldium(NonMovableObject):

    def __init__(self, position, texture_loader):
        path = texture_path('end_worldium.png')
        EndWorldium.image = texture_loader.load_texture(path)
        NonMovableObject.__init__(self, position, texture_loader)
