"""
Copyright (c) 2021-2022 OVGU LIA
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
"""
try:
    from models.aas_basic_elements import Identification,Reference,Key
except ImportError:
    from  src.main.models.aas_basic_elements import Identification,Reference,Key
import jsonpickle
class Role(object):
    def __init__(self,name: str):
        self.name = name

class EndPoint(object):
    def __init__(self,identification:Identification,role:Role):
        self.identification = identification 
        self.role = role

class I40PacketHeader(object):
    def __init__(self,semanticProtocol : Reference, _type: str, messageId: str,
                      sender: EndPoint, receiver: EndPoint, replyBy: str,
                      replyTo: str,conversationId: str):
        self.semanticProtocol =  semanticProtocol
        self.type = _type
        self.messageId = messageId
        self.sender = sender
        self.receiver = receiver 
        self.replyBy = replyBy
        self.replyTo = replyTo
        self.conversationId = conversationId 

        
class I40Packet(object):
    def __init__(self):
        self.frame = dict()
        self.interactionElements = []
    
    def create_key(self,_type,local,value,index,idType):
        return Key(_type,local,value,index,idType)
    
    def create_reference(self,keys):
        return Reference([self.create_key(_key.type,_key.local,_key.value,_key.index,_key.idType) 
                          for _key in keys])
    
    def _create_reference(self,keys):
        return Reference([self.create_key(_key["type"],_key["local"],_key["value"],_key["index"],_key["idType"]) 
                          for _key in keys])
            
    def create_endpoint(self,endpoint):
        _identification = endpoint["identification"]
        _role = endpoint["role"]
        return EndPoint(Identification(_identification["id"],_identification["idType"]),Role(_role["name"]))
    
    
    def create_frame(self,semanticProtocol,_type,messageId,sender,receiver,
                                        replyBy,replyTo,conversationId):
        return I40PacketHeader(semanticProtocol,_type,messageId,
                                        sender,receiver,replyBy,replyTo,
                                        conversationId)    
    def from_json(self,i40Json):
        try:
            frame = i40Json["frame"]
            semanticProtocol = self._create_reference(frame["semanticProtocol"]["keys"])
            sender =  self.create_endpoint(frame["sender"]) if "sender" in frame else None 
            receiver =  self.create_endpoint(frame["receiver"]) if "receiver" in frame else None 
            self.frame = self.create_frame(semanticProtocol,frame["type"],frame["messageId"],
                                        sender,receiver,frame["replyBy"],frame["replyTo"],
                                        frame["conversationId"])
            self.interactionElements = i40Json["interactionElements"]
        except Exception as E:  
            raise RuntimeError('Unable to decode the Packet') from E
    
    
    def to_json(self):
        return jsonpickle.encode(self,unpicklable=False)    
    


class I40PubSubPacket(I40Packet):
    def __init__(self):
        super().__init__()

    def _create_endpoint(self,endpoint):
        return EndPoint(Identification(endpoint[0],endpoint[1]),Role(endpoint[2]))
    
    def create_semanticprotocol(self):
        _key = self.create_key("GlobalReference", False, "http://www.vdi.de/gma720/vdi2193_2/pubsub", 0, "IRI")
        return self.create_reference([_key])
    
    def _create_frame_header(self,sender,receiver):
        _sender = self._create_endpoint(sender)
        _receiver = self._create_endpoint(receiver)
        return (_sender,_receiver)
        
    def create_connect_packet(self,messageId,sender,receiver,replyBy,replyTo,conversationId):
        semanticProtocol = self.create_semanticprotocol()
        _sender,_receiver = self._create_frame_header([sender,"idShort","connectrequest"], [receiver,"idShort","connectaccepter"],)
        self.frame = self.create_frame(semanticProtocol,"connect",messageId,_sender,_receiver,replyBy,replyTo,conversationId)
        self.interactionElements = []
        
    def create_connectack_packet(self,messageId,sender,receiver,replyBy,replyTo,conversationId):
        semanticProtocol = self.create_semanticprotocol()
        _sender,_receiver = self._create_frame_header([sender,"idShort","connectprovider"], [receiver,"idShort","connectreceiver"],)  
        self.frame = self.create_frame(semanticProtocol,"connack",messageId,_sender,_receiver,replyBy,replyTo,conversationId)
        self.interactionElements = []
    
    def create_subscribe_packet(self,messageId,sender,receiver,replyBy,replyTo,conversationId):
        semanticProtocol = self.create_semanticprotocol()
        _sender,_receiver = self._create_frame_header(sender, receiver)
        self.frame = self.create_frame(semanticProtocol,"subscribe",messageId,_sender,_receiver,replyBy,replyTo,conversationId)
        self.interactionElements = []
    
    def create_subscribeack_packet(self,messageId,sender,receiver,replyBy,replyTo,conversationId):
        semanticProtocol = self.create_semanticprotocol()
        _sender,_receiver = self._create_frame_header(sender, receiver)
        self.frame = self.create_frame(semanticProtocol,"suback",messageId,_sender,_receiver,replyBy,replyTo,conversationId)
        self.interactionElements = []
    
    def create_disconnect_packet(self,messageId,sender,receiver,replyBy,replyTo,conversationId):
        semanticProtocol = self.create_semanticprotocol()
        _sender,_receiver = self._create_frame_header(sender, receiver)
        self.frame = self.create_frame(semanticProtocol,"disconnect",messageId,_sender,_receiver,replyBy,replyTo,conversationId)
        self.interactionElements = []
    
    def create_disconnectack_packet(self,messageId,sender,receiver,replyBy,replyTo,conversationId):
        semanticProtocol = self.create_semanticprotocol()
        _sender,_receiver = self._create_frame_header(sender, receiver)
        self.frame = self.create_frame(semanticProtocol,"disconnectack",messageId,_sender,_receiver,replyBy,replyTo,conversationId)
        self.interactionElements = []
    
    def create_unsubscribe_packet(self,_type,messageId,sender,receiver,replyBy,replyTo,conversationId):
        semanticProtocol = self.create_semanticprotocol()
        _sender,_receiver = self._create_frame_header(sender, receiver)
        self.frame = self.create_frame(semanticProtocol,"unsubscribe",messageId,_sender,_receiver,replyBy,replyTo,conversationId)
        self.interactionElements = []
    
    def create_unsubscribeack_packet(self,messageId,sender,receiver,replyBy,replyTo,conversationId):
        semanticProtocol = self.create_semanticprotocol()
        _sender,_receiver = self._create_frame_header(sender, receiver)
        self.frame = self.create_frame(semanticProtocol,"unsubscribeack",messageId,_sender,_receiver,replyBy,replyTo,conversationId)
        self.interactionElements = []
    
    def create_publish_packet(self,messageId,sender,receiver,replyBy,replyTo,conversationId):
        semanticProtocol = self.create_semanticprotocol()
        _sender,_receiver = self._create_frame_header([sender,"idShort","connectprovider"], [receiver,"idShort","connectreceiver"],)  
        self.frame = self.create_frame(semanticProtocol,"publish",messageId,_sender,_receiver,replyBy,replyTo,conversationId)
        self.interactionElements = []
    
    def create_publishack_packet(self,messageId,sender,receiver,replyBy,replyTo,conversationId):
        semanticProtocol = self.create_semanticprotocol()
        _sender,_receiver = self._create_frame_header(sender, receiver)
        self.frame = self.create_frame(semanticProtocol,"publishack",messageId,_sender,_receiver,replyBy,replyTo,conversationId)
        self.interactionElements = []
    