"""
Copyright (c) 2023 Otto-von-Guericke-Universitaet Magdeburg, Lehrstuhl Integrierte Automation
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
"""

try:
    from utils.utils import Actor,AState
except ImportError:
    from main.utils.utils import Actor,AState
from opcua import ua,Client
import copy
import time
import uuid

class checkingSchedule(AState):
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.sendingRefuse_Enabled = True
        self.PriceCalculation_Enabled = True
            
    def opc_access(self):
        rValue = "error"
        try:
            plc_opcua_Client = Client("opc.tcp://192.168.1.51:4840/")
            plc_opcua_Client.description = str(uuid.uuid4())
            plc_opcua_Client.session_timeout = 600000
            plc_opcua_Client.secure_channel_timeout = 600000
            plc_opcua_Client.connect()
            rValue = (plc_opcua_Client.get_node("ns=4;s=|var|WAGO 750-8203 PFC200 CS 2ETH CAN.Application.PLC_PRG.sPermission")).get_value()
            print(rValue)
            plc_opcua_Client.disconnect()
            return rValue
        except:
            return rValue
            
    
    def actions(self) -> None:
        try:
            #sPermissionVariable = self.plcHandler.read(self.tdPropertiesList.get_property("sPermission").href)
            if self.opc_access() == "error":
                self.PriceCalculation_Enabled = False
            else:
                self.sendingRefuse_Enabled = False
        except Exception as E:
            self.PriceCalculation_Enabled = False

        
    def transitions(self) -> object:
        if (self.sendingRefuse_Enabled):
            return "sendingRefuse"
        if (self.PriceCalculation_Enabled):
            return "PriceCalculation"
        
class serviceProvision(AState):
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.sendinPropoposalporvisionConfirm_Enabled = True
        self.WaitForCallForProposal_Enabled = True

    def opc_access(self):
        rValue = "error"
        try:
            plc_opcua_Client = Client("opc.tcp://192.168.1.51:4840/")
            plc_opcua_Client.description = str(uuid.uuid4())
            plc_opcua_Client.session_timeout = 600000
            plc_opcua_Client.secure_channel_timeout = 600000
            plc_opcua_Client.connect()
            rValue = (plc_opcua_Client.get_node("ns=4;s=|var|WAGO 750-8203 PFC200 CS 2ETH CAN.Application.PLC_PRG.sPermission")).get_value()
            
            plc_opcua_Client.disconnect()
            return rValue
        except:
            return rValue                

    def wopc_access(self):
        rValue = "error"
        try:
            plc_opcua_Client = Client("opc.tcp://192.168.1.51:4840/")
            plc_opcua_Client.description = str(uuid.uuid4())
            plc_opcua_Client.session_timeout = 600000
            plc_opcua_Client.secure_channel_timeout = 600000
            plc_opcua_Client.connect()
            rValue = (plc_opcua_Client.get_node("ns=4;s=|var|WAGO 750-8203 PFC200 CS 2ETH CAN.Application.PLC_PRG.sPermission"))
            (rValue.set_value(ua.DataValue(True)))
            plc_opcua_Client.disconnect()
            return rValue
        except Exception as E:
            print(str(E))
            return rValue 
           
        
    def actions(self) -> None:
        try :
            #self.plcHandler.write(self.tdPropertiesList.get_property("sPermission").href,ua.DataValue(True))
            self.wopc_access()
            plcBoool = True
            while (plcBoool):
                #sPermissionVariable = self.plcHandler.read(self.tdPropertiesList.get_property("sPermission").href)
                if  ((str(self.opc_access())).upper() =="FALSE"):
                    plcBoool = False
            self.WaitForCallForProposal_Enabled = False
        except Exception as E:
            self.sendinPropoposalporvisionConfirm_Enabled = False
                
    def transitions(self) -> object:
        if (self.sendinPropoposalporvisionConfirm_Enabled):
            return "sendinPropoposalporvisionConfirm"
        if (self.WaitForCallForProposal_Enabled):
            return "WaitForCallForProposal"
        
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
        
class sendingProposal(AState):
    message_out =  ["proposal",]
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.waitingforServiceRequesterAnswer_Enabled = True

    def getPropertyElem(self,iSubmodel,propertyName):
        for submodelELem in iSubmodel["submodelElements"]:
            if submodelELem["idShort"] =="CommercialProperties":
                for sproperty in submodelELem["value"]:
                    if sproperty["idShort"] == propertyName:
                        return sproperty

    def addPropertyElems(self,oSubmodel1,iSubmodel1):
        oSubmodel1 = oSubmodel1
        iSubmodel1 = iSubmodel1
        i = 0
        listPrice = self.getPropertyElem(iSubmodel1,"listprice")
        CFP = self.getPropertyElem(iSubmodel1,"cfp")
        workStationLocation = self.getPropertyElem(iSubmodel1,"workStationLocation")
        for submodelELem in oSubmodel1["submodelElements"]:
            if submodelELem["idShort"] =="CommercialProperties":
                oSubmodel1["submodelElements"][i]["value"].append(listPrice)
                oSubmodel1["submodelElements"][i]["value"].append(workStationLocation)
                oSubmodel1["submodelElements"][i]["value"].append(CFP)
                break
            i = i + 1
        return oSubmodel1
            
    def create_outbound_message(self,msg_type) -> list:
        callForProposal = copy.deepcopy(self.retrieve("callForProposal"))
        receiverId = callForProposal["frame"]["sender"]["id"]
        receiverRole = callForProposal["frame"]["sender"]["role"]["name"]
        conV1 = callForProposal["frame"]["conversationId"]
        oMessage_Out = self.create_i40_message(msg_type,conV1,receiverId,receiverRole)
        submodel = self.GetSubmodelById('https://example.com/ids/sm/5554_7040_1122_5332')
        security = self.GetSubmodelELementByIdshoortPath('urn_BoringProvider2:IDiS:AG2:Pilot:NormAAS:ID:Submodel:StandardContent:62443', 'ProvisionSet-SAL-C')
        transportSubmodel = self.addPropertyElems(callForProposal["interactionElements"][0],submodel)
        oMessage_Out["interactionElements"].append(transportSubmodel)
        oMessage_Out["interactionElements"].append(security)
        self.save_out_message(oMessage_Out)
        return [oMessage_Out]
    
    def actions(self) -> None:
        pass
        
    def transitions(self) -> object:
        self.send(self.create_outbound_message(sendingProposal.message_out[0]))
        if (self.waitingforServiceRequesterAnswer_Enabled):
            return "waitingforServiceRequesterAnswer"
        
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
        
class feasibilityCheck(AState):
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.sendingRefuse_Enabled = True
        self.checkingSchedule_Enabled = True
            
    
    def actions(self) -> None:
        self.itemsCheck = {"MaterialOfWorkpiece":"Property","Height":"Range",
        "Depth":"Range","Width":"Range","ReferencedStandartOfMaterialShortName":"Property",
        "TensileStrengthOfMaterial":"Range","WeightOfWorkpiece":"Range","Hardness":"TRange",
        "drillingDiameter":"Range","drillingDepth":"Range",
        "RoughnessAverageOfBore":"Range","ISOToleranceClass":"Range"}
                
        feasibilityLen = 0
        proposalSubmodelTypes = self.retrieve("proposalSubmodelTypes")
        subModelTypes = self.retrieve("subModelTypes")
        for key in list(self.itemsCheck):
            item = self.itemsCheck[key]
            if  item == "Property":
                if (key == "MaterialOfWorkpiece"):
                    feasibilityLen = feasibilityLen + 1 
                elif ( proposalSubmodelTypes[key] == subModelTypes[key] ):
                    feasibilityLen = feasibilityLen + 1
                else :
                    pass
            elif item == "Range":
                value = proposalSubmodelTypes[key]
                min = float(subModelTypes[key]["min"])
                max = float(subModelTypes[key]["max"])
                if float(value) >= min and float(value) <= max :
                    feasibilityLen = feasibilityLen + 1
                else :
                    pass                    
            elif item == "TRange":
                value = proposalSubmodelTypes[key]
                min = float((subModelTypes[key]["min"]).split(" ")[1])
                max = float((subModelTypes[key]["max"]).split(" ")[1])
                tempValue = value.split(" ")[1]
                if float(tempValue) >= min and float(tempValue) <= max :
                    feasibilityLen = feasibilityLen + 1
                else :
                    pass#print(key,value,self.base_class.subModelTypes[key])                    
                    
        if feasibilityLen == 12:
            self.sendingRefuse_Enabled = False
        else:
            self.checkingSchedule_Enabled = False     

        
    def transitions(self) -> object:
        if (self.sendingRefuse_Enabled):
            return "sendingRefuse"
        if (self.checkingSchedule_Enabled):
            return "checkingSchedule"
        
class capabilitycheck(AState):
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.sendingNotUnderstood_Enabled = True
        self.feasibilityCheck_Enabled = True

    def getProperty(self,submodelElem):
        if submodelElem["modelType"] == "Property":
            return submodelElem["value"] 
        elif submodelElem["modelType"] == "Range":
            return  {"min":submodelElem["min"],"max":submodelElem["max"]} 
    
    def getPropertyList(self,submodel):
        tempDict = {}
        for submodelElem in submodel["submodelElements"]:
            if submodelElem["idShort"] == "CommercialProperties":
                for elem in submodelElem["value"]:
                    tempDict[elem["idShort"]] = self.getProperty(elem)
                    
            elif submodelElem["idShort"] == "TechnicalProperties": 
                for elem in submodelElem["value"]:
                    if elem["idShort"] == "FunctionalProperties" or elem["idShort"] == "EnvironmentalProperties": 
                        for ele in elem["value"]:
                            tempDict[ele["idShort"]] = self.getProperty(ele)
                    elif elem["idShort"] == "WorkpieceProperties": 
                        for ele in elem["value"]:
                            if ele["idShort"] == "Dimensions":
                                for el in ele["value"]:
                                    tempDict[el["idShort"]] = self.getProperty(el)
                            else:
                                tempDict[ele["idShort"]] = self.getProperty(ele)      
        return tempDict       
            
    
    def actions(self) -> None:
        self.submodel = self.GetSubmodelById("https://example.com/ids/sm/5554_7040_1122_5332")
        callForProposal = self.retrieve("callForProposal")
        tempDict1 = self.getPropertyList(self.submodel)
        tempDict = self.getPropertyList(callForProposal['interactionElements'][0])
        try:
            self.base_class.env = tempDict["env"]
            if (tempDict["env"] not in  ["live","cyclic"]):
                self.feasibilityCheck_Enabled = False
            else:       
                subModelTypes = dict()
                proposalSubmodelTypes = dict()
                for key in list(tempDict1.keys()):
                    subModelTypes[key] = tempDict1[key]        
                try:
                    for key in list(tempDict.keys()):
                        proposalSubmodelTypes[key] = tempDict[key]     
                    
                    submodelTypeList = list(subModelTypes.keys())
                    if len(list(proposalSubmodelTypes.keys())) == 0:
                        self.feasibilityCheck_Enabled = False
                    for key in list(proposalSubmodelTypes.keys()):
                        if (key in ["MaxDistanceToPreferredVenueOfProvision","PreferredVenueOfProvision","deliveryTime"]):
                            pass                
                        elif key not in submodelTypeList:
                            self.feasibilityCheck_Enabled = False
                            break
                except Exception as E:
                    print("Test 3 Exception check Failed")
                    self.feasibilityCheck_Enabled = False
                self.push("subModelTypes",subModelTypes)
                self.push("proposalSubmodelTypes",proposalSubmodelTypes) 
        except:
            self.feasibilityCheck_Enabled = False
        if self.feasibilityCheck_Enabled:
            self.sendingNotUnderstood_Enabled = False
        else:
            self.feasibilityCheck_Enabled = False        

        
    def transitions(self) -> object:
        if (self.sendingNotUnderstood_Enabled):
            return "sendingNotUnderstood"
        if (self.feasibilityCheck_Enabled):
            return "feasibilityCheck"
        
class PriceCalculation(AState):
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.sendingProposal_Enabled = True
            
    
    def actions(self) -> None:
        pass
        
    def transitions(self) -> object:
        if (self.sendingProposal_Enabled):
            return "sendingProposal"
        
class waitingforServiceRequesterAnswer(AState):
    message_in =  ["acceptProposal","rejectProposal",]       
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.WaitForCallForProposal_Enabled = True
        self.serviceProvision_Enabled = True
            
    
    def actions(self) -> None:
        if (self.wait_untill_message(1, waitingforServiceRequesterAnswer.message_in)):
            if (self.rcv_msg_count(waitingforServiceRequesterAnswer.message_in[0]) == 1):
                message = self.receive(waitingforServiceRequesterAnswer.message_in[0])
                self.save_in_message(message)
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
        
class BoringProvider2(Actor):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''      
        Actor.__init__(self,"BoringProvider2",
                       "www.admin-shell.io/interaction/bidding",
                       "Boring Provision","WaitForCallForProposal")
                        

    def start(self):
        self.run("WaitForCallForProposal")


if __name__ == '__main__':
    
    lm2 = BoringProvider2()
    lm2.Start('msgHandler')
