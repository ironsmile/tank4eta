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
import os
import sys
import glob
import world
import pygame
import pygame.joystick
import controllers
import time


def main():
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    pygame.init()

    # Ignore mouse motion (greatly reduces resources when not needed)
    pygame.event.set_blocked(pygame.MOUSEMOTION)

    available_maps = glob.glob(os.path.join(MAPS_DIR, '*.map'))
    available_maps = map(lambda m: os.path.basename(m), available_maps)

    selected = {
        'players_count': 1,
        'map': available_maps[0],
        'exit': False,
        'toggle_fullscreen': False
    }

    render = Render()

    while 42:
        selected = main_menu(render, available_maps, selected)
        if selected['exit']:
            break
        if selected['toggle_fullscreen']:
            render.toggle_full_screen()
            continue
        pygame.mixer.init(buffer=512)
        main_loop(render, players_count=selected['players_count'], map_name=selected['map'])
        pygame.mixer.stop()

    render.quit()
    pygame.quit()
    sys.exit(0)


def main_menu(render, available_maps, selected):
    OPTION_DEFAULT_STATE = 0
    OPTION_ONE_PLAYER = 1
    OPTION_TWO_PLAYERS = 2
    OPTION_SELECT_MAP = 3
    OPTION_EXIT = 4

    def show_map_name():
        explain_text = 'Selected map: %s' % selected['map'][:-4]
        map_font = pygame.font.Font(None, 24)
        selected_map_text = map_font.render(explain_text, True, (160, 160, 160))
        text_x = (render.screen.get_width() - selected_map_text.get_width()) / 2
        text_y = render.screen.get_height() - selected_map_text.get_width() - 50
        render.screen.blit(selected_map_text, (text_x, text_y))

    map_names = map(lambda m: m[:-4], available_maps)

    # cleanup the display from any leftover stuff
    render.clear_screen()

    menu = cMenu(50, 50, 20, 5, 'vertical', 100, render.screen, [
        ('1 player', OPTION_ONE_PLAYER, None),
        ('2 players', OPTION_TWO_PLAYERS, None),
        ('Change Map', OPTION_SELECT_MAP, None),
        ('Exit', OPTION_EXIT, None),
    ])
    menu.set_center(True, True)
    menu.set_alignment('center', 'center')
    menu.set_refresh_whole_surface_on_load(True)

    mapSelectMenu = cMenu(50, 50, 20, 5, 'vertical', 100, render.screen, zip(
        map_names, available_maps, [None] * len(available_maps)
    ))
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

    # the meny while loop
    while 42:
        # Check if the state has changed, if it has, then post a user event to
        # the queue to force the menu to be shown at least once
        if prev_state != state:
            pygame.event.post(pygame.event.Event(EVENT_CHANGE_STATE, key=OPTION_DEFAULT_STATE))
            prev_state = state

            if state == OPTION_SELECT_MAP or state in available_maps:
                render.clear_screen()

        # Get the next event
        e = pygame.event.wait()

        # Quit if the user presses the exit button
        if e.type == pygame.QUIT:
            selected['exit'] = True
            break

        if e.type == KEYUP and e.key == K_F11:
            selected['toggle_fullscreen'] = True
            break

        # Update the menu, based on which "state" we are in - When using the menu
        # in a more complex program, definitely make the states global variables
        # so that you can refer to them by a name
        if e.type == pygame.KEYDOWN or e.type == EVENT_CHANGE_STATE:
            if state == OPTION_DEFAULT_STATE:
                changed_regions_list, state = menu.update(e, state)
                show_map_name()
            elif state == OPTION_ONE_PLAYER:
                selected['players_count'] = 1
                break
            elif state == OPTION_TWO_PLAYERS:
                selected['players_count'] = 2
                break
            elif state == OPTION_SELECT_MAP:
                changed_regions_list, state = mapSelectMenu.update(e, state)
            elif state in available_maps:
                selected['map'] = state
                changed_regions_list, state = menu.update(e, state)
                show_map_name()
            else:
                selected['exit'] = True
                break

        # Update the screen
        pygame.display.update(changed_regions_list)

    return selected


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

    clock = pygame.time.Clock()

    while 42:
        deltat = clock.tick(FRAMES)
        events = eventer.get_events()
        if eventer.game_stopped():
            stats = game_world.get_end_game_stats()
            render.draw_end_game_screen("You Gave Up! Why?", stats)
            break

        if eventer.toggled_full_screen():
            render.toggle_full_screen()

        game_state = game_world.tick(deltat, events)
        if game_state == GAME_OVER:
            stats = game_world.get_end_game_stats()
            render.draw_end_game_screen("GAME OVER. You've lost!", stats)
            break
        if game_state == GAME_WON:
            stats = game_world.get_end_game_stats()
            render.draw_end_game_screen("Yey! You've won!", stats)
            break
        render.draw(game_world.get_drawables())

    time.sleep(3)


if __name__ == '__main__':
    main()
