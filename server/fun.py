#!/usr/bin/python
# -*- coding: UTF-8 -*-
import re
import os
import socket

# 十六进制转RGB
def toRgb(tmp):
    opt = re.findall(r'(.{2})', tmp[1:])
    rgb = []
    for i in range(0, len(opt)):
        rgb.append(int(opt[i], 16))
    return tuple(rgb)

# 获取本机电脑名
def getName():
    name = socket.getfqdn(socket.gethostbyname())
    return name

# 获取本机内网IP
def getIp():
    addr = socket.gethostbyname(getName())
    return addr

# 检测端口占用
def detectionPort():
    pass
    '''
    ip=os.popen("ifconfig eth0|grep 'inet addr'|awk -F ':' '{print $2}'|awk '{print $1}'")
    ip=ip.read().strip()
    pid=os.popen("netstat -anp|grep 8998 |awk '{print $7}'").read().split('/')[0]
    os.popen('kill -9 {0}'.format(int(pid)))
    '''