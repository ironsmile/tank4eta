#!/usr/bin/env python
#-*- coding: utf8 -*-

from locals import *
from utils import sock_send_all, sock_recv_all

import time
import socket
import threading

SERVER_PORT = 4983
SERVER_HELLO = 'Hello Tanks'
SERVER_HELLO_REPLY = 'Hello Server'

class GameServer (object):
    
    def __init__ (self, players_count):
        self.clients = []
        self.exited_clients = []
        self.players = []
        self._players_count = players_count
        self.socket = None
        
        self.events = []
        
    
    def bind_socket (self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(socket.gethostname(), SERVER_PORT)
        self.socket.listen(5)
    
    def start (self):
        self.bind_socket()
        self.accept_loop()
        self.game_loop()
    
    def accept_loop (self):
        
        while 42:
            cl_sock, cl_addr = self.socket.accept()
            
            sock_send_all(cl_sock, SERVER_HELLO)
            reply = sock_recv_all(cl_sock, len(SERVER_HELLO_REPLY))
            if reply != SERVER_HELLO_REPLY:
                cl_sock.close()
                continue
            
            self.start_client(cl_sock)
            
            if len(self.players) >= self._players_count:
                break
    
    def game_loop (self):
        
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
            print self.events
            self.events = []
    
    def start_client(self, cl_sock):
        sc = ServerClientThread(self, cl_sock)
        sc.start()
    
    def debug (self, msg):
        print msg
    
    def add_player (self, player):
        id = len(self.players)
        player.id = id
        self.players.append(player)
        return id
    

class ServerClientThread (threading.Thread):
    def __init__ (self, srv, sock):
        threading.Thread(self)
        srv.clients.append(self)
        self.srv_client = ServerClient(srv, sock, self.name)
    
    def run (self):
        
        try:
            self.srv_client.run()
        except Exception as err:
            self.srv_client.debug("Exception: %s" % str(err))
        
        # LOOOCK!
        self.srv_client.srv.clients.remove(self)
        self.srv_client.srv.exited_clients.append(self)
        # LOOOCK!


class ServerClient (object):
    
    def __init__ (self, srv, sock, tname):
        self.socket = sock
        self.srv = srv
        self.players = []
        self.thread_name = tname
    
    def debug (self, msg):
        self.srv.debug("[%s] %s" % (self.thread_name, str(msg)))
    
    def run (self):
        self.populate_players()
        if len(self.players) < 1:
            self.debug("This thread does not have any players. Exiting.")
            return
        self.event_loop()
    
    
    def populate_playres (self):
        self.send_message({'msg': 'get_num_players'})
        players_count = self.receive_message()
        
        if players_count is None or players_count < 1:
            return
        
        for i in xrange(players_count):
            player = None
            # LOOOCK!
            self.srv.add_player(player)
            # LOOOCK!
            self.players.append(player)
            
        
    
    def event_loop (self):
        pass
    
