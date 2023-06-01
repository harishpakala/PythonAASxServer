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
from copy import deepcopy
try:
    from utils.utils import Actor,AState
except ImportError:
    from main.utils.utils import Actor,AState

'''

'''    
class sendCompletionResponse(AState):
    
    def initialize(self):
        self.InputDocument = "NA"
        self.OutputDocument = "OrderResponse"
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
        self.save_out_message(oMessage_Out)
        outboundMessages.append(oMessage_Out)
        return outboundMessages
    
    def actions(self) -> None:
        pass
        
    def transitions(self) -> object:
        self.send(self.create_outbound_message())
        if (self.WaitforNewOrder_Enabled):
            ts = WaitforNewOrder(self.base_class,"WaitforNewOrder")
            return ts
        
class WaitforProposal(AState):
    
    def initialize(self):
        self.InputDocument = "proposal"
        self.OutputDocument = "NA"
        self.in_queue = self.base_class.WaitforProposal_Queue
        # Gaurd variables for enabling the transitions
        self.EvaluateProposal_Enabled = True
        self.sendCompletionResponse_Enabled = True
        
    
    def actions(self) -> None:
        if (self.wait(5)):
            if self.rcv_msg_count() == 1:
                self.base_class.proposal_In = self.receive()
                self.save_in_message(self.message)
                self.sendCompletionResponse_Enabled = False
            else:
                self.base_class.responseMessage["status"] = "E"
                self.base_class.responseMessage["code"] = "E.013"
                self.base_class.responseMessage["message"] = "Error processing the order."
                self.EvaluateProposal_Enabled = False
        
    def transitions(self) -> object:
        if (self.EvaluateProposal_Enabled):
            ts = EvaluateProposal(self.base_class,"EvaluateProposal")
            return ts
        if (self.sendCompletionResponse_Enabled):
            ts = sendCompletionResponse(self.base_class,"sendCompletionResponse")
            return ts
        
class SendCriteriaSelection(AState):
    
    def initialize(self):
        self.InputDocument = "NA"
        self.OutputDocument = "criteria"
        # Gaurd variables for enabling the transitions
        self.WaitforProductDetails_Enabled = True
        
    def create_outbound_message(self) -> list:
        outboundMessages = []
        message = self.base_class.proposal_In 
        receiverId = message["frame"]["sender"]["id"]
        receiverRole = message["frame"]["sender"]["role"]["name"]
        conV1 = message["frame"]["conversationId"]
        oMessage_Out = self.create_i40_message(self.OutputDocument,conV1,receiverId,receiverRole)
        oMessage_Out["interactionElements"].append(self.outsubmodel)
        self.save_out_message(oMessage_Out)
        outboundMessages.append(oMessage_Out)
        return outboundMessages
    
    def actions(self) -> None:
        self.outsubmodel = deepcopy(self.base_class.WaitForSelectionCriteria_In["interactionElements"][0])
        self.outsubmodel["submodelElements"][0]["value"] = "True"
        self.outsubmodel["submodelElements"][1]["value"] = "True"
        
        
    def transitions(self) -> object:
        self.send(self.create_outbound_message())
        if (self.WaitforProductDetails_Enabled):
            ts = WaitforProductDetails(self.base_class,"WaitforProductDetails")
            return ts
        
class WaitforModifiedProposal(AState):
    
    def initialize(self):
        self.InputDocument = "proposal-modify"
        self.OutputDocument = "NA"
        self.in_queue = self.base_class.WaitforModifiedProposal_Queue
        #Gaurd variables for enabling the transitions
        self.EvaluateProposal_Enabled = True
        
    
    def actions(self) -> None:
        if (self.wait_untill(1)):
            self.base_class.proposal_In = self.receive()
            self.save_in_message(self.message)
        
    def transitions(self) -> object:
        if (self.EvaluateProposal_Enabled):
            ts = EvaluateProposal(self.base_class,"EvaluateProposal")
            return ts
        
class EvaluateProposal(AState):
    
    def initialize(self):
        self.InputDocument = "NA"
        self.OutputDocument = "NA"
        # Gaurd variables for enabling the transitions
        self.sendModifiedRequest_Enabled = True
        self.confirmSelection_Enabled = True
        
    
    def actions(self) -> None:
        self.proposal = self.base_class.proposal_In["interactionElements"][0] 
        if (int(self.proposal["value"][0]["max"]) - int(self.proposal["value"][0]["min"]) < 10):
            self.sendModifiedRequest_Enabled = False
        else:
            self.confirmSelection_Enabled = False
        
    def transitions(self) -> object:
        if (self.sendModifiedRequest_Enabled):
            ts = sendModifiedRequest(self.base_class,"sendModifiedRequest")
            return ts
        if (self.confirmSelection_Enabled):
            ts = confirmSelection(self.base_class,"confirmSelection")
            return ts
        
class sendModifiedRequest(AState):
    
    def initialize(self):
        self.InputDocument = "NA"
        self.OutputDocument = "request-proposal-modify"
        # Gaurd variables for enabling the transitions
        self.WaitforModifiedProposal_Enabled = True
        
    def create_outbound_message(self) -> list:
        outboundMessages = []
        message = self.base_class.proposal_In
        receiverId = message["frame"]["sender"]["id"]
        receiverRole = message["frame"]["sender"]["role"]["name"]
        conV1 = message["frame"]["conversationId"]
        oMessage_Out = self.create_i40_message(self.OutputDocument,conV1,receiverId,receiverRole)
        oMessage_Out["interactionElements"].append(self.proposal)
        self.save_out_message(oMessage_Out)
        outboundMessages.append(oMessage_Out)
        return outboundMessages
    
    def actions(self) -> None:
        self.proposal = self.base_class.proposal_In["interactionElements"][0]
        self.proposal["value"][0]["min"] = int(self.proposal["value"][0]["min"]) + 10
        self.proposal["value"][0]["max"] = int(self.proposal["value"][0]["max"]) - 10
         
        
    def transitions(self) -> object:
        self.send(self.create_outbound_message())
        if (self.WaitforModifiedProposal_Enabled):
            ts = WaitforModifiedProposal(self.base_class,"WaitforModifiedProposal")
            return ts
        
class cfpConfiguration(AState):
    
    def initialize(self):
        self.InputDocument = "NA"
        self.OutputDocument = "NA"
        # Gaurd variables for enabling the transitions
        self.sendCompletionResponse_Enabled = True
        self.sendRequest_Enabled = True
        
    
    def actions(self) -> None:
        try:
            if self.base_class.WaitforNewOrder_In["interactionElements"][0]["submodelElements"][0]["value"][0]["value"] == "ww.ovgu.de/submodel/Besteller_Requests":
                self.sendCompletionResponse_Enabled = False
            else:
                self.sendRequest_Enabled = False
                self.base_class.responseMessage["status"] = "E"
                self.base_class.responseMessage["code"] = "E.013"
                self.base_class.responseMessage["message"] = "The relevant submodel is not selected"
        except Exception as E:
            self.sendRequest_Enabled = False
            self.base_class.responseMessage["status"] = "E"
            self.base_class.responseMessage["code"] = "E.013"
            self.base_class.responseMessage["message"] = "Error processing the order."
        
        
    def transitions(self) -> object:
        if (self.sendCompletionResponse_Enabled):
            ts = sendCompletionResponse(self.base_class,"sendCompletionResponse")
            return ts
        if (self.sendRequest_Enabled):
            ts = sendRequest(self.base_class,"sendRequest")
            return ts
        
class WaitforNewOrder(AState):
    
    def initialize(self):
        self.InputDocument = "Order"
        self.OutputDocument = "NA"
        self.in_queue = self.base_class.WaitforNewOrder_Queue
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
        
class sendRequest(AState):
    
    def initialize(self):
        self.InputDocument = "NA"
        self.OutputDocument = "request-proposal"
        # Gaurd variables for enabling the transitions
        self.WaitforProposal_Enabled = True
        
    def create_outbound_message(self) -> list:
        outboundMessages = []
        message = self.base_class.WaitforNewOrder_In 
        receiverId = "ww.ovgu.de/aas/62cc0c7f-1e37-40fc-a0e5-6ffc7b245d35"
        receiverRole = "VWSProduzent"
        conV1 = message["frame"]["conversationId"]
        oMessage_Out = self.create_i40_message(self.OutputDocument,conV1,receiverId,receiverRole)
        oMessage_Out["interactionElements"].append(self.request)
        self.save_out_message(oMessage_Out)
        outboundMessages.append(oMessage_Out)
        return outboundMessages
    
    def actions(self) -> None:
        submodelId = self.base_class.WaitforNewOrder_In["interactionElements"][0]["submodelElements"][0]["value"][0]["value"]
        idSHortPath = self.base_class.WaitforNewOrder_In["interactionElements"][0]["submodelElements"][0]["value"][2]["value"]
        self.request = self.GetSubmodelELementByIdshoortPath(submodelId, idSHortPath)
    def transitions(self) -> object:
        self.send(self.create_outbound_message())
        if (self.WaitforProposal_Enabled):
            ts = WaitforProposal(self.base_class,"WaitforProposal")
            return ts
        
class WaitforProductDetails(AState):
    
    def initialize(self):
        self.InputDocument = "product"
        self.OutputDocument = "NA"
        self.in_queue = self.base_class.WaitforProductDetails_Queue
        self.base_class.WaitforProductDetails_In = self.message
        # Gaurd variables for enabling the transitions
        self.sendCompletionResponse_Enabled = True
    
    def actions(self) -> None:
        if (self.wait_untill(1)):
            self.receive()
            self.save_in_message(self.message)
            self.base_class.responseMessage["status"] = "S"
            self.base_class.responseMessage["code"] = "A001"
            self.base_class.responseMessage["message"] = "The order is succesfully executed"
            
    def transitions(self) -> object:
        if (self.sendCompletionResponse_Enabled):
            ts = sendCompletionResponse(self.base_class,"sendCompletionResponse")
            return ts
        
class confirmSelection(AState):
    
    def initialize(self):
        self.InputDocument = "NA"
        self.OutputDocument = "selection"
        # Gaurd variables for enabling the transitions
        self.WaitForSelectionCriteria_Enabled = True
        
    def create_outbound_message(self) -> list:
        outboundMessages = []
        message = self.base_class.proposal_In
        receiverId = message["frame"]["sender"]["id"]
        receiverRole = message["frame"]["sender"]["role"]["name"]
        conV1 = message["frame"]["conversationId"]
        oMessage_Out = self.create_i40_message(self.OutputDocument,conV1,receiverId,receiverRole)
        oMessage_Out["interactionElements"].append(self.selection)
        self.save_out_message(oMessage_Out)
        outboundMessages.append(oMessage_Out)
        return outboundMessages
    
    def actions(self) -> None:
        self.selection = self.base_class.proposal_In["interactionElements"][0]
        self.selection["value"][0]["modelType"] = "Property"
        selectedValue =  int (self.selection["value"][0]["max"])
        del self.selection["value"][0]["min"]
        del self.selection["value"][0]["max"]
        self.selection["value"][0]["value"]  = selectedValue
        
    def transitions(self) -> object:
        self.send(self.create_outbound_message())
        if (self.WaitForSelectionCriteria_Enabled):
            ts = WaitForSelectionCriteria(self.base_class,"WaitForSelectionCriteria")
            return ts
        
class WaitForSelectionCriteria(AState):
    
    def initialize(self):
        self.InputDocument = "selection-criteria"
        self.OutputDocument = "NA"
        self.in_queue = self.base_class.WaitForSelectionCriteria_Queue
        # Gaurd variables for enabling the transitions
        self.SendCriteriaSelection_Enabled = True
        self.sendCompletionResponse_Enabled = True
        
    
    def actions(self) -> None:
        if (self.wait_untill(1)):
            self.base_class.WaitForSelectionCriteria_In = self.receive()
            self.save_in_message(self.message)
        
    def transitions(self) -> object:
        if (self.SendCriteriaSelection_Enabled):
            ts = SendCriteriaSelection(self.base_class,"SendCriteriaSelection")
            return ts
        if (self.sendCompletionResponse_Enabled):
            ts = sendCompletionResponse(self.base_class,"sendCompletionResponse")
            return ts
        



class VWSBesterller(Actor):
    '''
    classdocs
    '''

        
    def initstate_specific_queue_internal(self) -> None:
        """
        """
        self.QueueDict = dict()
        
        self.WaitforProposal_Queue = Queue.Queue()
        self.WaitforModifiedProposal_Queue = Queue.Queue()
        self.WaitforNewOrder_Queue = Queue.Queue()
        self.WaitforProductDetails_Queue = Queue.Queue()
        self.WaitForSelectionCriteria_Queue = Queue.Queue()
        
                
        self.QueueDict = {
              "proposal": self.WaitforProposal_Queue,
              "proposal-modify": self.WaitforModifiedProposal_Queue,
              "Order": self.WaitforNewOrder_Queue,
              "product": self.WaitforProductDetails_Queue,
              "selection-criteria": self.WaitForSelectionCriteria_Queue,
            }
    
    def init_inbound_messages(self) -> None:
        self.WaitforProposal_In = None
        self.WaitforModifiedProposal_In = None
        self.WaitforNewOrder_In = None
        self.WaitforProductDetails_In = None
        self.WaitForSelectionCriteria_In = None
        pass
    
    def __init__(self,pyaas):
        '''
        Constructor
        '''
        self.SKILL_STATES = {
                          "sendCompletionResponse": "sendCompletionResponse",  "WaitforProposal": "WaitforProposal",  "SendCriteriaSelection": "SendCriteriaSelection",  "WaitforModifiedProposal": "WaitforModifiedProposal",  "EvaluateProposal": "EvaluateProposal",  "sendModifiedRequest": "sendModifiedRequest",  "cfpConfiguration": "cfpConfiguration",  "WaitforNewOrder": "WaitforNewOrder",  "sendRequest": "sendRequest",  "WaitforProductDetails": "WaitforProductDetails",  "confirmSelection": "confirmSelection",  "WaitForSelectionCriteria": "WaitForSelectionCriteria",
                       }

        Actor.__init__(self,pyaas,"VWSBesterller",
                       "www.admin-shell.io/interaction/negotiation",
                       "VWS Order","WaitforNewOrder")

                
    def start(self, msgHandler,shellObject,_uid) -> None:
        """
            Starting of the Actor state machine
        """
        super().start( msgHandler,shellObject,_uid)
        
        WaitforNewOrder_1 = WaitforNewOrder(self,"WaitforNewOrder")
        #self.stateChange("WaitforNewOrder")
        self.currentState = WaitforNewOrder_1
        self.InitialState = "WaitforNewOrder"
        super().run(self.currentState,self.InitialState)
    
    def receiveMessage(self,inMessage) -> None:
        try:    
            _messageType = str(inMessage['frame']['type'])
            self.QueueDict[_messageType].put(inMessage)
        except Exception as E:
            pass



if __name__ == '__main__':
    
    lm2 = VWSBesterller()
    lm2.Start('msgHandler')
