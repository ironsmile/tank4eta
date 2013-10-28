#!/usr/bin/env python
#-*- coding: utf8 -*-

import random
from locals import *

class AI (object):

    moving_chance = 70
    turning_chance = 20

    def tick(self, enemies):

        for enemy in enemies:
            turning_roll = random.randint(0, 100)
            if  turning_roll <= self.turning_chance:
                pass
