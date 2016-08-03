#!/usr/bin/python
# coding=utf-8
import ConfigParser
import os, sys


class configReader(object):
    def __init__(self, configPath):
        self.configFile   = os.path.join(sys.path[0], configPath)
        self.cReader = ConfigParser.ConfigParser()
        self.cReader.read(self.configFile)

    def readConfig(self, section, item):
        return self.cReader.get(section, item)

    def getDict(self, section):
        dict = {}
        items = self.cReader.itmes(section)
        for key, value in items:
            dict[key] = value
        return dict

    def writeConfig(self, section, item, value):
        with open(self.configFile, 'w') as f:
            self.cReader.set(section, item, value)
            self.cReader.write(f)

