'''
Copyright (c) 2021-2022 OVGU LIA
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
'''
import uuid

class Generic(object):
    def __init__(self,aasID,skillName,semanticProtocol):
        self.aasID = aasID
        self.skillName = skillName
        self.semanticProtocol = semanticProtocol
    
    def toString(self,message32):
        message32 = message32.hex().rstrip("0")
        if len(message32) % 2 != 0:
            message32 = message32 + '0'
        message = bytes.fromhex(message32).decode('utf8')
        return message
    
    def getRestAPIFrame(self,aasId):
        I40Frame = {
                    "type":"RestRequest",
                    "messageId":"RestRequest",
                    "SenderAASID":aasId,
                    "SenderRolename":"restAPI",
                    "ReceiverAASID":"",
                    "rolename":"",
                    "replyBy":"NA",
                    "conversationId":"AASNetworkedBidding",
                    "semanticProtocol":"www.admin-shell.io/interaction/restapi"
                }
        return I40Frame
    
    def create_i40_message(self,oMessage,conVID,receiverId="",receiverRole= ""):
        frame = {
                    "semanticProtocol": {
                            "keys": [
                                {
                                    "type": "GlobalReference",
                                    "value": self.semanticProtocol, 
                                }
                            ],
                        "type" : "ExternalReference"
                    }, 
                    "type": oMessage,
                    "messageId": oMessage+"_"+str(uuid.uuid4()), 
                    "sender": {
                        "id": self.aasID,
                        "role": {
                            "name": self.skillName
                            }
                        },
                    "conversationId": conVID,
                    "replyBy" : "",
                    "replyTo" : ""
                }
        
        if (receiverId != ""):
            frame["receiver"] = {
                                    "id": receiverId, 
                                    "role": {
                                        "name": receiverRole
                                    }
                                }
     
        return {"frame" :frame, "interactionElements": []}
     
    def createHeartBeatMessage(self,assId,count):
        frame = {
                    "semanticProtocol": {
                    "keys": [
                        {
                            "type": "GlobalReference",
                            "local": "local", 
                            "value": "ovgu.de/heartbeat", 
                            "idType": False
                        }
                        ]
                    }, 
                    "type": "HeartBeat",
                    "messageId": "HeartBeat_"+str(count), 
                    "sender": {
                         "id": assId, 
                        "role": {
                            "name": "HeartBeatProtocol"
                            }
                        },
                    "conversationId": ""
                }

        frame["receiver"] = {
                                "id": "AASpillarbox", 
                                    "role": {
                                        "name": "HeartBeatHandler"
                                    }
                                }
     
        return {"frame":frame}             
    

