"""
Copyright (c) 2023 Otto-von-Guericke-Universitaet Magdeburg, Lehrstuhl Integrierte Automation
Author: Marco Weiss
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
class WaitforNewOrder(AState):
    
    def __init__(self, base_class):
        self.base_class = base_class
        self.state_name = "WaitforNewOrder"
        self.InputDocument = "Order"
        self.in_queue = self.base_class.WaitforNewOrder_Queue
        self.message = self.base_class.WaitforNewOrder_In
        
        # Gaurd variables for enabling the transitions
        
        self.cfpConfiguration_Enabled = True
        AState.__init__(self,self.base_class,self.state_name)

    def WaitforNewOrder_Logic(self):
        pass
    
    
    def run(self) -> None:
        super().run()
        
        if (self.wait_untill(1)):
            self.receive()
            self.save_message() 
        self.WaitforNewOrder_Logic()
        
    def next(self) -> object:
        OutputDocument = "NA"
        self.log_info("OutputDocumentType : " + OutputDocument)
        
        
        if (self.cfpConfiguration_Enabled):
            ts = cfpConfiguration(self.base_class)
            return ts
        
class EvaluateProposal(AState):
    
    def __init__(self, base_class):
        self.base_class = base_class
        self.state_name = "EvaluateProposal"
        self.InputDocument = "NA"
        
        # Gaurd variables for enabling the transitions
        
        self.sendrejectProposal_Enabled = True
        AState.__init__(self,self.base_class,self.state_name)
    
    def getListPrice(self,submodelElement):
        for value in submodelElement["value"]:
            if value['idShort'] == "listprice":
                return int(value['value']) 


    def EvaluateProposal_Logic(self):
        try:
            ListPrices = [] 
            for eachPorposal in self.base_class.proposalList:
                for submodelElement in eachPorposal['interactionElements']['submodelElements']:
                    if (submodelElement['idShort'] == 'CommercialProperties'):
                        ListPrices.append(self.getListPrice(submodelElement))

            bestPrice = min(ListPrices)
            bestPriceIndex = ListPrices.index(bestPrice)   
            self.base_class.rejectproposals_list = []
            self.base_class.acceptproposals_list = []        
            for i in range(0,len(self.base_class.proposalList)):
                if (i == bestPriceIndex):
                    self.base_class.acceptproposals_list.append(self.base_class.proposalList[i])
                else:
                    self.base_class.rejectproposals_list(self.base_class.proposalList[i])

        except Exception as e:
            self.logger_info("Evaluate Proposal Error" + str(e))

    
    def run(self) -> None:
        super().run()
        
        self.EvaluateProposal_Logic()
        
    def next(self) -> object:
        OutputDocument = "NA"
        self.log_info("OutputDocumentType : " + OutputDocument)
        
        
        if (self.sendrejectProposal_Enabled):
            ts = sendrejectProposal(self.base_class)
            return ts
        
class noProposalReceived(AState):
    
    def __init__(self, base_class):
        self.base_class = base_class
        self.state_name = "noProposalReceived"
        self.InputDocument = "NA"
        
        # Gaurd variables for enabling the transitions
        
        self.sendCompletionResponse_Enabled = True
        AState.__init__(self,self.base_class,self.state_name)
        
    def noProposalReceived_Logic(self):
        pass
    
    
    def run(self) -> None:
        super().run()
        
        self.noProposalReceived_Logic()
        
    def next(self) -> object:
        OutputDocument = "NA"
        self.log_info("OutputDocumentType : " + OutputDocument)
        
        
        if (self.sendCompletionResponse_Enabled):
            ts = sendCompletionResponse(self.base_class)
            return ts
        
class cfpConfiguration(AState):
    
    def __init__(self, base_class):
        self.base_class = base_class
        self.state_name = "cfpConfiguration"
        self.InputDocument = "NA"
        
        # Gaurd variables for enabling the transitions
        
        self.SendCFP_Enabled = True
        AState.__init__(self,self.base_class,self.state_name)
        
    def cfpConfiguration_Logic(self):
        pass
    
    
    def run(self) -> None:
        super().run()
        
        self.cfpConfiguration_Logic()
        
    def next(self) -> object:
        OutputDocument = "NA"
        self.log_info("OutputDocumentType : " + OutputDocument)
        
        
        if (self.SendCFP_Enabled):
            ts = SendCFP(self.base_class)
            return ts
        
class sendacceptProposal(AState):
    
    def __init__(self, base_class):
        self.base_class = base_class
        self.state_name = "sendacceptProposal"
        self.InputDocument = "NA"
        
        # Gaurd variables for enabling the transitions
        
        self.sendTransportOrder_Enabled = True
        AState.__init__(self,self.base_class,self.state_name)
        
    def sendacceptProposal_Logic(self):
        pass
    
    def create_Outbound_Message(self,msgtype) -> list:
        outboundMessages = []
        for _proposal in self.base_class.acceptproposals_list:
            message = _proposal
            receiverId = message["frame"]["sender"]["id"]
            receiverRole = message["frame"]["sender"]["role"]["name"]
            conV1 = message["frame"]["conversationId"]
            oMessage_Out = self.gen.create_i40_message(msgtype,conV1,receiverId,receiverRole)
            #submodel = self.GetSubmodelById('submodelId')
            self.save_conversation_message(oMessage_Out,"outbound")
            outboundMessages.append(oMessage_Out)
        return outboundMessages
    
    def run(self) -> None:
        super().run()
        
        self.sendacceptProposal_Logic()
        
    def next(self) -> object:
        OutputDocument = "acceptProposal"
        self.log_info("OutputDocumentType : " + OutputDocument)
        
        if (OutputDocument != "NA"):
            self.send(self.create_Outbound_Message(OutputDocument))
        
        if (self.sendTransportOrder_Enabled):
            ts = sendTransportOrder(self.base_class)
            return ts
        
class WaitforInformConfirm(AState):
    
    def __init__(self, base_class):
        self.base_class = base_class
        self.state_name = "WaitforInformConfirm"
        self.InputDocument = "informConfirm"
        self.in_queue = self.base_class.WaitforInformConfirm_Queue
        self.message = self.base_class.WaitforInformConfirm_In
        
        # Gaurd variables for enabling the transitions
        
        self.sendCompletionResponse_Enabled = True

        AState.__init__(self,self.base_class,self.state_name)
        
    def WaitforInformConfirm_Logic(self):
        self.baseClass.responseMessage["status"] = "S"
        self.baseClass.responseMessage["code"] = "A.013"
        self.baseClass.responseMessage["message"] =  "TheOrder is Succesfully Executed."  
    
    def run(self) -> None:
        super().run()
        
        if (self.wait_untill_timer(1,600)):
            self.receive()
            self.save_message() 
        self.WaitforInformConfirm_Logic()
        
    def next(self) -> object:
        OutputDocument = "NA"
        self.log_info("OutputDocumentType : " + OutputDocument)
        
        
        if (self.sendCompletionResponse_Enabled):
            ts = sendCompletionResponse(self.base_class)
            return ts
        
class sendTransportOrder(AState):
    
    def __init__(self, base_class):
        self.base_class = base_class
        self.state_name = "sendTransportOrder"
        self.InputDocument = "NA"
        
        # Gaurd variables for enabling the transitions
        
        self.WaitforTransportOrderCompletion_Enabled = True
        AState.__init__(self,self.base_class,self.state_name)
        
    def sendTransportOrder_Logic(self):
        pass
    
    def create_Outbound_Message(self,msgtype) -> list:
        outboundMessages = []
        message = self.base_class.WaitforNewOrder_In
        receiverId = message["frame"]["sender"]["id"]
        receiverRole = "mroRequester"
        conV1 = message["frame"]["conversationId"]
        oMessage_Out = self.gen.create_i40_message(msgtype,conV1,receiverId,receiverRole)
        #submodel = self.GetSubmodelById('submodelId')
        self.save_conversation_message(oMessage_Out,"outbound")
        outboundMessages.append(oMessage_Out)
        return outboundMessages
    
    def run(self) -> None:
        super().run()
        
        self.sendTransportOrder_Logic()
        
    def next(self) -> object:
        OutputDocument = "Order"
        self.log_info("OutputDocumentType : " + OutputDocument)
        
        if (OutputDocument != "NA"):
            self.send(self.create_Outbound_Message(OutputDocument))
        
        if (self.WaitforTransportOrderCompletion_Enabled):
            ts = WaitforTransportOrderCompletion(self.base_class)
            return ts
        
class sendrejectProposal(AState):
    
    def __init__(self, base_class):
        self.base_class = base_class
        self.state_name = "sendrejectProposal"
        self.InputDocument = "NA"
        
        # Gaurd variables for enabling the transitions
        
        self.sendacceptProposal_Enabled = True
        self.sendCompletionResponse_Enabled = True
        AState.__init__(self,self.base_class,self.state_name)
        
    def sendrejectProposal_Logic(self):
        if len(self.base_class.acceptproposals_list) == 0:
            self.sendacceptProposal_Enabled = False
            self.base_class.responseMessage["status"] = "E"
            self.base_class.responseMessage["code"] = "E.013"
            self.base_class.responseMessage["message"] =  "No Proposal is selected."
        
        else:
            self.sendCompletionResponse_Enabled = False
            
    def create_Outbound_Message(self,msgtype) -> list:
        outboundMessages = []
        for _proposal in self.base_class.rejectproposals_list:
            message = _proposal
            receiverId = message["frame"]["sender"]["id"]
            receiverRole = message["frame"]["sender"]["role"]["name"]
            conV1 = message["frame"]["conversationId"]
            oMessage_Out = self.gen.create_i40_message(msgtype,conV1,receiverId,receiverRole)
            #submodel = self.GetSubmodelById('submodelId')
            self.save_conversation_message(oMessage_Out,"outbound")
            outboundMessages.append(oMessage_Out)
        return outboundMessages
    
    
    def run(self) -> None:
        super().run()
        
        self.sendrejectProposal_Logic()
        
    def next(self) -> object:
        OutputDocument = "rejectProposal"
        self.log_info("OutputDocumentType : " + OutputDocument)
        
        if (OutputDocument != "NA"):
            self.send(self.create_Outbound_Message(OutputDocument))
        
        if (self.sendacceptProposal_Enabled):
            ts = sendacceptProposal(self.base_class)
            return ts
        if (self.sendCompletionResponse_Enabled):
            ts = sendCompletionResponse(self.base_class)
            return ts
        
class WaitForSPProposal(AState):
    
    def __init__(self, base_class):
        self.base_class = base_class
        self.state_name = "WaitForSPProposal"
        self.InputDocument = "proposal"
        self.in_queue = self.base_class.WaitForSPProposal_Queue
        self.message = self.base_class.WaitForSPProposal_In
        
        # Gaurd variables for enabling the transitions
        
        self.noProposalReceived_Enabled = True
        self.EvaluateProposal_Enabled = True
        AState.__init__(self,self.base_class,self.state_name)
        
    def WaitForSPProposal_Logic(self):
        if (self.WaitForSPProposal_In != None):
            self.noProposalReceived_Enabled = False
        else:
            self.EvaluateProposal_Enabled = False
    
    
    def run(self) -> None:
        super().run()
        
        if (self.wait_untill_timer(1,60)):
            self.receive()
            self.save_message() 
        self.WaitForSPProposal_Logic()
        
    def next(self) -> object:
        OutputDocument = "NA"
        self.log_info("OutputDocumentType : " + OutputDocument)
        
        
        if (self.noProposalReceived_Enabled):
            ts = noProposalReceived(self.base_class)
            return ts
        if (self.EvaluateProposal_Enabled):
            ts = EvaluateProposal(self.base_class)
            return ts
        
class WaitforTransportOrderCompletion(AState):
    
    def __init__(self, base_class):
        self.base_class = base_class
        self.state_name = "WaitforTransportOrderCompletion"
        self.InputDocument = "OrderStatus"
        self.in_queue = self.base_class.WaitforTransportOrderCompletion_Queue
        self.message = self.base_class.WaitforTransportOrderCompletion_In
        
        # Gaurd variables for enabling the transitions
        
        self.sendCompletionResponse_Enabled = True
        self.WaitforInformConfirm_Enabled = True
        AState.__init__(self,self.base_class,self.state_name)
        
    def WaitforTransportOrderCompletion_Logic(self):
        if self.message == None:
            self.WaitforInformConfirm_Enabled = False
            self.base_class.responseMessage["status"] = "E"
            self.base_class.responseMessage["code"] = "E.013"
            self.base_class.responseMessage["message"] =  "Transport Order not received."
        else:
            if self.message["interactionElements"][0]["submodelElements"][0]["value"] == "E":
                self.base_class.responseMessage["status"] = "E"
                self.base_class.responseMessage["code"] = "E.013"
                self.base_class.responseMessage["message"] =  "Transport Order not processed."
            else:
                self.sendCompletionResponse_Enabled = False
    
    
    def run(self) -> None:
        super().run()
        
        if (self.wait_untill_timer(1,120)):
            self.receive()
            self.save_message() 
        self.WaitforTransportOrderCompletion_Logic()
        
    def next(self) -> object:
        OutputDocument = "NA"
        self.log_info("OutputDocumentType : " + OutputDocument)
        
        
        if (self.sendCompletionResponse_Enabled):
            ts = sendCompletionResponse(self.base_class)
            return ts
        if (self.WaitforInformConfirm_Enabled):
            ts = WaitforInformConfirm(self.base_class)
            return ts
        
class sendCompletionResponse(AState):
    
    def __init__(self, base_class):
        self.base_class = base_class
        self.state_name = "sendCompletionResponse"
        self.InputDocument = "NA"
        
        # Gaurd variables for enabling the transitions
        
        self.WaitforNewOrder_Enabled = True
        AState.__init__(self,self.base_class,self.state_name)
        
    def sendCompletionResponse_Logic(self):
        pass
    
    def create_Outbound_Message(self,msgtype) -> list:
        outboundMessages = []
        message = self.base_class.WaitforNewOrder_In
        receiverId = message["frame"]["sender"]["id"]
        receiverRole = message["frame"]["sender"]["role"]["name"]
        conV1 = message["frame"]["conversationId"]
        oMessage_Out = self.gen.create_i40_message(msgtype,conV1,receiverId,receiverRole)
        #submodel = self.GetSubmodelById('submodelId')
        oMessage_Out.append(self.base_class.responseMessage)
        self.save_conversation_message(oMessage_Out,"outbound")
        outboundMessages.append(oMessage_Out)
        return outboundMessages
    
    def run(self) -> None:
        super().run()
        
        self.sendCompletionResponse_Logic()
        
    def next(self) -> object:
        OutputDocument = "OrderStatus"
        self.log_info("OutputDocumentType : " + OutputDocument)
        
        if (OutputDocument != "NA"):
            self.send(self.create_Outbound_Message(OutputDocument))
        
        if (self.WaitforNewOrder_Enabled):
            ts = WaitforNewOrder(self.base_class)
            return ts
                
class SendCFP(AState):
    
    def __init__(self, base_class):
        self.base_class = base_class
        self.state_name = "SendCFP"
        self.InputDocument = "NA"
        
        # Gaurd variables for enabling the transitions
        
        self.WaitForSPProposal_Enabled = True
        AState.__init__(self,self.base_class,self.state_name)
        
    def SendCFP_Logic(self):
        pass
    
    def create_Outbound_Message(self,msgtype) -> list:
        outboundMessages = []
        message = self.base_class.WaitforNewOrder_In
        receiverId = "https://dlr.de/mo/aas/e95ea183a87f48d3811c2cae77388044"
        receiverRole = "ProviderMRObasic"
        conV1 = message["frame"]["conversationId"]
        oMessage_Out = self.gen.create_i40_message(msgtype,conV1,receiverId,receiverRole)
        submodel = self.GetSubmodelById('https://dlr.de/mo/aas/74b8199bff764b60a1ed8986a0399a0c/ids/sm/1045_2160_2032_6529')
        oMessage_Out["interactionElements"].append(submodel)
        self.save_conversation_message(oMessage_Out,"outbound")
        outboundMessages.append(oMessage_Out)
        return outboundMessages
    
    def run(self) -> None:
        super().run()
        
        self.SendCFP_Logic()
        
    def next(self) -> object:
        OutputDocument = "callForProposal"
        self.log_info("OutputDocumentType : " + OutputDocument)
        
        if (OutputDocument != "NA"):
            self.send(self.create_Outbound_Message(OutputDocument))
        
        if (self.WaitForSPProposal_Enabled):
            ts = WaitForSPProposal(self.base_class)
            return ts
        



class mroRequester(Actor):
    '''
    classdocs
    '''

        
    def initstate_specific_queue_internal(self) -> None:
        """
        """
        self.QueueDict = dict()
        
        self.WaitforNewOrder_Queue = Queue.Queue()
        self.WaitforInformConfirm_Queue = Queue.Queue()
        self.WaitForSPProposal_Queue = Queue.Queue()
        self.WaitforTransportOrderCompletion_Queue = Queue.Queue()
        
                
        self.QueueDict = {
              "Order": self.WaitforNewOrder_Queue,
              "informConfirm": self.WaitforInformConfirm_Queue,
              "proposal": self.WaitForSPProposal_Queue,
              "OrderStatus": self.WaitforTransportOrderCompletion_Queue,
            }
    
    def init_inbound_messages(self) -> None:
        self.WaitforNewOrder_In = None
        self.WaitforTransportOrderCompletion_In = None
        self.WaitForSPProposal_In = None
        self.WaitforInformConfirm_In = None
        pass
    
    def __init__(self,pyaas):
        '''
        Constructor
        '''
        self.SKILL_STATES = {
                          "WaitforNewOrder": "WaitforNewOrder",  "EvaluateProposal": "EvaluateProposal",  "noProposalReceived": "noProposalReceived",  "cfpConfiguration": "cfpConfiguration",  "sendacceptProposal": "sendacceptProposal",  "WaitforInformConfirm": "WaitforInformConfirm",  "sendTransportOrder": "sendTransportOrder",  "sendrejectProposal": "sendrejectProposal",  "WaitForSPProposal": "WaitForSPProposal",  "WaitforTransportOrderCompletion": "WaitforTransportOrderCompletion",  "sendCompletionResponse": "sendCompletionResponse",  "SendCFP": "SendCFP",
                       }

        Actor.__init__(self,pyaas,"mroRequester",
                       "www.admin-shell.io/interaction/servicerequistion",
                       "MRO Requisition","WaitforNewOrder")

                
    def start(self, msgHandler,shellObject,_uid) -> None:
        """
            Starting of the Actor state machine
        """
        super().start(msgHandler,shellObject,_uid)
        
        WaitforNewOrder_1 = WaitforNewOrder(self)
        self.stateChange("WaitforNewOrder")
        self.currentState = WaitforNewOrder_1
        self.InitialState = "WaitforNewOrder"
        super().run(self.currentState,self.InitialState)
    
    def send(self, sendMessage) -> None:
        super().send(sendMessage)
    
    def receiveMessage(self,inMessage) -> None:
        try:    
            _messageType = str(inMessage['frame']['type'])
            self.QueueDict[_messageType].put(inMessage)
        except Exception as E:
            pass



if __name__ == '__main__':
    
    lm2 = mroRequester()
    lm2.Start('msgHandler')
