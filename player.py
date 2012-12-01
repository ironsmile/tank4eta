#!/usr/bin/env python
#-*- coding: utf8 -*-

class Player (object):
    
    def __init__ (self):
        self.tank = None
        self.controller = None
        self.name = 'player'
    
    def process_events (self, events):
        if self.controller is None or self.tank is None: return
        my_events = self.controller.process_events(events)
        self.tank.process_events(my_events)

