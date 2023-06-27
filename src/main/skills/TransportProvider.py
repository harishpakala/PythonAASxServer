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
import uuid

class checkingSchedule(AState):
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.sendingRefuse_Enabled = True
        self.PriceCalculation_Enabled = True

    def opc_access(self,nodeId):
        rValue = "error"
        try:
            plc_opcua_Client = Client("opc.tcp://192.168.1.2:4840/")
            plc_opcua_Client.description = str(uuid.uuid4())
            plc_opcua_Client.session_timeout = 600000
            plc_opcua_Client.secure_channel_timeout = 600000
            plc_opcua_Client.connect()
            rValue = (plc_opcua_Client.get_node(nodeId)).get_value()
            print(rValue)
            plc_opcua_Client.disconnect()
            return rValue
        except:
            return rValue 
            
    def asset_access(self):
        try:
            self.plcHandler = self.base_class.pyaas.asset_access_handlers["OPCUA"]
            sMessage_out_data = self.opc_access("ns=4;s=|var|HX-CP1H16.Application.PLC_PRG.sMessage_out_data")
            sMessage_out_purpose = self.opc_access("ns=4;s=|var|HX-CP1H16.Application.PLC_PRG.sMessage_out_purpose")
            
            if sMessage_out_data == "error" or sMessage_out_purpose == "error" :
                self.PriceCalculation_Enabled = False
            else :
                if sMessage_out_data == "ready" and sMessage_out_purpose == "Inform":
                    self.sendingRefuse_Enabled = False
                else:
                    self.PriceCalculation_Enabled = False
        
        except Exception as E:
            self.PriceCalculation_Enabled = False        
            
    
    def actions(self) -> None:
        self.asset_access()
        
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
        self.sMessage_out_data = ""
        self.sMessage_out_purpose = ""    

    def getLocation(self,specifier,submodelD):
        for submodelElem in submodelD["submodelElements"]:
            if (submodelElem["idShort"] == "TechnicalProperties"):
                for valueELem in submodelElem["value"]:
                    if (valueELem["idShort"] == "FunctionalProperties"):
                        for specifierElem in valueELem["value"]:
                            if (specifierElem["idShort"] == specifier):
                                return specifierElem["value"]
    def opc_access(self,nodeId):
        rValue = "error"
        try:
            plc_opcua_Client = Client("opc.tcp://192.168.1.2:4840/")
            plc_opcua_Client.description = str(uuid.uuid4())
            plc_opcua_Client.session_timeout = 600000
            plc_opcua_Client.secure_channel_timeout = 600000
            plc_opcua_Client.connect()
            rValue = (plc_opcua_Client.get_node(nodeId)).get_value()
            plc_opcua_Client.disconnect()
            return rValue
        except:
            return rValue 

    def wopc_access(self,nodeId,value):
        rValue = "error"
        try:
            plc_opcua_Client = Client("opc.tcp://192.168.1.2:4840/")
            plc_opcua_Client.description = str(uuid.uuid4())
            plc_opcua_Client.session_timeout = 600000
            plc_opcua_Client.secure_channel_timeout = 600000
            plc_opcua_Client.connect()
            rValue = (plc_opcua_Client.get_node(nodeId))
            (rValue.set_value(value))
            plc_opcua_Client.disconnect()
            return rValue
        except Exception as E:
            print(str(E))
            return rValue                 

    
    def service_execute(self):       
        cfpMessage = self.retrieve("callForProposal")
        self.plcHandler = self.base_class.pyaas.asset_access_handlers["OPCUA"]
        
        self.TargetLocation = ""
        self.CurrentLocation = ""
        try:
            self.TransportSubmodel = self.GetSubmodelById("https://example.com/ids/sm/4494_7040_1122_9311")
            self.CurrentLocation = self.getLocation("currentLocation",self.TransportSubmodel)
            self.TargetLocation = self.getLocation("targetLocation",cfpMessage["interactionElements"][0])
            
            try:  
                #self.plcHandler.write(self.tdPropertiesList.get_property("xProductionMode").href,"Process")
                if (self.CurrentLocation == self.TargetLocation):
                    self.TargetLocation = "Pos 0"
                self.base_class.skillLogger.info(self.CurrentLocation + " "+ self.TargetLocation)
                self.wopc_access("ns=4;s=|var|HX-CP1H16.Application.PLC_PRG.sMessage_in_purpose",ua.DataValue("Process"))
                self.wopc_access("ns=4;s=|var|HX-CP1H16.Application.PLC_PRG.sMessage_in_data_SR",ua.DataValue(self.CurrentLocation))
                self.wopc_access("ns=4;s=|var|HX-CP1H16.Application.PLC_PRG.sMessage_in_data_SP",ua.DataValue(self.TargetLocation))
                
            except Exception as E:
                print(str(E),"Error Write 1")
            
            plcBoool = True
            if (self.CurrentLocation == "Pos 0" and self.TargetLocation == "Pos 0"):
                pass
            else:
                while (plcBoool):
                    self.sMessage_out_data = self.opc_access("ns=4;s=|var|HX-CP1H16.Application.PLC_PRG.sMessage_out_data")
                    self.sMessage_out_purpose = self.opc_access("ns=4;s=|var|HX-CP1H16.Application.PLC_PRG.sMessage_out_purpose")
                    if  (self.sMessage_out_data == "end of process" and self.sMessage_out_purpose == "Acknowledge"):
                        plcBoool = False
            i = 0
            j = 0
            k = 0
            for submodelElem in self.TransportSubmodel["submodelElements"]:
                if (submodelElem["idShort"] == "TechnicalProperties"):
                    for valueELem in submodelElem["value"]:
                        if (valueELem["idShort"] == "FunctionalProperties"):
                            for specifierElem in valueELem["value"]:
                                if (specifierElem["idShort"] == "currentLocation"):
                                    self.TransportSubmodel["submodelElements"][i]["value"][j]["value"][k]["value"] = self.TargetLocation
                                k = k + 1
                        j = j + 1     
                i = i + 1
            self.save_submodel(copy.deepcopy(self.TransportSubmodel))
        
        except Exception as e:
            self.base_class.skillLogger.info(e)
        self.WaitForCallForProposal_Enabled = False        
           
        
    def actions(self) -> None:
        self.service_execute()
            
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
        self.oSubmodel1 = oSubmodel1
        self.iSubmodel1 = iSubmodel1
        i = 0
        listPrice = self.getPropertyElem(self.iSubmodel1,"listprice")
        CFP = self.getPropertyElem(self.iSubmodel1,"cfp")
        for submodelELem in self.oSubmodel1["submodelElements"]:
            if submodelELem["idShort"] =="CommercialProperties":
                self.oSubmodel1["submodelElements"][i]["value"].append(listPrice)
                self.oSubmodel1["submodelElements"][i]["value"].append(CFP)
                break
            i = i + 1
        return self.oSubmodel1
            
    def create_outbound_message(self,msg_type) -> list:
        callForProposal = copy.deepcopy(self.retrieve("callForProposal"))
        receiverId = callForProposal["frame"]["sender"]["id"]
        receiverRole = callForProposal["frame"]["sender"]["role"]["name"]
        conV1 = callForProposal["frame"]["conversationId"]
        oMessage_Out = self.create_i40_message(msg_type,conV1,receiverId,receiverRole)
        submodel = self.GetSubmodelById('https://example.com/ids/sm/4494_7040_1122_9311')
        security = self.GetSubmodelELementByIdshoortPath('urn_TransportProvider:IDiS:AG2:Pilot:NormAAS:ID:Submodel:StandardContent:62443', 'ProvisionSet-SAL-C')
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
         "TensileStrengthOfMaterial":"Range","WeightOfWorkpiece":"Range","Hardness":"TRange"}
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
                    
        if feasibilityLen == 8:
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
        self.submodel = self.GetSubmodelById("https://example.com/ids/sm/4494_7040_1122_9311")
        callForProposal = self.retrieve("callForProposal")
        tempDict1 = self.getPropertyList(self.submodel)
        tempDict = self.getPropertyList(callForProposal['interactionElements'][0])
        try:
            self.base_class.env = tempDict["env"]
            print("THis is the environment "+ self.base_class.env)
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
        
class TransportProvider(Actor):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''      
        Actor.__init__(self,"TransportProvider",
                       "www.admin-shell.io/interaction/bidding",
                       "Transport Provision","WaitForCallForProposal")
                        

    def start(self):
        self.run("WaitForCallForProposal")


if __name__ == '__main__':
    
    lm2 = TransportProvider()
    lm2.Start('msgHandler')
