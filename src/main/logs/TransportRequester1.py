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
    from utils.utils import Actor,AState
except ImportError:
    from main.utils.utils import Actor,AState


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
        if (len(self.base_class.WaitforNewOrder_In["interactionElements"]) == 1):
            transportIdentifier = self.base_class.WaitforNewOrder_In["interactionElements"][0][0]
            transport_submodel,status,statuscode = self.base_class.pyaas.dba.GetSubmodelById(transportIdentifier)
            if transport_submodel["semanticId"]["keys"][0]["value"] == "0173-1#01-ADR740#004":
                self.sendCompletionResponse_Enabled = False
            else:
                    self.base_class.responseMessage["status"] = "E"
                    self.base_class.responseMessage["code"] = "E.01"
                    self.base_class.responseMessage["message"] =  "The Transport submodel is not provided"
                    self.SendCFP_Enabled = False
        else:
            self.base_class.responseMessage["status"] = "E"
            self.base_class.responseMessage["code"] = "E.01"
            self.base_class.responseMessage["message"] =  "No submodel Id is provided"
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
        pass
        
    def transitions(self) -> object:
        self.send(self.create_outbound_message())
        if (self.sendCompletionResponse_Enabled):
            ts = sendCompletionResponse(self.base_class,"sendCompletionResponse")
            return ts
        if (self.sendacceptProposal_Enabled):
            ts = sendacceptProposal(self.base_class,"sendacceptProposal")
            return ts
        
class noProposalReceived(AState):
    
    def initialize(self):
        self.InputDocument = "NA"
        self.OutputDocument = "NA"
        # Gaurd variables for enabling the transitions
        self.sendCompletionResponse_Enabled = True
    
            
    
    def actions(self) -> None:
        pass
        
    def transitions(self) -> object:
        if (self.sendCompletionResponse_Enabled):
            ts = sendCompletionResponse(self.base_class,"sendCompletionResponse")
            return ts
        
class EvaluateProposal(AState):
    
    def initialize(self):
        self.InputDocument = "NA"
        self.OutputDocument = "NA"
        # Gaurd variables for enabling the transitions
        self.sendrejectProposal_Enabled = True
    
    def getItem(self,submodelElement,Item_Name):
        for value in submodelElement["value"]:
            if value['idShort'] == Item_Name:
                return int(value['value'])             
    
    def actions(self) -> None:
        try:
            proposlList = []
            ListPrice_CFP = [] 
            for eachPorposal in self.base_class.proposals:
                for submodelElement in eachPorposal['interactionElements'][0]['submodelElements']:
                    if (submodelElement['idShort'] == 'CommercialProperties'):
                        ListPrice_CFP.append([self.getItem(submodelElement,"cfp"),self.getItem(submodelElement,"listprice")])
            
            qoutes = []
            
            for lsp in ListPrice_CFP:
                qoutes.append(lsp[0] + lsp[1])
            
            bestPrice = min(qoutes)
            bestPriceIndex = qoutes.index(bestPrice)          
            self.base_class.CFP = ListPrice_CFP[bestPriceIndex][0]
            self.base_class.accept_proposals = []
            self.base_class.reject_proposals = []
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
        submodel = self.GetSubmodelById(self.base_class.WaitforNewOrder_In["interactionElements"][0][0])
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
            self.base_class.proposals = self.receive_all()
            for msg in self.base_class.proposals:
                self.save_in_message(msg)
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
        self.WaitforInformConfirm_Enabled = True
    
            
    def create_outbound_message(self) -> list:
        outboundMessages = []
        message = self.base_class.accept_proposals[0] 
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
        if (self.WaitforInformConfirm_Enabled):
            ts = WaitforInformConfirm(self.base_class,"WaitforInformConfirm")
            return ts
        



class TransportRequester(Actor):
    '''
    classdocs
    '''
    def initstate_specific_queue_internal(self) -> None:
        """
        """
        self.QueueDict = dict()
        
        self.WaitForSPProposal_Queue = Queue.Queue()
        self.WaitforInformConfirm_Queue = Queue.Queue()
        self.WaitforNewOrder_Queue = Queue.Queue()
        
                
        self.QueueDict = {
              "proposal": self.WaitForSPProposal_Queue,
              "informConfirm": self.WaitforInformConfirm_Queue,
              "Order": self.WaitforNewOrder_Queue,
            }
    
    def init_inbound_messages(self) -> None:
        self.WaitforNewOrder_In = None
        self.WaitForSPProposal_In = None
        self.WaitforInformConfirm_In = None
        pass
    
    def __init__(self,pyaas):
        '''
        Constructor
        '''
        self.SKILL_STATES = {
                          "cfpConfiguration": "cfpConfiguration",  "sendrejectProposal": "sendrejectProposal",  "noProposalReceived": "noProposalReceived",  "EvaluateProposal": "EvaluateProposal",  "SendCFP": "SendCFP",  "sendCompletionResponse": "sendCompletionResponse",  "WaitForSPProposal": "WaitForSPProposal",  "WaitforInformConfirm": "WaitforInformConfirm",  "WaitforNewOrder": "WaitforNewOrder",  "sendacceptProposal": "sendacceptProposal",
                       }
        
        self.skillName = "TransportRequester"
        self.enabledState = self.enabledStatus["Y"]
        self.semanticProtocol = "www.admin-shell.io/interaction/bidding"
        self.initialState = "WaitforNewOrder"
        self.skill_service = "Transport Requisition"
        
        Actor.__init__(self,pyaas,"TransportRequester",
                       "www.admin-shell.io/interaction/bidding",
                       "Transport Requisition","WaitforNewOrder")
                        
    
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
    
    lm2 = TransportRequester()
    lm2.Start('msgHandler')
