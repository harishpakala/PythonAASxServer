'''
Copyright (c) 2021-2022 OVGU LIA
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
'''

import json
import os
import threading
import uuid

try:
    from abstract.endpointhandler import AASEndPointHandler
except ImportError:
    from src.main.abstract.endpointhandler import AASEndPointHandler

import paho.mqtt.client as mqtt

class AASEndPointHandler(AASEndPointHandler):
    
    def __init__(self, pyAAS, msgHandler):
        self.pyAAS = pyAAS
        self.msgHandler = msgHandler
    
    def on_connect(self, client, userdata, flags, rc):
        pass#self.pyaas.serviceLogger.info("MQTT channels are succesfully connected.",client,userdata,flags,rc)
        
    def configure(self):
        self.ipaddressComdrv = self.pyAAS.lia_env_variable["LIA_AAS_MQTT_HOST"]
        self.portComdrv = int(self.pyAAS.lia_env_variable["LIA_AAS_MQTT_PORT"])
        
        self.client = mqtt.Client(client_id=str(uuid.uuid4()))
        self.client.on_connect = self.on_connect
        self.client.on_message = self.retrieveMessage
        
    def update(self):
        try:
            self.stop()
            self.client.connect(self.ipaddressComdrv, port=(self.portComdrv))
            topicsList = []
            for _id in self.pyAAS.aasShellHashDict._getKeys():
                topicsList.append((self.pyAAS.aasShellHashDict.__getHashEntry__(_id).aasELement["id"],0))
            print(" #############################################################################snnnnnnnnnnn")
            print(topicsList)
            print(" #############################################################################snnnnnnnnnnn")
            self.client.subscribe(topicsList)
            self.client.loop_forever()
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error with the MQTT Subscription"+ str(E))
    
    def restart(self):
        try :
            mqttClientThread1 = threading.Thread(target=self.update)
            mqttClientThread1.start()
          
        except Exception as e:
            self.pyAAS.serviceLogger.info('Unable to connect to the mqtt server ' + str(e))
            os._exit(0)
        self.pyAAS.serviceLogger.info("MQTT channels are started")
    
    def start(self):
        try :
            mqttClientThread1 = threading.Thread(target=self.update)
            mqttClientThread1.start()
          
        except Exception as e:
            self.pyAAS.serviceLogger.info('Unable to connect to the mqtt server ' + str(e))
            os._exit(0)
        self.pyAAS.serviceLogger.info("MQTT channels are started")
            

    def stop(self):
        try: 
            self.client.loop_stop(force=False)
            self.client.disconnect()
            
        except Exception as e:
            self.pyAAS.serviceLogger.info('Error disconnecting to the server ' + str(e))

    def dispatchMessage(self, send_Message): 
        publishTopic = "AASpillarbox"
        try:
            publishTopic = send_Message["frame"]["receiver"]["id"]
        except:
            pass
        try:
            if (publishTopic in list(self.pyAAS.aasHashDict._getKeys())):
                self.msgHandler.putIbMessage(send_Message)
            else:
                self.client.publish("AASpillarbox", str(json.dumps(send_Message)))                
        except Exception as e:
            self.pyAAS.serviceLogger.info("Unable to publish the message to the mqtt server", str(e))
            
    def retrieveMessage(self, client, userdata, msg):
        try:
            msg1 = str(msg.payload, "utf-8")
            jsonMessage = json.loads(msg1)
            if "receiver" in jsonMessage["frame"].keys():
                self.msgHandler.putIbMessage(jsonMessage)
            else:
                self.handleBoradCastMessage(jsonMessage)
        except:
            pass
            
    def handleBoradCastMessage(self,jsonMessage):
        if ((jsonMessage["frame"]["conversationId"] not in self.pyAAS.conversationInteractionList)):
            self.pyAAS.serviceLogger.info("Test1 handleBoradCastMessage")
            self.pyAAS.dba.createNewConversation(jsonMessage["frame"]["conversationId"])
            self.pyAAS.conversationInteractionList.append(jsonMessage["frame"]["conversationId"])
            self.instanceId = str(uuid.uuid1())
            self.pyAAS.dataManager.pushInboundMessage({"functionType":3,"instanceid":self.instanceId,
                                                           "conversationId":jsonMessage["frame"]["conversationId"],
                                                           "messageType":jsonMessage["frame"]["type"],
                                                           "messageId":jsonMessage["frame"]["messageId"],
                                                           "direction":"inbound",
                                                           "SenderAASID" : "Broadcast",
                                                           "message":jsonMessage})            
            self.msgHandler.putIbMessage(jsonMessage)