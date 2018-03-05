#!/usr/bin/env python
#-*- coding: utf8 -*-

import os
import glob
import pygame.transform
from objects import Object
from locals import TEXTURES_DIR


class AnimationException(Exception):
    pass


class Animation(Object):
    passable = True
    movable = True
    frame_time = 40  # ms
    directory = None
    texture_loader = None

    _looped = False

    def __init__(self, position):
        Object.__init__(self)
        self.frame = 0
        self._position = position
        self.frames = self._cls_frames[:]
        self.frames_count = len(self.frames)
        self._current_frame_time = 0
        self._finished = False
        self.load_frame()

    def update(self, deltat):
        if self._finished:
            return
        self._current_frame_time += deltat
        if self._current_frame_time < self.frame_time:
            return
        self.frame += 1
        if self.frame >= self.frames_count:
            if self._looped:
                self.frame = 0
            else:
                self._finished = True
                self.frame -= self.frames_count - 1
                return
        self._current_frame_time -= self.frame_time
        self.load_frame()

    def load_frame(self):
        self.image = self.frames[self.frame]
        self.rect = self.image.get_rect()
        self.rect.center = self._position

    def rotate(self, degrees):
        '''
            Returns a rotated animation from this one.
        '''
        new_frames = {}
        for ind, frame in enumerate(self.frames):
            new_frames[ind] = pygame.transform.rotate(frame, degrees)
        obj = self.__class__(self._position)
        obj.frames = new_frames
        return obj

    def current_frame(self):
        return self.frames[self.frame]

    def stop(self):
        self._finished = True

    def play(self):
        self._finished = False

    @classmethod
    def load_animation(cls, texture_loader):
        if cls.directory is None:
            raise AnimationException(
                'Animation of class {} does not have frams directory'.
                format(cls))

        cls._cls_frames.clear()
        cls.texture_loader = texture_loader

        images = glob.glob(os.path.join(cls.directory, '*.png'))
        images.sort()

        if len(images) < 1:
            raise AnimationException('No images found for animation')

        for image in images:
            cls._cls_frames.append(cls.texture_loader.load_texture(image))

    @property
    def finished(self):
        return self._finished


class BulletExplosion(Animation):
    directory = os.path.join(TEXTURES_DIR, 'animation_bullet_explosion')
    _cls_frames = []
    frame_time = 30


class FullSizeExplosion(Animation):
    directory = os.path.join(TEXTURES_DIR, 'animation_full_explosion')
    _cls_frames = []
    frame_time = 40


class PanzerTankMovement(Animation):
    directory = os.path.join(TEXTURES_DIR, 'player-panzer')
    _cls_frames = []
    frame_time = 20
    _looped = True


class BasicTankMovement(Animation):
    directory = os.path.join(TEXTURES_DIR, 'player-basic')
    _cls_frames = []
    frame_time = 20
    _looped = True
