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

class waitforRegisterAck(AState):
    message_in =  ["registerack",]       
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.notifyOnError_Enabled = True
        self.evaluateRegisterAck_Enabled = True
        
    
    def actions(self) -> None:
        if (self.wait_untill_message_timeout(1,100,waitforRegisterAck.message_in)):
            message = self.receive(waitforRegisterAck.message_in[0])
            self.save_in_message(message)
            self.push("registerack",message)
            self.notifyOnError_Enabled = False
        else:
            status = dict()
            status["status"] = "E"
            status["code"] =  "E.1"
            status["message"] = "No response from the registry"
            self.push("status",status)
            self.evaluateRegisterAck_Enabled = False
        
    def transitions(self) -> object:
        if (self.notifyOnError_Enabled):
            return "notifyOnError"
        if (self.evaluateRegisterAck_Enabled):
            return "evaluateRegisterAck"
        
class notifyOnError(AState):
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.sendCompletionResponse_Enabled = True
            
    
    def actions(self) -> None:
        pass
        
    def transitions(self) -> object:
        if (self.sendCompletionResponse_Enabled):
            return "sendCompletionResponse"
        
class CreateAndSendRegisterMessage(AState):
    message_out =  ["register",]
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.waitforRegisterAck_Enabled = True
            
    def create_outbound_message(self,msg_type) -> list:
        order = self.retrieve("Order")
        receiverId ="AASpillarbox"
        receiverRole = "RegistryHandler"
        conV1 = order["frame"]["conversationId"]
        _descriptor = self.configureDescriptor(self.retrieve("Order")["frame"]["sender"]["id"])
        oMessage_Out = self.create_i40_message(msg_type,conV1,receiverId,receiverRole)
        #submodel = self.GetSubmodelById('submodelId')
        oMessage_Out["interactionElements"].append(_descriptor)
        self.save_out_message(oMessage_Out)
        return [oMessage_Out]
    
    def actions(self) -> None:
        pass
        
    def transitions(self) -> object:
        self.send(self.create_outbound_message(CreateAndSendRegisterMessage.message_out[0]))
        if (self.waitforRegisterAck_Enabled):
            return "waitforRegisterAck"
        
class WaitforNewOrder(AState):
    message_in =  ["Order",]       
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.CreateAndSendRegisterMessage_Enabled = True
        self.flush_tape()
    
    def actions(self) -> None:
        if (self.wait_untill_message(1, WaitforNewOrder.message_in)):
            message = self.receive(WaitforNewOrder.message_in[0])
            self.push("Order",message)
            self.save_in_message(message)
        
    def transitions(self) -> object:
        if (self.CreateAndSendRegisterMessage_Enabled):
            return "CreateAndSendRegisterMessage"
        
class evaluateRegisterAck(AState):
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.notifyOnError_Enabled = True
        self.notifyonSuccessRegistration_Enabled = True
            
    
    def actions(self) -> None:
        status = dict()
        registerack = self.retrieve("registerack")
        status["status"] = registerack["interactionElements"][0]["submodelElements"][0]["value"]
        status["code"] = registerack["interactionElements"][0]["submodelElements"][1]["value"]
        status["message"] = registerack["interactionElements"][0]["submodelElements"][2]["value"]
        self.push("status",status)
        if status["status"] == "S":
            self.notifyOnError_Enabled = False
        else:
            self.notifyonSuccessRegistration_Enabled = False
        
    def transitions(self) -> object:
        if (self.notifyOnError_Enabled):
            return "notifyOnError"
        if (self.notifyonSuccessRegistration_Enabled):
            return "notifyonSuccessRegistration"
        
class notifyonSuccessRegistration(AState):
    
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
        order = self.receive("Order")
        receiverId = order["frame"]["sender"]["id"]
        receiverRole = order["frame"]["sender"]["role"]["name"]
        conV1 = order["frame"]["sender"]["conversationId"]
        oMessage_Out = self.create_i40_message(msg_type,conV1,receiverId,receiverRole)
        oMessage_Out["interactionElements"].append(self.statusSubmodel)
        self.save_out_message(oMessage_Out)
        return [oMessage_Out]
    
    def actions(self) -> None:
        self.statusSubmodel = self.getStatusResponseSM()
        response = self.retrieve("status")
        self.statusSubmodel["submodelElements"][0]["value"] = response["status"]
        self.statusSubmodel["submodelElements"][1]["value"] = response["code"]
        self.statusSubmodel["submodelElements"][2]["value"] = response["message"]

        
    def transitions(self) -> object:
        self.send(self.create_outbound_message(sendCompletionResponse.message_out[0]))
        if (self.WaitforNewOrder_Enabled):
            return "WaitforNewOrder"
        



class Register(Actor):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''      
        Actor.__init__(self,"Register",
                       "www.admin-shell.io/interaction/registration",
                       "Registration","WaitforNewOrder")
                        

    def start(self):
        self.run("WaitforNewOrder")


if __name__ == '__main__':
    
    lm2 = Register()
    lm2.Start('msgHandler')
