#!/usr/bin/python
# -*- coding: UTF-8 -*-
import threading
import os
import time
import glob

class guiEvent(threading.Thread):
    def __init__(self,socketPool,fun,*args):
        threading.Thread.__init__(self)
        self.socketPool = socketPool
        self.fun = fun
        self.args = args
        self.start()

    def run(self):
        if hasattr(self,self.fun):
            fun = getattr(self,self.fun)
            fun(self.args)


    def sendFile(self, list):
        pathnames = list[0]
        if pathnames is None:
            print u'发送列表为空'
            return False
        for pathname in pathnames:
            data = ''
            size = os.path.getsize(pathname)
            basename = os.path.basename(pathname)
            with open(pathname, 'rb') as f:
                data = f.read()
                for t in self.socketPool.values():
                    if t.student.choose_file:
                        t.sendFile(size, basename, data)

    def allSendFile(self,list):
        path = list[0]
        pathnames = self.getAllFile(path)
        pathDict = self.matchFile(pathnames)
        for key in pathDict.keys():
            for t in self.socketPool.values():
                if t.ip == key:
                    with open(pathDict[key], 'rb') as f:
                        data = f.read()
                        basename = os.path.basename(pathDict[key])
                        size = os.path.getsize(pathDict[key])
                        t.sendFile(size,basename,data)
                        continue

    def getAllFile(self,path):
        files = glob.glob(path + os.sep + '*')
        newfiles = []
        for file in files:
            if os.path.isfile(file):
                newfiles.append(file)
        return newfiles

    def matchFile(self,pathnames):
        pathDict = {}
        for pathname in pathnames:
            basename = os.path.basename(pathname)
            f = os.path.splitext(basename)[0]
            ip = f.split("##")[-1]
            pathDict[ip] = pathname
        return pathDict

    def collectionJob(self,list):
        for t in self.socketPool.values():
            t.sendJson({"type":"getStudentJobs"})