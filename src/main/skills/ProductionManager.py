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
class WaitforNewOrder(AState):
    
    def initialize(self):
        self.InputDocument = "ProductionOrder"
        self.OutputDocument = "NA"
        self.in_queue = self.base_class.WaitforNewOrder_Queue
        # Gaurd variables for enabling the transitions
        self.retrieveProductionStepSeq_Enabled = True
        
    
    def actions(self) -> None:
        if (self.wait_untill(1)):
            self.base_class.WaitforNewOrder_In = self.receive()
            self.save_in_message(self.message)
        
    def transitions(self) -> object:
        if (self.retrieveProductionStepSeq_Enabled):
            ts = retrieveProductionStepSeq(self.base_class,"retrieveProductionStepSeq")
            return ts
        
class excProductionStepSeq(AState):
    
    def initialize(self):
        self.InputDocument = "NA"
        self.OutputDocument = "NA"
        # Gaurd variables for enabling the transitions
        self.sendProductionStepOrder_Enabled = True
        self.sendCompletionResponse_Enabled = True
        self.sendFailureResponse_Enabled = True
        
    
    def actions(self) -> None:
        aasId = self.base_class.WaitforNewOrder_In["frame"]["sender"]["id"]
        _uid = self.base_class.pyaas.aasHashDict.__getHashEntry__(aasId).__getId__()
        aasShellObject = self.base_class.pyaas.aasShellHashDict.__getHashEntry__(_uid)
        if len(aasShellObject.productionStepList) == 0:
            self.sendProductionStepOrder_Enabled = False
            self.sendFailureResponse_Enabled = False
            self.base_class.responseMessage["status"] = "S"
            self.base_class.responseMessage["code"] = "A00.12"
            self.base_class.responseMessage["message"] = "The placed order is successfully executed."

        else:
            self.sendCompletionResponse_Enabled = False
            self.sendFailureResponse_Enabled = False
        
    def transitions(self) -> object:
        if (self.sendProductionStepOrder_Enabled):
            ts = sendProductionStepOrder(self.base_class,"sendProductionStepOrder")
            return ts
        if (self.sendCompletionResponse_Enabled):
            ts = sendCompletionResponse(self.base_class,"sendCompletionResponse")
            return ts
        if (self.sendFailureResponse_Enabled):
            ts = sendFailureResponse(self.base_class,"sendFailureResponse")
            return ts
        
class waitforStepOrderCompletion(AState):
    
    def initialize(self):
        self.InputDocument = "OrderStatus"
        self.OutputDocument = "NA"
        self.in_queue = self.base_class.waitforStepOrderCompletion_Queue
        # Gaurd variables for enabling the transitions
        self.excProductionStepSeq_Enabled = True
        self.sendFailureResponse_Enabled = True
        
    
    def actions(self) -> None:
        if (self.wait(60)):
            if self.rcv_msg_count() == 0:
                self.base_class.responseMessage["status"] = "E"
                self.base_class.responseMessage["code"] = "E.013"
                self.base_class.responseMessage["message"] = "The placed order is not successfully executed please try it later."
                self.excProductionStepSeq_Enabled = False
            else:
                self.receive()
                self.save_in_message(self.message)
                self.orderStatus = \
                self.message["interactionElements"][0]["submodelElements"][0]["value"]
                if (self.orderStatus == "E"):
                    self.excProductionStepSeq_Enabled = False
                    self.base_class.responseMessage["status"] = "E"
                    self.base_class.responseMessage["code"] = "E.013"
                    self.base_class.responseMessage["message"] = \
                    "The placed order is not successfully executed please try it later."
                else:
                    self.sendFailureResponse_Enabled = False
        
    def transitions(self) -> object:
        if (self.excProductionStepSeq_Enabled):
            ts = excProductionStepSeq(self.base_class,"excProductionStepSeq")
            return ts
        if (self.sendFailureResponse_Enabled):
            ts = sendFailureResponse(self.base_class,"sendFailureResponse")
            return ts
        
class sendProductionStepOrder(AState):
    
    def initialize(self):
        self.InputDocument = "NA"
        self.OutputDocument = "Order"
        # Gaurd variables for enabling the transitions
        self.waitforStepOrderCompletion_Enabled = True
    
    def create_properties(self):
        _property =      {"value": "WaitforNewOrder","idShort": "InitialState",
                            "kind": "Instance","valueType": "xs:string",
                            "modelType": "Property"
                        }
        submodel = {"idShort": "OrderData","kind": "Instance",
            "submodelElements": [], "modelType": "Submodel"
        }
        
        for in_row in self.productionStep["submodel_id_idSHort_list"]:
            submodelCollection = {"idShort": "OrderDataC","kind": "Instance",
            "value": [], "modelType": "SubmodelElementCollection"
            }
            _id = deepcopy(_property) 
            _id["idShort"] = "id"
            _id["value"] = in_row[0]
            submodelCollection["value"].append(_id)
            _idShort = deepcopy(_property)
            _idShort["idShort"] = "idShort"
            _idShort["value"] = in_row[1]
            submodelCollection["value"].append(_idShort)
            _idShortPath = deepcopy(_property) 
            _idShortPath["idShort"] = "idShortPath"
            _idShortPath["value"] = in_row[2]
            submodelCollection["value"].append(_idShortPath)
            submodel["submodelElements"].append(submodelCollection)
        
        return submodel
        
    def create_outbound_message(self) -> list:
        outboundMessages = []
        message = self.base_class.WaitforNewOrder_In 
        receiverId = message["frame"]["sender"]["id"]
        receiverRole = self.productionStep["skill_name"]#message["frame"]["sender"]["role"]["name"]
        conV1 = message["frame"]["conversationId"]
        oMessage_Out = self.create_i40_message(self.OutputDocument,conV1,receiverId,receiverRole)
        oMessage_Out["interactionElements"].append(self.create_properties())
        self.save_out_message(oMessage_Out)
        outboundMessages.append(oMessage_Out)
        return outboundMessages
    
    def actions(self) -> None:
        aasId = self.base_class.WaitforNewOrder_In["frame"]["sender"]["id"]
        _uid = self.base_class.pyaas.aasHashDict.__getHashEntry__(aasId).__getId__()
        aasShellObject = self.base_class.pyaas.aasShellHashDict.__getHashEntry__(_uid)
        self.productionStepLen = len(aasShellObject.productionStepList)
        self.productionStep = aasShellObject.productionStepList[0]
        del aasShellObject.productionStepList[0]        
        
    def transitions(self) -> object:
        self.send(self.create_outbound_message())
        if (self.waitforStepOrderCompletion_Enabled):
            ts = waitforStepOrderCompletion(self.base_class,"waitforStepOrderCompletion")
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
        oMessage_Out["interactionElements"].append(self.InElem)
        self.save_out_message(oMessage_Out)
        outboundMessages.append(oMessage_Out)
        return outboundMessages
    
    def actions(self) -> None:
        self.InElem = self.base_class.statusInElem
        self.InElem["submodelElements"][0]["value"] = self.base_class.responseMessage["status"]
        self.InElem["submodelElements"][1]["value"] = self.base_class.responseMessage["code"]
        self.InElem["submodelElements"][2]["value"] = self.base_class.responseMessage["message"]
         
        self.base_class.responseMessage = {}
        
    def transitions(self) -> object:
        self.send(self.create_outbound_message())
        if (self.WaitforNewOrder_Enabled):
            ts = WaitforNewOrder(self.base_class,"WaitforNewOrder")
            return ts
        
class retrieveProductionStepSeq(AState):
    
    def initialize(self):
        self.InputDocument = "NA"
        self.OutputDocument = "NA"
        # Gaurd variables for enabling the transitions
        self.excProductionStepSeq_Enabled = True
        
    
    def actions(self) -> None:
        pass
        
    def transitions(self) -> object:
        if (self.excProductionStepSeq_Enabled):
            ts = excProductionStepSeq(self.base_class,"excProductionStepSeq")
            return ts
        
class sendFailureResponse(AState):
    
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
        oMessage_Out["interactionElements"].append(self.InElem)
        self.save_out_message(oMessage_Out)
        outboundMessages.append(oMessage_Out)
        return outboundMessages
    
    def actions(self) -> None:
        self.InElem = self.base_class.statusInElem
        self.InElem["submodelElements"][0]["value"] = self.base_class.responseMessage["status"]
        self.InElem["submodelElements"][1]["value"] = self.base_class.responseMessage["code"]
        self.InElem["submodelElements"][2]["value"] = self.base_class.responseMessage["message"]

        aasId = self.base_class.WaitforNewOrder_In["frame"]["sender"]["id"]
        _uid = self.base_class.pyaas.aasHashDict.__getHashEntry__(aasId).__getId__()
        aasShellObject = self.base_class.pyaas.aasShellHashDict.__getHashEntry__(_uid)
        aasShellObject.productionStepList.clear()
        self.base_class.responseMessage = {}
        
    def transitions(self) -> object:
        self.send(self.create_outbound_message())
        if (self.WaitforNewOrder_Enabled):
            ts = WaitforNewOrder(self.base_class,"WaitforNewOrder")
            return ts
        



class ProductionManager(Actor):
    '''
    classdocs
    '''

        
    def initstate_specific_queue_internal(self) -> None:
        """
        """
        self.QueueDict = dict()
        
        self.WaitforNewOrder_Queue = Queue.Queue()
        self.waitforStepOrderCompletion_Queue = Queue.Queue()
        
                
        self.QueueDict = {
              "ProductionOrder": self.WaitforNewOrder_Queue,
              "OrderStatus": self.waitforStepOrderCompletion_Queue,
            }
    
    def init_inbound_messages(self) -> None:
        self.WaitforNewOrder_In = None
        self.waitforStepOrderCompletion_In = None
        pass
    
    def __init__(self,pyaas):
        '''
        Constructor
        '''
        self.SKILL_STATES = {
                          "WaitforNewOrder": "WaitforNewOrder",  "excProductionStepSeq": "excProductionStepSeq",  "waitforStepOrderCompletion": "waitforStepOrderCompletion",  "sendProductionStepOrder": "sendProductionStepOrder",  "sendCompletionResponse": "sendCompletionResponse",  "retrieveProductionStepSeq": "retrieveProductionStepSeq",  "sendFailureResponse": "sendFailureResponse",
                       }

        Actor.__init__(self,pyaas,"ProductionManager",
                       "www.admin-shell.io/interaction/productionmanagement",
                       "ProductionManager","WaitforNewOrder")

                
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
    
    lm2 = ProductionManager()
    lm2.Start('msgHandler')
