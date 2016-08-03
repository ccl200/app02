#!/usr/bin/python
# -*- coding: UTF-8 -*-
import threading
import socket
import time

class heartbeatThread(threading.Thread):
    def __init__(self,socketPool = None):
        threading.Thread.__init__(self)
        self.socketPool = socketPool
        self.stop = False
        self.lock = threading.Lock()

    def run(self):
        while True:
            if not self.stop:
                for t in self.socketPool.keys():
                    try:
                        self.socketPool[t].send("heartbeat")
                    except socket.error, e:
                        print u'{}号电脑连接中断'.format(t)
                        self.lock.acquire()
                        self.socketPool[t].student.button.Disable()
                        del self.socketPool[t]
                        self.lock.release()
            time.sleep(5)