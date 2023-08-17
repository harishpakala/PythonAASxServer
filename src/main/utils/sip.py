"""
Copyright (c) 2023 Otto-von-Guericke-Universitaet Magdeburg, Lehrstuhl Integrierte Automation
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
"""
from abc import abstractmethod
from copy import deepcopy
from datetime import datetime
from importlib import import_module
from inspect import isclass
from typing import final  
import asyncio
import base64
import copy
import logging
import sys
import time
import uuid
try:
    from utils.utils import ExecuteDBModifier,ExecuteDBRetriever,ProductionStepOrder
except ImportError:
    from main.utils.utils import ExecuteDBModifier,ExecuteDBRetriever,ProductionStepOrder

try:
    from assetaccessadapters.io_opcua import OPCUAEndPointHandler
except ImportError:
    from main.assetaccessadapters.io_opcua import OPCUAEndPointHandler


try:
    from utils.aaslog import ServiceLogHandler,LogList
except ImportError:
    from main.utils.aaslog import ServiceLogHandler,LogList



try:
    from utils.i40data import Generic
except ImportError:
    from main.utils.i40data import Generic

class AState:

    def __init__(self,StateName):
        self.StateName = StateName
        self.initialize()
        self.base_class = None
    
    def set_base_class(self,base_class):
        self.base_class = base_class
    
    @abstractmethod
    def initialize(self):
        ...
    
    @abstractmethod
    def transitions(self):
        ...
        
    @abstractmethod
    def actions(self):
        ...
    
    def send(self,messages:list) -> None:
        for msg in messages:
            self.base_class.send(msg)
     
    def receive(self,msg_in) -> object:
        try:
            return self.base_class.in_messages[msg_in].pop(0)
        except Exception as E:
            return None
            
    def receive_all(self,msg_in) -> list:
        try:
            msgs =  copy.deepcopy(self.base_class.in_messages[msg_in])
            self.base_class.in_messages[msg_in].clear()
            return msgs
        except Exception as E:
            return []
        
    def log_info(self,log_text):
        self.base_class.skillLogger.info(log_text);
    
    def create_i40_message(self,oMessage,conV1,receiverId,receiverRole):
        return self.base_class.gen.create_i40_message(oMessage,conV1,receiverId,receiverRole)
    
    def save_in_message(self,save_message):
        instanceId = str(uuid.uuid1())
        self.base_class.pyaas.dataManager.pushInboundMessage({"functionType":3,"instanceid":instanceId,
                                                            "conversationId":save_message["frame"]["conversationId"],
                                                            "messageType":save_message["frame"]["type"],
                                                            "messageId":save_message["frame"]["messageId"],
                                                            "direction" : "inbound",
                                                            "SenderAASID" : save_message["frame"]["sender"]["id"],
                                                            "message":deepcopy(save_message)})

    def save_out_message(self,save_message):
        instanceId = str(uuid.uuid1())
        self.base_class.pyaas.dataManager.pushInboundMessage({"functionType":3,"instanceid":instanceId,
                                                            "conversationId":save_message["frame"]["conversationId"],
                                                            "messageType":save_message["frame"]["type"],
                                                            "messageId":save_message["frame"]["messageId"],
                                                            "direction" : "outbound",
                                                            "SenderAASID" : save_message["frame"]["sender"]["id"],
                                                            "message":deepcopy(save_message)})
    
    
    @final    
    def run(self) -> None:
        self.log_info("\n #############################################################################")
        self.log_info("StartState: "+self.StateName)
        self.actions()
    
    @final
    def next(self) -> object:
        return self.transitions()
    
    def GetSubmodelById(self,submodelId):
        submodel,status,statuscode = self.base_class.pyaas.dba.GetSubmodelById(submodelId)
        if status:
            return submodel
        else:
            return None
    
    def save_submodel(self,submodel):
        edm = ExecuteDBModifier(self.base_class.pyaas)
        data,status,statuscode = edm.execute({"data":{"submodelIdentifier":submodel["id"], "_submodel":submodel},
                                                            "method": "PutSubmodelById",
                                                                "instanceId" : str(uuid.uuid1())})
        return status
    
    def GetSubmodelELementByIdshoortPath(self,submodelId,IdShortPath):
        submodelElem,status,statuscode = self.base_class.pyaas.dba.GetSubmodelElementByPath_SRI(submodelId,IdShortPath)
        if status:
            return submodelElem
        else:
            return None
       
    def wait_untill_timeout(self,timer_count) -> bool:
        try:
            time.sleep(timer_count)
            return True
        except Exception as E:
            return False
        
    def wait_untill_message(self,message_count,msg_types) -> bool:
        try:        
            while (self.base_class.get_message_count(msg_types) < message_count): 
                time.sleep(1)
                
            if (self.base_class.get_message_count(msg_types) == message_count):
                return True
            else:
                return False
        except Exception as E:
            return False
        
    def wait_untill_message_timeout(self,message_count,timer,msg_types) -> bool:
        try:
            i = 1
            while (self.base_class.get_message_count(msg_types) < message_count) and (i < timer): 
                time.sleep(1)
                i = i + 1
            
            if (self.base_class.get_message_count(msg_types) == message_count):
                return True
            else:
                return False 
        except Exception as E:
            return False

    def configureDescriptor(self,_shellId):
        return self.base_class.pyaas.aasConfigurer.configureDescriptor(_shellId)
    
    def rcv_msg_count(self,msg_type):
        try:
            return len(self.base_class.in_messages[msg_type])
        except Exception as E:
            return 0
      
    def set_cfp_properties(self,conversationId,_cfp):
        endTime = datetime.now()
        self.base_class.pyaas.dba.setFinalProperties(conversationId,
                             endTime,_cfp)
    
    def push(self,key,value):
        self.base_class.push(key,value)
    
    def retrieve(self,key):
        return self.base_class.retrieve(key)
    
    def flush_tape(self):
        try:
            return self.base_class.flush_tape()
        except Exception as E:
            return False
    
    def get_aid_property(self,propertname):
        return self.base_class.get_aid_property(propertname)
    
    def aid_property_read(self,propertyname):
        aid_property = self.get_aid_property(propertyname)
        if aid_property.href[0:7] == "opc.tcp": 
            opcuaeHandler = OPCUAEndPointHandler()
            return asyncio.run(opcuaeHandler._write(aid_property.href))

    def aid_property_write(self,propertyname,value):
        aid_property = self.get_aid_property(propertyname)
        if aid_property.href[0:7] == "opc.tcp": 
            opcuaeHandler = OPCUAEndPointHandler()
            return asyncio.run(opcuaeHandler._write(aid_property.href,value))

    def getStatusResponseSM(self):
        return self.base_class.getStatusResponseSM()
    
    def get_ProdutionStepList(self,aasId):
        return self.base_class.get_ProdutionStepList(aasId)
    
    def get_production_step(self,aasId):
        return self.base_class.get_production_step(aasId)
    
    def create_new_sub_conversationId(self,aasId,convsersationId):    
        return self.base_class.create_new_sub_conversationId(aasId,convsersationId)
    
    def create_transport_conv_id(self,aasId,convsersationId):
        return self.base_class.create_transport_conv_id(aasId,convsersationId)
        
class Actor:
    def __init__(self,skillName,semanticProtocol,SkillService,initialState):
        
        self.QueueDict = dict()
        self.productionStepSeq = []
        self.responseMessage = {}
        
        self.SkillService = SkillService
        self.skillName = skillName
        self.semanticProtocol = semanticProtocol
        self.initialState = initialState
        
        self.currentConversationId = "temp"
        
        self.enabledStatus = {"Y":True, "N":False}
        self.enabledState = "Y"
                         
        self.tape = dict()
        self.in_messages = dict()
        self.set_in_messages()
        
    def set_in_messages(self):
        skillModule = import_module("." + self.skillName, package="skills")
        elems = dir(skillModule)
        elems.remove(self.skillName)
        elems.remove("Actor")
        elems.remove("AState")
        actor_states = [ x for x in elems  if isclass(getattr(skillModule, x))]
        for _state in actor_states:
            _skill = import_module("."+self.skillName, package="skills")
            a_state = getattr(_skill, _state)(_state)
            try:
                for _msg_type in a_state.message_in:
                    if _msg_type is not None:
                        self.in_messages[_msg_type] = []
            except Exception as e:
                pass
    
    def get_message_count(self,msg_types):
        try:
            ed =  sum([len(self.in_messages[x]) for x in msg_types])
            return ed
        except Exception as E:
            return 0
            
    def set_base(self,pyaas):
        self.pyaas = pyaas
        
    def push(self,key,value) -> None:
        self.tape[key] = value
    
    def retrieve(self,key) -> object:
        return self.tape[key]
    
    def flush_tape(self) -> bool:
        try:
            self.tape.clear()
            return True
        except:
            return False        
        
    def create_status_message(self) -> None:
        self.statusMessage = self.gen.create_i40_message("StausChange","AASNetworkedBidding",
                                                       self.aasID + "/"+self.skillName,
                                                       "SkillStatusChange")
        self.statusMessage["interactionElements"].append(self.pyaas.aasConfigurer.getStatusResponseSubmodel())

    def _start(self, msgHandler,shellObject,_uid):
        self.statusInElem = self.pyaas.aasConfigurer.getStatusResponseSubmodel()
        self.StatusResponseSM = self.pyaas.aasConfigurer.getStatusResponseSubmodel()
        self.msgHandler = msgHandler
        self.shellObject = shellObject
        self.aasID = shellObject.aasELement["id"]
        self.uuid  = _uid
        self.gen = Generic(self.aasID,self.skillName,self.semanticProtocol)
        self.create_status_message()
        self.skillLogger = logging.getLogger(self.aasID+"."+self.skillName)
        self.skillLogger.setLevel(logging.DEBUG)
        
        self.commandLogger_handler = logging.StreamHandler(stream=sys.stdout)
        self.commandLogger_handler.setLevel(logging.DEBUG)

        bString = base64.b64encode(bytes(self.aasID,'utf-8'))
        base64_string= bString.decode('utf-8')
        
        self.fileLogger_Handler = logging.FileHandler(self.pyaas.base_dir+"/logs/"+"_"+str(base64_string)+"_"+self.skillName+".LOG")
        self.fileLogger_Handler.setLevel(logging.DEBUG)
        
        self.listHandler = ServiceLogHandler(LogList())
        self.listHandler.setLevel(logging.DEBUG)
        
        self.Handler_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%m/%d/%Y %I:%M:%S %p')
        
        self.listHandler.setFormatter(self.Handler_format)
        self.commandLogger_handler.setFormatter(self.Handler_format)
        self.fileLogger_Handler.setFormatter(self.Handler_format)
        
        self.skillLogger.addHandler(self.listHandler)
        self.skillLogger.addHandler(self.commandLogger_handler)
        self.skillLogger.addHandler(self.fileLogger_Handler)
        self.start()
        
    def geCurrentSKILLState(self) -> str:
        return self.SKILL_STATE
 
    
    def stateChange(self, STATE) -> None:
        self.statusMessage["interactionElements"][0]["submodelElements"][0]["value"] = "I"
        self.statusMessage["interactionElements"][0]["submodelElements"][1]["value"] = "A006. internal-status-change"
        self.statusMessage["interactionElements"][0]["submodelElements"][2]["value"] = str(datetime.now()) +" "+STATE
        #self.sendMessage(self.statusMessage)
     
    def send(self, sendMessage) -> None:
        self.msgHandler.putObMessage(sendMessage)

    
    def receiveMessage(self,inMessage) -> None:
        try:    
            _messageType = str(inMessage['frame']['type'])
            if _messageType in self.in_messages:
                self.in_messages[_messageType].append(inMessage)
                print(self.in_messages)
            else:
                self.in_messages[_messageType] = [inMessage]
        except Exception as E:
            pass
    
    def get_class_object(self,_state):
        _skill = import_module("."+self.skillName, package="skills")
        a_state = getattr(_skill, _state)(_state)
        a_state.set_base_class(self)
        return a_state
        
    def run(self,currentState_string):
        ts = self.get_class_object(currentState_string)
        self.currentState = ts
        while (True):
            if ((self.currentState.__class__.__name__) == self.initialState):
                if(self.enabledState):
                    self.currentState.run()
                    ts_string = self.currentState.next()
                    ts = self.get_class_object(ts_string)
                    #self.stateChange(ts.__class__.__name__)
                    self.currentState = ts
                    self.skillLogger.info("TargettState: " + ts.__class__.__name__)
                    self.skillLogger.info("############################################################################# \n")
                else:
                    time.sleep(1)
            else:
                self.currentState.run()
                ts_string = self.currentState.next()
                ts = self.get_class_object(ts_string)
                if not (ts):
                    break
                else:
                    #self.stateChange(ts.__class__.__name__)
                    self.currentState = ts
    
    def get_aid_property(self,propertname):
        _uid = self.pyaas.aasHashDict.__getHashEntry__(self.aasID).__getId__()
        aasShellObject = self.pyaas.aasShellHashDict.__getHashEntry__(_uid)
        if aasShellObject.asset_interface_description is not None:
            if propertname in list(aasShellObject.asset_interface_description.properties.keys()):
                return aasShellObject.asset_interface_description[propertname]
            else:
                return None
        else:
            return None 
        
    def getStatusResponseSM(self):
        return copy.deepcopy(self.StatusResponseSM)
    
    def get_ProdutionStepList(self,aasId):
        _uid = self.pyaas.aasHashDict.__getHashEntry__(aasId).__getId__()
        aasShellObject = self.pyaas.aasShellHashDict.__getHashEntry__(_uid)
        return aasShellObject.productionStepList
    
    def get_production_step(self,aasId):
        _uid = self.pyaas.aasHashDict.__getHashEntry__(aasId).__getId__()
        aasShellObject = self.pyaas.aasShellHashDict.__getHashEntry__(_uid)
        self.productionStepLen = len(aasShellObject.productionStepList)
        productionStep = aasShellObject.productionStepList[0]
        del aasShellObject.productionStepList[0]        
        return productionStep
    
    def create_new_sub_conversationId(self,aasId,conversationId):
        ps0 = ProductionStepOrder(self.pyaas,aasId)
        conversationId = ps0.createStepOrderConversation(aasId, conversationId +
                                                          "_" + str(self.productionStepLen))
    
        return conversationId
    def create_transport_conv_id(self,aasId,conversationId):
        ps0 = ProductionStepOrder(self.pyaas,aasId)
        return ps0.createTransportStepOrder(aasId, conversationId)