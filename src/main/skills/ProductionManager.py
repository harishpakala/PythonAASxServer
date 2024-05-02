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

class waitforStepOrderCompletion(AState):
    message_in =  ["OrderStatus",]       
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.excProductionStepSeq_Enabled = True
        self.sendFailureResponse_Enabled = True
            
    
    def actions(self) -> None:
        responseSM = self.getStatusResponseSM()
        if (self.wait_untill_message_timeout(1, 240, waitforStepOrderCompletion.message_in)):
            message = self.receive(waitforStepOrderCompletion.message_in[0])
            self.save_in_message(message)
            self.orderStatus = message["interactionElements"][0]["submodelElements"][0]["value"]
            
            if (self.orderStatus == "E"):
                self.excProductionStepSeq_Enabled = False
                responseSM["submodelElements"][0]["value"] = "E"
                responseSM["submodelElements"][1]["value"] = "E.013"
                responseSM["submodelElements"][2]["value"] = "The placed order is not successfully executed please try it later."
            else:
                self.sendFailureResponse_Enabled = False
                responseSM["submodelElements"][0]["value"] = "E"
                responseSM["submodelElements"][1]["value"] = "E.013"
                responseSM["submodelElements"][2]["value"] = "The placed order is successfully executed."
                
        else:
            responseSM["submodelElements"][0]["value"] = "E"
            responseSM["submodelElements"][1]["value"] = "E.013"
            responseSM["submodelElements"][2]["value"] = "The placed order is not successfully executed please try it later."
        self.push("responseSM", responseSM)
            
    def transitions(self) -> object:
        if (self.excProductionStepSeq_Enabled):
            return "excProductionStepSeq"
        if (self.sendFailureResponse_Enabled):
            return "sendFailureResponse"
        
class sendFailureResponse(AState):
    message_out =  ["OrderStatus",]
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.WaitforNewOrder_Enabled = True
            
    def create_outbound_message(self,msg_type) -> list:
        message = self.retrieve("ProductionOrder")
        receiverId = message["frame"]["sender"]["id"]
        receiverRole = message["frame"]["sender"]["role"]["name"]
        conV1 = message["frame"]["conversationId"]
        oMessage_Out = self.create_i40_message(msg_type,conV1,receiverId,receiverRole)
        #submodel = self.GetSubmodelById('submodelId')
        oMessage_Out["interactionElements"].append(self.retrieve("responseSM"))
        self.save_out_message(oMessage_Out)
        return [oMessage_Out]    
    def actions(self) -> None:
        pass
        
    def transitions(self) -> object:
        self.send(self.create_outbound_message(sendFailureResponse.message_out[0]))
        if (self.WaitforNewOrder_Enabled):
            return "WaitforNewOrder"
        
class retrieveProductionStepSeq(AState):
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.excProductionStepSeq_Enabled = True
            
    
    def actions(self) -> None:
        pass
        
    def transitions(self) -> object:
        if (self.excProductionStepSeq_Enabled):
            return "excProductionStepSeq"
        
class excProductionStepSeq(AState):
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.sendProductionStepOrder_Enabled = True
        self.sendCompletionResponse_Enabled = True
        self.sendFailureResponse_Enabled = True
            
    
    def actions(self) -> None:
        aasId = self.retrieve("ProductionOrder")["frame"]["sender"]["id"]
        
        if len(self.get_ProdutionStepList(aasId)) == 0:
            self.sendProductionStepOrder_Enabled = False
            self.sendFailureResponse_Enabled = False
            responseSM = self.getStatusResponseSM()
            responseSM["status"] = "S"
            responseSM["code"] = "A00.12"
            responseSM["message"] = "The placed order is successfully executed."
            self.push("responseSM", responseSM)
        else:
            self.sendCompletionResponse_Enabled = False
            self.sendFailureResponse_Enabled = False

        
    def transitions(self) -> object:
        if (self.sendProductionStepOrder_Enabled):
            return "sendProductionStepOrder"
        if (self.sendCompletionResponse_Enabled):
            return "sendCompletionResponse"
        if (self.sendFailureResponse_Enabled):
            return "sendFailureResponse"
        
class sendCompletionResponse(AState):
    message_out =  ["ProductionOrderStatus",]
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.WaitforNewOrder_Enabled = True
            
    def create_outbound_message(self,msg_type) -> list:
        message = self.retrieve("ProductionOrder")
        receiverId = message["frame"]["sender"]["id"]
        receiverRole = message["frame"]["sender"]["role"]["name"]
        conV1 = message["frame"]["conversationId"]
        oMessage_Out = self.create_i40_message(msg_type,conV1,receiverId,receiverRole)
        #submodel = self.GetSubmodelById('submodelId')
        oMessage_Out["interactionElements"].append(self.retrieve("responseSM"))
        self.save_out_message(oMessage_Out)
        return oMessage_Out
    
    def actions(self) -> None:
        pass
        
    def transitions(self) -> object:
        self.send(self.create_outbound_message(sendCompletionResponse.message_out[0]))
        if (self.WaitforNewOrder_Enabled):
            return "WaitforNewOrder"
        
class sendProductionStepOrder(AState):
    message_out =  ["Order",]
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.waitforStepOrderCompletion_Enabled = True
            
    def create_outbound_message(self,msg_type) -> list:
        message = self.retrieve("ProductionOrder")
        convsersationId = message["frame"]["conversationId"]
        receiverId = message["frame"]["sender"]["id"]
        receiverRole = self.productionStep["skill_name"]
        conV1 = self.create_new_sub_conversationId(receiverId,convsersationId)
        oMessage_Out = self.create_i40_message(msg_type,conV1,receiverId,receiverRole)
        #submodel = self.GetSubmodelById('submodelId')
        oMessage_Out["interactionElements"].extend(self.productionStep["submodel_id_idSHort_list"])
        self.save_out_message(oMessage_Out)
        return [oMessage_Out]
    
    def actions(self) -> None:
        aasId = self.retrieve("ProductionOrder")["frame"]["sender"]["id"]
        
        self.productionStep = self.get_production_step(aasId)
        self.productionStepLen = len(self.get_ProdutionStepList(aasId)) 
        
    def transitions(self) -> object:
        self.send(self.create_outbound_message(sendProductionStepOrder.message_out[0]))
        if (self.waitforStepOrderCompletion_Enabled):
            return "waitforStepOrderCompletion"
        
class WaitforNewOrder(AState):
    message_in =  ["ProductionOrder",]       
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.retrieveProductionStepSeq_Enabled = True
        self.WaitforNewOrder_Enabled = True
    
    def actions(self) -> None:
        if (self.wait_untill_message(1, WaitforNewOrder.message_in)):
            message = self.receive(WaitforNewOrder.message_in[0])
            self.save_in_message(message)
            self.push("ProductionOrder",message)
            print(message["frame"]["sender"]["id"], self.base_class.aasID)
            if message["frame"]["sender"]["id"] == self.base_class.aasID:
                self.WaitforNewOrder = False
            else:
                self.retrieveProductionStepSeq_Enabled = False
        else:
            self.actions()
        
    def transitions(self) -> object:
        if (self.retrieveProductionStepSeq_Enabled):
            return "retrieveProductionStepSeq"
        
        if (self.WaitforNewOrder_Enabled):
            return "WaitforNewOrder"


class ProductionManager(Actor):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''      
        Actor.__init__(self,"ProductionManager",
                       "www.admin-shell.io/interaction/productionmanagement",
                       "ProductionManager","WaitforNewOrder")
                        

    def start(self):
        self.run("WaitforNewOrder")


if __name__ == '__main__':
    
    lm2 = ProductionManager()
    lm2.Start('msgHandler')
