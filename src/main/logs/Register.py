"""
Copyright (c) 2023 Otto-von-Guericke-Universitaet Magdeburg, Lehrstuhl Integrierte Automation
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
"""
from test.test_structmembers import ts

try:
    import queue as Queue
except ImportError:
    import Queue as Queue 
try:
    from utils.utils import Actor,AState
except ImportError:
    from main.utils.utils import Actor,AState

class WaitforNewOrder(AState):
    
    def initialize(self):
        self.InputDocument = "Order"
        self.OutputDocument = "NA"
        self.in_queue = self.base_class.WaitforNewOrder_Queue
        # Gaurd variables for enabling the transitions
        self.CreateAndSendRegisterMessage_Enabled = True
        
    
    def actions(self) -> None:
        if (self.wait_untill(1)):
            self.base_class.WaitforNewOrder_In = self.receive()
            self.save_in_message(self.message)
        
    def transitions(self) -> object:
        if (self.CreateAndSendRegisterMessage_Enabled):
            ts = CreateAndSendRegisterMessage(self.base_class,"CreateAndSendRegisterMessage")
            return ts

class CreateAndSendRegisterMessage(Actor):
    def initialize(self):
        self.InputDocument = "NA"
        self.OutputDocument = "NA"
        self.waitforRegisterAck_Enabled = True
    
    def actions(self) -> None:
        self.InElem = self.baseClass.pyaas.aasConfigurer.configureDescriptor(self.baseClass.WaitforNewOrder_In["frame"]["sender"]["id"])
    
    def create_outbound_message(self) -> list:
        outboundMessages = []
        message = self.base_class.WaitforNewOrder_In 
        receiverId = message["frame"]["sender"]["id"]
        receiverRole = self.productionStep["skill_name"]#message["frame"]["sender"]["role"]["name"]
        conV1 = message["frame"]["conversationId"]
        oMessage_Out = self.create_i40_message(self.OutputDocument,conV1,receiverId,receiverRole)
        oMessage_Out["interactionElements"].append(self.InElem)
        self.save_out_message(oMessage_Out)
        outboundMessages.append(oMessage_Out)
        return outboundMessages

    def transitions(self) -> object:
        self.send(self.create_outbound_message())
        if (self.waitforRegisterAck_Enabled):
            ts = CreateAndSendRegisterMessage(self.base_class,"waitforRegisterAck")
            return ts

class waitforRegisterAck(Actor):
    def initialize(self):
        self.InputDocument = "registerack"
        self.OutputDocument = "NA"
        self.notifyOnError_Enabled = True
        self.evaluateRegisterAck_Enabled = True
    
    def actions(self) -> None:
        if (self.wait_untill_timer(1,20)):
            self.base_class.WaitforNewOrder_In = self.receive()
            self.save_in_message(self.message)  
            self.notifyOnError_Enabled = False
        else:
            self.baseClass.responseMessage["status"] = "E"
            self.baseClass.responseMessage["code"] = "E.01"
            self.baseClass.responseMessage["message"] =  "No response form the RIC"          
            self.evaluateRegisterAck_Enabled = False     
             
    def transitions(self) -> object:
        if (self.notifyOnError_Enabled):
            ts = notifyOnError(self.base_class,"notifyOnError")
            return ts
        if (self.evaluateRegisterAck_Enabled):
            ts = evaluateRegisterAck(self.base_class,"evaluateRegisterAck")
            return ts

class notifyOnError:
    def initialize(self):    
        self.sendCompletionResponse_Enabled = True
    
    def actions(self):
        pass
    
    def transitions(self):
        if (self.sendCompletionResponse_Enabled):
            ts = sendCompletionResponse(self.base_class,"sendCompletionResponse")
            return ts

class sendCompletionResponse:
    def initialize(self):   
        self.WaitforNewOrder_Enabled = True
        self.InputDocument = "NA"
        self.OutputDocument = "OrderStatus"
        
    def actions(self):
        self.InElem = self.baseClass.statusInElem
        self.InElem["submodelElements"][0]["value"] = self.baseClass.responseMessage["status"]
        self.InElem["submodelElements"][1]["value"] = self.baseClass.responseMessage["code"]
        self.InElem["submodelElements"][2]["value"] = self.baseClass.responseMessage["message"]

    def create_outbound_message(self) -> list:
        outboundMessages = []
        message = self.base_class.WaitforNewOrder_In 
        receiverId = message["frame"]["sender"]["id"]
        receiverRole = self.productionStep["skill_name"]#message["frame"]["sender"]["role"]["name"]
        conV1 = message["frame"]["conversationId"]
        oMessage_Out = self.create_i40_message(self.OutputDocument,conV1,receiverId,receiverRole)
        oMessage_Out["interactionElements"].append(self.InElem)
        self.save_out_message(oMessage_Out)
        outboundMessages.append(oMessage_Out)
        return outboundMessages
                
    def transitions(self):
        self.send(self.create_outbound_message())
        if (self.WaitforNewOrder_Enabled):
            ts = WaitforNewOrder(self.base_class,"WaitforNewOrder")
            return ts
        
class evaluateRegisterAck(Actor):
    def initialize(self):
        self.InputDocument = "registerack"
        self.OutputDocument = "NA"
        self.notifyOnError_Enabled = True
        self.evaluateRegisterAck_Enabled = True
    
    def actions(self):
        pass
    
    def transitions(self):
        if self.notifyOnError_Enabled:
            ts = notifyOnError(self.base_class,"notifyOnError")
            return ts
        if self.evaluateRegisterAck_Enabled:
            ts = evaluateRegisterAck(self.base_class,"evaluateRegisterAck")


class Register(Actor):
    '''
    classdocs
    '''
        
    def initstate_specific_queue_internal(self) -> None:
        """
        """

        self.WaitforNewOrder_Queue = Queue.Queue()
        self.waitforRegisterAck_Queue = Queue.Queue()
        
                
        self.QueueDict = {
              "Order": self.WaitforNewOrder_Queue,
              "registerack": self.waitforRegisterAck_Queue,
            }
    

    def __init__(self,pyaas):
        '''
        Constructor
        '''
        Actor.__init__(self,pyaas,"ProductionManager",
                       "www.admin-shell.io/interaction/productionmanagement",
                       "ProductionManager","WaitforNewOrder")

                
    def start(self):
        WaitforNewOrder_1 = WaitforNewOrder(self)
        #self.stateChange("WaitforNewOrder")
        currentState = WaitforNewOrder_1
        self.run(currentState)

    def receiveMessage(self,inMessage) -> None:
        try:    
            _messageType = str(inMessage['frame']['type'])
            self.QueueDict[_messageType].put(inMessage)
        except Exception as E:
            pass



if __name__ == '__main__':
    
    lm2 = Register()
    lm2.Start('msgHandler')
            