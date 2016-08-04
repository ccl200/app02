#!/usr/bin/python
# encoding=utf8
import wx
from wx import xrc
import wx.lib.buttons as buttons
import json
from student import Student
from configReader import configReader
import fun
from startThread import startThread
from wx.lib.pubsub import pub
from guiEvent import guiEvent

import sys
reload(sys)
sys.setdefaultencoding('utf8')

CONFIG_NAME = 'config.ini'

class MyApp(wx.App):
    def OnInit(self):
        self.socketPool = {}
        self.readConfig()
        self.rec = xrc.XmlResource('gui.xrc')
        self.init_frame()
        self.create_student(56)
        self.layout_stuent()
        self.bind_event()
        self.run()
        return True

    def init_frame(self):
        self.frame = self.rec.LoadFrame(None, "MyFrame")
        self.panel = xrc.XRCCTRL(self.frame, "m_panel")
        self.panel_grid_sizer = xrc.XRCCTRL(self.panel, "m_panel_grid_sizer")
        self.button_task_case = xrc.XRCCTRL(self.panel, "m_button_task_case")
        self.button_job_case  = xrc.XRCCTRL(self.panel, "m_button_job_case")
        self.button_file_case = xrc.XRCCTRL(self.panel, "m_button_file_case")
        self.button_select_all = xrc.XRCCTRL(self.panel, "m_button_select_all")
        self.button_reset     = xrc.XRCCTRL(self.panel, "m_button_reset")
        self.textCtrl = xrc.XRCCTRL(self.panel, "m_textCtrl")
        self.button_send_task = xrc.XRCCTRL(self.panel, "m_button_send_task")
        self.button_empty_task = xrc.XRCCTRL(self.panel , "m_button_empty_task")
        self.button_empty_job = xrc.XRCCTRL(self.panel , "m_button_empty_job")
        self.button_collection_job = xrc.XRCCTRL(self.panel, "m_button_collection_job")
        self.button_send_job = xrc.XRCCTRL(self.panel, "m_button_send_job")
        self.button_send_all = xrc.XRCCTRL(self.panel, "m_button_send_all")

        self.button_select_all.Disable()
        self.frame.Show()

    def readConfig(self):
        cf = configReader(CONFIG_NAME)
        self.config = {}
        self.config['button_student_choose_on'] = fun.toRgb(cf.readConfig('Colour', 'button_student_choose_on'))
        self.config['button_file_choose_on'] = fun.toRgb(cf.readConfig('Colour', 'button_file_choose_on'))
        self.config['button_choose_on'] = fun.toRgb(cf.readConfig('Colour', 'button_choose_on'))
        self.config['button_choose_off'] = fun.toRgb(cf.readConfig('Colour', 'button_choose_off'))
        self.config['host'] = cf.readConfig('Server','host')
        self.config['port'] = int(cf.readConfig('Server','port'))
        self.config['text_ctrl_colour'] = cf.readConfig('Font','text_ctrl_colour')
        self.config['text_ctrl_fontsize'] = cf.readConfig('Font','text_ctrl_fontsize')
        self.config['server_store_file_path'] = cf.readConfig('File','server_store_file_path')
        self.config['server_send_file_path'] = cf.readConfig('File', 'server_send_file_path')
        self.config['client_send_file_path'] = cf.readConfig('Client', 'client_send_file_path')
        self.config['client_store_file_path'] = cf.readConfig('Client', 'client_store_file_path')
        self.config['split_sep'] = cf.readConfig('File','split_sep')
        self.config['task'] = True
        self.config['job'] = False
        self.config['file'] = False

    def create_student(self,num):
        self.students = []
        for i in range(num):
            button = buttons.GenButton(self.panel_grid_sizer, -1, str(i+1),wx.DefaultPosition,(30,30),0)
            self.students.append(Student(button,self.config))

    def layout_stuent(self):
        gbs = wx.GridBagSizer(0,0)
        i = 0
        for j in range(8):#行数
            for n in range(7):#列数
                if i >= len(self.students):
                    break
                gbs.Add(self.students[i].button,(j,n),(1,1),wx.ALL|wx.EXPAND, 5)
                i+=1
        self.panel_grid_sizer.SetSizer(gbs)
        for i in range(7):
            gbs.AddGrowableCol(i, 1)
        for i in range(8):
            gbs.AddGrowableRow(i, 1)
        gbs.Fit(self.panel_grid_sizer)
        #自适应按钮
        self.frame.SetSizeHints(830,520)#最小尺寸
        size = self.frame.GetSize()
        self.frame.SetSize((size[0]+1,size[1]+1))

    def run(self):
        self.st = startThread(self.config,self.students,self.socketPool)
        self.st.setDaemon(True)
        self.st.start()

    def bind_data(self):
        data = [
            (wx.EVT_BUTTON, self.on_task_case, xrc.XRCID("m_button_task_case")),
            (wx.EVT_BUTTON, self.on_job_case, xrc.XRCID("m_button_job_case")),
            (wx.EVT_BUTTON, self.on_file_case, xrc.XRCID("m_button_file_case")),
            (wx.EVT_BUTTON, self.on_select_all, xrc.XRCID("m_button_select_all")),
            (wx.EVT_BUTTON, self.on_reset, xrc.XRCID("m_button_reset")),
            (wx.EVT_BUTTON, self.on_send_task, xrc.XRCID("m_button_send_task")),
            (wx.EVT_BUTTON, self.on_empty_task, xrc.XRCID("m_button_empty_task")),
            (wx.EVT_BUTTON, self.on_empty_job, xrc.XRCID("m_button_empty_job")),
            (wx.EVT_BUTTON, self.on_collection_job, xrc.XRCID("m_button_collection_job")),
            (wx.EVT_BUTTON, self.on_send_job, xrc.XRCID("m_button_send_job")),
            (wx.EVT_BUTTON, self.on_send_all, xrc.XRCID("m_button_send_all"))
        ]
        for student in self.students:
            data.append((wx.EVT_BUTTON, student.on_client, student.buttonId))
        return data

    def bind_event(self):
        pub.subscribe(self.frame.Refresh,'update')
        for data in self.bind_data():
            self.frame.Bind(data[0],data[1],id = data[2])

    def on_task_case(self,event):
        self.config['task'] = True
        self.config['job']  = False
        self.config['file'] = False
        self.button_task_case.SetDefault()
        self.button_select_all.Disable()
        for student in self.students:
            student.task_set_background_colour()
        self.frame.Refresh()

    def on_job_case(self,event):
        self.config['task'] = False
        self.config['job']  = True
        self.config['file'] = False
        self.button_job_case.SetDefault()
        self.button_select_all.Disable()
        for student in self.students:
            student.job_set_background_colour()
        self.frame.Refresh()

    def on_file_case(self,event):
        self.config['task'] = False
        self.config['job'] = False
        self.config['file'] = True
        self.button_file_case.SetDefault()
        self.button_select_all.Enable()
        for student in self.students:
            student.file_set_background_colour()
        self.frame.Refresh()

    def on_select_all(self,event):
        if self.config['file']:
            for t in self.socketPool:
                t.student.choose_file = True
                t.student.file_set_background_colour()
        self.frame.Refresh()

    def on_reset(self,event):
        for student in self.students:
            if(self.config['task']):
                student.choose_task = False
                student.task_set_background_colour()
            if(self.config['job']):
                student.choose_job  = False
                student.job_set_background_colour()
        self.frame.Refresh()

    def on_send_task(self,event):
        content = self.textCtrl.GetValue()
        for t in self.socketPool.values():
            t.sendJson({"type":"taskInfo","data":content})
            t.sendJson({"type":"taskButton","data":True})

    def on_empty_task(self,event):
        for t in self.socketPool.values():
            t.sendJson({"type": "taskInfo", "data": ""})
            t.sendJson({"type":"taskButton","data":False})

    def on_empty_job(self,event):
        for t in self.socketPool.values():
            t.sendJson({"type":"uploadButton","data":False})

    def on_collection_job(self,event):
        guiEvent(self.socketPool,self.config,"collectionJob")

    def on_send_job(self,event):
        pathnames = None
        dialog = wx.FileDialog(self.frame, u"选择文件", style=wx.FD_OPEN | wx.FD_MULTIPLE)
        if dialog.ShowModal() == wx.ID_OK:
            pathnames = dialog.GetPaths()
            guiEvent(self.socketPool, self.config,"sendFile", pathnames)
        dialog.Destroy()

    def on_send_all(self, event):
        guiEvent(self.socketPool, self.config, "allSendFile",self.config['server_send_file_path'])


if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()