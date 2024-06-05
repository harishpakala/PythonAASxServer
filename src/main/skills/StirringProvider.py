"""
Copyright (c) 2023 Otto-von-Guericke-Universitaet Magdeburg, Lehrstuhl Integrierte Automation
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
"""

try:
    from utils.sip import Actor,AState
except ImportError:
    from src.main.utils.sip import Actor,AState

import copy
import time

class capabilitycheck(AState):
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.sendingNotUnderstood_Enabled = True
        self.feasibilityCheck_Enabled = True

    def getProperty(self,submodelElem):
        if submodelElem["modelType"] == "Property":
            return submodelElem["value"] 
        elif submodelElem["modelType"] == "Range":
            return  {"min":int(submodelElem["min"]),"max":int(submodelElem["max"])} 
            
    def getPropertyList(self,submodel):
        tempDict = {}
        for submodelElem in submodel["submodelElements"]:
            if submodelElem["idShort"] == "CapabilitySet":
                for elem in submodelElem["value"]:
                    if elem["idShort"] == "StirringContinuousContainer":
                        for ele in elem["value"]:
                            if ele["idShort"] == "PropertySet":
                                for el in ele["value"]:
                                    if el["idShort"] == "TimeContainer":
                                        for _property in el["value"]:
                                            if _property["idShort"] == "Time":
                                                tempDict["Time"] = self.getProperty(_property)
                                    if el["idShort"] == "RoundsPerMinuteContainer":
                                        for _property in el["value"]:
                                            if _property["idShort"] == "RoundsPerMinute": 
                                                tempDict["RoundsPerMinute"] = self.getProperty(_property)
                
        return tempDict
        
    def actions(self) -> None:
        self.submodel = self.GetSubmodelById("https://www.iat.rwth-aachen.de/pls-lab/pumping_station/HC20/CapabilityDescription")
        callForProposal = self.retrieve("callForProposal")
        try:
            spDict = self.getPropertyList(self.submodel)
            srDict = self.getPropertyList(callForProposal['interactionElements'][0])
            self.push("sp_properties",spDict)
            self.push("sr_propertoes",srDict)
            for _key in spDict.keys():
                if _key not in list(srDict.keys()):
                    self.feasibilityCheck_Enabled = False
                    break
                else:
                    self.sendingNotUnderstood_Enabled = False
        except Exception as E:
            self.feasibilityCheck_Enabled = False

    def transitions(self) -> object:
        if (self.sendingNotUnderstood_Enabled):
            return "sendingNotUnderstood"
        if (self.feasibilityCheck_Enabled):
            return "feasibilityCheck"
        
class feasibilityCheck(AState):
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.sendingRefuse_Enabled = True
        self.checkingSchedule_Enabled = True
            
    
    def actions(self) -> None:
        spDict = self.retrieve("sp_properties")
        srDict = self.retrieve("sr_propertoes")
        
        try:
            for _key in spDict:
                if type(spDict[_key]) == str:
                    if spDict[_key] != srDict[_key]:
                        self.checkingSchedule_Enabled = False
                        break
                    else:
                        self.sendingRefuse_Enabled = False
                elif type(spDict[_key]) == dict:
                    if int(srDict[_key]) >= spDict[_key]["min"] or int(srDict[_key]) <= spDict[_key]["max"]:
                        self.sendingRefuse_Enabled = False
                    else:
                        self.checkingSchedule_Enabled = False 
                        break
            
        except Exception as E:
            self.checkingSchedule_Enabled = False
                
                
    def transitions(self) -> object:
        if (self.sendingRefuse_Enabled):
            return "sendingRefuse"
        if (self.checkingSchedule_Enabled):
            return "checkingSchedule"
        
class waitingforServiceRequesterAnswer(AState):
    message_in =  ["acceptProposal","rejectProposal"]       
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.WaitForCallForProposal_Enabled = True
        self.serviceProvision_Enabled = True
            
    
    def actions(self) -> None:
        if (self.wait_untill_message_timeout(1,100,waitingforServiceRequesterAnswer.message_in)):
            message = self.receive_msgtypes_all(waitingforServiceRequesterAnswer.message_in)[0]
            self.save_in_message(message)
            if message["frame"]["type"] == "acceptProposal":
                self.WaitForCallForProposal_Enabled = False
            else:
                self.serviceProvision_Enabled = False
        else:
            self.serviceProvision_Enabled = False
        
    def transitions(self) -> object:
        if (self.WaitForCallForProposal_Enabled):
            return "WaitForCallForProposal"
        if (self.serviceProvision_Enabled):
            return "serviceProvision"
        
class sendingProposal(AState):
    message_out =  ["proposal",]
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.waitingforServiceRequesterAnswer_Enabled = True
            
    def create_outbound_message(self,msg_type) -> list:
        callForProposal = copy.deepcopy(self.retrieve("callForProposal"))
        receiverId = callForProposal["frame"]["sender"]["id"]
        receiverRole = callForProposal["frame"]["sender"]["role"]["name"]
        conV1 = callForProposal["frame"]["conversationId"]
        oMessage_Out = self.create_i40_message(msg_type,conV1,receiverId,receiverRole)
        
        offer001 = self.GetSubmodelELementByIdshoortPath('https://template.smartfactory.de/sm/Offers','Offer001')
        oMessage_Out["interactionElements"].append(offer001)
        self.save_out_message(oMessage_Out)
        return [oMessage_Out]

    
    def actions(self) -> None:
        pass
        
    def transitions(self) -> object:
        self.send(self.create_outbound_message(sendingProposal.message_out[0]))
        if (self.waitingforServiceRequesterAnswer_Enabled):
            return "waitingforServiceRequesterAnswer"
        
class checkingSchedule(AState):
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.sendingRefuse_Enabled = True
        self.PriceCalculation_Enabled = True
            
    
    def actions(self) -> None:
        self.sendingRefuse_Enabled = False
        
    def transitions(self) -> object:
        if (self.sendingRefuse_Enabled):
            return "sendingRefuse"
        if (self.PriceCalculation_Enabled):
            return "PriceCalculation"
        
class sendingNotUnderstood(AState):
    message_out =  ["notUnderstood",]
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.WaitForCallForProposal_Enabled = True
            
    def create_outbound_message(self,msg_type) -> list:
        message = self.retrieve("callForProposal")
        receiverId = message["frame"]["sender"]["id"]
        receiverRole = message["frame"]["sender"]["role"]["name"]
        conV1 = message["frame"]["conversationId"]
        oMessage_Out = self.create_i40_message(msg_type,conV1,receiverId,receiverRole)
        #submodel = self.GetSubmodelById('submodelId')
        #oMessage_Out["interactionElements"].append(submodel)
        self.save_out_message(oMessage_Out)
        return [oMessage_Out]
    
    def actions(self) -> None:
        pass
        
    def transitions(self) -> object:
        self.send(self.create_outbound_message(sendingNotUnderstood.message_out[0]))
        if (self.WaitForCallForProposal_Enabled):
            return "WaitForCallForProposal"
        
class serviceProvision(AState):
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.sendinPropoposalporvisionConfirm_Enabled = True
        self.WaitForCallForProposal_Enabled = True
            
    
    def actions(self) -> None:
        time.sleep(5)
        self.WaitForCallForProposal_Enabled = False
        
    def transitions(self) -> object:
        if (self.sendinPropoposalporvisionConfirm_Enabled):
            return "sendinPropoposalporvisionConfirm"
        if (self.WaitForCallForProposal_Enabled):
            return "WaitForCallForProposal"
        
class WaitForCallForProposal(AState):
    message_in =  ["callForProposal",]       
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.capabilitycheck_Enabled = True
            
    
    def actions(self) -> None:
        self.flush_tape()
        self.clear_messages()        
        if (self.wait_untill_message(1, WaitForCallForProposal.message_in)):
            message = self.receive(WaitForCallForProposal.message_in[0])
            self.save_in_message(message)
            self.push("callForProposal",message)
        
    def transitions(self) -> object:
        if (self.capabilitycheck_Enabled):
            return "capabilitycheck"
        
class sendinPropoposalporvisionConfirm(AState):
    message_out =  ["informConfirm",]
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.WaitForCallForProposal_Enabled = True
            
    def create_outbound_message(self,msg_type) -> list:
        message = self.retrieve("callForProposal")
        receiverId = message["frame"]["sender"]["id"]
        receiverRole = message["frame"]["sender"]["role"]["name"]
        conV1 = message["frame"]["conversationId"]
        oMessage_Out = self.create_i40_message(msg_type,conV1,receiverId,receiverRole)
        #submodel = self.GetSubmodelById('submodelId')
        #oMessage_Out["interactionElements"].append(submodel)
        self.save_out_message(oMessage_Out)
        return [oMessage_Out]
    
    def actions(self) -> None:
        pass
        
    def transitions(self) -> object:
        self.send(self.create_outbound_message(sendinPropoposalporvisionConfirm.message_out[0]))
        if (self.WaitForCallForProposal_Enabled):
            return "WaitForCallForProposal"
        
class PriceCalculation(AState):
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.sendingProposal_Enabled = True
            
    
    def actions(self) -> None:
        pass
        
    def transitions(self) -> object:
        if (self.sendingProposal_Enabled):
            return "sendingProposal"
        
class sendingRefuse(AState):
    message_out =  ["refuseProposal",]
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.WaitForCallForProposal_Enabled = True
            
    def create_outbound_message(self,msg_type) -> list:
        message = self.retrieve("callForProposal")
        receiverId = message["frame"]["sender"]["id"]
        receiverRole = message["frame"]["sender"]["role"]["name"]
        conV1 = message["frame"]["conversationId"]
        oMessage_Out = self.create_i40_message(msg_type,conV1,receiverId,receiverRole)
        #submodel = self.GetSubmodelById('submodelId')
        #oMessage_Out["interactionElements"].append(submodel)
        self.save_out_message(oMessage_Out)
        return [oMessage_Out]
    
    def actions(self) -> None:
        pass
        
    def transitions(self) -> object:
        self.send(self.create_outbound_message(sendingRefuse.message_out[0]))
        if (self.WaitForCallForProposal_Enabled):
            return "WaitForCallForProposal"

class StirringProvider(Actor):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''      
        Actor.__init__(self,"StirringProvider",
                       "www.admin-shell.io/interaction/bidding",
                       "Stirring Provision","WaitForCallForProposal")
                        

    def start(self):
        self.run("WaitForCallForProposal")


if __name__ == '__main__':
    
    lm2 = StirringProvider()
    lm2.Start('msgHandler')
