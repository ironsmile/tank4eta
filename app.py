#!/usr/bin/env python
#-*- coding: utf8 -*-

from animations import *
from event_manage import EventManager
from locals import *
from player import Player
from pygame.locals import *
from render import Render
from stuff_on_map import *
from utils import *
import argparse
import config
import controllers
import gettext
import glob
import language
import logging
import menu
import os
import pygame
import pygame.joystick
import sys
import textures
import time
import world
import world_map

gettext.install('tank4eta')
eventer = EventManager()


def main(args):
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    desired_lang = os.environ.get('LANGUAGE', 'en')[:2]
    cfg = config.Parse()

    if 'language' in cfg:
        desired_lang = cfg['language']
    else:
        cfg['language'] = desired_lang

    language.select(desired_lang)

    # Hint the window manager to put the window in the center of the screen
    os.putenv('SDL_VIDEO_CENTERED', '1')

    pygame.init()
    pygame.joystick.init()
    for i in range(pygame.joystick.get_count()):
        pygame.joystick.Joystick(i).init()

    # Ignore mouse motion (greatly reduces resources when not needed)
    pygame.event.set_blocked(pygame.MOUSEMOTION)
    pygame.mouse.set_visible(False)

    available_maps = glob.glob(os.path.join(MAPS_DIR, '*.map'))
    available_maps = [os.path.basename(m) for m in available_maps]
    available_maps.sort()

    selected = {
        'players_count': 1,
        'map': available_maps[0],
        'exit': False,
        'toggle_fullscreen': None,
        'language': None,
        'fullscreen': False,
        'new_settings_applied': False,
    }

    render = Render(fullscreen=cfg.get('fullscreen', False))

    if args.debug:
        render.show_fps = True

    while 42:
        selected['new_settings_applied'] = False
        selected = menu.main_menu(cfg, render, available_maps, selected)
        if selected['exit']:
            break
        if selected['toggle_fullscreen'] is not None:
            render.toggle_full_screen(selected['toggle_fullscreen'])
            selected['toggle_fullscreen'] = None
            continue
        if selected['language'] is not None:
            language.select(selected['language'])
            selected['language'] = None
            continue
        if selected['new_settings_applied']:
            continue
        pygame.mixer.init(buffer=512)
        game_loop(
            cfg,
            render,
            players_count=selected['players_count'],
            map_name=selected['map']
        )
        pygame.mixer.stop()

    render.quit()
    pygame.quit()
    sys.exit(0)


def game_loop(cfg, render, players_count, map_name):
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

    render.clear_screen()
    game_world = world.World(play_map, players, texture_loader)
    game_world.init()

    clock = pygame.time.Clock()
    end_message = None

    while 42:
        deltat = clock.tick(FRAMES)
        events = eventer.get_events()

        if eventer.game_stopped():
            pygame.mixer.pause()
            selected = menu.pause_menu(cfg, render)
            if selected == menu.PauseMenu.PAUSE_MENU_QUIT:
                end_message = _("You Gave Up! Why?")
                break
            else:
                render.clear_screen()
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
    time.sleep(2)


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
