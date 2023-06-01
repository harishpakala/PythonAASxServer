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
import datetime
import os
import time
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
        self.rejected_files = [] 
        
        # Gaurd variables for enabling the transitions
        
        self.cfpConfiguration_Enabled = True
        self.WaitforNewOrder_Enabled = True
        AState.__init__(self,self.base_class,self.state_name)
        
    def WaitforNewOrder_Logic(self):
        self.submodelId  = "https://dlr.de/mo/aas/74b8199bff764b60a1ed8986a0399a0c/ids/sm/5420_6132_4032_6775"
        
        endpoint_url = self.GetSubmodelELementByIdshoortPath(self.submodelId,"TechnicalProperties.FunctionalProperties.endpoint_url")
        threshold_age_min = self.GetSubmodelELementByIdshoortPath(self.submodelId,"TechnicalProperties.FunctionalProperties.threshold_age_min")
        threshold_age_max = self.GetSubmodelELementByIdshoortPath(self.submodelId,"TechnicalProperties.FunctionalProperties.threshold_age_max")
        threshold_size_min = self.GetSubmodelELementByIdshoortPath(self.submodelId,"TechnicalProperties.FunctionalProperties.threshold_size_min")
        threshold_size_max = self.GetSubmodelELementByIdshoortPath(self.submodelId,"TechnicalProperties.FunctionalProperties.threshold_size_max")

        while True:

            path = "/DATA_LOG"  # Path to the folder you want to search through

            # Today's date
            today = datetime.datetime.now()

            # A list to store the found files
            old_files = []

            # Traverse through the folder and all subfolders
            for root, dirs, files in os.walk(path):
                for file in files:
                    # The full path to the current file
                    file_path = os.path.join(root, file)

                    # The date when the file was last modified
                    mod_date = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))

                    # The size of the file in bytes
                    size = os.path.getsize(file_path)

                    # Check if the file is older than the age threshold or larger than the size threshold
                    if ((today - mod_date).days > float(threshold_age_min)) and (size > float(threshold_size_min)*1024*1024) and \
                       ((today - mod_date).days < float(threshold_age_max)) and (size < float(threshold_size_max)*1024*1024):

                        old_files.append(file_path)

            if len(old_files) > 0:
                break

            time.sleep(60)

        # SELECT FIRST FILE OUT OF LIST WHICH IS NOT IN THE REJECTED LIST - FORWARDING TO REQUEST CfP
        for jj in range(len(old_files)):

            if os.path.basename(old_files[jj]) not in self.rejected_files:

                self.log_info(f"rejected files: {self.rejected_files}")
                self.log_info(f"file: {os.path.basename(old_files[jj])}")

                self.file_name = os.path.basename(old_files[jj])
                self.file_size = os.path.getsize(old_files[jj])
                self.file_type = os.path.splitext(old_files[jj])[1]
                self.file_age = (today - datetime.datetime.fromtimestamp(os.path.getmtime(old_files[jj]))).days
                self.file_path_url = endpoint_url
                self.file_path_local = old_files[jj]

                SendCFP.file_name = self.file_name
                SendCFP.file_path_url = self.file_path_url
                SendCFP.file_size = self.file_size
                SendCFP.file_age = self.file_age
                SendCFP.file_type = self.file_type

                WaitforInformConfirm.file_name = self.file_name
                WaitforInformConfirm.file_path_local = self.file_path_local

                self.log_info(f"Data storage order received for file: {self.file_name}")

                break
    
    
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
        
        if (self.WaitforNewOrder_Enabled):
            ts = WaitforNewOrder(self.base_class)
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
        self.base_class.responseMessage["status"] = "S"
        self.base_class.responseMessage["code"] = "A.013"
        self.base_class.responseMessage["message"] =  "TheOrder is Succesfully Executed."

        try:
            archive_path = "/DATA_ARCHIVE"
            archive_file_path = os.path.join(archive_path, self.file_name)

            # MOVE FILE TO ARCHIVE
            os.makedirs(os.path.dirname(archive_file_path), exist_ok=True)
            os.rename(self.file_path_local, archive_file_path)

            # REMOVE FOLDER FROM LOG
            os.rmdir(os.path.dirname(self.file_path_local))

            self.log_info(f"File {self.file_name} has been archived locally and on SKYSTASH")
        except:
            self.log_info(f"NOTE: File {self.file_name} was archived on SKYSTASH, but NOT locally")

    
    
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
        
        if (self.wait_untill_timer(1,20)):
            self.base_class.proposalList = self.receive_all()
            self.save_message(self.base_class.proposalList) 
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
        
class sendacceptProposal(AState):
    
    def __init__(self, base_class):
        self.base_class = base_class
        self.state_name = "sendacceptProposal"
        self.InputDocument = "NA"
        
        # Gaurd variables for enabling the transitions
        
        self.WaitforInformConfirm_Enabled = True
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
    
    file_name = None
    file_path_url = None
    file_size = None
    file_age = None
    file_type = None

    
    def __init__(self, base_class):
        self.base_class = base_class
        self.state_name = "SendCFP"
        self.InputDocument = "NA"
        
        # Gaurd variables for enabling the transitions
        
        self.WaitForSPProposal_Enabled = True
        AState.__init__(self,self.base_class,self.state_name)
        
    def SendCFP_Logic(self):
        self.submodel = self.GetSubmodelById("https://dlr.de/mo/aas/74b8199bff764b60a1ed8986a0399a0c/ids/sm/5420_6132_4032_6775")

        i = 0
        j = 0
        k = 0
        for submodelElem in self.submodel["submodelElements"]:
            if (submodelElem["idShort"] == "TechnicalProperties"):
                for valueELem in submodelElem["value"]:
                    if (valueELem["idShort"] == "ItemProperties"):
                        for specifierElem in valueELem["value"]:
                            if (specifierElem["idShort"] == "FileName"):
                                self.submodel["submodelElements"][i]["value"][j]["value"][k]["value"] = str(self.file_name)
                            if (specifierElem["idShort"] == "FileSize"):
                                self.submodel["submodelElements"][i]["value"][j]["value"][k]["value"] = str(self.file_size / 1024 / 1024)
                            if (specifierElem["idShort"] == "FileAge"):
                                self.submodel["submodelElements"][i]["value"][j]["value"][k]["value"] = str(self.file_age)
                            if (specifierElem["idShort"] == "FileType"):
                                self.submodel["submodelElements"][i]["value"][j]["value"][k]["value"] = str(self.file_type)
                            k = k + 1
                    j = j + 1
            i = i + 1

        i = 0
        j = 0
        k = 0

        for submodelElem in self.submodel["submodelElements"]:
            if (submodelElem["idShort"] == "TechnicalProperties"):
                for valueELem in submodelElem["value"]:
                    if (valueELem["idShort"] == "FunctionalProperties"):
                        for specifierElem in valueELem["value"]:
                            if (specifierElem["idShort"] == "endpointURL"):
                                self.InElem[0]["submodelElements"][i]["value"][j]["value"][k]["value"] = self.file_path_url
                            k = k + 1
                    j = j + 1
            i = i + 1

        noProposalReceived.file_name = self.file_name
    
    def create_Outbound_Message(self,msgtype) -> list:
        outboundMessages = []
        message = self.base_class.WaitforNewOrder_In
        receiverId = "https://dlr.de/mo/aas/2f329c96b9b4435fab456746e24f44c2"
        receiverRole = "storageDownloader"
        conV1 = message["frame"]["conversationId"]
        oMessage_Out = self.gen.create_i40_message(msgtype,conV1,receiverId,receiverRole)
        #submodel = self.GetSubmodelById('submodelId')
        oMessage_Out["interactionElements"].appen(self.submodel)
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
        
class noProposalReceived(AState):
    
    def __init__(self, base_class):
        self.base_class = base_class
        self.state_name = "noProposalReceived"
        self.InputDocument = "NA"
        
        # Gaurd variables for enabling the transitions
        
        self.sendCompletionResponse_Enabled = True
        AState.__init__(self,self.base_class,self.state_name)
        
    def noProposalReceived_Logic(self):
        self.base_class.responseMessage["status"] = "E"
        self.base_class.responseMessage["code"] = "E.013"
        self.base_class.responseMessage["message"] =  "No Proposals are received"
        
    
    def run(self) -> None:
        super().run()
        
        self.noProposalReceived_Logic()
        
    def next(self) -> object:
        OutputDocument = "NA"
        self.log_info("OutputDocumentType : " + OutputDocument)
        
        
        if (self.sendCompletionResponse_Enabled):
            ts = sendCompletionResponse(self.base_class)
            return ts
        



class DataStorageRequester(Actor):
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
        
                
        self.QueueDict = {
              "Order": self.WaitforNewOrder_Queue,
              "informConfirm": self.WaitforInformConfirm_Queue,
              "proposal": self.WaitForSPProposal_Queue,
            }
    
    def init_inbound_messages(self) -> None:
        self.WaitforInformConfirm_In = None
        self.WaitForSPProposal_In = None
        self.WaitforNewOrder_In = None
        pass
    
    def __init__(self,pyaas):
        '''
        Constructor
        '''
        self.SKILL_STATES = {
                          "WaitforNewOrder": "WaitforNewOrder",  "WaitforInformConfirm": "WaitforInformConfirm",  "WaitForSPProposal": "WaitForSPProposal",  "sendrejectProposal": "sendrejectProposal",  "EvaluateProposal": "EvaluateProposal",  "sendacceptProposal": "sendacceptProposal",  "sendCompletionResponse": "sendCompletionResponse",  "SendCFP": "SendCFP",  "cfpConfiguration": "cfpConfiguration",  "noProposalReceived": "noProposalReceived",
                       }

        Actor.__init__(self,pyaas,"DataStorageRequester",
                       "www.admin-shell.io/interaction/servicerequistion",
                       "DataStorageRequester","WaitforNewOrder")

                
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
    
    lm2 = DataStorageRequester()
    lm2.Start('msgHandler')
