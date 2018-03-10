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
from animations import *
import os
import sys
import glob
import world
import config
import world_map
import pygame
import argparse
import pygame.joystick
import controllers
import textures
import logging
import time
import gettext

# Testing a new menu class
import pygameMenu                # This imports classes and other things
from pygameMenu.locals import *  # Import constants (like actions)

gettext.install('tank4eta')
eventer = EventManager()


def main(args):
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    desired_lang = os.environ.get('LANGUAGE', 'en')[:2]
    cfg = config.Parse()

    if 'language' in cfg:
        desired_lang = cfg['language']

    lang = gettext.translation(
        'tank4eta',
        localedir='data/lang',
        languages=[desired_lang],
        fallback=True
    )
    lang.install()

    # Hint the window manager to put the window in the center of the screen
    os.putenv('SDL_VIDEO_CENTERED', '1')

    pygame.init()
    pygame.joystick.init()
    for i in range(pygame.joystick.get_count()):
        pygame.joystick.Joystick(i).init()

    # Ignore mouse motion (greatly reduces resources when not needed)
    pygame.event.set_blocked(pygame.MOUSEMOTION)

    available_maps = glob.glob(os.path.join(MAPS_DIR, '*.map'))
    available_maps = [os.path.basename(m) for m in available_maps]
    available_maps.sort()

    selected = {
        'players_count': 1,
        'map': available_maps[0],
        'exit': False,
        'toggle_fullscreen': False,
        'language': None,
        'fullscreen': False
    }

    render = Render(fullscreen=cfg.get('fullscreen', False))

    if args.debug:
        render.show_fps = True

    while 42:
        selected = main_menu(cfg, render, available_maps, selected)
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


def main_menu(cfg, render, available_maps, selected):
    OPTION_DEFAULT_STATE = 0
    OPTION_ONE_PLAYER = 1
    OPTION_TWO_PLAYERS = 2
    OPTION_SETTINGS = 5
    OPTION_EXIT = 4
    OPTION_SETTINGS_FULLSCREEN = 6
    OPTION_SETTINGS_WINDOWED = 10
    OPTION_CHANGE_LANGUAGE_BG = 7
    OPTION_CHANGE_LANGUAGE_EN = 9
    OPTION_BACK = 8
    OPTION_SETTINGS_APPLY = 5

    selected['toggle_fullscreen'] = False

    map_names = [m[:-4] for m in available_maps]

    # cleanup the display from any leftover stuff
    render.clear_screen()

    menu = cMenu(50, 50, 20, 5, 'vertical', 100, render.screen, [
        (_('1 player'), OPTION_ONE_PLAYER, None),
        (_('2 players'), OPTION_TWO_PLAYERS, None),
        (_('Settings'), OPTION_SETTINGS, None),
        (_('Exit'), OPTION_EXIT, None),
    ])
    configure_menu(menu)

    optionsMenu = cMenu(50, 50, 20, 5, 'Horizontal', 2, render.screen, [
        (_('Fullscreen'), OPTION_SETTINGS_FULLSCREEN, None),
        (_('Windowed'), OPTION_SETTINGS_WINDOWED, None),
        ('български', OPTION_CHANGE_LANGUAGE_BG, None),
        ('English', OPTION_CHANGE_LANGUAGE_EN, None),
        (_('Back'), OPTION_BACK, None),
        (_('Apply'), OPTION_SETTINGS_APPLY, None),
    ])
    configure_menu(optionsMenu)

    mapSelectMenu = cMenu(50, 50, 20, 5, 'vertical', 100, render.screen, list(zip(
        map_names, available_maps, [None] * len(available_maps)
    )))
    configure_menu(mapSelectMenu)

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
                render.show_menu_instruction(_('Select Level'))

        # Get the next event
        e = eventer.wait()

        if e.type == KEYUP and e.key == K_F11:
            selected['toggle_fullscreen'] = True
            break

        if is_back_button(e) and back_menu is not None:
            state = OPTION_DEFAULT_STATE

        # Update the menu, based on which "state" we are in - When using the menu
        # in a more complex program, definitely make the states global variables
        # so that you can refer to them by a name
        if is_menu_event(e):
            if state == OPTION_DEFAULT_STATE or state == OPTION_BACK:
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
            elif state == OPTION_SETTINGS:
                back_menu = menu
                changed_regions_list, state = optionsMenu.update(e, state)
            elif state in available_maps:
                selected['map'] = state
                break
            elif state == OPTION_EXIT:
                selected['exit'] = True
                break
            elif state == OPTION_SETTINGS_APPLY:
                state = OPTION_BACK

        # Update the screen
        pygame.display.update(changed_regions_list)

    return selected


def game_loop(render, players_count, map_name):
    texture_loader = textures.Loader()
    play_map = world_map.Map(map_path(map_name), render, texture_loader)
    play_map.build_grid()

    BulletExplosion.load_animation(texture_loader)
    FullSizeExplosion.load_animation(texture_loader)
    PanzerTankMovement.load_animation(texture_loader)
    BasicTankMovement.load_animation(texture_loader)
    EnemyOneMovement.load_animation(texture_loader)
    EnemyTwoMovement.load_animation(texture_loader)

    players = []

    for i in range(players_count):
        player = Player()
        player.name = _('Player %d') % i
        players.append(player)

    keyboard_controllers = controllers.keyboard_controls()
    for i in range(pygame.joystick.get_count()):
        if i >= len(players):
            break
        j = pygame.joystick.Joystick(i)
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
            raise Exception(_("Not enough start points for players!"))

    game_world = world.World(play_map, players, texture_loader)
    game_world.init()

    clock = pygame.time.Clock()
    end_message = None

    while 42:
        deltat = clock.tick(FRAMES)
        events = eventer.get_events()

        if eventer.game_stopped():
            pygame.mixer.pause()
            selected = pause_menu(render)
            if selected == PauseMenu.PAUSE_MENU_QUIT:
                end_message = _("You Gave Up! Why?")
                break
            else:
                render.draw_background()
                pygame.mixer.unpause()
                clock.tick()
                continue

        game_state = game_world.tick(deltat, events)
        if game_state == GAME_OVER:
            end_message = _("GAME OVER. You've lost!")
            break
        if game_state == GAME_WON:
            end_message = _("Yey! You've won!")
            break
        render.update_fps(clock)
        render.draw(game_world.get_drawables())

    for player in players:
        if player.tank is not None:
            player.tank.stop()

    while game_world.active_animations_count() > 0:
        deltat = clock.tick(FRAMES)
        events = eventer.get_events()
        game_world.tick_only_animations(deltat, events)
        render.update_fps(clock)
        render.draw(game_world.get_drawables())

    stats = game_world.get_end_game_stats()
    render.draw_end_game_screen(end_message, stats)
    time.sleep(3)


class PauseMenu(Object):

    PAUSE_MENU_RESUME = 100
    PAUSE_MENU_QUIT = 200

    def __init__(self):
        self.resume = False
        self.quit = False

    def on_select(self, c):
        if c == self.PAUSE_MENU_RESUME:
            self.resume = True
        elif c == self.PAUSE_MENU_QUIT:
            self.quit = True


def pause_menu(render):
    pm = PauseMenu()

    p_menu = pygameMenu.Menu(
        render.screen,
        window_width=render.aspect_resolution[0],
        window_height=render.aspect_resolution[1],
        menu_alpha=1,
        font=FONT_SERIF_PATH,
        onclose=PYGAME_MENU_DISABLE_CLOSE,
        title=_('Game Paused'),
        dopause=False,
        color_selected=ORANGE,
        menu_color_title=SILVER,
        menu_color=BLUE
    )

    p_menu.add_option(_('Resume'), pm.on_select, pm.PAUSE_MENU_RESUME)
    p_menu.add_option(_('Quit Game'), pm.on_select, pm.PAUSE_MENU_QUIT)

    while True:
        events = pygame.event.get()
        p_menu.mainloop(events)
        if pm.resume:
            return PauseMenu.PAUSE_MENU_RESUME
        if pm.quit:
            return PauseMenu.PAUSE_MENU_QUIT


def is_back_button(e):
    return (e.type == KEYUP and e.key == K_ESCAPE) or \
            (e.type == pygame.JOYBUTTONDOWN and e.button == 1)


def is_menu_event(e):
    motion_events_types = [
        pygame.KEYDOWN,
        pygame.JOYHATMOTION,
        pygame.JOYBUTTONDOWN,
        pygame.JOYAXISMOTION
    ]
    return e.type in motion_events_types or e.type == EVENT_CHANGE_STATE


def configure_menu(menu):
    menu.set_font(serif_normal)
    menu.set_center(True, True)
    menu.set_alignment('center', 'center')
    menu.set_refresh_whole_surface_on_load(True)
    menu.set_selected_color(ORANGE)


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
