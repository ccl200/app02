#!/usr/bin/python
# -*- coding: UTF-8 -*-

class Student(object):
    def __init__(self, button = None,config = None, name = '', studentId = 0,):
        self.button = button
        self.buttonId = button.GetId()
        self.config = config
        self.name   = name
        self.studentId   = studentId
        self.button.Disable()
        self.activity = False
        self.choose_task = False
        self.choose_job  = False
        self.choose_file = False

    #按钮事件
    def on_client(self,event):
        if(self.config['task']):
            self.choose_task = not self.choose_task
            self.task_set_background_colour()
        if(self.config['job']):
            self.choose_job = not self.choose_job
            self.job_set_background_colour()
        if(self.config['file']):
            self.choose_file = not self.choose_file
            self.file_set_background_colour()

    def task_set_background_colour(self):
        self.button.SetBackgroundColour(self.config['button_choose_off'])
        if (self.choose_task):
            self.button.SetBackgroundColour(self.config['button_student_choose_on'])

    def job_set_background_colour(self):
        self.button.SetBackgroundColour(self.config['button_choose_off'])
        if (self.choose_job):
            self.button.SetBackgroundColour(self.config['button_choose_on'])

    def file_set_background_colour(self):
        self.button.SetBackgroundColour(self.config['button_choose_off'])
        if (self.choose_file):
            self.button.SetBackgroundColour(self.config['button_file_choose_on'])
