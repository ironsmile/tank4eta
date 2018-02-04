#!/usr/bin/env python
#-*- coding: utf8 -*-

from stuff_on_map import *
from pygame.locals import *
from locals import *
from utils import *
from player import Player
from render import Render
from event_manage import EventManager
import os
import sys
import world
import pygame
import pygame.joystick
import controllers
import time


def main():
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    pygame.init()
    pygame.mixer.init(buffer=512)
    render = Render()

    main_menu()
    main_loop(render, players_count=2, map_name="map2.map")

    pygame.mixer.stop()
    pygame.quit()
    sys.exit(0)


def main_menu():
    pass


def main_loop(render, players_count, map_name):
    play_map = world.Map()
    play_map.load(map_path(map_name))

    players = []

    for i in xrange(players_count):
        player = Player()
        player.name = 'Player %d' % i
        players.append(player)

    keyboard_controllers = controllers.keyboard_controls()
    pygame.joystick.init()
    for i in xrange(pygame.joystick.get_count()):
        if i >= len(players):
            break
        j = pygame.joystick.Joystick(i)
        j.init()
        players[i].controller = controllers.Gamepad(j)

    for player in players:
        if player.controller is not None:
            continue
        player.controller = keyboard_controllers.next()

    for i, position in enumerate(play_map.player_starts):
        if i >= players_count:
            break
        tank = Tank(position, play_map)
        players[i].tank = tank

    for player in players:
        if player.tank is None:
            raise Exception("Not enough start points for players!")

    game_world = world.World(play_map, players)
    eventer = EventManager()
    pygame.event.set_blocked(pygame.MOUSEMOTION)

    clock = pygame.time.Clock()

    while 42:
        deltat = clock.tick(FRAMES)
        events = eventer.get_events()
        if eventer.game_stopped():
            break
        if eventer.toggled_full_screen():
            render.toggle_full_screen()
        game_state = game_world.tick(deltat, events)
        if game_state == GAME_OVER:
            break
        render.draw(game_world.get_drawables())

    render.draw_end_screen()
    time.sleep(3)
    render.quit()


if __name__ == '__main__':
    main()
