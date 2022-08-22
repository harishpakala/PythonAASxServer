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
                            "local": "local", 
                            "value": "ovgu.de/"+I40Frame["semanticProtocol"], 
                            "idType": False
                        }
                        ]
                    }, 
                    "type": I40Frame["type"],
                    "messageId": I40Frame["messageId"], 
                    "sender": {
                        "identification": {
                            "id": I40Frame["SenderAASID"],
                            "idType": "URI"
                        }, 
                        "role": {
                            "name": I40Frame["SenderRolename"]
                            }
                        },
                    "conversationId": I40Frame["conversationId"]
                }
        
        if (I40Frame["ReceiverAASID"] != ""):
            frame["receiver"] = {
                                    "identification": {
                                        "id": I40Frame["ReceiverAASID"],
                                        "idType": "URI"
                                    }, 
                                    "role": {
                                        "name": I40Frame["ReceiverRolename"]
                                    }
                                }
     
        return frame
    
    def createInteractionElements(self,I40IElem):
        InteractionElem = {}
    
    def createEthereumInMessage(self,message):
        jsonMessage = {
                      "frame": {
                        "semanticProtocol": {
                          "keys": [
                            {
                              "type": "GlobalReference",
                              "local": "local",
                              "value": "ovgu.de/http://www.vdi.de/gma720/vdi2193_2/bidding",
                              "idType": False
                            }
                          ]
                        },
                        "type": message["msgType"],
                        "messageId": message["messageId"],
                        "sender": {
                          "identification": {
                            "id": message["senderId"],
                            "idType": "URI"
                          },
                          "role": {
                            "name": message["senderRole"]
                          }
                        },
                        "conversationId": message["conversationId"]
                      }
                    } 
        if message["receiverId"] != "NA":
            
            jsonMessage["receiverId"] = {
                                  "identification": {
                                    "id": message["receiverId"],
                                    "idType": "URI"
                                  },
                                  "role": {
                                    "name": message["receiverRole"]
                                  }
                                }
        if message["propertyX"] != "NA":
            jsonMessage["interactionElements"] = [ {
                                                      "semanticId": {
                                                        "keys": [
                                                          {
                                                            "type": "GlobalReference",
                                                            "local": False,
                                                            "value": "0173-1#01-AKG243#015",
                                                            "index": 0,
                                                            "idType": "IRDI"
                                                          }
                                                        ]
                                                      },
                                                      "identification": {
                                                        "idType": "IRI",
                                                        "id": "www.company.com/ids/sm/3145_4121_8002_1792"
                                                      },
                                                      "idShort": "2DPlotSubmodel",
                                                      "modelType": {
                                                        "name": "Submodel"
                                                      },
                                                      "kind": "Instance",
                                                      "submodelElements": [
                                                        {
                                                          "value": message["propertyX"],
                                                          "idShort": "propertyX",
                                                          "modelType": {
                                                            "name": "Property"
                                                          },
                                                          "valueType": {
                                                            "dataObjectType": {
                                                              "name": ""
                                                            }
                                                          }
                                                        },
                                                        {
                                                          "value": message["propertyY"],
                                                          "idShort": "propertyY",
                                                          "modelType": {
                                                            "name": "Property"
                                                          },
                                                          "valueType": {
                                                            "dataObjectType": {
                                                              "name": ""
                                                            }
                                                          }
                                                        }
                                                      ]
                                                    }
                                                  ]
            if message["listPrice"]  != "NA":
                listPriceDict = {
                                    "value": message["listPrice"],
                                    "idShort": "listPrice",
                                    "modelType": {
                                        "name": "Property"
                                        },
                                    "valueType": {
                                        "dataObjectType": {
                                            "name": ""
                                            }
                                        }
                                }
                jsonMessage["interactionElements"][0]["submodelElements"].append(listPriceDict)
        return jsonMessage
    
    def createEthereumOutMessage(self,outMessage):
        senderId = outMessage["frame"]["sender"]["identification"]["id"]
        senderRole = outMessage["frame"]["sender"]["role"]["name"]
        msgType = outMessage["frame"]["type"]
        conversationId = outMessage["frame"]["conversationId"]
        replyBy = outMessage["frame"]["replyBy"]
        replyTo = outMessage["frame"]["replyTo"]
        acct = "ss"#Account.create('12345')
        messageId = acct.address
        try:
            receiverId = outMessage["frame"]["receiver"]["identification"]["id"]
            receiverRole = outMessage["frame"]["receiver"]["role"]["name"]
        except Exception as e:
            receiverId = "NA"
            receiverRole = "NA"
        try:
            propertyX = outMessage["interactionElements"][0]["submodelElements"][0]["value"]
            propertyY = outMessage["interactionElements"][0]["submodelElements"][1]["value"]
        except Exception as e:
            propertyX = "NA"
            propertyY = "NA"
        
        try:
            listPrice = outMessage["interactionElements"][0]["submodelElements"][1]["value"]
        except Exception as e:
            listPrice = "NA"
         
        message = [bytes(senderId,'utf-8'),bytes(receiverId,'utf-8'),bytes(senderRole,'utf-8'),
                bytes(receiverRole,'utf-8'), bytes(msgType,'utf-8'),(messageId), bytes(propertyX,'utf-8'),
                bytes(propertyY,'utf-8'), bytes(listPrice,'utf-8'),bytes(conversationId,"utf-8"),
                bytes(replyBy,"utf-8"),bytes(replyTo,"utf-8")]
        return message
        
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
                        "identification": {
                            "id": assId,
                            "idType": "URI"
                        }, 
                        "role": {
                            "name": "HeartBeatProtocol"
                            }
                        },
                    "conversationId": ""
                }

        frame["receiver"] = {
                                    "identification": {
                                        "id": "AASpillarbox",
                                        "idType": "URI"
                                    }, 
                                    "role": {
                                        "name": "HeartBeatHandler"
                                    }
                                }
     
        return {"frame":frame}             
    

