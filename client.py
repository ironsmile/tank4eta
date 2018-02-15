#!/usr/bin/env python
#-*- coding: utf8 -*-

from locals import *
from utils import sock_send_all, sock_recv_all
from server import SERVER_PORT, SERVER_HELLO, SERVER_HELLO_REPLY

import traceback
import logging
import struct
import socket
import time
import json


class GameClient (object):
    
    def __init__(self, number_of_players):
        self.socket = None
        self.number_of_players = number_of_players

    
    def connect(self, server_address):

        self.debug("Connecting to %s" % server_address)
        self.socket = socket.create_connection((server_address, SERVER_PORT))
        self.debug("Connected.")
        hello = sock_recv_all(self.socket, len(SERVER_HELLO))

        if hello != SERVER_HELLO:
            self.socket.close()
            self.debug("Prompt was bullshit: %s" % hello)

        self.debug("Received prompt. Sending reply.")
        sock_send_all(self.socket, SERVER_HELLO_REPLY)

        self.debug("Sending number of players: %d" % self.number_of_players)
        self.send_message(self.number_of_players)

    def start(self, server_address):
        self.connect(server_address)
        self.main_loop()


    def main_loop(self):
        if self.socket is None:
            return

        self.debug("Main loop: lalala every few seconds")

        while 42:
            self.send_message("lalala")
            time.sleep(0.5)

    #!TODO: remove code duplication
    def send_message(self, msg):
        encoded_msg = json.dumps(msg)
        message = struct.pack('I%ds' % len(encoded_msg), len(encoded_msg), encoded_msg)
        self.socket.sendall(message)

    #!TODO: remove code duplication
    def receive_message(self):
        expected = sock_recv_all(self.socket, 4)
        (expected_bytes, ) = struct.unpack('I', expected)
        if expected_bytes < 0 or expected_bytes > 10e4:
            return
        message_raw = sock_recv_all(self.socket, expected_bytes)
        return json.loads(message_raw)

    def debug(self, message):
        logging.debug(message)


if __name__ == '__main__':
    try:
        client = GameClient(number_of_players=1)
        client.start('127.0.0.1')
    except Exception:
        traceback.print_exc()
        client.socket.close()
    except KeyboardInterrupt:
        logging.debug("Ctrl+C - Stopping")
        client.socket.close()
