#!/usr/bin/env python
#-*- coding: utf8 -*-

from locals import *
from server import SERVER_PORT
import socket


class GameClient (object):
    
    def __init__(self):
        self.socket = None
    
    def connect(self, server_ip):
        pass
