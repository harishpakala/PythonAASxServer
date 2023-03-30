'''
Copyright (c) 2021-2022 OVGU LIA
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
'''

class Generic(object):
    def __init__(self):
        pass
    
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
    
    def createFrame(self,I40Frame):
        frame = {
                    "semanticProtocol": {
                    "keys": [
                        {
                            "type": "GlobalReference",
                            "value": "ovgu.de/"+I40Frame["semanticProtocol"], 
                        }
                        ]
                    }, 
                    "type": I40Frame["type"],
                    "messageId": I40Frame["messageId"], 
                    "sender": {
                        "id": I40Frame["SenderAASID"],
                        "role": {
                            "name": I40Frame["SenderRolename"]
                            }
                        },
                    "conversationId": I40Frame["conversationId"],
                    "replyBy" : "",
                    "replyTo" : ""
                }
        
        if (I40Frame["ReceiverAASID"] != ""):
            frame["receiver"] = {
                                    "id": I40Frame["ReceiverAASID"], 
                                    "role": {
                                        "name": I40Frame["ReceiverRolename"]
                                    }
                                }
     
        return frame
    

  
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
    

