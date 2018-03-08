#!/usr/bin/env python
#-*- coding: utf8 -*-

import os
import json
import logging


CONFIG_FILE = 'config.json'
DEFAULT_CONFIG = {}


def Parse():
    if not os.path.isfile(CONFIG_FILE):
        return DEFAULT_CONFIG

    try:
        with open(CONFIG_FILE, 'r') as fh:
            cfg = json.load(fh)
    except Exception as e:
        logging.error('Error decoding config: %s', e)
        return DEFAULT_CONFIG

    if not isinstance(cfg, dict):
        logging.error('Config is not a dict')
        return DEFAULT_CONFIG

    return cfg
