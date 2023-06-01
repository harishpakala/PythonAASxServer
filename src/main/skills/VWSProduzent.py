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
class WaitForResoponse(AState):
    
    def initialize(self):
        self.InputDocument = "request-proposal-modify / selection"
        self.OutputDocument = "NA"
        self.in_queue = self.base_class.WaitForResoponse_Queue
        # Gaurd variables for enabling the transitions
        self.reperformFeasibility_Enabled = True
        self.SendSelectionCriteria_Enabled = True
        
    
    def actions(self) -> None:
        if (self.wait_untill(1)):
            self.base_class.WaitForResoponse_In = self.receive()
            #self.save_in_message(self.message)
            if self.message["frame"]["type"] == "request-proposal-modify":
                self.SendSelectionCriteria_Enabled = False
            else:
                selection_elem = self.base_class.WaitForResoponse_In["interactionElements"][0]
                self.base_class.selectedAussendurchMesser = selection_elem["value"][0]["value"]
                self.reperformFeasibility_Enabled = False
        
    def transitions(self) -> object:
        if (self.reperformFeasibility_Enabled):
            ts = reperformFeasibility(self.base_class,"reperformFeasibility")
            return ts
        if (self.SendSelectionCriteria_Enabled):
            ts = SendSelectionCriteria(self.base_class,"SendSelectionCriteria")
            return ts
        
class SendSelectionCriteria(AState):
    
    def initialize(self):
        self.InputDocument = "NA"
        self.OutputDocument = "selection-criteria"
        self.in_queue = self.base_class.SendSelectionCriteria_Queue
        self.base_class.SendSelectionCriteria_In = self.message
        # Gaurd variables for enabling the transitions
        self.WaitForCriteria_Enabled = True
        
    #
    def actions(self) -> None:
        pass
        
    
    def create_outbound_message(self) -> list:
        outboundMessages = []
        message = self.base_class.WaitforRequestProposal_In 
        receiverId = message["frame"]["sender"]["id"]
        receiverRole = message["frame"]["sender"]["role"]["name"]
        conV1 = message["frame"]["conversationId"]
        oMessage_Out = self.create_i40_message(self.OutputDocument,conV1,receiverId,receiverRole)
        self.selection_submodel = self.GetSubmodelById("ww.ovgu.de/submodel/SelectionMechanism")
        oMessage_Out["interactionElements"].append(self.selection_submodel)
        #self.save_out_message(oMessage_Out)
        outboundMessages.append(oMessage_Out)
        return outboundMessages
    
    def transitions(self) -> object:
        self.send(self.create_outbound_message())
        if (self.WaitForCriteria_Enabled):
            ts = WaitForCriteria(self.base_class,"WaitForCriteria")
            return ts
        
class WaitForCriteria(AState):
    
    def initialize(self):
        self.InputDocument = "criteria"
        self.OutputDocument = "NA"
        self.in_queue = self.base_class.WaitForCriteria_Queue
        # Gaurd variables for enabling the transitions
        self.ProductSelection_Enabled = True
        
    
    def actions(self) -> None:
        if (self.wait_untill(1)):
            self.base_class.WaitForCriteria_In = self.receive()
            #self.save_in_message(self.message)
        
    def transitions(self) -> object:
        if (self.ProductSelection_Enabled):
            ts = ProductSelection(self.base_class,"ProductSelection")
            return ts
        
class SendProduct(AState):
    
    def initialize(self):
        self.InputDocument = "NA"
        self.OutputDocument = "product"
        # Gaurd variables for enabling the transitions
        self.WaitforRequestProposal_Enabled = True
        
    def create_outbound_message(self) -> list:
        outboundMessages = []
        message = self.base_class.WaitforRequestProposal_In 
        receiverId = message["frame"]["sender"]["id"]
        receiverRole = message["frame"]["sender"]["role"]["name"]
        conV1 = message["frame"]["conversationId"]
        oMessage_Out = self.create_i40_message(self.OutputDocument,conV1,receiverId,receiverRole)
        oMessage_Out["interactionElements"].append(self.selectedProducts[0])
        #self.save_out_message(oMessage_Out)
        outboundMessages.append(oMessage_Out)
        return outboundMessages
        
    def actions(self) -> None:
        selectionSubmodel = deepcopy(self.base_class.WaitForCriteria_In["interactionElements"][0])
        
        self.selectedProducts = []
        data_submodel = self.GetSubmodelById("ww.ovgu.de/submodel/KatologSubmodel")
        for product in data_submodel["submodelElements"]:
            if int(float(product["value"][1]["value"])) == self.base_class.selectedAussendurchMesser:
                self.selectedProducts.append(product)
                   
        
        #LeastCFP = selectionSubmodel["value"][0]["value"] 
        #LeastPrice = selectionSubmodel["value"][1]["value"] 
        
        
        
    def transitions(self) -> object:
        self.send(self.create_outbound_message())
        if (self.WaitforRequestProposal_Enabled):
            ts = WaitforRequestProposal(self.base_class,"WaitforRequestProposal")
            return ts
        
class reperformFeasibility(AState):
    
    def initialize(self):
        self.InputDocument = "NA"
        self.OutputDocument = "NA"
        # Gaurd variables for enabling the transitions
        self.sendModifiedProposal_Enabled = True
        
    
    def actions(self) -> None:
        aussenDurchmesser = [int(float(row[1])) for row in self.base_class.data_rows]
        aussenDurchmesser.sort()
        self.base_class.in_request = deepcopy(self.base_class.WaitforRequestProposal_In["interactionElements"][0]) 
        in_request_aussenDurchmesser_min = int(self.base_class.in_request["value"][0]["min"])
        in_request_aussenDurchmesser_max = int(self.base_class.in_request["value"][0]["max"])
        
        if aussenDurchmesser[0] > in_request_aussenDurchmesser_min:
            self.base_class.in_request["value"][0]["min"] = aussenDurchmesser[0]
        
        if aussenDurchmesser[-1] < in_request_aussenDurchmesser_max:
            self.base_class.in_request["value"][0]["max"] = aussenDurchmesser[-1]    
        
        
    def transitions(self) -> object:
        if (self.sendModifiedProposal_Enabled):
            ts = sendModifiedProposal(self.base_class,"sendModifiedProposal")
            return ts
        
class ProductSelection(AState):
    
    def initialize(self):
        self.InputDocument = "NA"
        self.OutputDocument = "NA"
        # Gaurd variables for enabling the transitions
        self.SendProduct_Enabled = True
        
    
    def actions(self) -> None:
        self.data_submodel = self.GetSubmodelById("ww.ovgu.de/submodel/KatologSubmodel")
        
        
    def transitions(self) -> object:
        if (self.SendProduct_Enabled):
            ts = SendProduct(self.base_class,"SendProduct")
            return ts
        
class WaitforRequestProposal(AState):
    
    def initialize(self):
        self.InputDocument = "request-proposal"
        self.OutputDocument = "NA"
        self.in_queue = self.base_class.WaitforRequestProposal_Queue
        # Gaurd variables for enabling the transitions
        self.performFeasibilityCheck_Enabled = True
        
    def create_data_records(self):
        self.base_class.data_rows = []
        for data_row in self.data_submodel["submodelElements"]:
            _row_value = data_row["value"]
            _row = [r["value"] for r in _row_value]
            self.base_class.data_rows.append(_row)
    
    def actions(self) -> None:
        if (self.wait_untill(1)):
            self.base_class.WaitforRequestProposal_In = self.receive()
            #self.save_in_message(self.message)
            self.data_submodel = self.GetSubmodelById("ww.ovgu.de/submodel/KatologSubmodel")
            self.create_data_records()
            
    def transitions(self) -> object:
        if (self.performFeasibilityCheck_Enabled):
            ts = performFeasibilityCheck(self.base_class,"performFeasibilityCheck")
            return ts
        
class sendProposal(AState):
    
    def initialize(self):
        self.InputDocument = "NA"
        self.OutputDocument = "proposal"
        # Gaurd variables for enabling the transitions
        self.WaitForResoponse_Enabled = True
        
    def create_outbound_message(self) -> list:
        outboundMessages = []
        message = self.base_class.WaitforRequestProposal_In 
        receiverId = message["frame"]["sender"]["id"]
        receiverRole = message["frame"]["sender"]["role"]["name"]
        conV1 = message["frame"]["conversationId"]
        oMessage_Out = self.create_i40_message(self.OutputDocument,conV1,receiverId,receiverRole)
        oMessage_Out["interactionElements"].append(self.base_class.in_request)
        #self.save_out_message(oMessage_Out)
        outboundMessages.append(oMessage_Out)
        return outboundMessages
    
    def actions(self) -> None:
        pass
            
    def transitions(self) -> object:
        self.send(self.create_outbound_message())
        if (self.WaitForResoponse_Enabled):
            ts = WaitForResoponse(self.base_class,"WaitForResoponse")
            return ts
        
class sendModifiedProposal(AState):
    
    def initialize(self):
        self.InputDocument = "NA"
        self.OutputDocument = "proposal-modify"
        # Gaurd variables for enabling the transitions
        self.WaitForResoponse_Enabled = True
    
    def create_outbound_message(self) -> list:
        outboundMessages = []
        message = self.base_class.WaitforRequestProposal_In 
        receiverId = message["frame"]["sender"]["id"]
        receiverRole = message["frame"]["sender"]["role"]["name"]
        conV1 = message["frame"]["conversationId"]
        oMessage_Out = self.create_i40_message(self.OutputDocument,conV1,receiverId,receiverRole)
        oMessage_Out["interactionElements"].append(self.base_class.in_request)
        #self.save_out_message(oMessage_Out)
        outboundMessages.append(oMessage_Out)
        return outboundMessages
        
    
    def actions(self) -> None:
        pass
        
    def transitions(self) -> object:
        self.send(self.create_outbound_message())
        if (self.WaitForResoponse_Enabled):
            ts = WaitForResoponse(self.base_class,"WaitForResoponse")
            return ts
        
class performFeasibilityCheck(AState):
    
    def initialize(self):
        self.InputDocument = "NA"
        self.OutputDocument = "NA"
        # Gaurd variables for enabling the transitions
        self.sendProposal_Enabled = True
        
    
    def actions(self) -> None:
        aussenDurchmesser = [int(float(row[1])) for row in self.base_class.data_rows]
        aussenDurchmesser.sort()
        self.base_class.in_request = deepcopy(self.base_class.WaitforRequestProposal_In["interactionElements"][0]) 
        in_request_aussenDurchmesser_min = self.base_class.in_request["value"][0]["min"]
        in_request_aussenDurchmesser_max = self.base_class.in_request["value"][0]["max"]
        
        if aussenDurchmesser[0] > int(in_request_aussenDurchmesser_min):
            self.base_class.in_request["value"][0]["min"] = aussenDurchmesser[0]
        
        if aussenDurchmesser[-1] < int(in_request_aussenDurchmesser_max):
            self.base_class.in_request["value"][0]["max"] = aussenDurchmesser[-1]    
        
    def transitions(self) -> object:
        if (self.sendProposal_Enabled):
            ts = sendProposal(self.base_class,"sendProposal")
            return ts


class VWSProduzent(Actor):
    '''
    classdocs
    '''

        
    def initstate_specific_queue_internal(self) -> None:
        """
        """
        self.QueueDict = dict()
        
        self.WaitForResoponse_Queue = Queue.Queue()
        self.SendSelectionCriteria_Queue = Queue.Queue()
        self.WaitForCriteria_Queue = Queue.Queue()
        self.WaitforRequestProposal_Queue = Queue.Queue()
        
                
        self.QueueDict = {
              "request-proposal-modify": self.WaitForResoponse_Queue,
              "selection": self.WaitForResoponse_Queue,
              "selection-criteria": self.SendSelectionCriteria_Queue,
              "criteria": self.WaitForCriteria_Queue,
              "request-proposal": self.WaitforRequestProposal_Queue,
            }
    
    def init_inbound_messages(self) -> None:
        self.WaitForCriteria_In = None
        self.WaitforRequestProposal_In = None
        self.WaitForResoponse_In = None
        self.SendSelectionCriteria_In = None
        pass
    
    def __init__(self,pyaas):
        '''
        Constructor
        '''
        self.SKILL_STATES = {
                          "WaitForResoponse": "WaitForResoponse",  "SendSelectionCriteria": "SendSelectionCriteria",  "WaitForCriteria": "WaitForCriteria",  "SendProduct": "SendProduct",  "reperformFeasibility": "reperformFeasibility",  "ProductSelection": "ProductSelection",  "WaitforRequestProposal": "WaitforRequestProposal",  "sendProposal": "sendProposal",  "sendModifiedProposal": "sendModifiedProposal",  "performFeasibilityCheck": "performFeasibilityCheck",
                       }

        Actor.__init__(self,pyaas,"VWSProduzent","www.admin-shell.io/interaction/negotiation","VWS Order","WaitforRequestProposal")

                
    def start(self, msgHandler,shellObject,_uid) -> None:
        """
            Starting of the Actor state machine
        """
        super().start( msgHandler,shellObject,_uid)
        
        WaitforRequestProposal_1 = WaitforRequestProposal(self,"WaitforRequestProposal")
        #self.stateChange("WaitforRequestProposal")
        self.currentState = WaitforRequestProposal_1
        self.InitialState = "WaitforRequestProposal"
        super().run(self.currentState,self.InitialState)
    
    def receiveMessage(self,inMessage) -> None:
        try:    
            _messageType = str(inMessage['frame']['type'])
            self.QueueDict[_messageType].put(inMessage)
        except Exception as E:
            pass



if __name__ == '__main__':
    
    lm2 = VWSProduzent()
    lm2.Start('msgHandler')
