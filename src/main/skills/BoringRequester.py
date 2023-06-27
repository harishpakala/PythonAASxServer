"""
Copyright (c) 2023 Otto-von-Guericke-Universitaet Magdeburg, Lehrstuhl Integrierte Automation
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
"""
from datetime import datetime
try:
    from utils.utils import Actor,AState
except ImportError:
    from main.utils.utils import Actor,AState

class sendTransportOrder(AState):
    message_out =  ["Order",]
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.WaitforTransportOrderCompletion_Enabled = True
            
    def create_outbound_message(self,msg_type) -> list:
        message = self.retrieve("Order")
        receiverId = message["frame"]["sender"]["id"]
        receiverRole = "TransportRequester"
        conV1 = self.create_transport_conv_id(receiverId,message["frame"]["conversationId"])
        oMessage_Out = self.create_i40_message(msg_type,conV1,receiverId,receiverRole)
        #submodel = self.GetSubmodelById('submodelId')
        oMessage_Out["interactionElements"].append(message["interactionElements"][1])
        self.save_out_message(oMessage_Out)
        return [oMessage_Out]
    
    def actions(self) -> None:
        try:
            acceptproposalMessage = self.retrieve("accept_proposals")[0]
            
            for submodelElem in acceptproposalMessage["interactionElements"][0]["submodelElements"]:
                if (submodelElem['idShort'] == 'CommercialProperties'):
                    for value in submodelElem["value"]:
                        if value['idShort'] == "workStationLocation":
                            self.TargetLocation = value["value"]               
        except Exception as e:
            print("Error ", str(e))
        i = 0
        j = 0
        k = 0
        transportIdentifier = self.retrieve("Order")["interactionElements"][1][0]
        self.TransportSubmodel = self.GetSubmodelById(transportIdentifier)
        for submodelElem in self.TransportSubmodel["submodelElements"]:
            if (submodelElem["idShort"] == "TechnicalProperties"):
                for valueELem in submodelElem["value"]:
                    if (valueELem["idShort"] == "FunctionalProperties"):
                        for specifierElem in valueELem["value"]:
                            if (specifierElem["idShort"] == "targetLocation"):
                                self.TransportSubmodel["submodelElements"][i]["value"][j]["value"][k]["value"] = self.TargetLocation
                            k = k + 1
                    j = j + 1
            i = i + 1
 
        self.save_submodel(self.TransportSubmodel)
        
    def transitions(self) -> object:
        self.send(self.create_outbound_message(sendTransportOrder.message_out[0]))
        if (self.WaitforTransportOrderCompletion_Enabled):
            return "WaitforTransportOrderCompletion"
        
class sendacceptProposal(AState):
    message_out =  ["acceptProposal",]
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.sendTransportOrder_Enabled = True
            
    def create_outbound_message(self,msg_type) -> list:
        accept_proposals = self.retrieve("accept_proposals")
        messages = []
        for ap in accept_proposals:
            receiverId = ap["frame"]["sender"]["id"]
            receiverRole = ap["frame"]["sender"]["role"]["name"]
            conV1 = ap["frame"]["conversationId"]
            oMessage_Out = self.create_i40_message(msg_type,conV1,receiverId,receiverRole)
            #submodel = self.GetSubmodelById('submodelId')
            #oMessage_Out["interactionElements"].append(submodel)
            self.save_out_message(oMessage_Out)
            messages.append(oMessage_Out)
        return messages
    
    
    def actions(self) -> None:
        pass
        
    def transitions(self) -> object:
        self.send(self.create_outbound_message(sendacceptProposal.message_out[0]))
        if (self.sendTransportOrder_Enabled):
            return "sendTransportOrder"
        
class cfpConfiguration(AState):
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.sendCompletionResponse_Enabled = True
        self.SendCFP_Enabled = True
            
    
    def actions(self) -> None:
        Order = self.retrieve("Order")
        if (len(Order["interactionElements"]) == 2):
            Identifier1 = Order["interactionElements"][0]
            Identifier2 = Order["interactionElements"][1]
            submodel1 = self.GetSubmodelById(Identifier1[0])
            submodel2 = self.GetSubmodelById(Identifier2[0])
            
            if submodel1 is not None and submodel1 is not None:
                if (submodel1["semanticId"]["keys"][0]["value"] == "0173-1#01-AKG243#015"):
                    if (submodel2["semanticId"]["keys"][0]["value"] == "0173-1#01-ADR740#004"):
                        self.sendCompletionResponse_Enabled = False
                    else:
                        responseSM = self.getStatusResponseSM()
                        responseSM["submodelElements"][0]["value"] = "E"
                        responseSM["submodelElements"][1]["value"] = "E.01"
                        responseSM["submodelElements"][2]["value"] = "The Transport submodel is not provided."
                        self.push("responseSM", responseSM)
                        self.SendCFP_Enabled = False
                elif (submodel2["semanticId"]["keys"][0]["value"] == "0173-1#01-AKG243#015"):
                    if (submodel1["semanticId"]["keys"][0]["value"] == "0173-1#01-ADR740#004"):
                        Order["interactionElements"][0] = Identifier2
                        Order["interactionElements"][1] = Identifier1
                        self.sendCompletionResponse_Enabled = False
                    else:
                        responseSM = self.getStatusResponseSM()
                        responseSM["submodelElements"][0]["value"] = "E"
                        responseSM["submodelElements"][1]["value"] = "E.01"
                        responseSM["submodelElements"][2]["value"] = "The Transport submodel is not provided."
                        self.push("responseSM", responseSM)
                        self.SendCFP_Enabled = False
                else: 
                    self.base_class.responseMessage["status"] = "E"
                    self.base_class.responseMessage["code"] = "E.01"
                    self.base_class.responseMessage["message"] =  "The boring submodel is not provided."
                    self.SendCFP_Enabled = False
            else:
                responseSM = self.getStatusResponseSM()
                responseSM["submodelElements"][0]["value"] = "E"
                responseSM["submodelElements"][1]["value"] = "E.01"
                responseSM["submodelElements"][2]["value"] = "Error retrieving the submodels."
                self.push("responseSM", responseSM)                
                self.SendCFP_Enabled = False
        else:
            responseSM = self.getStatusResponseSM()
            responseSM["submodelElements"][0]["value"] = "E"
            responseSM["submodelElements"][1]["value"] = "E.01"
            responseSM["submodelElements"][2]["value"] = "Enough number of submodel Id's are not provided."
            self.push("responseSM", responseSM)
            self.SendCFP_Enabled = False
        
        
    def transitions(self) -> object:
        if (self.sendCompletionResponse_Enabled):
            return "sendCompletionResponse"
        if (self.SendCFP_Enabled):
            return "SendCFP"
        
class WaitforNewOrder(AState):
    message_in =  ["Order",]       
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.cfpConfiguration_Enabled = True
            
    
    def actions(self) -> None:
        if (self.wait_untill_message(1, WaitforNewOrder.message_in)):
            message = self.receive(WaitforNewOrder.message_in[0])
            self.save_in_message(message)
            startTime = datetime.now()
            self.base_class.pyaas.dba.setInitialValue(message["frame"]["conversationId"],
                             self.base_class.skillName,startTime)            
            self.push("Order", message)
        
    def transitions(self) -> object:
        if (self.cfpConfiguration_Enabled):
            return "cfpConfiguration"
        
class WaitforTransportOrderCompletion(AState):
    message_in =  ["OrderStatus",]       
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.WaitforInformConfirm_Enabled = True
        self.sendCompletionResponse_Enabled = True
            
    
    def actions(self) -> None:
        if (self.wait_untill_message_timeout(1, 120, WaitforTransportOrderCompletion.message_in)):
            message = self.receive(WaitforTransportOrderCompletion.message_in[0])
            self.save_in_message(message)
            statusMessage = message["interactionElements"][0]
            statusResponse = statusMessage["submodelElements"][0]["value"]
            if (statusResponse == "E"):
                responseSM = self.getStatusResponseSM()
                responseSM["submodelElements"][0]["value"] = "E"
                responseSM["submodelElements"][1]["value"] = statusMessage["submodelElements"][1]["value"]
                responseSM["submodelElements"][2]["value"] =  statusMessage["submodelElements"][2]["value"]
                self.push("responseSM", responseSM)
                self.WaitforInformConfirm_Enabled = False
            else:
                self.sendCompletionResponse_Enabled = False
        else:
            responseSM = self.getStatusResponseSM()
            responseSM["submodelElements"][0]["value"] = "E"
            responseSM["submodelElements"][1]["value"] = "E.02"
            responseSM["submodelElements"][2]["value"] =  "The transport order is not succesfully executed"
            self.push("responseSM", responseSM)
            self.WaitforInformConfirm_Enabled = False
            
    def transitions(self) -> object:
        if (self.WaitforInformConfirm_Enabled):
            return "WaitforInformConfirm"
        if (self.sendCompletionResponse_Enabled):
            return "sendCompletionResponse"
        
class sendCompletionResponse(AState):
    message_out =  ["OrderStatus",]
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.WaitforNewOrder_Enabled = True
            
    def create_outbound_message(self,msg_type) -> list:
        message = self.retrieve("Order")
        receiverId = message["frame"]["sender"]["id"]
        receiverRole = message["frame"]["sender"]["role"]["name"]
        conV1 = message["frame"]["conversationId"]
        oMessage_Out = self.create_i40_message(msg_type,conV1,receiverId,receiverRole)
        #submodel = self.GetSubmodelById('submodelId')
        oMessage_Out["interactionElements"].append(self.retrieve("responseSM"))
        self.save_out_message(oMessage_Out)
        return [oMessage_Out]

    def set_cfp_properties(self,conversationId,_cfp):
        endTime = datetime.now()
        self.base_class.pyaas.dba.setFinalProperties(conversationId,
                             endTime,_cfp)
    
    def actions(self) -> None:
        try:
            self.set_cfp_properties(self.retrieve("Order")["frame"]["conversationId"],
                                self.retrieve("CFP"))
        except:
            self.set_cfp_properties(self.retrieve("Order")["frame"]["conversationId"],
                                0)
        
    def transitions(self) -> object:
        self.send(self.create_outbound_message(sendCompletionResponse.message_out[0]))
        self.flush_tape()
        self.clear_messages()
        if (self.WaitforNewOrder_Enabled):
            return "WaitforNewOrder"
        
class sendrejectProposal(AState):
    message_out =  ["rejectProposal",]
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.sendCompletionResponse_Enabled = True
        self.sendacceptProposal_Enabled = True
            
    def create_outbound_message(self,msg_type) -> list:
        reject_proposals = self.retrieve("reject_proposals")
        messages = []
        for rp in reject_proposals:
            receiverId = rp["frame"]["sender"]["id"]
            receiverRole = rp["frame"]["sender"]["role"]["name"]
            conV1 = rp["frame"]["conversationId"]
            oMessage_Out = self.create_i40_message(msg_type,conV1,receiverId,receiverRole)
            #submodel = self.GetSubmodelById('submodelId')
            oMessage_Out["interactionElements"].append(rp["interactionElements"][0])
            self.save_out_message(oMessage_Out)
            messages.append(oMessage_Out)
        return messages
    
    def actions(self) -> None:
        if (len(self.retrieve("accept_proposals")) == 0):
            self.sendacceptProposal_Enabled = False
            responseSM = self.getStatusResponseSM()
            responseSM["submodelElements"][0]["value"] = "E"
            responseSM["submodelElements"][1]["value"] = "E.06"
            responseSM["submodelElements"][2]["value"] = "No proposal is selected"
            self.push("responseSM",responseSM)
        else:
            self.sendCompletionResponse_Enabled = False        
        
    def transitions(self) -> object:
        self.send(self.create_outbound_message(sendrejectProposal.message_out[0]))
        if (self.sendCompletionResponse_Enabled):
            return "sendCompletionResponse"
        if (self.sendacceptProposal_Enabled):
            return "sendacceptProposal"
        
class noProposalReceived(AState):
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.sendCompletionResponse_Enabled = True
            
    
    def actions(self) -> None:
        responseSM = self.getStatusResponseSM()
        responseSM["submodelElements"][0]["value"] = "E"
        responseSM["submodelElements"][1]["value"] = "E.06"
        responseSM["submodelElements"][2]["value"] = "No proposals are received."
        self.push("responseSM",responseSM)
        
    def transitions(self) -> object:
        if (self.sendCompletionResponse_Enabled):
            return "sendCompletionResponse"
        
class WaitforInformConfirm(AState):
    message_in =  ["informConfirm",]       
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.sendCompletionResponse_Enabled = True
            
    
    def actions(self) -> None:
        if (self.wait_untill_message_timeout(1, 120, WaitforInformConfirm.message_in)):
            message = self.receive(WaitforInformConfirm.message_in[0])
            self.save_in_message(message)
            responseSM = self.getStatusResponseSM()
            responseSM["submodelElements"][0]["value"] = "A"
            responseSM["submodelElements"][1]["value"] = "A.06"
            responseSM["submodelElements"][2]["value"] = "The service provision is completed"
            self.push("responseSM",responseSM)
        else:
            responseSM = self.getStatusResponseSM()
            responseSM["submodelElements"][0]["value"] = "E"
            responseSM["submodelElements"][1]["value"] = "E.06"
            responseSM["submodelElements"][2]["value"] = "Service provision Failure"
            self.push("responseSM",responseSM)
                        
    def transitions(self) -> object:
        if (self.sendCompletionResponse_Enabled):
            return "sendCompletionResponse"
        
class WaitForSPProposal(AState):
    message_in =  ["proposal",]       
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.noProposalReceived_Enabled = True
        self.EvaluateProposal_Enabled = True
            
    
    def actions(self) -> None:
        self.wait_untill_timeout(10)
        if (self.rcv_msg_count(WaitForSPProposal.message_in[0])):
            messages = self.receive_all(WaitForSPProposal.message_in[0])
            self.push("proposals",messages)
            for message in messages : self.save_in_message(message)
            self.noProposalReceived_Enabled = False
        else:
            self.EvaluateProposal_Enabled = False
            
    def transitions(self) -> object:
        if (self.noProposalReceived_Enabled):
            return "noProposalReceived"
        if (self.EvaluateProposal_Enabled):
            return "EvaluateProposal"
        
class EvaluateProposal(AState):
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.sendrejectProposal_Enabled = True

    def getItem(self,submodelElement,Item_Name):
        for value in submodelElement["value"]:
            if value['idShort'] == Item_Name:
                return int(value['value']) 
    
    def actions(self) -> None:
        accept_proposals = []
        reject_proposals = []
            
        try:
            proposlList = []
            ListPrice_CFP = []
            proposlList = self.retrieve("proposals")
            for eachPorposal in proposlList:
                for submodelElement in eachPorposal['interactionElements'][0]['submodelElements']:
                    if (submodelElement['idShort'] == 'CommercialProperties'):
                        ListPrice_CFP.append([self.getItem(submodelElement,"cfp"),self.getItem(submodelElement,"listprice")])
            
            qoutes = []
            
            for lsp in ListPrice_CFP:
                qoutes.append(lsp[0] + lsp[1])
                        
            bestPrice = min(qoutes)
            bestPriceIndex = qoutes.index(bestPrice)          
            self.push("CFP",ListPrice_CFP[bestPriceIndex][0])
            
            if (len((proposlList)) == 1):
                for _p in proposlList:
                    if _p["interactionElements"][1]['value'][0]["value"] == "SAL-C-3":
                        accept_proposals.append(_p)
                    else:
                        _p["interactionElements"].clear()
                        responseSM = self.getStatusResponseSM()
                        responseSM["submodelElements"][0]["value"] = "E"
                        responseSM["submodelElements"][1]["value"] = "E.06"
                        responseSM["submodelElements"][2]["value"] = "The work station does not satisfy the required security level of SAL-C-3"                
                        _p["interactionElements"].append(responseSM)
                        reject_proposals.append(_p)
            else:
                porposalNotFound = True
                for i  in range(0,len(proposlList)):
                    _p = proposlList[i]
                    if (qoutes[i] == bestPrice):
                        if porposalNotFound:
                            if _p["interactionElements"][1]['value'][0]["value"] == "SAL-C-3" and porposalNotFound:
                                accept_proposals.append(_p)
                                porposalNotFound = False
                            else:
                                _p["interactionElements"].clear()
                                responseSM = self.getStatusResponseSM()
                                responseSM["submodelElements"][0]["value"] = "E"
                                responseSM["submodelElements"][1]["value"] = "E.06"
                                responseSM["submodelElements"][2]["value"] = "The work station does not satisfy the required security level of SAL-C-3"                   
                                _p["interactionElements"].append(responseSM)
                                reject_proposals.append(_p)
                        else:
                            sec = _p["interactionElements"][1]['value'][0]["value"]
                            _p["interactionElements"].clear()
                            responseSM = self.getStatusResponseSM()
                            responseSM["submodelElements"][0]["value"] = "E"
                            responseSM["submodelElements"][1]["value"] = "E.06"
                            if sec == "SAL-C-3":
                                responseSM["submodelElements"][2]["value"] = "The proposal is too slow"
                            else:
                                responseSM["submodelElements"][2]["value"] = "The work station does not satisfy the required security level of SAL-C-3"
                            _p["interactionElements"].append(responseSM)
                            reject_proposals.append(_p)
                    else:
                        _p["interactionElements"].clear()
                        responseSM = self.getStatusResponseSM()
                        responseSM["submodelElements"][0]["value"] = "E"
                        responseSM["submodelElements"][1]["value"] = "E.06"
                        responseSM["submodelElements"][2]["value"] = "The work station has a higher list price."                   
                        _p["interactionElements"].append(responseSM)
                        reject_proposals.append(_p)
                
            self.push("accept_proposals",accept_proposals)
            self.push("reject_proposals",reject_proposals)
            
        except Exception as e:
            self.push("accept_proposals",accept_proposals)
            self.push("reject_proposals",reject_proposals)
            self.base_class.skillLogger.info("Evaluate Proposal Error" + str(e))

        
    def transitions(self) -> object:
        if (self.sendrejectProposal_Enabled):
            return "sendrejectProposal"
        
class SendCFP(AState):
    message_out =  ["callForProposal",]
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.WaitForSPProposal_Enabled = True
            
    def create_outbound_message(self,msg_type) -> list:
        receiverId =""
        receiverRole = ""
        conV1 = self.retrieve("Order")["frame"]["conversationId"]
        oMessage_Out = self.create_i40_message(msg_type,conV1,receiverId,receiverRole)
        submodelIdentifier = self.retrieve("Order")["interactionElements"][0][0]
        oMessage_Out["interactionElements"].append(self.GetSubmodelById(submodelIdentifier))
        self.save_out_message(oMessage_Out)
        return [oMessage_Out]
    
    def actions(self) -> None:
        pass
        
    def transitions(self) -> object:
        self.send(self.create_outbound_message(SendCFP.message_out[0]))
        if (self.WaitForSPProposal_Enabled):
            return "WaitForSPProposal"

class BoringRequester(Actor):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''      
        Actor.__init__(self,"BoringRequester",
                       "www.admin-shell.io/interaction/bidding",
                       "Boring Requisition","WaitforNewOrder")
                        

    def start(self):
        self.run("WaitforNewOrder")


if __name__ == '__main__':
    
    lm2 = BoringRequester()
    lm2.Start('msgHandler')
