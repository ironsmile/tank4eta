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


PLAYERS = 2


def main():
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    pygame.mixer.init(buffer=512)
    
    play_map = world.Map()
    play_map.load(map_path("first_map.map"))
    
    players = []
    
    for i in xrange(PLAYERS):
        player = Player()
        player.name = 'Player %d' % i
        players.append(player)
    
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
        player.controller = controllers.Keyboard()
    
    for i, position in enumerate(play_map.player_starts):
        if i >= PLAYERS:
            break
        tank = Tank(position, play_map)
        players[i].tank = tank
    
    for player in players:
        if player.tank is None:
            raise Exception("Not enough start points for players!")
    
    game_world = world.World(play_map, players)
    render = Render(game_world)
    eventer = EventManager()

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
        render.draw()

    pygame.mixer.stop()
    render.draw_end_screen()
    time.sleep(3)
    render.quit()
    sys.exit(0)
            
    
if __name__ == '__main__':
    main()
