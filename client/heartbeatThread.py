#!/usr/bin/python
# -*- coding: UTF-8 -*-
import threading
import socket
import time

class heartbeatThread(threading.Thread):
    def __init__(self,pool = None):
        threading.Thread.__init__(self)
        self.pool = pool
        self.stop = False

    def run(self):
        while True:
            if not self.stop:
                for sock in self.pool:
                    try:
                        sock.send("heartbeat")
                    except socket.error, e:
                        print u'连接中断'.format(e)
                        sock.connected = False
                        sock.sock.close()
            time.sleep(5)