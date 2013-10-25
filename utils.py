#!/usr/bin/env python
#-*- coding: utf8 -*-

from locals import *
import os


def sound_path(sound):
    return os.path.join(SOUNDS_DIR, sound)


def texture_path(texture):
    return os.path.join(TEXTURES_DIR, texture)


def map_path(mapf):
    return os.path.join(MAPS_DIR, mapf)


def sock_send_all(sock, data):
    return sock.sendall(data)


def sock_recv_all(sock, bytes):
    received = 0
    buf = ""
    while received < bytes:
        rbuf = sock.recv(bytes - received)
        received += len(rbuf)
        buf += rbuf
    return buf
