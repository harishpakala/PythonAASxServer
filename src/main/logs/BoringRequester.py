"""
Copyright (c) 2023 Otto-von-Guericke-Universitaet Magdeburg, Lehrstuhl Integrierte Automation
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
"""

try:
    import queue as Queue
except ImportError:
    import Queue as Queue 
try:
    from utils.utils import Actor,AState,ProductionStepOrder
except ImportError:
    from main.utils.utils import Actor,AState,ProductionStepOrder


try:
    from utils.aaslog import ServiceLogHandler,LogList
except ImportError:
    from src.main.utils.aaslog import ServiceLogHandler,LogList

'''

'''    
class cfpConfiguration(AState):
    
    def initialize(self):
        self.InputDocument = "NA"
        self.OutputDocument = "NA"
        # Gaurd variables for enabling the transitions
        self.sendCompletionResponse_Enabled = True
        self.SendCFP_Enabled = True
    
    def actions(self) -> None:
        if (len(self.base_class.WaitforNewOrder_In["interactionElements"]) == 2):
            Identifier1 = self.base_class.WaitforNewOrder_In["interactionElements"][0]
            Identifier2 = self.base_class.WaitforNewOrder_In["interactionElements"][1]
            submodel1 = self.GetSubmodelById(Identifier1[0])
            submodel2 = self.GetSubmodelById(Identifier2[0])
            
            if submodel1 != None and submodel2 != None:
                if (submodel1["semanticId"]["keys"][0]["value"] == "0173-1#01-AKG243#015"):
                    if (submodel2["semanticId"]["keys"][0]["value"] == "0173-1#01-ADR740#004"):
                        self.sendCompletionResponse_Enabled = False
                    else:
                        self.base_class.responseMessage["status"] = "E"
                        self.base_class.responseMessage["code"] = "E.01"
                        self.base_class.responseMessage["message"] =  "The Transport submodel is not provided."
                        self.SendCFP_Enabled = False
                elif (submodel2["semanticId"]["keys"][0]["value"] == "0173-1#01-AKG243#015"):
                    if (submodel1["semanticId"]["keys"][0]["value"] == "0173-1#01-ADR740#004"):
                        self.base_class.WaitforNewOrder_In["interactionElements"][0] = Identifier2
                        self.base_class.WaitforNewOrder_In["interactionElements"][1] = Identifier1
                        self.sendCompletionResponse_Enabled = False
                    else:
                        self.base_class.responseMessage["status"] = "E"
                        self.base_class.responseMessage["code"] = "E.01"
                        self.base_class.responseMessage["message"] =  "The Transport submodel is not provided."
                        self.SendCFP_Enabled = False
                else: 
                    self.base_class.responseMessage["status"] = "E"
                    self.base_class.responseMessage["code"] = "E.01"
                    self.base_class.responseMessage["message"] =  "The boring submodel is not provided."
                    self.SendCFP_Enabled = False
            else:
                self.base_class.responseMessage["status"] = "E"
                self.base_class.responseMessage["code"] = "E.01"
                self.base_class.responseMessage["message"] =  "Error retriving the submodels"
                self.SendCFP_Enabled = False
        else:
            self.base_class.responseMessage["status"] = "E"
            self.base_class.responseMessage["code"] = "E.01"
            self.base_class.responseMessage["message"] =  "Enough number of submodel Id's are not provided"
            self.SendCFP_Enabled = False

        
    def transitions(self) -> object:
        if (self.sendCompletionResponse_Enabled):
            ts = sendCompletionResponse(self.base_class,"sendCompletionResponse")
            return ts
        if (self.SendCFP_Enabled):
            ts = SendCFP(self.base_class,"SendCFP")
            return ts
        
class sendrejectProposal(AState):
    
    def initialize(self):
        self.InputDocument = "NA"
        self.OutputDocument = "rejectProposal"
        # Gaurd variables for enabling the transitions
        self.sendCompletionResponse_Enabled = True
        self.sendacceptProposal_Enabled = True
    
            
    def create_outbound_message(self) -> list:
        outboundMessages = []
        if len(self.base_class.reject_proposals) > 0:  
            message = self.base_class.sendrejectProposal_In[0] 
            receiverId = message["frame"]["sender"]["id"]
            receiverRole = message["frame"]["sender"]["role"]["name"]
            conV1 = message["frame"]["conversationId"]
            oMessage_Out = self.create_i40_message(self.OutputDocument,conV1,receiverId,receiverRole)
            #submodel = self.GetSubmodelById('submodelId')
            self.save_out_message(oMessage_Out)
            outboundMessages.append(oMessage_Out)
        return outboundMessages
    
    def actions(self) -> None:
        if (self.base_class.sendacceptProposal_Queue.qsize() == 0):
            self.sendacceptProposal_Enabled = False
            self.base_class.responseMessage["status"] = "E"
            self.base_class.responseMessage["code"] = "E.06"
            self.base_class.responseMessage["message"] =  "None of the provider is selected."           
        else:
            self.sendCompletionResponse_Enabled = False        
        
    def transitions(self) -> object:
        self.send(self.create_outbound_message())
        if (self.sendCompletionResponse_Enabled):
            ts = sendCompletionResponse(self.base_class,"sendCompletionResponse")
            return ts
        if (self.sendacceptProposal_Enabled):
            ts = sendacceptProposal(self.base_class,"sendacceptProposal")
            return ts
        
class WaitforTransportOrderCompletion(AState):
    
    def initialize(self):
        self.InputDocument = "OrderStatus"
        self.OutputDocument = "NA"
        self.in_queue = self.base_class.WaitforTransportOrderCompletion_Queue
        self.base_class.WaitforTransportOrderCompletion_In = self.message
        # Gaurd variables for enabling the transitions
        self.WaitforInformConfirm_Enabled = True
        self.sendCompletionResponse_Enabled = True
    
            
    
    def actions(self) -> None:
        if (self.wait_untill_timer(1,120)):
            self.receive()
            self.base_class.WaitforTransportOrderCompletion_In = self.save_in_message(self.message)
            try:
                statusMessage = self.base_class.WaitforTransportOrderCompletion_In["interactionElements"][0]
                statusResponse = statusMessage["submodelElements"][0]["value"]
                if (statusResponse == "E"):
                    self.base_class.responseMessage["status"] = "E"
                    self.base_class.responseMessage["code"] = statusMessage["submodelElements"][1]["value"]
                    self.base_class.responseMessage["message"] =  statusMessage["submodelElements"][2]["value"]
                    self.WaitforInformConfirm_Enabled = False
                else:
                    self.sendCompletionResponse_Enabled = False
            except Exception as e:
                self.base_class.responseMessage["status"] = "E"
                self.base_class.responseMessage["code"] = "E.014"
                self.base_class.responseMessage["message"] =  "Error Processing the Order"
                self.WaitforInformConfirm_Enabled = False            
        else:
            self.base_class.responseMessage["status"] = "E"
            self.base_class.responseMessage["code"] = "E.014"
            self.base_class.responseMessage["message"] =  "Error Processing the Order"
            self.WaitforInformConfirm_Enabled = True
        
    def transitions(self) -> object:
        if (self.WaitforInformConfirm_Enabled):
            ts = WaitforInformConfirm(self.base_class,"WaitforInformConfirm")
            return ts
        if (self.sendCompletionResponse_Enabled):
            ts = sendCompletionResponse(self.base_class,"sendCompletionResponse")
            return ts
        
class noProposalReceived(AState):
    
    def initialize(self):
        self.InputDocument = "NA"
        self.OutputDocument = "NA"
        # Gaurd variables for enabling the transitions
        self.sendCompletionResponse_Enabled = True
    
            
    
    def actions(self) -> None:
        self.base_class.responseMessage["status"] = "E"
        self.base_class.responseMessage["code"] = "E.06"
        self.base_class.responseMessage["message"] =  "No proposals received from any of the Service Providers"
        
    def transitions(self) -> object:
        if (self.sendCompletionResponse_Enabled):
            ts = sendCompletionResponse(self.base_class,"sendCompletionResponse")
            return ts
        
class sendTransportOrder(AState):
    
    def initialize(self):
        self.InputDocument = "NA"
        self.OutputDocument = "Order"
        # Gaurd variables for enabling the transitions
        self.WaitforTransportOrderCompletion_Enabled = True
    
            
    def create_outbound_message(self) -> list:
        outboundMessages = []
        message = self.base_class.WaitforNewOrder_In
        psp = ProductionStepOrder(self.base_class.pyaas)
        currentConvId = message["frame"]["conversationId"] 
        receiverId = message["frame"]["sender"]["id"]
        receiverRole = "TransportRequester"
        conV1 = message["frame"]["conversationId"]
        oMessage_Out = self.create_i40_message(self.OutputDocument,conV1,receiverId,receiverRole)
        #submodel = self.GetSubmodelById('submodelId')
        oMessage_Out["interactionElements"] = self.base_class.WaitforNewOrder_In["interactionElements"][1]
        self.save_out_message(oMessage_Out)
        outboundMessages.append(oMessage_Out)
        return outboundMessages
    
    def actions(self) -> None:
        try:
            #acceptproposalMessageList = list(self.base_class.sendacceptProposal_Queue.queue) # in case for further processing is required
            acceptproposalMessage = self.base_class.acceptProposal#acceptproposalMessageList[0]
            
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
        transportIdentifier = self.base_class.WaitforNewOrder_In["interactionElements"][1][0]
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
 
        try:
            status = self.save_submodel(self.TransportSubmodel["id"])
        except Exception as e:
            self.base_class.skillLogger.info("Error" + str(e))   
        
        
    def transitions(self) -> object:
        self.send(self.create_outbound_message())
        if (self.WaitforTransportOrderCompletion_Enabled):
            ts = WaitforTransportOrderCompletion(self.base_class,"WaitforTransportOrderCompletion")
            return ts
        
class EvaluateProposal(AState):
    
    def initialize(self):
        self.InputDocument = "NA"
        self.OutputDocument = "NA"
        # Gaurd variables for enabling the transitions
        self.sendrejectProposal_Enabled = True
    
    def getItem(self,submodelElement,Item_Name) -> int:
        for value in submodelElement["value"]:
            if value['idShort'] == Item_Name:
                return int(value['value'])              
    
    def check_list_price(self):
        pass
    
    def check_security_standard_submodel(self):
        pass
    
    def actions(self) -> None:
        try:
            proposlList = []
            ListPrice_CFP = [] 
            qsize = self.base_class.WaitForSPProposal_Queue.qsize()
            for i in range (0,qsize):
                proposlList.append(self.base_class.WaitForSPProposal_Queue.get())
            for eachPorposal in proposlList:
                for submodelElement in eachPorposal['interactionElements'][0]['submodelElements']:
                    if (submodelElement['idShort'] == 'CommercialProperties'):
                        ListPrice_CFP.append([self.getItem(submodelElement,"cfp"),self.getItem(submodelElement,"listprice")])
            
            qoutes = []
            
            for lsp in ListPrice_CFP:
                qoutes.append(lsp[0] + lsp[1])
            self.base_class.accept_proposals = []
            self.base_class.reject_proposals = []
            bestPrice = min(qoutes)
            bestPriceIndex = qoutes.index(bestPrice)  
            self.base_class.CFP = ListPrice_CFP[bestPriceIndex][0]        
            for i  in range(0,len(proposlList)):
                if (i == bestPriceIndex):
                    self.base_class.accept_proposals.append(proposlList[i])
                else:
                    self.base_class.reject_proposals.append(proposlList[i])
        except Exception as e:
            self.base_class.skillLogger.info("Evaluate Proposal Error" + str(e))        
        
    def transitions(self) -> object:
        if (self.sendrejectProposal_Enabled):
            ts = sendrejectProposal(self.base_class,"sendrejectProposal")
            return ts
        
class SendCFP(AState):
    
    def initialize(self):
        self.InputDocument = "NA"
        self.OutputDocument = "callForProposal"
        # Gaurd variables for enabling the transitions
        self.WaitForSPProposal_Enabled = True
    
            
    def create_outbound_message(self) -> list:
        outboundMessages = []
        message = self.base_class.WaitforNewOrder_In 
        receiverId = message["frame"]["sender"]["id"]
        receiverRole = message["frame"]["sender"]["role"]["name"]
        conV1 = message["frame"]["conversationId"]
        oMessage_Out = self.create_i40_message(self.OutputDocument,conV1,receiverId,receiverRole)
        submodel = self.GetSubmodelById(message["interactionElements"][0][0])
        oMessage_Out["interactionElements"].append(submodel)
        self.save_out_message(oMessage_Out)
        outboundMessages.append(oMessage_Out)
        return outboundMessages
    
    def actions(self) -> None:
        pass
        
    def transitions(self) -> object:
        self.send(self.create_outbound_message())
        if (self.WaitForSPProposal_Enabled):
            ts = WaitForSPProposal(self.base_class,"WaitForSPProposal")
            return ts
        
class sendCompletionResponse(AState):
    
    def initialize(self):
        self.InputDocument = "NA"
        self.OutputDocument = "OrderStatus"
        # Gaurd variables for enabling the transitions
        self.WaitforNewOrder_Enabled = True
    
    def create_outbound_message(self) -> list:
        outboundMessages = []
        message = self.base_class.WaitforNewOrder_In 
        receiverId = message["frame"]["sender"]["id"]
        receiverRole = message["frame"]["sender"]["role"]["name"]
        conV1 = message["frame"]["conversationId"]
        oMessage_Out = self.create_i40_message(self.OutputDocument,conV1,receiverId,receiverRole)
        #submodel = self.GetSubmodelById('submodelId')
        oMessage_Out[ "interactionElements"].append(self.InElem)
        self.save_out_message(oMessage_Out)
        outboundMessages.append(oMessage_Out)
        return outboundMessages
    
    def actions(self) -> None:
        self.InElem = self.base_class.StatusResponseSM
        self.InElem[0]["submodelElements"][0]["value"] = self.base_class.responseMessage["status"]
        self.InElem[0]["submodelElements"][1]["value"] = self.base_class.responseMessage["code"]
        self.InElem[0]["submodelElements"][2]["value"] = self.base_class.responseMessage["message"]
        self.set_cfp_properties(self.base_class.WaitforNewOrder_In["frame"]["conversationId"],
                                self.base_class.CFP)
        self.base_class.responseMessage = {}
        
    def transitions(self) -> object:
        self.send(self.create_outbound_message())
        if (self.WaitforNewOrder_Enabled):
            ts = WaitforNewOrder(self.base_class,"WaitforNewOrder")
            return ts
        
class WaitForSPProposal(AState):
    
    def initialize(self):
        self.InputDocument = "proposal"
        self.OutputDocument = "NA"
        self.in_queue = self.base_class.WaitForSPProposal_Queue
        self.base_class.WaitForSPProposal_In = self.message
        # Gaurd variables for enabling the transitions
        self.noProposalReceived_Enabled = True
        self.EvaluateProposal_Enabled = True
              
    
    def actions(self) -> None:
        if (self.wait_untill_timer(1,10)):
            self.receive()
            self.save_in_message(self.message)
            self.noProposalReceived_Enabled = False
        else:
            self.EvaluateProposal_Enabled = False
        
    def transitions(self) -> object:
        if (self.noProposalReceived_Enabled):
            ts = noProposalReceived(self.base_class,"noProposalReceived")
            return ts
        if (self.EvaluateProposal_Enabled):
            ts = EvaluateProposal(self.base_class,"EvaluateProposal")
            return ts
        
class WaitforInformConfirm(AState):
    
    def initialize(self):
        self.InputDocument = "informConfirm"
        self.OutputDocument = "NA"
        self.in_queue = self.base_class.WaitforInformConfirm_Queue
        self.base_class.WaitforInformConfirm_In = self.message
        # Gaurd variables for enabling the transitions
        self.sendCompletionResponse_Enabled = True
    
            
    
    def actions(self) -> None:
        if (self.wait_untill_timer(1,60)):
            self.receive()
            self.save_in_message(self.message)
            self.base_class.responseMessage["status"] = "S"
            self.base_class.responseMessage["code"] = "A.013"
            self.base_class.responseMessage["message"] =  "The Order is Succesfully Executed."      
        else:
            self.base_class.responseMessage["status"] = "E"
            self.base_class.responseMessage["code"] = "E.01"
            self.base_class.responseMessage["message"] =  "The placed order not executed successfully."      
        
    def transitions(self) -> object:
        if (self.sendCompletionResponse_Enabled):
            ts = sendCompletionResponse(self.base_class,"sendCompletionResponse")
            return ts
        
class WaitforNewOrder(AState):
    
    def initialize(self):
        self.InputDocument = "Order"
        self.OutputDocument = "NA"
        self.in_queue = self.base_class.WaitforNewOrder_Queue
        self.base_class.WaitforNewOrder_In = self.message
        # Gaurd variables for enabling the transitions
        self.cfpConfiguration_Enabled = True
        self.base_class.empty_all_queues()
            
    
    def actions(self) -> None:
        if (self.wait_untill(1)):
            self.base_class.WaitforNewOrder_In = self.receive()
            self.save_in_message(self.message)
        
    def transitions(self) -> object:
        if (self.cfpConfiguration_Enabled):
            ts = cfpConfiguration(self.base_class,"cfpConfiguration")
            return ts
        
class sendacceptProposal(AState):
    
    def initialize(self):
        self.InputDocument = "NA"
        self.OutputDocument = "acceptProposal"
        # Gaurd variables for enabling the transitions
        self.sendTransportOrder_Enabled = True
    
            
    def create_outbound_message(self) -> list:
        outboundMessages = []
        message = self.base_class.sendacceptProposal_Queue.get() 
        self.base_class.acceptProposal = message
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
        if (self.sendTransportOrder_Enabled):
            ts = sendTransportOrder(self.base_class,"sendTransportOrder")
            return ts
        



class BoringRequester(Actor):
    '''
    classdocs
    '''
    def initstate_specific_queue_internal(self) -> None:
        """
        """
        self.QueueDict = dict()
        
        self.WaitforTransportOrderCompletion_Queue = Queue.Queue()
        self.WaitForSPProposal_Queue = Queue.Queue()
        self.WaitforInformConfirm_Queue = Queue.Queue()
        self.WaitforNewOrder_Queue = Queue.Queue()
        
                
        self.QueueDict = {
              "OrderStatus": self.WaitforTransportOrderCompletion_Queue,
              "proposal": self.WaitForSPProposal_Queue,
              "informConfirm": self.WaitforInformConfirm_Queue,
              "Order": self.WaitforNewOrder_Queue,
            }
    
    def init_inbound_messages(self) -> None:
        self.WaitforNewOrder_In = None
        self.WaitForSPProposal_In = None
        self.WaitforInformConfirm_In = None
        self.WaitforTransportOrderCompletion_In = None
        pass
    
    def __init__(self,pyaas):
        '''
        Constructor
        '''
        self.SKILL_STATES = {
                          "cfpConfiguration": "cfpConfiguration",  "sendrejectProposal": "sendrejectProposal",  "WaitforTransportOrderCompletion": "WaitforTransportOrderCompletion",  "noProposalReceived": "noProposalReceived",  "sendTransportOrder": "sendTransportOrder",  "EvaluateProposal": "EvaluateProposal",  "SendCFP": "SendCFP",  "sendCompletionResponse": "sendCompletionResponse",  "WaitForSPProposal": "WaitForSPProposal",  "WaitforInformConfirm": "WaitforInformConfirm",  "WaitforNewOrder": "WaitforNewOrder",  "sendacceptProposal": "sendacceptProposal",
                       }
        
        self.skillName = "BoringRequester"
        self.enabledState = self.enabledStatus["Y"]
        self.semanticProtocol = "www.admin-shell.io/interaction/bidding"
        self.initialState = "WaitforNewOrder"
        self.skill_service = "Boring Requisition"
        
        Actor.__init__(self,pyaas,"BoringRequester",
                       "www.admin-shell.io/interaction/bidding",
                       "Boring Requisition","WaitforNewOrder")
                        
    
    def sendMessage(self, sendMessage) -> None:
        self.send(sendMessage)
    
    def receiveMessage(self,inMessage) -> None:
        try:    
            _messageType = str(inMessage['frame']['type'])
            self.QueueDict[_messageType].put(inMessage)
        except Exception as E:
            pass
    
    def start(self):
        WaitforNewOrder_1 = WaitforNewOrder(self)
        #self.stateChange("WaitforNewOrder")
        currentState = WaitforNewOrder_1
        self.run(currentState)


if __name__ == '__main__':
    
    lm2 = BoringRequester()
    lm2.Start('msgHandler')
