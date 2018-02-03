#!/usr/bin/env python
#-*- coding: utf8 -*-

import random
from locals import *


class AI (object):

    fire_chance = 1
    moving_chance = 70
    turning_chance = 5
    turns_list = [
        DIRECTION_UP,
        DIRECTION_DOWN,
        DIRECTION_LEFT,
        DIRECTION_RIGHT,
    ]

    def tick(self, enemies):

        for enemy in enemies:

            firing_roll = random.randint(0, 100)
            if firing_roll <= self.fire_chance:
                enemy.fire()

            turning_roll = random.randint(0, 100)
            if turning_roll <= self.turning_chance:
                turn_index = random.randint(0, 3)
                turn_direction = self.turns_list[turn_index]
                enemy.move(turn_direction)
                continue

            moving_roll = random.randint(0, 100)
            if moving_roll <= self.moving_chance:
                enemy.move(enemy.facing)
            else:
                enemy.stop()
