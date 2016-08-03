#!/usr/bin/python
# -*- coding: UTF-8 -*-
import time
import threading
import os
import wx
from wx.lib.pubsub import pub
import json
import re

class socketThread(threading.Thread):
    BUFFER_SIZE = 2048*100
    PATHNAME = "d:/"
    def __init__(self, conn = None, student = None, ip = None, socketPool = None,heartbeat = None):
        threading.Thread.__init__(self)
        print u'接收到来自:{}的连接'.format(ip)
        self.conn = conn
        self.student = student
        self.ip = ip
        self.socketPool = socketPool
        self.lock = threading.Lock()
        self.student.button.Enable()
        self.student.activity = True
        self.heartbeat = heartbeat

    def getIp(self):
        return self.ip

    def send(self, info):
        self.heartbeat.stop = True
        self.conn.sendall(info)
        self.heartbeat.stop = False

    def sendJson(self, info):
        self.heartbeat.stop = True
        self.conn.sendall(json.dumps(info))
        self.heartbeat.stop = False

    def recv(self,size):
        data = self.conn.recv(size)
        if len(data):
            if(data != "heartbeat"):
                return data
        return ''

    def run(self):
        while True:
            try:
                data = self.recv(self.BUFFER_SIZE)
                #分析内容
                self.analysis(data)
            except Exception, e:
                print u'socket 连接中断,{}'.format(e)
                name = str(int(self.ip[-2:]))
                self.lock.acquire()
                if name in self.socketPool.keys():
                    self.socketPool[name].student.button.Disable()
                    del self.socketPool[name]
                self.lock.release()
                break

    def analysis(self,data):
        m = re.findall(r"{.*}",data)
        if m:
            for i in m:
                try:
                    d = json.loads(i)
                    if d["type"] == "taskButton":
                        self.receiveTaskButton(d["data"])
                    elif d["type"] == "file":
                        self.receiveFile(d)
                    elif d["type"] == "EOF":
                        print u"上传成功"
                except Exception,e:
                    print str(e)

    def receiveFile(self,d):
        filesize = int(d['size'])
        restsize = filesize
        basename = d["basename"]
        data = ""
        startTime = time.time()
        while True:
            if restsize > self.BUFFER_SIZE:
                data += self.recv(self.BUFFER_SIZE)
            else:
                data += self.recv(restsize)
            restsize = filesize - len(data)
            if (time.time() - startTime > 30) or (restsize <= 0):
                break
        pathname = os.path.join(self.PATHNAME,basename)
        with open(pathname,'wb') as f:
            f.write(data)

    def receiveTaskButton(self,d):
        self.student.choose_task = d
        self.student.task_set_background_colour()
        #更新界面
        wx.CallAfter(pub.sendMessage,'update')

    def sendFile(self,size,basename,data):
        self.sendJson({"type":"file","size":size,"basename":basename})
        self.send(data)



