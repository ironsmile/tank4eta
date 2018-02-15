#!/usr/bin/env python
#-*- coding: utf8 -*-

from locals import *
from utils import sock_send_all, sock_recv_all

import json
import time
import socket
import struct
import logging
import threading
import traceback

SERVER_PORT = 4983
SERVER_HELLO = 'Hello Tanks'
SERVER_HELLO_REPLY = 'Hello Server'

class DummyPlayer (object):
    pass


class GameServer (object):
    
    def __init__(self, players_count):
        self.clients = []
        self.exited_clients = []
        self.players = []
        self._players_count = players_count
        self.socket = None
        
        self.events = []
        self.server_global_lock = threading.Lock()
        
    def bind_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        hostname = '127.0.0.1'
        address = (hostname, SERVER_PORT)
        self.socket.bind(address)
        self.debug("Bound to address (%s, %d)" % address)
        self.socket.listen(5)
    
    def start(self):
        self.debug("Binding socket")
        self.bind_socket()
        self.debug("Accept loop")
        self.accept_loop()
        self.debug("Game loop")
        self.game_loop()
    
    def accept_loop(self):
        
        while 42:
            cl_sock, cl_addr = self.socket.accept()
            
            sock_send_all(cl_sock, SERVER_HELLO)
            reply = sock_recv_all(cl_sock, len(SERVER_HELLO_REPLY))
            if reply != SERVER_HELLO_REPLY:
                cl_sock.close()
                continue
            
            self.start_client(cl_sock)
            
            # op! Race condition. The thread which adds to the count
            # may be slower than this if.
            if len(self.players) >= self._players_count:
                break
    
    def game_loop(self):
        
        while 42:
            exited = []
            for c in self.exited_clients:
                c.join(0.01)
                if not c.is_alive():
                    exited.append(c)
            
            for c in exited:
                self.debug("Thread %s is dead. Cleaning up." % c.name)
                self.exited_clients.remove(c)
            
            time.sleep(1)
            self.debug("Events: %s" % str(self.events))
            self.events = []
    
    def start_client(self, cl_sock):
        sc = ServerClientThread(self, cl_sock)
        sc.start()
    
    def debug(self, msg):
        logging.debug(msg)
    
    def add_player(self, player):
        id = len(self.players)
        player.id = id
        self.players.append(player)
        return id

    def stop(self):
        for cl in self.clients:
            cl.stop()
            cl.join()
    

class ServerClientThread (threading.Thread):

    def __init__(self, srv, sock):
        threading.Thread.__init__(self)
        srv.clients.append(self)
        self.srv_client = ServerClient(srv, sock, self.name)
    
    def run(self):
        
        try:
            self.srv_client.run()
        except Exception as err:
            traceback.print_exc()
            self.srv_client.debug("Exception: %s" % str(err))
            self.srv_client.socket.close()
        
        self.srv_client.srv.server_global_lock.acquire()
        self.srv_client.srv.clients.remove(self)
        self.srv_client.srv.exited_clients.append(self)
        self.srv_client.srv.server_global_lock.release()

    def stop(self):
        self.srv_client.stop()


class ServerClient (object):
    
    def __init__(self, srv, sock, tname):
        self.socket = sock
        self.srv = srv
        self.players = []
        self.thread_name = tname
    
    def debug(self, msg):
        self.srv.debug("[%s] %s" % (self.thread_name, str(msg)))
    
    def run(self):
        self.populate_players()
        if len(self.players) < 1:
            self.debug("This thread does not have any players. Exiting.")
            self.socket.close()
            return
        self.event_loop()
    
    def populate_players(self):
        # self.send_message({'msg': 'get_num_players'})
        players_count = self.receive_message()

        self.debug("Players count received: %s" % str(players_count))
        
        if players_count is None or players_count < 1:
            return
        
        for i in range(players_count):
            player = DummyPlayer()
            self.srv.server_global_lock.acquire()
            self.srv.add_player(player)
            self.srv.server_global_lock.release()
            self.players.append(player)
            
    def event_loop(self):
        while 42:
            message = self.receive_message()
            self.debug(message)

    def send_message(self, msg):
        encoded_msg = json.dumps(msg)
        message = struct.pack('I%ds' % len(encoded_msg), len(encoded_msg), encoded_msg)
        self.socket.sendall(message)

    def receive_message(self):
        expected = sock_recv_all(self.socket, 4)
        (expected_bytes, ) = struct.unpack('I', expected)
        if expected_bytes < 0 or expected_bytes > 10e3:
            self.debug("Expected bytes: %d" % expected_bytes)
            return
        message_unpacked = sock_recv_all(self.socket, expected_bytes)
        (message_raw,) = struct.unpack('%ds' % expected_bytes, message_unpacked)
        return json.loads(message_raw)

    def stop(self):
        self.socket.close()

if __name__ == '__main__':
    try:
        server = GameServer(players_count=1)
        server.start()
    except Exception:
        traceback.print_exc()
        server.stop()
    except KeyboardInterrupt:
        logging.debug("Ctrl+C - Stopping")
        server.stop()
