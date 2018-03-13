#!/usr/bin/env python
#-*- coding: utf8 -*-

from locals import *
from pygameMenu.locals import *
import config
import fonts
import logging
import pygame
import pygameMenu


class MainMenu(object):

    def __init__(self, cfg):
        self.cfg = cfg
        self.exit_pressed = False
        self.apply_selected = False
        self.game_started = False
        self.settings_changed = False
        self.selected = {}

    def on_select_players(self, count):
        logging.debug('selected %d player(s)', count)
        self.selected['players_count'] = count

    def on_select_map(self, game_map):
        logging.debug('selected map: %s', game_map)
        self.selected['map'] = game_map

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

    def on_game_start(self):
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

    l_menu = pygameMenu.Menu(render.screen, title=_('Select Level'), **menu_args)
    l_menu.add_option(_('Start Game'), mm_obj.on_game_start)
    l_menu.add_selector(
        _('Level:'),
        [m for m in zip(available_maps, available_maps)],
        mm_obj.on_select_map,
        None  # onreturn
    )
    l_menu.add_selector(
        _('Players:'),
        [
            (_('1 player'), 1),
            (_('2 players'), 2),
        ],
        mm_obj.on_select_players,
        None  # onreturn
    )
    l_menu.add_option(_('Back'), PYGAME_MENU_BACK)

    m_menu = pygameMenu.Menu(render.screen, title=_('Main Menu'), **menu_args)
    m_menu.add_option(_('New Game'), l_menu)
    m_menu.add_option(s_menu.get_title(), s_menu)
    m_menu.add_option(_('Exit'), mm_obj.on_exit)

    clck = pygame.time.Clock()
    while 42:
        clck.tick(60)
        events = pygame.event.get()
        m_menu.mainloop(events)
        if mm_obj.exitted():
            selected['exit'] = True
            break
        if mm_obj.apply_selected:
            mm_obj.apply_selected = False
            selected['new_settings_applied'] = True
            break
        if mm_obj.game_started:
            mm_obj.game_started = False
            break

    m_menu.disable()
    selected.update(mm_obj.selected)

    return selected


class PauseMenu(object):

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

    clck = pygame.time.Clock()
    while 42:
        clck.tick(60)
        events = pygame.event.get()
        p_menu.mainloop(events)
        if pm.resume:
            return PauseMenu.PAUSE_MENU_RESUME
        if pm.quit:
            return PauseMenu.PAUSE_MENU_QUIT
