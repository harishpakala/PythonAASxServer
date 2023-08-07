"""
Copyright (c) 2021-2022 OVGU LIA
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
"""
from datetime import datetime,timedelta
try:
    from pubsub.utils import SocketConfig,I40PacketS
except ImportError:
    from  src.main.utis import SocketConfig,I40PacketS
    
try:
    import queue as Queue
except ImportError:
    import Queue as Queue     

import json
import threading
import time
import uuid

AASELEMENTS = ["Submodel"
                "Asset",
                "AssetAdministrationShell",
                "ConceptDescription",
                "Submodel",
                "AccessPermissionRule",
                "AnnotatedRelationshipElement",
                "BasicEvent",
                "Blob",
                "Capability",
                "ConceptDictionary",
                "DataElement",
                "File",
                "Entity",
                "Event",
                "MultiLanguageProperty",
                "Operation",
                "Property",
                "Range",
                "ReferenceElement",
                "RelationshipElement",
                "SubmodelElement",
                "SubmodelElementCollection",
                "View",
                "GlobalReference",
                "FragmentReference",
                "Constraint",
                "Formula",
                "Qualifier"]

try:
    from pubsub.i40packet import I40PubSubPacket,I40Packet
except ImportError:
    from  main.models.i40packet import I40PubSubPacket,I40Packet

class SocketSession(object):
    def __init__(self,connectionHandle,clientInfo,sessionname,encodingFormat,headerpacketsize,pyAAS,qos=0):
        self.connectionHandle = connectionHandle
        self.clientInfo = clientInfo
        self.sessionname = sessionname
        self.subscriptions = set([])
        self.lastReconnect = ""
        self.send_message_queue = Queue.Queue()
        self.client_status = []
        self.connected = True
        self.encodingFormat = encodingFormat
        self.headerpacketsize = headerpacketsize
        self.qos = qos
        self.pyAAS = pyAAS
        
    def add_subscription_message(self,subMessage):
        self.send_message_queue.put(subMessage)
    
    def get_send_message(self):
        try:
            return (list(self.send_message_queue.queue))[0]
        except Exception as E:
            print(str(E))
            return None
    
    def remove_send_message(self):
        try:
            self.send_message_queue.get()
            return True
        except Exception as E:
            print(str(E))
            return None
        
    def add_subscription(self,aasElement):
        self.subscriptions.add(aasElement)
    
    def delete_subscription(self,aasELement):
        self.subscriptions.remove(aasELement)
    
    def socket_send(self,sendMessage):
        try:
            self.connectionHandle.send(sendMessage)
            return True
        except Exception as E:
            str(E)
            return False
            
    def send_messages(self):
        try :
            while True:
                if self.send_message_queue.qsize() != 0:
                    sendI40Packet = self.get_send_message()
                    if sendI40Packet is not None:
                        message = sendI40Packet.encode(self.encodingFormat)
                        msg_length = len(message)
                        send_length = str(msg_length).encode(self.encodingFormat)
                        send_length += b' ' * (self.headerpacketsize - len(send_length))
                        self.socket_send(send_length)
                        self.socket_send(message)                     
                        if (self.socket_send(sendI40Packet)):
                            self.remove_send_message()
                        else:
                            if (self.qos == 0):
                                self.remove_send_message()
        except Exception as E:
            print(str(E))
            return False

    def create_send_connack(self,messageId,sender,receiver,replyBy,replyTo,conversationId):
        connAckPacket = I40PubSubPacket()
        connAckPacket.create_connectack_packet(messageId,sender,receiver,replyBy,replyTo,conversationId)
        connAckPacket.interactionElements.append("SUCCESS")
        self.send_message_queue.put(connAckPacket.to_json())
        
    def create_send_publishack(self,i40Packet,message):
        pubAckPacket = I40PubSubPacket()
        subscribe_ack = pubAckPacket.create_publish_packet(i40Packet)
        subscribe_ack.interactionElements.append(message)
        self.send_message_queue(pubAckPacket.to_json())
                        
    def handle_publish(self,i40Packet):
        if len(i40Packet.interactionElements) == 0:
            self.create__send_publishack(i40Packet,"data ELements are empty. nothing to publish")
            return 
        
        for dataElement in i40Packet.interactionElements:
            try:
                modelType = dataElement["modelType"]["name"]
                if modelType not in AASELEMENTS:
                    self.create__send_publishack(i40Packet,"The Data Element is not an AAS element ")
                else:
                    pass
            except Exception as E:
                print(str(E))
                self.create__send_publishack(i40Packet,"Error processing the publish request")
                
    def handle_subscribe(self,i40Packet):
        try:
            for subscriptionELem in i40Packet.interactionElements:
                try:
                    self.pyAAS.aasHashDict.__getHashEntry__(subscriptionELem).subscribers.add(self.sessionname)
                except Exception as E:
                    pass
            i40Packet = I40PubSubPacket()
            i40Packet.create_subscribeack_packet("ddd","jjjs",self.sessionname,"dd","fff","vvf")
            self.send_message_queue.put(i40Packet.to_json())
        except Exception as E:
            print(str(E))
            
    def handle_unsubscribe(self,i40Packet):
        try:
            for subscriptionELem in i40Packet.interactionElements:
                self.delete_subscription(subscriptionELem)
            i40Packet = I40PubSubPacket()
            i40Packet.create_unsubscribeack_packet("ddd","jjjs",self.sessionname,"dd","fff","vvf")
            self.send_message_queue.put(i40Packet.to_json())
        except Exception as E:
            print(str(E))        
    
    def handle_puback(self,i40Packet):
        if len(i40Packet.interactionElements) != 0:
            if str(i40Packet.interactionElements[0]) == "Error":
                # notify or create an event
                print(i40Packet.interactionElements[0])
    
    def handle_suback(self,i40Packet):
        if len(i40Packet.interactionElements) != 0:
            if str(i40Packet.interactionElements[0]) == "Error":
                # notify or create an event
                print(i40Packet.interactionElements[0])

    def handle_unsuback(self,i40Packet):
        if len(i40Packet.interactionElements) != 0:
            if str(i40Packet.interactionElements[0]) == "Error":
                # notify or create an event
                print(i40Packet.interactionElements[0])    
    
    def handle_connect(self):
        try:
            self.create_send_connack("ddd","jjjs",self.sessionname,"dd","fff","vvf")
            thread = threading.Thread(target=self.send_messages,)
            thread.start() 
            while self.connected:                              
                msg_length = self.connectionHandle.recv(self.headerpacketsize).decode(self.encodingFormat)
                if msg_length:
                    msg_length = int(msg_length)
                    msg = self.connectionHandle.recv(msg_length).decode(self.encodingFormat)
                    messagePacket = json.loads(str(msg))
                    i40Packet = I40Packet()
                    i40Packet.from_json(messagePacket)
                    MESSAGETYPE = i40Packet.frame.type

                    if MESSAGETYPE == I40PacketS.CONNECT:
                        pass                   
                    
                    if MESSAGETYPE == I40PacketS.PUBLISH:
                        self.handle_publish(i40Packet)
                        
                    elif MESSAGETYPE == I40PacketS.PUBACK:
                        self.handle_puback(i40Packet)
                        
                    elif MESSAGETYPE == I40PacketS.SUBSCRIBE:
                        self.handle_subscribe(i40Packet)

                    elif MESSAGETYPE == I40PacketS.SUBACK:
                        self.handle_suback(i40Packet)                        

                    elif MESSAGETYPE == I40PacketS.UNSUBSCRIBE:
                        self.handle_unsubscribe(i40Packet)
                        
                    elif MESSAGETYPE == I40PacketS.UNSUBACK:
                        self.handle_unsuback(i40Packet)
                        
                    elif MESSAGETYPE == I40PacketS.DISCONNECT:
                        self.stop_polling()
                    
                    else:
                        pass                    
            self.session_terminate()        
        except Exception as E:
            print(str(E))
    
    def stop_polling(self):
        self.connected = False
        return True
    
    def empty_send_messages(self):
        self.send_message_queue.clear()
        return True

    def empty_subscrptions(self):
        self.subscriptions.clear()
        return True
        
    def session_terminate(self):
        try:
            self.stop_polling()
            self.empty_send_messages()
            self.empty_subscrptions()
            i40Packet = I40PubSubPacket()
            disconnect_ack = i40Packet.create_disconnectack_packet()
            self.send_messages(disconnect_ack)
            time.sleep(2)
            self.connectionHandle.close()
        except Exception as E:
            print(str(E))

class SocketListner(object):
    def __init__(self,socketConfig:SocketConfig,serverInstance,pyAAS):
        self.socketConfig = socketConfig
        self.serverInstance = serverInstance
        self.listnerName = socketConfig.socketname
        self.sessions = dict()
        self.socketActive = True
        self.subsciptionListner = True
        self.subscription_forward_messages = Queue.Queue()
        self.pyAAS = pyAAS
    
    def subscriptionlistner(self):
        while self.subsciptionListner:
            if (self.subscription_forward_messages.qsize() != 0):
                new_subscription_forward = self.subscription_forward_messages.get()
                for subscriber in new_subscription_forward.subscribers:
                    try:
                        subscriptionI40Packet = I40PubSubPacket()
                        subscriptionI40Packet.create_publish_packet(str(uuid.uuid4()),"ddd",subscriber,"0000","0000","temp")
                        subscriptionI40Packet.interactionElements.append(new_subscription_forward.subscriptiondata)
                        self.sessions[subscriber].send_message_queue.put((subscriptionI40Packet.to_json()))
                    except Exception as E:
                        print(str(E))
                        
    def socket_start(self):
        ADDR = (self.socketConfig.host,int(self.socketConfig.port))
        self.serverInstance.bind(ADDR)
        sLthread = threading.Thread(target=self.subscriptionlistner,)
        sLthread.start()
        self.serverInstance.listen()
        self.socket_poll()
        print("socket listners are activated" + str(ADDR))

    def socket_poll(self):
        while self.socketActive:
            try:
                conn, addr = self.serverInstance.accept()
                messagePacket = dict()
                while True:
                    msg_length = str(conn.recv(self.socketConfig.headerpacketsize).decode(self.socketConfig.encodingFormat))
                    msg_length = int(msg_length)
                    msg = conn.recv(msg_length).decode(self.socketConfig.encodingFormat)
                    messagePacket = json.loads(str(msg))
                    i40Packet = I40Packet()                    
                    i40Packet.from_json(messagePacket)
                    break
                self.handle_packet(i40Packet,conn, addr)
            except Exception as E:
                print(str(E))
        
    def create_session(self,connectionHandle,addr,sessionname):
        sokcetClient = SocketSession(connectionHandle,addr,sessionname,self.socketConfig.encodingFormat,self.socketConfig.headerpacketsize,self.pyAAS)
        self.sessions[sessionname] = sokcetClient
        thread = threading.Thread(target=sokcetClient.handle_connect,)
        thread.start()
        
    def delete_seesion(self,sessionname):
        self.sessions[sessionname].session_terminate()
        del self.sessions[sessionname]
        
    def reactivate_session(self,sessionname):
        self.session[sessionname].lastReconnect = ((datetime.now()+ timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S.%f"))[:-3]
    
    def handle_packet(self,i40Packet,conn, addr):
        try:
            if (i40Packet.frame.type == "connect"):
                if "sessionname" not in self.sessions:
                    self.create_session(conn,addr,i40Packet.frame.sender.identification.id)
                else:
                    self.reactivate_session()
            else:
                conn.close()
        except Exception as E:
            print(str(E))
            conn.close()
    
    def clear_subscription_forward_messages(self):
        self.subscription_forward_messages.clear()
    
    def socket_shutdown(self):
        # stopping the socket listner to accept any new incoming connection requests
        self.socketActive = False
        
        if (self.subscription_forward_messages.qsize() != 0):
            print("All SUBSCRIPTION messages are not yet handled")
        
        # stopping the subscription listner to process any pending subscription messages
        self.subsciptionListner = False
        self.clear_subscription_forward_messages()
        
        for sessionname in self.sessions.keys():
            self.sessionname[sessionname].session_terminate()
        print("All the active client connections are closed")
        self.socketIntance.shutdown()