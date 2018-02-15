#!/usr/bin/env python
#-*- coding: utf8 -*-

import pygame.image
import pygame.transform


class Loader(object):

    def __init__(self):
        self.textures = {}

    def set_dimensions(self, size, scaled_size, scale_factor):
        self.size = size
        self.scaled_size = scaled_size
        self.scale_factor = scale_factor

    def load_texture(self, path):
        if path in self.textures:
            return self.textures[path]
        texture = pygame.image.load(path).convert_alpha()
        if self.scaled_size != self.size and \
                texture.get_width() == self.size and \
                texture.get_height == self.size:
            texture = pygame.transform.smoothscale(
                texture,
                (self.scaled_size, self.scaled_size)
            )
        elif self.scale_factor != 1:
            new_w = round(self.scale_to_screen(texture.get_width()))
            new_h = round(self.scale_to_screen(texture.get_height()))
            texture = pygame.transform.smoothscale(
                texture,
                (new_w, new_h)
            )
        self.textures[path] = texture
        return self.textures[path]

    def scale_to_screen(self, val):
        return val * self.scale_factor
