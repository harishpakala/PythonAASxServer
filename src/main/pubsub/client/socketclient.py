'''
Copyright (c) 2021-2022 OVGU LIA
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
'''
import json
import socket
import time
import threading
try:
    from pubsub.utils import SocketConfig,I40PacketS
except ImportError:
    from  main.utis import SocketConfig,I40PacketS

try:
    from pubsub.i40packet import I40Packet,I40PubSubPacket
except ImportError:
    from  main.i40packet import I40Packet,I40PubSubPacket


class SocketClient(object):
    def __init__(self,clientId,serverConfig:SocketConfig):
        self.clientId = clientId
        self.lastReconnect = "" 
        self.stayAlive = True
        self.serverConfig = serverConfig
        self.waitingtime = 10
        self.isConnected = False
        self.checkPublishAck = False
        self.subAck = False
        self.unSubAck = False
        self.description = ""
        self.on_message = None
        
    def create_socket(self):
        self.socketClient = socket.socket(self.serverConfig.AF_INET, self.serverConfig.SOCK_STREAM)

    def socket_send(self,sendmessage):
        try:
            self.socketClient.send(sendmessage)
            return True
        except Exception as E:
            str(E)
            return False
    
    def send_message(self,sendI40Packet:I40Packet):
        try:
            sendI40JSON = sendI40Packet.to_json()
            message = sendI40JSON.encode(self.serverConfig.encodingFormat)
            msg_length = len(message)
            send_length = str(msg_length).encode(self.serverConfig.encodingFormat)
            send_length += b' ' * (self.serverConfig.headerpacketsize - len(send_length))
            self.socket_send(send_length)
            time.sleep(2)
            if sendI40Packet.frame.type == "connect":
                thread = threading.Thread(target=self.handle_connect,)
                thread.start()
            self.socket_send(message)  
            return True
        except Exception as E:
            print(str(E))
            return False
    
    def handle_connect(self):
        try:
            while self.stayAlive:
                msg_length = self.socketClient.recv(self.serverConfig.headerpacketsize).decode(self.serverConfig.encodingFormat)
                if msg_length:
                    msg_length = int(msg_length)
                    msg = self.socketClient.recv(msg_length).decode(self.serverConfig.encodingFormat)
                    messagePacket = json.loads(str(msg))
                    i40Packet = I40Packet()
                    i40Packet.from_json(messagePacket)
                    _MESSAGETYPE = i40Packet.frame.type
                    if (_MESSAGETYPE == I40PacketS.CONNACK):
                        self.handle_connectack(i40Packet)
                    
                    elif (_MESSAGETYPE == I40PacketS.PUBACK):
                        self.handle_puback(i40Packet)
                        
                    elif  (_MESSAGETYPE == I40PacketS.SUBACK):
                        self.handle_suback(i40Packet)
                    
                    elif  (_MESSAGETYPE == I40PacketS.UNSUBACK):
                        self.handle_unsuback(i40Packet)
                        
                    elif  (_MESSAGETYPE == I40PacketS.PUBLISH):
                        self.handle_publish(i40Packet)
                                                
        except Exception as E:
            str(E)
            return False
            
    
    def connect(self,sourceId):
        try:
            self.create_socket()
            self.socketClient.connect((self.serverConfig.host,int(self.serverConfig.port)))
            self.connectwaitingtime = 10
            if self.on_message is None:
                return False
            connecti40packet = I40PubSubPacket()
            connecti40packet.create_connect_packet("eer",self.clientId,sourceId,"test","test","testC")
            incr = 0
            if (self.send_message(connecti40packet)):
                while not self.isConnected:
                    incr = incr + 1
                    time.sleep(1)
                    if (incr == self.connectwaitingtime and not self.isConnected):
                        return False
                return True
            else:
                return False            
        except Exception as E:
            print(str(E))
            return False
        
    def disconnect(self):
        try:
            self.stayAlive = False
            self.connectionHandle.close()
            return True
        except Exception as E:
            print(str(E))
            return False
        
    def publish(self,i40message):
        try:
            i40Packet = I40Packet()
            i40Packet.from_json(i40message)
            self.checkPublishAck = True
            incr = 0
            if  self.send_message(i40Packet):
                while self.checkPublishAck:
                    incr = incr + 1
                    time.sleep(1)
                    if (incr == self.waitingtime):
                        return False
                return True
            else:
                return False
        except Exception as E:
            print(str(E))
            return False
    
    def handle_publish(self,i40Packet):
        de = json.loads(i40Packet.to_json())
        self.on_message(de)
    
    def handle_puback(self,i40Packet):
        self.checkPublishAck = False
        
    def subscribe(self,sourceId,idslist):
        try:
            i40Packet = I40PubSubPacket()
            i40Packet.create_subscribe_packet("eer",self.clientId,sourceId,"test","test","testC")
            for _id in idslist:
                i40Packet.interactionElements.append(_id)
            self.subAck = True
            incr = 0
            if  self.send_message(i40Packet):
                while self.subAck:
                    incr = incr + 1
                    time.sleep(1)
                    if (incr == self.waitingtime):
                        return False
                return True
            else:
                return False
        except Exception as E:
            print(str(E))
            return False

    def handle_suback(self,i40Packet):
        self.subAck = False
    
    def unsubscribe(self,i40message,idslist):
        try:
            i40Packet = I40Packet()
            i40Packet.from_json(i40message)
            for _id in idslist:
                i40Packet.interactionElements.append()
            self.unSubAck = True
            incr = 0
            if  self.send_message(i40Packet):
                while self.unSubAck:
                    incr = incr + 1
                    time.sleep(1)
                    if (incr == self.waitingtime):
                        return False
                return True
            else:
                return False
        except Exception as E:
            print(str(E))
            return False
    
    def handle_unsuback(self,i40Packet):
        self.unSubAck = False

    def handle_connectack(self,i40Packet):
        try:
            if i40Packet.interactionElements[0] == "SUCCESS":
                self.isConnected = True
            else:
                pass
        except Exception as E:
            print(str(E))
    