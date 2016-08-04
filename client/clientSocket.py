#!/usr/bin/python
# -*- coding: UTF-8 -*-
import threading
import time
import socket
import os
import glob
import wx
import json
import re
from wx.lib.pubsub import pub

class clientSocket(threading.Thread):
    BUFFER_SIZE = 2048 * 100

    def __init__(self,config = None,gui = None,heartbeat = None):
        threading.Thread.__init__(self)
        self.sock = None
        self.stop = False
        self.connected = False
        self.config = config
        self.button_misson = gui.button_misson
        self.button_upload = gui.button_upload
        self.status_bar    = gui.status_bar
        self.textCtrl = gui.textCtrl1
        self.heartbeat = heartbeat

    def connect(self):
        startTime = time.time()
        timeDelta = 0
        while timeDelta <= self.config['timeOut']:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE,1)
                self.sock.connect((self.config['host'], self.config['port']))
                self.connected = True
                return True
            except Exception, e:
                print str(e)
                time.sleep(1)
                timeDelta = int(time.time() - startTime)
            if timeDelta >self.config['timeOut']:
                print u'连接超时'
                return False

    def run(self):
        while not self.stop:
            if not self.connected:
                print u'开始连接'
                if self.connect():
                    print u'连接成功'
            else:
                try:
                    data = self.recv(self.BUFFER_SIZE)
                    if data is not None:
                        self.analysis(data)
                except Exception, e:
                    print 'socket error, because:{}'.format(e)
                    self.connected = False
                    self.sock.close()
                    continue

    def analysis(self,data):
        m = re.findall(r"{.*}",data)
        if m:
            for i in m:
                try:
                    d = json.loads(i)
                    if d["type"] == "taskButton":
                        self.change_gui(self.button_misson, d['data'])
                    elif d["type"] == "uploadButton":
                        self.change_gui(self.button_upload, d['data'])
                    elif d["type"] == "file":
                        self.receiveFile(d)
                    elif d["type"] == "getStudentJobs":
                        self.uploadFile(d)
                    elif d["type"] == "taskInfo":
                        self.change_textCtrl(d['data'])
                    elif d["type"] == "EOF":
                        print u"上传成功"
                except Exception,e:
                    print str(e)

    def change_gui(self,button,status):
        button.Enable(status)
        wx.CallAfter(pub.sendMessage, "update")

    def change_textCtrl(self,content):
        self.textCtrl.SetValue(content)
        wx.CallAfter(pub.sendMessage, "update")

    def send(self,data):
        self.heartbeat.stop = True
        self.sock.sendall(data)
        self.heartbeat.stop = False

    def sendJson(self, data):
        self.heartbeat.stop = True
        self.sock.sendall(json.dumps(data))
        self.heartbeat.stop = False

    def recv(self,size):
        data = self.sock.recv(size)
        if len(data):
            if(data != "heartbeat"):
                return data
        return None

    def receiveFile(self,d):
        filesize = int(d["size"])
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
        pathname = os.path.join(d["client_store_file_path"], basename)
        with open(pathname, 'wb') as f:
            f.write(data)

    def sendFile(self,pathname):
        size = os.path.getsize(pathname)
        basename = os.path.basename(pathname)
        self.sendJson({"type":"file","size":size,"basename":basename})
        data = ""
        with open(pathname,"rb") as f:
            data = f.read()
        self.send(data)

    def uploadFile(self,d):
        path = d["client_send_file_path"]
        list = glob.glob(path + os.sep +'*')
        for l in list:
            if os.path.isfile(l):
                self.sendFile(l)






