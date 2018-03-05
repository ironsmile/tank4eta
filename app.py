#!/usr/bin/env python
#-*- coding: utf8 -*-

from stuff_on_map import *
from pygame.locals import *
from locals import *
from utils import *
from player import Player
from render import Render
from event_manage import EventManager
from menu import cMenu, EVENT_CHANGE_STATE
from fonts import serif_normal
import os
import sys
import glob
import world
import world_map
import pygame
import argparse
import pygame.joystick
import controllers
import textures
import logging
import time

eventer = EventManager()


def main(args):
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    # Hint the window manager to put the window in the center of the screen
    os.putenv('SDL_VIDEO_CENTERED', '1')

    pygame.init()

    # Ignore mouse motion (greatly reduces resources when not needed)
    pygame.event.set_blocked(pygame.MOUSEMOTION)

    available_maps = glob.glob(os.path.join(MAPS_DIR, '*.map'))
    available_maps = [os.path.basename(m) for m in available_maps]
    available_maps.sort()

    selected = {
        'players_count': 1,
        'map': available_maps[0],
        'exit': False,
        'toggle_fullscreen': False
    }

    render = Render()

    if args.debug:
        render.show_fps = True

    while 42:
        selected = main_menu(render, available_maps, selected)
        if selected['exit']:
            break
        if selected['toggle_fullscreen']:
            render.toggle_full_screen()
            continue
        pygame.mixer.init(buffer=512)
        game_loop(render, players_count=selected['players_count'], map_name=selected['map'])
        pygame.mixer.stop()

    render.quit()
    pygame.quit()
    sys.exit(0)


def main_menu(render, available_maps, selected):
    OPTION_DEFAULT_STATE = 0
    OPTION_ONE_PLAYER = 1
    OPTION_TWO_PLAYERS = 2
    OPTION_EXIT = 4

    selected['toggle_fullscreen'] = False

    map_names = [m[:-4] for m in available_maps]

    # cleanup the display from any leftover stuff
    render.clear_screen()

    menu = cMenu(50, 50, 20, 5, 'vertical', 100, render.screen, [
        ('1 player', OPTION_ONE_PLAYER, None),
        ('2 players', OPTION_TWO_PLAYERS, None),
        ('Exit', OPTION_EXIT, None),
    ])
    menu.set_font(serif_normal)
    menu.set_center(True, True)
    menu.set_alignment('center', 'center')
    menu.set_refresh_whole_surface_on_load(True)

    mapSelectMenu = cMenu(50, 50, 20, 5, 'vertical', 100, render.screen, list(zip(
        map_names, available_maps, [None] * len(available_maps)
    )))
    mapSelectMenu.set_font(serif_normal)
    mapSelectMenu.set_center(True, True)
    mapSelectMenu.set_alignment('center', 'center')
    mapSelectMenu.set_refresh_whole_surface_on_load(True)

    # Create the state variables (make them different so that the user event is
    # triggered at the start of the "while 1" loop so that the initial display
    # does not wait for user input)
    state = OPTION_DEFAULT_STATE
    prev_state = OPTION_ONE_PLAYER

    # changed_regions_list is the list of pygame.Rect's that will tell pygame where to
    # update the screen (there is no point in updating the entire screen if only
    # a small portion of it changed!)
    changed_regions_list = []

    back_menu = None

    # the meny while loop
    while 42:
        # Check if the state has changed, if it has, then post a user event to
        # the queue to force the menu to be shown at least once
        if prev_state != state:
            pygame.event.post(pygame.event.Event(
                EVENT_CHANGE_STATE,
                key=OPTION_DEFAULT_STATE
            ))
            prev_state = state
            render.clear_screen()

            if state in [OPTION_ONE_PLAYER, OPTION_TWO_PLAYERS]:
                render.show_menu_instruction('Select Level')

        # Get the next event
        e = eventer.wait()

        if e.type == KEYUP and e.key == K_F11:
            selected['toggle_fullscreen'] = True
            break

        if e.type == KEYUP and e.key == K_ESCAPE and back_menu is not None:
            state = OPTION_DEFAULT_STATE

        # Update the menu, based on which "state" we are in - When using the menu
        # in a more complex program, definitely make the states global variables
        # so that you can refer to them by a name
        if e.type == pygame.KEYDOWN or e.type == EVENT_CHANGE_STATE:
            if state == OPTION_DEFAULT_STATE:
                back_menu = None
                changed_regions_list, state = menu.update(e, state)
            elif state == OPTION_ONE_PLAYER:
                selected['players_count'] = 1
                back_menu = menu
                changed_regions_list, state = mapSelectMenu.update(e, state)
            elif state == OPTION_TWO_PLAYERS:
                selected['players_count'] = 2
                back_menu = menu
                changed_regions_list, state = mapSelectMenu.update(e, state)
            elif state in available_maps:
                selected['map'] = state
                break
            else:
                selected['exit'] = True
                break

        # Update the screen
        pygame.display.update(changed_regions_list)

    return selected


def game_loop(render, players_count, map_name):
    texture_loader = textures.Loader()
    play_map = world_map.Map(map_path(map_name), render, texture_loader)
    play_map.build_grid()

    players = []

    for i in range(players_count):
        player = Player()
        player.name = 'Player %d' % i
        players.append(player)

    keyboard_controllers = controllers.keyboard_controls()
    pygame.joystick.init()
    for i in range(pygame.joystick.get_count()):
        if i >= len(players):
            break
        j = pygame.joystick.Joystick(i)
        j.init()
        players[i].controller = controllers.Gamepad(j)

    for player in players:
        if player.controller is not None:
            continue
        player.controller = next(keyboard_controllers)

    for i, position in enumerate(play_map.player_starts):
        if i >= players_count:
            break
        tank = Tank(position, texture_loader)
        players[i].tank = tank

    for player in players:
        if player.tank is None:
            raise Exception("Not enough start points for players!")

    game_world = world.World(play_map, players, texture_loader)
    game_world.init()

    clock = pygame.time.Clock()

    while 42:
        deltat = clock.tick(FRAMES)
        events = eventer.get_events()

        if eventer.game_stopped():
            pygame.mixer.pause()
            selected = pause_menu(render)
            if selected == PAUSE_MENU_QUIT:
                stats = game_world.get_end_game_stats()
                render.draw_end_game_screen("You Gave Up! Why?", stats)
                break
            else:
                render.draw_background()
                pygame.mixer.unpause()
                clock.tick()
                continue

        game_state = game_world.tick(deltat, events)
        if game_state == GAME_OVER:
            stats = game_world.get_end_game_stats()
            render.draw_end_game_screen("GAME OVER. You've lost!", stats)
            break
        if game_state == GAME_WON:
            stats = game_world.get_end_game_stats()
            render.draw_end_game_screen("Yey! You've won!", stats)
            break
        render.update_fps(clock)
        render.draw(game_world.get_drawables())

    time.sleep(3)


def pause_menu(render):
    OPTION_DEFAULT_STATE = 0

    menu = cMenu(50, 50, 20, 5, 'vertical', 100, render.screen, [
        ('Resume', PAUSE_MENU_RESUME, None),
        ('Quit Game', PAUSE_MENU_QUIT, None),
    ])
    menu.set_font(serif_normal)
    menu.set_center(True, True)
    menu.set_alignment('center', 'center')
    menu.set_refresh_whole_surface_on_load(True)

    # cleanup the display from any leftover stuff
    render.show_menu_instruction('Game Paused')

    state = OPTION_DEFAULT_STATE
    prev_state = PAUSE_MENU_RESUME
    changed_regions_list = []

    while 42:
        # Check if the state has changed, if it has, then post a user event to
        # the queue to force the menu to be shown at least once
        if prev_state != state:
            pygame.event.post(pygame.event.Event(
                EVENT_CHANGE_STATE,
                key=OPTION_DEFAULT_STATE
            ))
            prev_state = state

        # Get the next event
        e = eventer.wait()

        if e.type == pygame.KEYDOWN or e.type == EVENT_CHANGE_STATE:
            if state == OPTION_DEFAULT_STATE:
                changed_regions_list, state = menu.update(e, state)
            elif state == PAUSE_MENU_RESUME:
                return PAUSE_MENU_RESUME
            elif state == PAUSE_MENU_QUIT:
                return PAUSE_MENU_QUIT

        pygame.display.update(changed_regions_list)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='The game with tanks!.')
    parser.add_argument('-D', dest='debug', action='store_true',
                        default=False,
                        help='Start the game in debug mode')

    args = parser.parse_args()

    loggingLevel = logging.ERROR

    if args.debug:
        loggingLevel = logging.DEBUG

    logging.basicConfig(level=loggingLevel)
    main(args)
