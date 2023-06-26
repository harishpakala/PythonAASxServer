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
    from utils.utils import Actor,AState,message_in,message_out
except ImportError:
    from main.utils.utils import Actor,AState,message_in,message_out

class EvaluateProposal(AState):
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.sendrejectProposal_Enabled = True
            
    
    def actions(self) -> None:
        pass
        
    def transitions(self) -> object:
        if (self.sendrejectProposal_Enabled):
            return "sendrejectProposal"
        
class sendCompletionResponse(AState):
    message_out.OrderStatus =  "OrderStatus"
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.WaitforNewOrder_Enabled = True
            
    def create_outbound_message(self,msg_type) -> list:
        receiverId =""
        receiverRole = ""
        conV1 = ""
        oMessage_Out = self.create_i40_message(msg_type,conV1,receiverId,receiverRole)
        #submodel = self.GetSubmodelById('submodelId')
        #oMessage_Out["interactionElements"].append(submodel)
        self.save_out_message(oMessage_Out)
        return oMessage_Out
    
    def actions(self) -> None:
        pass
        
    def transitions(self) -> object:
        self.send(self.create_outbound_message(sendCompletionResponse.message_out.NONE))
        if (self.WaitforNewOrder_Enabled):
            return "WaitforNewOrder"
        
class sendrejectProposal(AState):
    message_out.rejectProposal =  "rejectProposal"
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.sendCompletionResponse_Enabled = True
        self.sendacceptProposal_Enabled = True
            
    def create_outbound_message(self,msg_type) -> list:
        receiverId =""
        receiverRole = ""
        conV1 = ""
        oMessage_Out = self.create_i40_message(msg_type,conV1,receiverId,receiverRole)
        #submodel = self.GetSubmodelById('submodelId')
        #oMessage_Out["interactionElements"].append(submodel)
        self.save_out_message(oMessage_Out)
        return oMessage_Out
    
    def actions(self) -> None:
        pass
        
    def transitions(self) -> object:
        self.send(self.create_outbound_message(sendrejectProposal.message_out.NONE))
        if (self.sendCompletionResponse_Enabled):
            return "sendCompletionResponse"
        if (self.sendacceptProposal_Enabled):
            return "sendacceptProposal"
        
class cfpConfiguration(AState):
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.SendCFP_Enabled = True
            
    
    def actions(self) -> None:
        pass
        
    def transitions(self) -> object:
        if (self.SendCFP_Enabled):
            return "SendCFP"
        
class sendacceptProposal(AState):
    message_out.acceptProposal =  "acceptProposal"
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.WaitforInformConfirm_Enabled = True
            
    def create_outbound_message(self,msg_type) -> list:
        receiverId =""
        receiverRole = ""
        conV1 = ""
        oMessage_Out = self.create_i40_message(msg_type,conV1,receiverId,receiverRole)
        #submodel = self.GetSubmodelById('submodelId')
        #oMessage_Out["interactionElements"].append(submodel)
        self.save_out_message(oMessage_Out)
        return oMessage_Out
    
    def actions(self) -> None:
        pass
        
    def transitions(self) -> object:
        self.send(self.create_outbound_message(sendacceptProposal.message_out.NONE))
        if (self.WaitforInformConfirm_Enabled):
            return "WaitforInformConfirm"
        
class noProposalReceived(AState):
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.sendCompletionResponse_Enabled = True
            
    
    def actions(self) -> None:
        pass
        
    def transitions(self) -> object:
        if (self.sendCompletionResponse_Enabled):
            return "sendCompletionResponse"
        
class WaitForSPProposal(AState):
    message_in.proposal =  "proposal"
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.noProposalReceived_Enabled = True
        self.EvaluateProposal_Enabled = True
            
    
    def actions(self) -> None:
        if (self.wait_untill_timeout(10)):
            self.receive(WaitForSPProposal.message_out.NONE)
            self.save_in_message(self.message)
        
    def transitions(self) -> object:
        if (self.noProposalReceived_Enabled):
            return "noProposalReceived"
        if (self.EvaluateProposal_Enabled):
            return "EvaluateProposal"
        
class WaitforNewOrder(AState):
    message_in.Order =  "Order"
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.cfpConfiguration_Enabled = True
            
    
    def actions(self) -> None:
        if (self.wait_untill_timeout(10)):
            self.receive(WaitforNewOrder.message_out.NONE)
            self.save_in_message(self.message)
        
    def transitions(self) -> object:
        if (self.cfpConfiguration_Enabled):
            return "cfpConfiguration"
        
class SendCFP(AState):
    message_out.callForProposal =  "callForProposal"
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.WaitForSPProposal_Enabled = True
            
    def create_outbound_message(self,msg_type) -> list:
        receiverId =""
        receiverRole = ""
        conV1 = ""
        oMessage_Out = self.create_i40_message(msg_type,conV1,receiverId,receiverRole)
        #submodel = self.GetSubmodelById('submodelId')
        #oMessage_Out["interactionElements"].append(submodel)
        self.save_out_message(oMessage_Out)
        return oMessage_Out
    
    def actions(self) -> None:
        pass
        
    def transitions(self) -> object:
        self.send(self.create_outbound_message(SendCFP.message_out.NONE))
        if (self.WaitForSPProposal_Enabled):
            return "WaitForSPProposal"
        
class WaitforInformConfirm(AState):
    message_in.informConfirm =  "informConfirm"
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.sendCompletionResponse_Enabled = True
            
    
    def actions(self) -> None:
        if (self.wait_untill_timeout(10)):
            self.receive(WaitforInformConfirm.message_out.NONE)
            self.save_in_message(self.message)
        
    def transitions(self) -> object:
        if (self.sendCompletionResponse_Enabled):
            return "sendCompletionResponse"
        



class TransportRequester(Actor):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''      
        Actor.__init__(self,"TransportRequester",
                       "www.admin-shell.io/interaction/bidding",
                       "Transport Requisition","WaitforNewOrder")
                        

    def start(self):
        self.run("WaitforNewOrder")


if __name__ == '__main__':
    
    lm2 = TransportRequester()
    lm2.Start('msgHandler')
