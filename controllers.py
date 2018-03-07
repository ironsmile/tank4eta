#!/usr/bin/env python
#-*- coding: utf8 -*-

from locals import *
from pygame.locals import *


class Gamepad (object):

    def __init__(self, joystick):
        self.joystick = joystick
        self.moving_on_axis = None

    def process_events(self, events):
        event_queue = []
        for event in events:
            if event.type not in [JOYBUTTONDOWN, JOYHATMOTION, JOYAXISMOTION]:
                continue
            if event.joy != self.joystick.get_id():
                continue
            if event.type == JOYBUTTONDOWN and event.button in [0, 1, 2, 3]:
                event_queue.append(EVENT_FIRE)
                continue

            # The dead zone for analog inputs. Everything below this value would
            # be considered a random noise.
            dead_zone = 0.5

            if event.type == JOYHATMOTION:
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
            elif event.type == JOYAXISMOTION:
                if event.value > -dead_zone and event.value < dead_zone and \
                        event.axis == self.moving_on_axis:
                    event_queue.append(EVENT_STOP)
                    self.moving_on_axis = None
                elif event.axis == 1 and event.value < -dead_zone:
                    event_queue.append(EVENT_MOVE_UP)
                    self.moving_on_axis = event.axis
                elif event.axis == 1 and event.value > dead_zone:
                    event_queue.append(EVENT_MOVE_DOWN)
                    self.moving_on_axis = event.axis
                elif event.axis == 0 and event.value < -dead_zone:
                    event_queue.append(EVENT_MOVE_LEFT)
                    self.moving_on_axis = event.axis
                elif event.axis == 0 and event.value > dead_zone:
                    event_queue.append(EVENT_MOVE_RIGHT)
                    self.moving_on_axis = event.axis

        return event_queue


class KeyboardScheme (object):

    def __init__(self, scheme):
        self.left = scheme['left']
        self.right = scheme['right']
        self.up = scheme['up']
        self.down = scheme['down']
        self.fire = scheme['fire']


class Keyboard (object):

    def __init__(self, scheme):
        self.direction = None
        self.scheme = scheme

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


def keyboard_controls():
    schemas = [
        KeyboardScheme({
            'left': K_LEFT,
            'right': K_RIGHT,
            'up': K_UP,
            'down': K_DOWN,
            'fire': K_SPACE,
        }),

        KeyboardScheme({
            'left': K_a,
            'right': K_d,
            'up': K_w,
            'down': K_s,
            'fire': K_t,
        }),
    ]

    for scheme in schemas:
        yield Keyboard(scheme)
