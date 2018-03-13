#!/usr/bin/env python
#-*- coding: utf8 -*-

import fonts
import gettext


def select(desired_lang):
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
