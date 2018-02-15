#!/usr/bin/env python
#-*- coding: utf8 -*-

from pygame.locals import *
from locals import *
import pygame


class Object (pygame.sprite.Sprite):
    passable = False
    movable = False

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)


class MovableObject (Object):
    passable = False
    movable = True

    def __init__(self, image, position, texture_loader):
        Object.__init__(self)
        self.image_src = texture_loader.load_texture(image)
        self.image = self.image_src
        self.rect = self.image.get_rect()
        self.rect.center = position
        self.direction = DIRECTION_NONE
        self.calculate_images()
        self.set_movement_speed(MOVE_SPEED)
        self.moving_on_axis = None
        self.facing = DIRECTION_NONE
        self.texture_loader = texture_loader

    def set_movement_speed(self, speed):
        self.movements = {
            DIRECTION_DOWN: (0, speed),
            DIRECTION_LEFT: (-speed, 0),
            DIRECTION_UP: (0, -speed),
            DIRECTION_RIGHT: (speed, 0),
        }

    def calculate_images(self):
        self.images = {
            DIRECTION_DOWN: self.image_src,
            DIRECTION_LEFT: pygame.transform.rotate(self.image_src, 270),
            DIRECTION_UP: pygame.transform.rotate(self.image_src, 180),
            DIRECTION_RIGHT: pygame.transform.rotate(self.image_src, 90),
        }

    def undo(self):
        self.rect.center = self.previous_position

    def change_axis(self, new_axis):
        if new_axis == self.moving_on_axis:
            return
        x, y = self.rect.center
        if self.moving_on_axis != AXIS_Y:
            self.rect.center = (self.round_position_coord(x), y)
        else:
            self.rect.center = (x, self.round_position_coord(y))
        self.moving_on_axis = new_axis

    def round_position_coord(self, num):
        box_size = self.texture_loader.scaled_size
        resid = num % (box_size / 2)
        if resid == 0:
            return num
        if resid < (box_size / 4):
            return num - resid
        else:
            return num + (box_size / 2) - resid

    def move(self, direction):
        self.direction = direction
        self.facing = direction
        self.image = self.images[direction]

    def stop(self):
        self.direction = DIRECTION_NONE

    def update(self, delta):

        self.previous_position = self.rect.center
        dt = delta / 33.3

        if self.direction != DIRECTION_NONE:
            x, y = self.rect.center
            dx, dy = self.movements[self.direction]
            dx = round(self.texture_loader.scale_to_screen(dx * dt))
            dy = round(self.texture_loader.scale_to_screen(dy * dt))
            self.rect.center = (x + dx, y + dy)

    @property
    def moving(self):
        return self.direction != DIRECTION_NONE

    @property
    def stopped(self):
        return not self.moving


class NonMovableObject (Object):
    passable = False
    movable = False

    def __init__(self, position, texture_loader):
        Object.__init__(self)
        self.rect = pygame.Rect(self.image.get_rect())
        self.rect.center = position
        self.texture_loader = texture_loader
