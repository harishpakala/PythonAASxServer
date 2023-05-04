"""
Copyright (c) 2021-2022 OVGU LIA
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
"""
import socket


class I40PacketS(object):

    INITIATE = "initiate"
    ACKNOWLEDGE = "acknowledge"
    INSERT = "insert"
    DELETE = "delete"
    MODIFY = "modify"
    INSERTACK = "insertack"
    DELETEACK = "deleteack"
    MODIFYACK = "modifyack"
    MONITOR = "monitor"
    UNMONITOR = "unmonitor"
    READREQUEST = "readrequest"
    MONITORACK = "monitorack"
    READRESPOSE = "readresponse"
    NOTIFY = "notify"
    TERMINATE = "terminate"


class SocketConfig(object):
    def __init__(self, host, port, socketname):
        self.host = host
        self.port = port
        self.encodingformat = "utf-8"
        self.header = 64
        self.sessiontimout = 3600
        self.qos = 0
        self.reconnect_attempts = 4
        self.AF_INET = socket.AF_INET
        self.SOCK_STREAM = socket.SOCK_STREAM
        self.socketname = socketname
        self.headerpacketsize = 8
        self.listnername = socketname
    
    def set_encodingformat(self, encodingformat):
        self.encodingformat = encodingformat
    
    def set_header(self, header):
        self.header = header
    
    def set_qos(self, qos):
        self.qos = qos
    
    def set_sesiontimeout(self, sessiontimout):
        self.sessiontimout = sessiontimout
    
    def set_headerpacketsize(self, headerpacketsize):
        self.headerpacketsize = headerpacketsize