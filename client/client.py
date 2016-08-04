#!/usr/bin/python
# -*- coding: UTF-8 -*-
import wx
from wx import xrc
from wx.lib.pubsub import pub
from clientSocket import clientSocket
from configReader import configReader
from heartbeatThread import heartbeatThread
import sys
reload(sys)
sys.setdefaultencoding('utf8')

CONFIG_PATH = 'config.ini'

class MyApp(wx.App):
    def OnInit(self):
        self.pool = []
        self.rec = xrc.XmlResource('gui.xrc')
        self.readConfig()
        self.init_frame()
        self.init_env()
        self.bind_event()
        self.runHeartBeat()
        self.run()
        return True

    def init_frame(self):
        self.frame = self.rec.LoadFrame(None,'MyFrame1')
        self.panel = xrc.XRCCTRL(self.frame, 'panel1')
        self.textCtrl1  = xrc.XRCCTRL(self.panel, 'm_textCtrl1')
        self.button_upload = xrc.XRCCTRL(self.panel, 'm_button_upload')
        self.button_misson = xrc.XRCCTRL(self.panel, 'm_button_misson')
        self.status_bar = xrc.XRCCTRL(self.frame, 'm_statusBar1')
        self.frame.Show()

    def init_env(self):
        self.textCtrl1.SetValue(u"目前没有任务,请等待。")
        self.status_bar.SetStatusText(u"提示: ", 0)
        self.button_upload.Disable()
        self.button_misson.Disable()


    def readConfig(self):
        self.config = {}
        self.cf = configReader(CONFIG_PATH)
        self.config['host'] = self.cf.readConfig('Server', 'host')
        self.config['port'] = int(self.cf.readConfig('Server', 'port'))
        self.config['timeOut'] = int(self.cf.readConfig('Server', 'timeOut'))
        self.config['sendDialog'] = self.cf.readConfig('Info', 'sendDialog')
        self.config['sendSuccess'] = self.cf.readConfig('Info', 'sendSuccess')
        self.config['sendError'] = self.cf.readConfig('Info', 'sendError')
        self.config['uploadDialog'] = self.cf.readConfig('Info', 'uploadDialog')
        self.config['uploadSuccess'] = self.cf.readConfig('Info', 'uploadSuccess')
        self.config['uploadError'] = self.cf.readConfig('Info', 'uploadError')
        self.config['waitTask'] = self.cf.readConfig('Info', 'waitTask')

    #绑定事件
    def bind_event(self):
        self.frame.Bind(wx.EVT_BUTTON, self.on_upload, self.button_upload)
        self.frame.Bind(wx.EVT_BUTTON, self.on_task, self.button_misson)
        pub.subscribe(self.frame.Refresh,"update")

    #作品上传按钮
    def on_upload(self, event):
        dialog = wx.MessageDialog(self.frame,u'',self.config['uploadDialog'],wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        if dialog.ShowModal() == wx.ID_OK:
            self.sock.uploadFile()
            self.status_bar.SetStatusText(u"提示:正在上传文件 ", 0)
        dialog.Destroy()


    #任务完成按钮
    def on_task(self, event):
        dialog = wx.MessageDialog(self.frame, '', self.config['sendDialog'], wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        if dialog.ShowModal() == wx.ID_OK:
            print "taskButton"
            self.sock.sendJson({"type":"taskButton","data":True})

    def run(self):
        self.sock = clientSocket(self.config,self,self.heartbeat)
        self.sock.setDaemon(True)
        self.sock.start()
        self.pool.append(self.sock)

    def runHeartBeat(self):
        self.heartbeat = heartbeatThread(self.pool)
        self.heartbeat.setDaemon(True)
        self.heartbeat.start()

if  __name__ == "__main__":
    app = MyApp()
    app.MainLoop()