#!/usr/bin/python
# -*- coding: UTF-8 -*-
import socket
import threading
from socketThread import socketThread
from heartbeatThread import heartbeatThread
import fun

class startThread(threading.Thread):
    def __init__(self,config,students,socketPool):
        threading.Thread.__init__(self)
        self.config = config
        self.students = students
        self.sock = None
        self.socketPool = socketPool
        self.lock = threading.Lock()

    def run(self):
        self.connect()
        self.runHeartbeat()
        self.dispatch()

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.config['host'],self.config['port']))
            print u'服务器地址为  {}:{}'.format(self.config['host'],self.config['port'])
            self.sock.listen(5)
        except Exception, e:
            print u'服务器错误'.format(e)

    def runHeartbeat(self):
        self.heartbeat = heartbeatThread(self.socketPool)
        self.heartbeat.setDaemon(True)
        self.heartbeat.start()

    def dispatch(self):
        while True:
            if self.sock:
                try:
                    conn, addr = self.sock.accept()
                    print addr[0]
                    self.lock.acquire()
                    ip = addr[0]
                    name = str(int(ip[-2:]))
                    student = self.pair(name)
                    oneSock = socketThread(conn,student,ip,self.socketPool,self.heartbeat,self.config)
                    oneSock.setDaemon(True)
                    oneSock.start()
                    self.socketPool[name] = oneSock
                    self.lock.release()
                except Exception, e:
                    print str(e)
                    self.sock.close()
                    raise

    def pair(self,name):
        for student in self.students:
            if name == student.button.GetLabel():
                return student

