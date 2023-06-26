"""
Copyright (c) 2023 Otto-von-Guericke-Universitaet Magdeburg, Lehrstuhl Integrierte Automation
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
"""
from opcua import ua
from opcua import Client
try:
    import queue as Queue
except ImportError:
    import Queue as Queue 
try:
    from utils.utils import Actor,AState
except ImportError:
    from main.utils.utils import Actor,AState

import copy
import uuid
'''

'''    
class waitingforServiceRequesterAnswer(AState):
    
    def initialize(self):
        self.InputDocument = "acceptProposal / rejectProposal"
        self.OutputDocument = "NA"
        self.in_queue = self.base_class.waitingforServiceRequesterAnswer_Queue
        self.base_class.waitingforServiceRequesterAnswer_In = self.message
        # Gaurd variables for enabling the transitions
        self.WaitForCallForProposal_Enabled = True
        self.serviceProvision_Enabled = True
    
            
    
    def actions(self) -> None:
        if (self.wait_untill_timer(1,60)):
            self.receive()
            self.save_in_message(self.message)
            if self.message["frame"]["type"] == "accept":
                self.WaitForCallForProposal_Enabled = False
            else:
                self.serviceProvision = False
        else:
            self.serviceProvision = False
        
    def transitions(self) -> object:
        if (self.WaitForCallForProposal_Enabled):
            ts = WaitForCallForProposal(self.base_class,"WaitForCallForProposal")
            return ts
        if (self.serviceProvision_Enabled):
            ts = serviceProvision(self.base_class,"serviceProvision")
            return ts
        
class sendingProposal(AState):
    
    def initialize(self):
        self.InputDocument = "NA"
        self.OutputDocument = "proposal"
        # Gaurd variables for enabling the transitions
        self.waitingforServiceRequesterAnswer_Enabled = True

    def getPropertyElem(self,iSubmodel,propertyName):
        for submodelELem in iSubmodel["submodelElements"]:
            if submodelELem["idShort"] =="CommercialProperties":
                for sproperty in submodelELem["value"]:
                    if sproperty["idShort"] == propertyName:
                        return sproperty
             
             
    def addPropertyElems(self,oSubmodel1,iSubmodel1):
        self.oSubmodel1 = oSubmodel1
        self.iSubmodel1 = iSubmodel1
        i = 0
        listPrice = self.getPropertyElem(self.iSubmodel1,"listprice")
        CFP = self.getPropertyElem(self.iSubmodel1,"cfp")
        workStationLocation = self.getPropertyElem(self.iSubmodel1,"workStationLocation")
        for submodelELem in self.oSubmodel1["submodelElements"]:
            if submodelELem["idShort"] =="CommercialProperties":
                self.oSubmodel1["submodelElements"][i]["value"].append(listPrice)
                self.oSubmodel1["submodelElements"][i]["value"].append(workStationLocation)
                self.oSubmodel1["submodelElements"][i]["value"].append(CFP)
                break
            i = i + 1
        return self.oSubmodel1    
            
    def create_outbound_message(self) -> list:
        outboundMessages = []
        message = copy.deepcopy(self.base_class.WaitForCallForProposal_In)
        receiverId = message["frame"]["sender"]["id"]
        receiverRole = message["frame"]["sender"]["role"]["name"]
        conV1 = message["frame"]["conversationId"]
        oMessage_Out = self.create_i40_message(self.OutputDocument,conV1,receiverId,receiverRole)
        submodel = self.GetSubmodelById('https://example.com/ids/sm/2334_7040_1122_4553')
        oMessage_Out["interactionElements"].append(submodel)
        self.save_out_message(oMessage_Out)
        outboundMessages.append(oMessage_Out)
        return outboundMessages
    
    def actions(self) -> None:
        pass
        
    def transitions(self) -> object:
        self.send(self.create_outbound_message())
        if (self.waitingforServiceRequesterAnswer_Enabled):
            ts = waitingforServiceRequesterAnswer(self.base_class,"waitingforServiceRequesterAnswer")
            return ts
        
class sendinPropoposalporvisionConfirm(AState):
    
    def initialize(self):
        self.InputDocument = "NA"
        self.OutputDocument = "informConfirm"
        # Gaurd variables for enabling the transitions
        self.WaitForCallForProposal_Enabled = True
    
            
    def create_outbound_message(self) -> list:
        outboundMessages = []
        message = self.base_class.WaitForCallForProposal_In 
        receiverId = message["frame"]["sender"]["id"]
        receiverRole = message["frame"]["sender"]["role"]["name"]
        conV1 = message["frame"]["conversationId"]
        oMessage_Out = self.create_i40_message(self.OutputDocument,conV1,receiverId,receiverRole)
        #submodel = self.GetSubmodelById('submodelId')
        self.save_out_message(oMessage_Out)
        outboundMessages.append(oMessage_Out)
        return outboundMessages
    
    def actions(self) -> None:
        pass
        
    def transitions(self) -> object:
        self.send(self.create_outbound_message())
        if (self.WaitForCallForProposal_Enabled):
            ts = WaitForCallForProposal(self.base_class,"WaitForCallForProposal")
            return ts
        
class PriceCalculation(AState):
    
    def initialize(self):
        self.InputDocument = "NA"
        self.OutputDocument = "NA"
        # Gaurd variables for enabling the transitions
        self.sendingProposal_Enabled = True
     
    def actions(self) -> None:
        pass
        
    def transitions(self) -> object:
        if (self.sendingProposal_Enabled):
            ts = sendingProposal(self.base_class,"sendingProposal")
            return ts
        
class capabilitycheck(AState):
    
    def initialize(self):
        self.InputDocument = "NA"
        self.OutputDocument = "NA"
        # Gaurd variables for enabling the transitions
        self.sendingNotUnderstood_Enabled = True
        self.feasibilityCheck_Enabled = True

    def getProperty(self,submodelElem):
        if submodelElem["modelType"] =="Property":
            return submodelElem["value"] 
        elif submodelElem["modelType"] =="Range":
            return  {"min":submodelElem["min"],"max":submodelElem["max"]} 
    
    def getPropertyList(self,submodel):
        tempDict = {}
        for submodelElem in submodel["submodelElements"]:
            if submodelElem["idShort"] =="CommercialProperties":
                for elem in submodelElem["value"]:
                    tempDict[elem["idShort"]] = self.getProperty(elem)
                    
            elif submodelElem["idShort"] =="TechnicalProperties": 
                for elem in submodelElem["value"]:
                    if elem["idShort"] =="FunctionalProperties" or elem["idShort"] =="EnvironmentalProperties": 
                        for ele in elem["value"]:
                            tempDict[ele["idShort"]] = self.getProperty(ele)
                    elif elem["idShort"] =="WorkpieceProperties": 
                        for ele in elem["value"]:
                            if ele["idShort"] =="Dimensions":
                                for el in ele["value"]:
                                    tempDict[el["idShort"]] = self.getProperty(el)
                            else:
                                tempDict[ele["idShort"]] = self.getProperty(ele)      
        return tempDict                  
    
            
    
    def actions(self) -> None:
        self.submodel = self.GetSubmodelById("https://example.com/ids/sm/2334_7040_1122_4553")
        tempDict1 = self.getPropertyList(self.submodel)
        tempDict = self.getPropertyList(self.base_class.WaitForCallForProposal_In['interactionElements'][0])

        try:
            if (tempDict["env"] !="live"):
                self.feasibilityCheck_Enabled = False
                self.base_class.skillLogger.info("Environment Error")
            else:       
                for key in list(tempDict1.keys()):
                    self.base_class.subModelTypes[key] = tempDict1[key]        
                
                for key in list(tempDict.keys()):
                    self.base_class.proposalSubmodelTypes[key] = tempDict[key]     
                    
                submodelTypeList = list(self.base_class.subModelTypes.keys())
                if len(list(self.base_class.proposalSubmodelTypes.keys())) == 0:
                    self.feasibilityCheck_Enabled = False
                    self.base_class.skillLogger.info("Not Equal number of property types")
                    
                for key in list(self.base_class.proposalSubmodelTypes.keys()):
                    if (key in ["MaxDistanceToPreferredVenueOfProvision","PreferredVenueOfProvision","deliveryTime"]):
                        pass                
                    elif key not in submodelTypeList:
                        self.feasibilityCheck_Enabled = False
                        self.base_class.skillLogger.info("one of the property missing" + str(key))
                        break
        except Exception as E:
            self.feasibilityCheck_Enabled = False
        
        if self.feasibilityCheck_Enabled:
            self.sendingNotUnderstood_Enabled = False
        else:
            self.feasibilityCheck_Enabled = False
        
        
    def transitions(self) -> object:
        if (self.sendingNotUnderstood_Enabled):
            ts = sendingNotUnderstood(self.base_class,"sendingNotUnderstood")
            return ts
        if (self.feasibilityCheck_Enabled):
            ts = feasibilityCheck(self.base_class,"feasibilityCheck")
            return ts
        
class feasibilityCheck(AState):
    
    def initialize(self):
        self.InputDocument = "NA"
        self.OutputDocument = "NA"
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
        for key in list(self.itemsCheck):
            item = self.itemsCheck[key]
            if  item =="Property":
                if (key =="MaterialOfWorkpiece"):
                    feasibilityLen = feasibilityLen + 1 
                elif ( self.base_class.proposalSubmodelTypes[key] == self.base_class.subModelTypes[key] ):
                    feasibilityLen = feasibilityLen + 1
                else :
                    print(key,self.base_class.proposalSubmodelTypes[key],self.base_class.subModelTypes[key])
            elif item =="Range":
                value = self.base_class.proposalSubmodelTypes[key]
                min = float(self.base_class.subModelTypes[key]["min"])
                max = float(self.base_class.subModelTypes[key]["max"])
                if float(value) >= min and float(value) <= max :
                    feasibilityLen = feasibilityLen + 1
                else :
                    print(key,value,self.base_class.subModelTypes[key])                    
            elif item =="TRange":
                value = self.base_class.proposalSubmodelTypes[key]
                min = float((self.base_class.subModelTypes[key]["min"]).split(" ")[1])
                max = float((self.base_class.subModelTypes[key]["max"]).split(" ")[1])
                tempValue = value.split(" ")[1]
                if float(tempValue) >= min and float(tempValue) <= max :
                    feasibilityLen = feasibilityLen + 1
                else :
                    print(key,value,self.base_class.subModelTypes[key])                    
                    
        if feasibilityLen == 12:
            self.sendingRefuse_Enabled = False
        else:
            self.checkingSchedule_Enabled = False
        
    def transitions(self) -> object:
        if (self.sendingRefuse_Enabled):
            ts = sendingRefuse(self.base_class,"sendingRefuse")
            return ts
        if (self.checkingSchedule_Enabled):
            ts = checkingSchedule(self.base_class,"checkingSchedule")
            return ts
        
class sendingRefuse(AState):
    
    def initialize(self):
        self.InputDocument = "NA"
        self.OutputDocument = "refuseProposal"
        # Gaurd variables for enabling the transitions
        self.WaitForCallForProposal_Enabled = True
    
            
    def create_outbound_message(self) -> list:
        outboundMessages = []
        message = self.base_class.sendingRefuse_In 
        receiverId = message["frame"]["sender"]["id"]
        receiverRole = message["frame"]["sender"]["role"]["name"]
        conV1 = message["frame"]["conversationId"]
        oMessage_Out = self.create_i40_message(self.OutputDocument,conV1,receiverId,receiverRole)
        #submodel = self.GetSubmodelById('submodelId')
        self.save_out_message(oMessage_Out)
        outboundMessages.append(oMessage_Out)
        return outboundMessages
    
    def actions(self) -> None:
        pass
        
    def transitions(self) -> object:
        self.send(self.create_outbound_message())
        if (self.WaitForCallForProposal_Enabled):
            ts = WaitForCallForProposal(self.base_class,"WaitForCallForProposal")
            return ts
        
class sendingNotUnderstood(AState):
    
    def initialize(self):
        self.InputDocument = "NA"
        self.OutputDocument = "notUnderstood"
        # Gaurd variables for enabling the transitions
        self.WaitForCallForProposal_Enabled = True
    
            
    def create_outbound_message(self) -> list:
        outboundMessages = []
        message = self.base_class.sendingNotUnderstood_In 
        receiverId = message["frame"]["sender"]["id"]
        receiverRole = message["frame"]["sender"]["role"]["name"]
        conV1 = message["frame"]["conversationId"]
        oMessage_Out = self.create_i40_message(self.OutputDocument,conV1,receiverId,receiverRole)
        #submodel = self.GetSubmodelById('submodelId')
        self.save_out_message(oMessage_Out)
        outboundMessages.append(oMessage_Out)
        return outboundMessages
    
    def actions(self) -> None:
        pass
        
    def transitions(self) -> object:
        self.send(self.create_outbound_message())
        if (self.WaitForCallForProposal_Enabled):
            ts = WaitForCallForProposal(self.base_class,"WaitForCallForProposal")
            return ts
        
class checkingSchedule(AState):
    
    def initialize(self):
        self.InputDocument = "NA"
        self.OutputDocument = "NA"
        # Gaurd variables for enabling the transitions
        self.sendingRefuse_Enabled = True
        self.PriceCalculation_Enabled = True
    
    def opc_access(self):
        rValue = "error"
        try:
            plc_opcua_Client = Client("opc.tcp://admin:wago@192.168.1.52:4840/")
            plc_opcua_Client.description = str(uuid.uuid4())
            plc_opcua_Client.session_timeout = 600000
            plc_opcua_Client.secure_channel_timeout = 600000
            plc_opcua_Client.connect()
            rValue = (plc_opcua_Client.get_node("ns=4;s=|var|WAGO 750-8202 PFC200 CS 2ETH RS.Application.PLC_PRG.sPermission")).get_value()
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
            ts = sendingRefuse(self.base_class,"sendingRefuse")
            return ts
        if (self.PriceCalculation_Enabled):
            ts = PriceCalculation(self.base_class,"PriceCalculation")
            return ts
        
class serviceProvision(AState):
    
    def initialize(self):
        self.InputDocument = "NA"
        self.OutputDocument = "NA"
        # Gaurd variables for enabling the transitions
        self.sendinPropoposalporvisionConfirm_Enabled = True
        self.WaitForCallForProposal_Enabled = True
    
    def opc_access(self):
        rValue = "error"
        try:
            plc_opcua_Client = Client("opc.tcp://admin:wago@192.168.1.52:4840/")
            plc_opcua_Client.description = str(uuid.uuid4())
            plc_opcua_Client.session_timeout = 600000
            plc_opcua_Client.secure_channel_timeout = 600000
            plc_opcua_Client.connect()
            rValue = (plc_opcua_Client.get_node("ns=4;s=|var|WAGO 750-8202 PFC200 CS 2ETH RS.Application.PLC_PRG.sPermission")).get_value()
            print(rValue)
            plc_opcua_Client.disconnect()
            return rValue
        except:
            return rValue                

    def wopc_access(self):
        rValue = "error"
        try:
            plc_opcua_Client = Client("opc.tcp://admin:wago@192.168.1.52:4840/")
            plc_opcua_Client.description = str(uuid.uuid4())
            plc_opcua_Client.session_timeout = 600000
            plc_opcua_Client.secure_channel_timeout = 600000
            plc_opcua_Client.connect()
            rValue = (plc_opcua_Client.get_node("ns=4;s=|var|WAGO 750-8202 PFC200 CS 2ETH RS.Application.PLC_PRG.sPermission"))
            print(rValue.set_value(ua.DataValue(True)))
            plc_opcua_Client.disconnect()
            return rValue
        except Exception as E:
            return rValue                  
    
    def actions(self) -> None:
        try :
            #self.plcHandler.write(self.tdPropertiesList.get_property("sPermission").href,ua.DataValue(True))
            self.wopc_access()
            plcBoool = True
            while (plcBoool):
                #time.sleep(20)
                #sPermissionVariable = self.plcHandler.read(self.tdPropertiesList.get_property("sPermission").href)
                if  ((str(self.opc_access())).upper() =="FALSE"):
                    plcBoool = False
            self.WaitForCallForProposal_Enabled = False
        except Exception as E:
            self.sendinPropoposalporvisionConfirm_Enabled = False        
        
    def transitions(self) -> object:
        if (self.sendinPropoposalporvisionConfirm_Enabled):
            ts = sendinPropoposalporvisionConfirm(self.base_class,"sendinPropoposalporvisionConfirm")
            return ts
        if (self.WaitForCallForProposal_Enabled):
            ts = WaitForCallForProposal(self.base_class,"WaitForCallForProposal")
            return ts
        
class WaitForCallForProposal(AState):
    
    def initialize(self):
        self.InputDocument = "callForProposal"
        self.OutputDocument = "NA"
        self.in_queue = self.base_class.WaitForCallForProposal_Queue
        self.base_class.WaitForCallForProposal_In = self.message
        # Gaurd variables for enabling the transitions
        self.capabilitycheck_Enabled = True
    
            
    
    def actions(self) -> None:
        if (self.wait_untill(1)):
            self.base_class.WaitForCallForProposal_In  = self.receive()
            self.save_in_message(self.message)
        
    def transitions(self) -> object:
        if (self.capabilitycheck_Enabled):
            ts = capabilitycheck(self.base_class,"capabilitycheck")
            return ts
        



class BoringProvider(Actor):
    '''
    classdocs
    '''
    def initstate_specific_queue_internal(self) -> None:
        """
        """
        self.waitingforServiceRequesterAnswer_Queue = Queue.Queue()
        self.WaitForCallForProposal_Queue = Queue.Queue()
        
                
        self.QueueDict = {
              "acceptProposal / rejectProposal": self.waitingforServiceRequesterAnswer_Queue,
              "callForProposal": self.WaitForCallForProposal_Queue,
            }
    
    def __init__(self,pyaas):
        '''
        Constructor
        '''
        
        Actor.__init__(self,pyaas,"BoringProvider",
                       "www.admin-shell.io/interaction/bidding",
                       "Boring Provision","WaitForCallForProposal")
    
    def start(self):
        WaitForCallForProposal_1 = WaitForCallForProposal(self)
        #self.stateChange("WaitForCallForProposal")
        currentState = WaitForCallForProposal_1
        self.run(currentState)


if __name__ == '__main__':
    
    lm2 = BoringProvider()
    lm2.Start('msgHandler')
