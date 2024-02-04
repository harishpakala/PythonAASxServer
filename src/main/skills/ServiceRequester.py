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

class WaitforTransportOrderCompletion(AState):
    message_in =  ["OrderStatus",]       
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.WaitforInformConfirm_Enabled = True
        self.sendCompletionResponse_Enabled = True
            
    
    def actions(self) -> None:
        if (self.wait_untill_timeout(10)):
            message = self.receive(WaitforTransportOrderCompletion.message_in[0])
            self.save_in_message(message)
        
    def transitions(self) -> object:
        if (self.WaitforInformConfirm_Enabled):
            return "WaitforInformConfirm"
        if (self.sendCompletionResponse_Enabled):
            return "sendCompletionResponse"
        
class sendTransportOrder(AState):
    message_out =  ["Order",]
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.WaitforTransportOrderCompletion_Enabled = True
            
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
        self.send(self.create_outbound_message(sendTransportOrder.message_out[0]))
        if (self.WaitforTransportOrderCompletion_Enabled):
            return "WaitforTransportOrderCompletion"
        
class sendrejectProposal(AState):
    message_out =  ["rejectProposal",]
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
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
        self.send(self.create_outbound_message(sendrejectProposal.message_out[0]))
        if (self.sendacceptProposal_Enabled):
            return "sendacceptProposal"
        
class WaitforSelection(AState):
    message_in =  ["selectproposal",]       
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.sendConfirmation_Enabled = True
            
    
    def actions(self) -> None:
        if (self.wait_untill_timeout(10)):
            message = self.receive(WaitforSelection.message_in[0])
            self.save_in_message(message)
        
    def transitions(self) -> object:
        if (self.sendConfirmation_Enabled):
            return "sendConfirmation"
        
class WaitforInformConfirm(AState):
    message_in =  ["informConfirm",]       
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.sendCompletionResponse_Enabled = True
            
    
    def actions(self) -> None:
        if (self.wait_untill_timeout(10)):
            message = self.receive(WaitforInformConfirm.message_in[0])
            self.save_in_message(message)
        
    def transitions(self) -> object:
        if (self.sendCompletionResponse_Enabled):
            return "sendCompletionResponse"
        
class sendacceptProposal(AState):
    message_out =  ["acceptProposal",]
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.sendTransportOrder_Enabled = True
            
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
        self.send(self.create_outbound_message(sendacceptProposal.message_out[0]))
        if (self.sendTransportOrder_Enabled):
            return "sendTransportOrder"
        
class noProposalReceived(AState):
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.sendCompletionResponse_Enabled = True
            
    
    def actions(self) -> None:
        pass
        
    def transitions(self) -> object:
        if (self.sendCompletionResponse_Enabled):
            return "sendCompletionResponse"
        
class sendCompletionResponse(AState):
    message_out =  ["OrderStatus",]
    
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
        self.send(self.create_outbound_message(sendCompletionResponse.message_out[0]))
        if (self.WaitforNewOrder_Enabled):
            return "WaitforNewOrder"
        
class SendListofProposals(AState):
    message_in =  ["listofproposals",]       
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.WaitforSelection_Enabled = True
            
    
    def actions(self) -> None:
        if (self.wait_untill_timeout(10)):
            message = self.receive(SendListofProposals.message_in[0])
            self.save_in_message(message)
        
    def transitions(self) -> object:
        if (self.WaitforSelection_Enabled):
            return "WaitforSelection"
        
class sendConfirmation(AState):
    message_in =  ["confirmation",]       
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.sendrejectProposal_Enabled = True
            
    
    def actions(self) -> None:
        if (self.wait_untill_timeout(10)):
            message = self.receive(sendConfirmation.message_in[0])
            self.save_in_message(message)
        
    def transitions(self) -> object:
        if (self.sendrejectProposal_Enabled):
            return "sendrejectProposal"
        
class WaitForSPProposal(AState):
    message_in =  ["proposal",]       
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.noProposalReceived_Enabled = True
        self.SendListofProposals_Enabled = True
            
    
    def actions(self) -> None:
        if (self.wait_untill_timeout(10)):
            message = self.receive(WaitForSPProposal.message_in[0])
            self.save_in_message(message)
        
    def transitions(self) -> object:
        if (self.noProposalReceived_Enabled):
            return "noProposalReceived"
        if (self.SendListofProposals_Enabled):
            return "SendListofProposals"
        
class WaitforNewOrder(AState):
    message_in =  ["Order",]       
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.cfpConfiguration_Enabled = True
            
    
    def actions(self) -> None:
        if (self.wait_untill_message(1,WaitforNewOrder.message_in[0])):
            message = self.receive(WaitforNewOrder.message_in[0])
            self.save_in_message(message)
        
    def transitions(self) -> object:
        if (self.cfpConfiguration_Enabled):
            return "cfpConfiguration"
        
class SendCFP(AState):
    message_out =  ["callForProposal",]
    
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
        self.send(self.create_outbound_message(SendCFP.message_out[0]))
        if (self.WaitForSPProposal_Enabled):
            return "WaitForSPProposal"
        
class cfpConfiguration(AState):
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.sendCompletionResponse_Enabled = True
        self.SendCFP_Enabled = True
            
    
    def actions(self) -> None:
        pass
        
    def transitions(self) -> object:
        if (self.sendCompletionResponse_Enabled):
            return "sendCompletionResponse"
        if (self.SendCFP_Enabled):
            return "SendCFP"
        
class ServiceRequester(Actor):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''      
        Actor.__init__(self,"ServiceRequester",
                       "www.admin-shell.io/interaction/bidding",
                       "Service Requisition","WaitforNewOrder")
                        

    def start(self):
        self.run("WaitforNewOrder")


if __name__ == '__main__':
    
    lm2 = ServiceRequester()
    lm2.Start('msgHandler')
