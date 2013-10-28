#!/usr/bin/env python
#-*- coding: utf8 -*-

from locals import *
from pygame.locals import *


class Gamepad (object):
    
    def __init__(self, joystick):
        self.joystick = joystick
    
    def process_events(self, events):
        event_queue = []
        for event in events:
            if event.type not in [JOYBUTTONDOWN, JOYHATMOTION]:
                continue
            if event.joy != self.joystick.get_id():
                continue
            if event.type == JOYBUTTONDOWN and event.button in [0, 1, 2, 3]:
                event_queue.append(EVENT_FIRE)
                continue
            
            if not event.type == JOYHATMOTION:
                continue
            
            if event.value == JOY_CENTERED:
                event_queue.append(EVENT_STOP)
            elif event.value == JOY_RIGHT:
                event_queue.append(EVENT_MOVE_RIGHT)
            elif event.value == JOY_LEFT:
                event_queue.append(EVENT_MOVE_LEFT)
            elif event.value == JOY_UP:
                event_queue.append(EVENT_MOVE_UP)
            elif event.value == JOY_DOWN:
                event_queue.append(EVENT_MOVE_DOWN)
        
        return event_queue


class KeyboardScheme (object):

    def __init__(self, scheme):
        self.left = scheme['left']
        self.right = scheme['right']
        self.up = scheme['up']
        self.down = scheme['down']
        self.fire = scheme['fire']


class Keyboard (object):
    
    def __init__(self):
        self.direction = None
        self.scheme = KeyboardScheme({
            'left': K_LEFT,
            'right': K_RIGHT,
            'up': K_UP,
            'down': K_DOWN,
            'fire': K_SPACE,
        })
    
    def process_events(self, events):
        
        event_queue = []
        for event in events:
            if not hasattr(event, 'key'):
                continue
            down = event.type == KEYDOWN
            
            if down:
                if event.key == self.scheme.right:
                    event_queue.append(EVENT_MOVE_RIGHT)
                    self.direction = EVENT_MOVE_RIGHT
                elif event.key == self.scheme.left:
                    event_queue.append(EVENT_MOVE_LEFT)
                    self.direction = EVENT_MOVE_LEFT
                elif event.key == self.scheme.up:
                    event_queue.append(EVENT_MOVE_UP)
                    self.direction = EVENT_MOVE_UP
                elif event.key == self.scheme.down:
                    event_queue.append(EVENT_MOVE_DOWN)
                    self.direction = EVENT_MOVE_DOWN
                elif event.key == self.scheme.fire:
                    event_queue.append(EVENT_FIRE)
            else:
                if event.key == self.scheme.right and self.direction == EVENT_MOVE_RIGHT:
                    event_queue.append(EVENT_STOP)
                elif event.key == self.scheme.left and self.direction == EVENT_MOVE_LEFT:
                    event_queue.append(EVENT_STOP)
                elif event.key == self.scheme.up and self.direction == EVENT_MOVE_UP:
                    event_queue.append(EVENT_STOP)
                elif event.key == self.scheme.down and self.direction == EVENT_MOVE_DOWN:
                    event_queue.append(EVENT_STOP)
        
        return event_queue


class Network (object):
    
    def __init__(self):
        pass
