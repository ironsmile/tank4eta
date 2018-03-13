#!/usr/bin/env python
#-*- coding: utf8 -*-

from stuff_on_map import *
from pygame.locals import *
from locals import *
from utils import *
from player import Player
from render import Render
from event_manage import EventManager
from animations import *
import os
import sys
import glob
import world
import fonts
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
    else:
        cfg['language'] = desired_lang

    select_language(desired_lang)

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
        'back_to_main_menu': False,
    }

    render = Render(fullscreen=cfg.get('fullscreen', False))

    if args.debug:
        render.show_fps = True

    while 42:
        selected = main_menu(cfg, render, available_maps, selected)
        if selected['exit']:
            break
        if selected['toggle_fullscreen'] is not None:
            render.toggle_full_screen(selected['toggle_fullscreen'])
            selected['toggle_fullscreen'] = None
            continue
        if selected['language'] is not None:
            select_language(selected['language'])
            selected['language'] = None
            continue
        if selected['back_to_main_menu']:
            selected['back_to_main_menu'] = False
            continue
        pygame.mixer.init(buffer=512)
        game_loop(cfg, render, players_count=selected['players_count'], map_name=selected['map'])
        pygame.mixer.stop()

    render.quit()
    pygame.quit()
    sys.exit(0)


def select_language(desired_lang):
    lang = gettext.translation(
        'tank4eta',
        localedir='data/lang',
        languages=[desired_lang],
        fallback=True
    )
    lang.install()
    if desired_lang == 'jp':
        fonts.switch_to_japanese()
    else:
        fonts.switch_to_western()


class MainMenu(Object):

    def __init__(self, cfg):
        self.cfg = cfg
        self.exit_pressed = False
        self.apply_selected = False
        self.game_started = False
        self.settings_changed = False
        self.back_button_pressed = False
        self.selected = {}

    def on_select_players(self, render, count, available_maps):
        logging.debug('selected %d player', count)
        self.selected['players_count'] = count

        menu_args = self.get_menu_args(render)
        l_menu = pygameMenu.Menu(render.screen, title=_('Select Level'), **menu_args)
        l_menu.add_selector(
            _('Level:'),
            [m for m in zip(available_maps, available_maps)],
            None,  # onchange
            self.on_game_start
        )
        l_menu.add_option(_('Back'), self.on_back_button)

        while True:
            events = pygame.event.get()
            l_menu.mainloop(events)
            if self.game_started:
                break
            if self.back_button_pressed:
                self.back_button_pressed = False
                break

    def on_back_button(self):
        self.back_button_pressed = True

    def exitted(self):
        return self.exit_pressed

    def on_apply_settings(self):
        self.apply_selected = True
        if not self.settings_changed:
            return
        config.Store(self.cfg)
        self.settings_changed = False

    def on_exit(self):
        self.exit_pressed = True

    def on_screen_setting_change(self, c):
        if c is ScreenSetting.windowed and self.cfg.get('fullscreen', False):
            logging.debug('Changed to windowed')
            self.cfg['fullscreen'] = False
            self.settings_changed = True
            self.selected['toggle_fullscreen'] = False
        if c is ScreenSetting.fullscreen and not self.cfg.get('fullscreen', False):
            logging.debug('Changed to fullscreen')
            self.cfg['fullscreen'] = True
            self.settings_changed = True
            self.selected['toggle_fullscreen'] = True

    def on_language_setting_change(self, c):
        if self.cfg.get('langauge', None) == c:
            return
        logging.debug('Selected language %s', c)
        self.cfg['language'] = c
        self.settings_changed = True
        self.selected['language'] = c

    def on_game_start(self, selected_map):
        self.selected['map'] = selected_map
        self.game_started = True

    def get_menu_args(self, render):
        return {
            'window_width': render.screen.get_width(),
            'window_height': render.screen.get_height(),
            'menu_width': render.screen.get_width(),
            'menu_height': render.screen.get_height(),
            'font': fonts.get_serif_path(),
            'onclose': PYGAME_MENU_DISABLE_CLOSE,
            'dopause': False,
            'color_selected': ORANGE,
            'menu_color_title': SILVER,
            'menu_color': BACKGROUND_COLOUR,
        }


def main_menu(cfg, render, available_maps, selected):
    mm_obj = MainMenu(cfg)
    menu_args = mm_obj.get_menu_args(render)

    screen_settings = [
        (_('Windowed'), ScreenSetting.windowed),
        (_('Fullscreen'), ScreenSetting.fullscreen),
    ]

    # Make sure the value from cfg is currently selected
    if cfg.get('fullscreen'):
        screen_settings.reverse()

    language_settings = [
        ('български', 'bg'),
        ('English', 'en'),
        (_('Japanese'), 'jp'),
    ]

    # Make sure the value from cfg is currently selected
    if 'en' == cfg.get('language', 'en'):
        lng = language_settings.pop(1)
        language_settings.insert(0, lng)

    # Make sure the value from cfg is currently selected
    if 'jp' == cfg.get('language', 'en'):
        lng = language_settings.pop(2)
        language_settings.insert(0, lng)

    s_menu = pygameMenu.Menu(render.screen, title=_('Settings'), **menu_args)
    s_menu.add_selector(
        _('Screen:'),
        screen_settings,
        mm_obj.on_screen_setting_change,
        None  # onreturn
    )
    s_menu.add_selector(
        _('Language:'),
        language_settings,
        mm_obj.on_language_setting_change,
        None  # onreturn
    )
    s_menu.add_option(_('Apply Settings'), mm_obj.on_apply_settings)
    s_menu.add_option(_('Back'), PYGAME_MENU_BACK)

    m_menu = pygameMenu.Menu(render.screen, title=_('Main Menu'), **menu_args)
    m_menu.add_option(
        _('1 player'), mm_obj.on_select_players,
        render, 1, available_maps
    )
    m_menu.add_option(
        _('2 players'), mm_obj.on_select_players,
        render, 2, available_maps
    )
    m_menu.add_option(s_menu.get_title(), s_menu)
    m_menu.add_option(_('Exit'), mm_obj.on_exit)

    while True:
        events = pygame.event.get()
        m_menu.mainloop(events)
        if mm_obj.exitted():
            selected['exit'] = True
            break
        if mm_obj.apply_selected:
            mm_obj.apply_selected = False
            selected['back_to_main_menu'] = True
            break
        if mm_obj.game_started:
            mm_obj.game_started = False
            break

    selected.update(mm_obj.selected)

    return selected


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
            selected = pause_menu(cfg, render)
            if selected == PauseMenu.PAUSE_MENU_QUIT:
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


def pause_menu(cfg, render):
    pm = PauseMenu()

    p_menu = pygameMenu.Menu(
        render.screen,
        window_width=render.screen.get_width(),
        window_height=render.screen.get_height(),
        menu_width=render.screen.get_width(),
        menu_height=render.screen.get_height(),
        menu_alpha=1,
        font=fonts.get_serif_path(),
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
