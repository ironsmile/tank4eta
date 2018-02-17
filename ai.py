#!/usr/bin/env python
#-*- coding: utf8 -*-

import math
import random
import logging

from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.diagonal_movement import DiagonalMovement

from locals import *


class Random (object):
    '''
    The Random AI would just do some thing at random at predefined
    chance of happening. It may fire, move forward or turn at any
    direction.
    '''

    fire_chance = 1
    moving_chance = 70
    turning_chance = 5
    turns_list = [
        DIRECTION_UP,
        DIRECTION_DOWN,
        DIRECTION_LEFT,
        DIRECTION_RIGHT,
    ]

    def __init__(self, world):
        self.world = world

    def do_random_thing(self, enemy):
        firing_roll = random.randint(0, 100)
        if firing_roll <= self.fire_chance:
            enemy.fire()

        turning_roll = random.randint(0, 100)
        if turning_roll <= self.turning_chance:
            turn_index = random.randint(0, 3)
            turn_direction = self.turns_list[turn_index]
            enemy.move(turn_direction)
            return

        moving_roll = random.randint(0, 100)
        if moving_roll <= self.moving_chance:
            enemy.move(enemy.facing)
        else:
            enemy.stop()

    def tick(self, deltat, enemies):
        for enemy in enemies:
            self.do_random_thing(enemy)


class ZombieDriver (Random):
    '''
    The ZombieDriver AI would follow the player relentlessly around without any
    thought or self preservation mechanism!
    '''

    def __init__(self, world):
        self.world = world
        self.map = world.map
        self.pathfinder = AStarFinder(
            diagonal_movement=DiagonalMovement.never,
            time_limit=0.005
        )
        self.path_cache_duration = 1000

    def tick(self, deltat, enemies):
        interesting_objects = []

        for player in self.world.players:
            if player.tank is None:
                continue
            interesting_objects.append(player.tank.rect)

        for enemy in enemies:
            self.process_enemy(enemy, deltat, interesting_objects)

    def process_enemy(self, enemy, deltat, interesting_objects):
        enemy.update_path_duration(deltat)
        own_coords = enemy.rect
        own_grid_pos = self.map.world_to_grid_coords(own_coords.centerx, own_coords.centery)

        if enemy.path_duration <= self.path_cache_duration:
            self.continue_path(enemy, own_grid_pos)
            return

        heat_obj = None
        heat_dist = math.inf
        for obj in interesting_objects:
            dist = math.sqrt(
                abs(own_coords.centerx - obj.centerx) ** 2 +
                abs(own_coords.centery - obj.centery) ** 2
            )
            if dist < heat_dist:
                heat_dist = dist
                heat_obj = obj

        if heat_obj is None:
            logging.error("ZombieDriver AI finds nothing interesting on the map! How can that be!?")
            self.do_random_thing(enemy)
            return

        hobjx, hobjy = heat_obj.centerx, heat_obj.centery
        hobj_grid_pos = self.map.world_to_grid_coords(hobjx, hobjy)

        if hobj_grid_pos == enemy.current_target:
            enemy.reset_path_duration()
            self.continue_path(enemy, own_grid_pos)
            return

        # WTF!? You have to rebiuld the *whole* grid every time find_path is called!
        # Definately change to a better library or write A* myself.
        self.map.build_grid()

        pf_start = self.map.grid.node(*own_grid_pos)
        pf_end = self.map.grid.node(*hobj_grid_pos)

        path, runs = self.pathfinder.find_path(
            pf_start,
            pf_end,
            self.map.grid
        )

        enemy.set_current_path(path)
        self.continue_path(enemy, own_grid_pos)

    def continue_path(self, enemy, grid_pos):
        next_node = enemy.get_path_next(grid_pos)

        if next_node is None:
            self.do_random_thing(enemy)
            return

        direction = self.map.grid_direction(grid_pos, next_node)

        if direction == DIRECTION_NONE:
            logging.error("For some reason the calculate direction returned NONE after pathfinding")
            self.do_random_thing(enemy)
        else:
            enemy.move(direction)
