"""
Copyright (c) 2023 Otto-von-Guericke-Universitaet Magdeburg, Lehrstuhl Integrierte Automation
Author: Kamleen
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
"""
from datetime import datetime
try:
    import queue as Queue
except ImportError:
    import Queue as Queue 
import base64
import logging
import sys
import time
import uuid
try:
    from utils.utils import ExecuteDBModifier,ProductionStepOrder,ExecuteDBRetriever,AASMetaModelValidator,Generate_AAS_Shell,UUIDGenerator
except ImportError:
    from src.main.utils.utils import ExecuteDBModifier,ProductionStepOrder,ExecuteDBRetriever,AASMetaModelValidator,Generate_AAS_Shell,UUIDGenerator
try:
    from utils.i40data import Generic
except ImportError:
    from main.utils.i40data import Generic

try:
    from utils.aaslog import ServiceLogHandler,LogList
except ImportError:
    from main.utils.aaslog import ServiceLogHandler,LogList

'''
    The skill generator extracts all the states from the transitions list.
    For each STATE, a seperate python class is created. This python class has two main
    functions run() and the next(). The run method is required to execute a set
    of instructions so that the class which represents a state could exhibit a specific behavior. 
    The next method defines the next class that has to be executed.
    
    Each transition is attributed by input document and outpput document.
    
    In the case of  input document, the class is expected to wait for the 
    arrival of a specific document type. While for the output document, the class
    is expected to send out the output document.
    
    This source-code consists of a base class and the all the classes each pertaining 
    to definite state of the skill state-machine. The base class represents the skill 
    and coordinates the transition from one state to another.
    
    The baseclass is responsible for collecting the documents from the external
    world (either from other skill that is part of the AAS or a skill part of 
    of another AAS). For this the baseclass maintains a queue one for each class. 
    
    The communication between any two skills of the same AAS or the skills of 
    different AAS is done in I4.0 language.
    
    An I4.0 message packet consists of a frame header and the interactionElements
    detail part. The frame element consists of Sender and Receiver elements. Under
    this the AASID's and respective skillnames can be specified.
    
    Also  every message packet is associated with a type, the type information is 
    specified in the Input and Output property tags under Transition collection in
    the AASx package.
    
    Based on the receive information in the frame header, the message is routed appropriate
    Skill. The base-class maintains a specific InboundQueue, into the messages dropped by the
    messagehandler. 
    
    A class specific inbound queue is defined in the baseclass for the classes defined in this
    source-code. A dictionary is also manitained, with key representing the messagetype and the
    value being the class specific inboundqueue.
    
    Every inbound message to the skill, is routed to the specific class based on its message type
    from the base CLaas.  
    
    For operational purposes, a dictionary variable is defined for each message type that this skill
    expects. 

    StateName_In         
    StateName_Queue 
        
    The sendMessage method in the baseclass submits an outbound message to the message handler so that
    it could be routed to its destination. Every class can access this method and publish the outbound
    messgae.  
    
    Accessing the asset entry within a specific class
        For accessing the asset, a developer has to write specific modules in the assetaccessadaptors
        package. In this version of LIAPAAS framework PLC OPCUA adaptor for reading and writing OPCUA
        variables is provided.
        
        The asset access information like IP address, port, username, password and the opcua variables
        are defined in the AASx configuration file.
        
        The module and the related OPCUA variable definitions with thin the skill.
        
        MODULE_NAME = "PLC_OPCUA"
        #Accessing the specifc assetaaccess adaptor 
        self.plcHandler = self.base_class.pyaas.assetaccessEndpointHandlers[MODULE_NAME] # 1
        
        #accessing the list property variables Dictionary are specified in the configuration file.  
        self.propertylist = self.base_class.shellObject.thing_description
        
        PLC_OPCUA represents the module specific to opcua adaptor to access the PLC
        
        The code snippets 1 and 2 need to be initialized in the constructor of the class        
        
    def StateName_Logic(self):
        self.plcHandler.read(self.propertylist["sPermission"])
        self.plcHandler.write(self.propertylist["sPermission"],"value")
        time.sleep(10)
      
       The propertylist is the dictionary, that has asset specific keys *OPCUA variables and the respective
        addresses.
    
    creating an outbound I40 message.
    
    Note : The communication between the skills that are part of the same AAS, or different
    AAS should happen within the I40 data format structure.
    
    A generic class is provided within the package utils.i40data (it is imported in the code).
    
    code snippet
    
    self.gen = Generic()
    self.frame = self.gen.createFrame(I40FrameData)
    
    
    If the receiver is a skill within the same AAS, the ReceiverAASID would be same as SenderAASID
    where the ReceiverRolename would be specific skill Name 
    
    The ReceiverAASID and ReceiverRolename could be obtained from sender part of the incoming message
    and these are to be provided empty, if there is no receiver.
    receiverId = self.base_class.StateName_In["frame"]["sender"]["id"]
    receiverRole = self.base_class.StateName_In["frame"]["sender"]["role"]["name"]
    
    I40FrameData is a dictionary
    
    language : English, German
    format : Json, XML //self.base_class.pyaas.preferredCommunicationFormat
    reply-to : HTTP,MQTT,OPCUA (endpoint) // self.base_class.pyaas.preferedI40EndPoint
    serviceDesc : "short description of the message"

        {
        "type" : ,
        "messageId":messageId,
        "SenderAASID" : self.base_class.aasID,
        "SenderRolename" : "StateMachine_Requester_MnO",
        "conversationId" : "AASNetworkedBidding",
        "replyBy" :  "",   # "The communication protocol that the AAS needs to use while sending message to other AAS."
        "replyTo" : "",    # "The communication protocol that the receipient AAS should use for reply"   
                           # In case the message needs to be routed to another skill please "Internal"
        "ReceiverAASID" :  receiverId,
        "ReceiverRolename" : receiverRole,
        "params" : {},
        "serviceDesc" : "",
        "language" : "",
        "format" : ""  
    } # In proposal needs to be confirmed
    
    the interactionElements part of the I40 frame usually contain the submodel elements,
    the respective the submodel element could be fetched from the submodel dictionary.
    
    The fetching of the submodel elements is done dynamically from the database.
    
    example Boring (should be same as the one specified in AASX file.)
    submodel,status,statuscode = self.base_class.pyaas.dba.GetSubmodelById("submodelIdentifier")
    Here status is a boolean variable and when it is False submodel is not returned.
    statuscode can be ignored in this context 
    # result is list
    I40OutBoundMessage = {
                            "frame" : frame,
                            "interactionElements" : boringSubmodel
                        }
                        
    Saving the inbound and outbound messages into the datastore
    
    example :
    
    def retrieveMessage(self):
        self.base_class.StateName_In = self.base_class.StateName_Queue.get()
    
    def saveMessage(self):
        inboundQueueList = list(self.base_class.StateName_Queue.queue) # in case for further processing is required
        # else creation of the new queue is not required.
        for i in range (0, self.base_class.StateName_Queue.qsize()):
            message = inboundQueueList[i]
            self.instanceId = str(uuid.uuid1())
            self.base_class.pyaas.dataManager.pushInboundMessage({"functionType":3,"instanceid":self.instanceId,
                                                            "conversationId":message["frame"]["conversationId"],
                                                            "messageType":message["frame"]["type"],
                                                            "messageId":message["frame"]["messageId"],
                                                            "direction": "inbound",
                                                            "SenderAASID" : message["frame"]["sender"]["id"],
                                                            "message":message})
        
    
'''
    
class WaitforOrder:
    
    def __init__(self, base_class):
        """
        """
        self.base_class = base_class
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.createnSendRequest_Enabled = True
    
    def retrieve_WaitforOrder_Message(self) -> None:
        """
            Method to retrieve the inbound i4.0 message from the relevant queue.
            The retrieved message is assigned to the dictionary variabel designed
            in the base clase. The Variable and the queue name are based on the 
            current state.
        """
        self.base_class.WaitforOrder_In = self.base_class.WaitforOrder_Queue.get()
    
    def saveMessage(self) -> None:
        """
            Method to save the message into the database
        """
        inboundQueueList = list(self.base_class.WaitforOrder_Queue.queue) # in case for further processing is required
        # else creation of the new queue is not required.
        for i in range (0, self.base_class.WaitforOrder_Queue.qsize()):
            message = inboundQueueList[i]
            self.instanceId = str(uuid.uuid1())
            self.base_class.pyaas.dataManager.pushInboundMessage({"functionType":3,"instanceid":self.instanceId,
                                                            "conversationId":message["frame"]["conversationId"],
                                                            "messageType":message["frame"]["type"],
                                                            "messageId":message["frame"]["messageId"],
                                                            "direction": "inbound",
                                                            "SenderAASID" : self.base_class.aasID,
                                                            "message":message})
            

    def WaitforOrder_Logic(self):
        """
            The actualy logic this state  goes into this method.
            It is upto the developer to add the relevant code.
        """
        
    
    def run(self) -> None:
        """
            This method is first called form the base class after instantiating the
            class. The method executes the entire of the state.
        """
        self.base_class.skillLogger.info("\n #############################################################################")
        # StartState
        self.base_class.skillLogger.info("StartState: WaitforOrder")
        # InputDocumentType"
        InputDocument = "Order"
        self.base_class.skillLogger.info("InputDocument : " + InputDocument)
        
        '''
            In case a class expects an input document then.
            It would need to lookup to its specific queue
            that is defined in the based class
        '''
        if (InputDocument != "NA"):
            self.messageExist = True
            i = 0
            sys.stdout.write(" Waiting for response")
            sys.stdout.flush()
            while (((self.base_class.WaitforOrder_Queue).qsize()) == 0):
                time.sleep(1)
            if (self.messageExist):
                self.saveMessage() # in case we need to store the incoming message
                self.retrieve_WaitforOrder_Message() # in case of multiple inbound messages this function should 
                                                      # not be invoked. 
        self.WaitforOrder_Logic()
        
    def next(self) -> object:
        """
            This methods returns the object to the next state the needs
            to be executed by the base class
        """
        OutputDocument = "NA"
        self.base_class.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        
        if (self.createnSendRequest_Enabled):
            self.base_class.skillLogger.info("Condition :" + "true")
            ts = createnSendRequest(self.base_class)
            self.base_class.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.base_class.skillLogger.info("############################################################################# \n")
            return ts
        
class ExamineFeedback:
    
    def __init__(self, base_class):
        """
        """
        self.base_class = base_class
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.GenerateNegativeResponse_Enabled = True
        self.GeneratePositiveResponse_Enabled = True
    

    def ExamineFeedback_Logic(self):
        """
            The actualy logic this state  goes into this method.
            It is upto the developer to add the relevant code.
        """
        self.GenerateNegativeResponse_Enabled = False
    
    def run(self) -> None:
        """
            This method is first called form the base class after instantiating the
            class. The method executes the entire of the state.
        """
        self.base_class.skillLogger.info("\n #############################################################################")
        # StartState
        self.base_class.skillLogger.info("StartState: ExamineFeedback")
        # InputDocumentType"
        InputDocument = "NA"
        self.base_class.skillLogger.info("InputDocument : " + InputDocument)
        
        self.ExamineFeedback_Logic()
        
    def next(self) -> object:
        """
            This methods returns the object to the next state the needs
            to be executed by the base class
        """
        OutputDocument = "NA"
        self.base_class.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        
        if (self.GenerateNegativeResponse_Enabled):
            self.base_class.skillLogger.info("Condition :" + "true")
            ts = GenerateNegativeResponse(self.base_class)
            self.base_class.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.base_class.skillLogger.info("############################################################################# \n")
            return ts
        if (self.GeneratePositiveResponse_Enabled):
            self.base_class.skillLogger.info("Condition :" + "true")
            ts = GeneratePositiveResponse(self.base_class)
            self.base_class.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.base_class.skillLogger.info("############################################################################# \n")
            return ts
        
class GeneratePositiveResponse:
    
    def __init__(self, base_class):
        """
        """
        self.base_class = base_class
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.NotifyFeedBacktoMnO_Enabled = True
    

    def GeneratePositiveResponse_Logic(self):
        """
            The actualy logic this state  goes into this method.
            It is upto the developer to add the relevant code.
        """
        self.base_class.responseMessage["status"] = "S"
        self.base_class.responseMessage["code"] = "A.013"
        self.base_class.responseMessage["message"] =  "The Order is Succesfully Executed."
        
    def create_Outbound_Message(self) -> list:
        """
            The method is used to create the outbound I4.0 messages.
            The message type is carried from the json file.
        """
        self.oMessages = "positivefeedback".split("/")
        outboundMessages = []
        for oMessage in self.oMessages:
            message = self.base_class.WaitforOrder_In
            self.gen = Generic()
            #receiverId = "" # To be decided by the developer
            #receiverRole = "" # To be decided by the developer
            
            # For broadcast message the receiverId and the 
            # receiverRole could be empty 
            
            # For the return reply these details could be obtained from the inbound Message
            receiverId = message["frame"]["sender"]["id"]
            receiverRole = message["frame"]["sender"]["role"]["name"]
            
            # For sending the message to an internal skill
            # The receiver Id should be
            
            I40FrameData =      {
                                    "semanticProtocol": self.base_class.semanticProtocol,
                                    "type" : oMessage,
                                    "messageId" : oMessage+"_"+str(self.base_class.pyaas.dba.getMessageCount()[0]+1),
                                    "SenderAASID" : self.base_class.aasID,
                                    "SenderRolename" : self.base_class.skillName,
                                    "conversationId" : message["frame"]["conversationId"],
                                    "replyBy" :  self.base_class.pyaas.lia_env_variable["LIA_PREFEREDI40ENDPOINT"],
                                    "replyTo" :  message["frame"]["replyBy"],
                                    "ReceiverAASID" :  receiverId,
                                    "ReceiverRolename" : receiverRole
                                }
        
            self.frame = self.gen.createFrame(I40FrameData)
    
            #oMessage_Out = {"frame": self.frame}
            # Usually the interaction Elements are the submodels fro that particualar skill
            # the relevant submodel could be retrieved using
            # interactionElements
            
            #submodel,status,statuscode = self.base_class.pyaas.dba.GetSubmodelById("submodelIdentifier")
            oMessage_Out = {"frame": self.frame,
                                "interactionElements":self.InElem}
            self.instanceId = str(uuid.uuid1())
            self.base_class.pyaas.dataManager.pushInboundMessage({"functionType":3,"instanceid":self.instanceId,
                                                            "conversationId":oMessage_Out["frame"]["conversationId"],
                                                            "messageType":oMessage_Out["frame"]["type"],
                                                            "messageId":oMessage_Out["frame"]["messageId"],
                                                            "direction" : "outbound",
                                                            "SenderAASID" : self.base_class.aasID,
                                                            "message":oMessage_Out})
            outboundMessages.append(oMessage_Out)
        return outboundMessages
    
    def run(self) -> None:
        """
            This method is first called form the base class after instantiating the
            class. The method executes the entire of the state.
        """
        self.base_class.skillLogger.info("\n #############################################################################")
        # StartState
        self.base_class.skillLogger.info("StartState: GeneratePositiveResponse")
        # InputDocumentType"
        InputDocument = "NA"
        self.base_class.skillLogger.info("InputDocument : " + InputDocument)
        
        self.GeneratePositiveResponse_Logic()
        
    def next(self) -> object:
        """
            This methods returns the object to the next state the needs
            to be executed by the base class
        """
        OutputDocument = "positivefeedback"
        self.base_class.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        if (OutputDocument != "NA"):
            pass
            #self.outboundMessages = self.create_Outbound_Message()
            #for outbMessage in self.outboundMessages:
            #    pass#self.base_class.sendMessage(outbMessage)
        
        if (self.NotifyFeedBacktoMnO_Enabled):
            self.base_class.skillLogger.info("Condition :" + "true")
            ts = NotifyFeedBacktoMnO(self.base_class)
            self.base_class.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.base_class.skillLogger.info("############################################################################# \n")
            return ts
        
class WaitforFeedBack:
    
    def __init__(self, base_class):
        """
        """
        self.base_class = base_class
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.GenerateNegativeResponse_Enabled = True
        self.ExamineFeedback_Enabled = True
    
    def retrieve_WaitforFeedBack_Message(self) -> None:
        """
            Method to retrieve the inbound i4.0 message from the relevant queue.
            The retrieved message is assigned to the dictionary variabel designed
            in the base clase. The Variable and the queue name are based on the 
            current state.
        """
        self.base_class.WaitforFeedBack_In = self.base_class.WaitforFeedBack_Queue.get()
    
    def saveMessage(self) -> None:
        """
            Method to save the message into the database
        """
        inboundQueueList = list(self.base_class.WaitforFeedBack_Queue.queue) # in case for further processing is required
        # else creation of the new queue is not required.
        for i in range (0, self.base_class.WaitforFeedBack_Queue.qsize()):
            message = inboundQueueList[i]
            self.instanceId = str(uuid.uuid1())
            self.base_class.pyaas.dataManager.pushInboundMessage({"functionType":3,"instanceid":self.instanceId,
                                                            "conversationId":message["frame"]["conversationId"],
                                                            "messageType":message["frame"]["type"],
                                                            "messageId":message["frame"]["messageId"],
                                                            "direction": "inbound",
                                                            "SenderAASID" : self.base_class.aasID,
                                                            "message":message})
            

    def WaitforFeedBack_Logic(self):
        """
            The actualy logic this state  goes into this method.
            It is upto the developer to add the relevant code.
        """
        pass
    
    def run(self) -> None:
        """
            This method is first called form the base class after instantiating the
            class. The method executes the entire of the state.
        """
        self.base_class.skillLogger.info("\n #############################################################################")
        # StartState
        self.base_class.skillLogger.info("StartState: WaitforFeedBack")
        # InputDocumentType"
        InputDocument = "feedback"
        self.base_class.skillLogger.info("InputDocument : " + InputDocument)
        
        '''
            In case a class expects an input document then.
            It would need to lookup to its specific queue
            that is defined in the based class
        '''
        if (InputDocument != "NA"):
            self.messageExist = True
            i = 0
            sys.stdout.write(" Waiting for response")
            sys.stdout.flush()
            while (((self.base_class.WaitforFeedBack_Queue).qsize()) == 0):
                time.sleep(1)
                i = i + 1 
                if i > 30: # Time to wait the next incoming message
                    self.messageExist = False # If the waiting time expires, the loop is broken
                    break
            if (self.messageExist):
                self.saveMessage() # in case we need to store the incoming message
                self.retrieve_WaitforFeedBack_Message() # in case of multiple inbound messages this function should 
                                                      # not be invoked.
                self.GenerateNegativeResponse_Enabled = False
            else:
                self.ExamineFeedback_Enabled = False
        #self.WaitforFeedBack_Logic()
        
    def next(self) -> object:
        """
            This methods returns the object to the next state the needs
            to be executed by the base class
        """
        OutputDocument = "NA"
        self.base_class.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        
        if (self.GenerateNegativeResponse_Enabled):
            self.base_class.skillLogger.info("Condition :" + "true")
            ts = GenerateNegativeResponse(self.base_class)
            self.base_class.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.base_class.skillLogger.info("############################################################################# \n")
            return ts
        if (self.ExamineFeedback_Enabled):
            self.base_class.skillLogger.info("Condition :" + "true")
            ts = ExamineFeedback(self.base_class)
            self.base_class.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.base_class.skillLogger.info("############################################################################# \n")
            return ts
        
class NotifyFeedBacktoMnO:
    
    def __init__(self, base_class):
        """
        """
        self.base_class = base_class
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.Start_Enabled = True
    

    def NotifyFeedBacktoMnO_Logic(self):
        """
            The actualy logic this state  goes into this method.
            It is upto the developer to add the relevant code.
        """
        self.InElem = self.base_class.StatusResponseSM
        self.InElem[0]["submodelElements"][0]["value"] = self.base_class.responseMessage["status"]
        self.InElem[0]["submodelElements"][1]["value"] = self.base_class.responseMessage["code"]
        self.InElem[0]["submodelElements"][2]["value"] = self.base_class.responseMessage["message"]
        
    def create_Outbound_Message(self) -> list:
        """
            The method is used to create the outbound I4.0 messages.
            The message type is carried from the json file.
        """
        self.oMessages = "OrderStatus".split("/")
        outboundMessages = []
        for oMessage in self.oMessages:
            message = self.base_class.WaitforOrder_In
            self.gen = Generic()
            #receiverId = "" # To be decided by the developer
            #receiverRole = "" # To be decided by the developer
            
            # For broadcast message the receiverId and the 
            # receiverRole could be empty 
            
            # For the return reply these details could be obtained from the inbound Message
            receiverId = message["frame"]["sender"]["id"]
            receiverRole = message["frame"]["sender"]["role"]["name"]
            
            # For sending the message to an internal skill
            # The receiver Id should be
            
            I40FrameData =      {
                                    "semanticProtocol": self.base_class.semanticProtocol,
                                    "type" : oMessage,
                                    "messageId" : oMessage+"_"+str(self.base_class.pyaas.dba.getMessageCount()[0]+1),
                                    "SenderAASID" : self.base_class.aasID,
                                    "SenderRolename" : self.base_class.skillName,
                                    "conversationId" : message["frame"]["conversationId"],
                                    "replyBy" :  self.base_class.pyaas.lia_env_variable["LIA_PREFEREDI40ENDPOINT"],
                                    "replyTo" :  message["frame"]["replyBy"],
                                    "ReceiverAASID" :  receiverId,
                                    "ReceiverRolename" : receiverRole
                                }
        
            self.frame = self.gen.createFrame(I40FrameData)
    
            #oMessage_Out = {"frame": self.frame}
            # Usually the interaction Elements are the submodels fro that particualar skill
            # the relevant submodel could be retrieved using
            # interactionElements
            
            #submodel,status,statuscode = self.base_class.pyaas.dba.GetSubmodelById("submodelIdentifier")
            oMessage_Out = {"frame": self.frame,
                                "interactionElements":self.InElem}
            self.instanceId = str(uuid.uuid1())
            self.base_class.pyaas.dataManager.pushInboundMessage({"functionType":3,"instanceid":self.instanceId,
                                                            "conversationId":oMessage_Out["frame"]["conversationId"],
                                                            "messageType":oMessage_Out["frame"]["type"],
                                                            "messageId":oMessage_Out["frame"]["messageId"],
                                                            "direction" : "outbound",
                                                            "SenderAASID" : self.base_class.aasID,
                                                            "message":oMessage_Out})
            outboundMessages.append(oMessage_Out)
        return outboundMessages
    
    def run(self) -> None:
        """
            This method is first called form the base class after instantiating the
            class. The method executes the entire of the state.
        """
        self.base_class.skillLogger.info("\n #############################################################################")
        # StartState
        self.base_class.skillLogger.info("StartState: NotifyFeedBacktoMnO")
        # InputDocumentType"
        InputDocument = "NA"
        self.base_class.skillLogger.info("InputDocument : " + InputDocument)
        
        self.NotifyFeedBacktoMnO_Logic()
        
    def next(self) -> object:
        """
            This methods returns the object to the next state the needs
            to be executed by the base class
        """
        OutputDocument = "feedback"
        self.base_class.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        if (OutputDocument != "NA"):
            self.outboundMessages = self.create_Outbound_Message()
            for outbMessage in self.outboundMessages:
                self.base_class.sendMessage(outbMessage)
        
        if (self.Start_Enabled):
            self.base_class.skillLogger.info("Condition :" + "true")
            ts = Start(self.base_class)
            self.base_class.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.base_class.skillLogger.info("############################################################################# \n")
            return ts
        
class GenerateNegativeResponse:
    
    def __init__(self, base_class):
        """
        """
        self.base_class = base_class
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.NotifyFeedBacktoMnO_Enabled = True
    

    def GenerateNegativeResponse_Logic(self):
        """
            The actualy logic this state  goes into this method.
            It is upto the developer to add the relevant code.
        """
        self.base_class.responseMessage["status"] = "E"
        self.base_class.responseMessage["code"] = "E.06"
        self.base_class.responseMessage["message"] =  "Negative feedback from the VOR Server"
  
    def create_Outbound_Message(self) -> list:
        """
            The method is used to create the outbound I4.0 messages.
            The message type is carried from the json file.
        """
        self.oMessages = "negativefeedback".split("/")
        outboundMessages = []
        for oMessage in self.oMessages:
            message = self.base_class.WaitforOrder_In
            self.gen = Generic()
            #receiverId = "" # To be decided by the developer
            #receiverRole = "" # To be decided by the developer
            
            # For broadcast message the receiverId and the 
            # receiverRole could be empty 
            
            # For the return reply these details could be obtained from the inbound Message
            receiverId = message["frame"]["sender"]["id"]
            receiverRole = message["frame"]["sender"]["role"]["name"]
            
            # For sending the message to an internal skill
            # The receiver Id should be
            
            I40FrameData =      {
                                    "semanticProtocol": self.base_class.semanticProtocol,
                                    "type" : oMessage,
                                    "messageId" : oMessage+"_"+str(self.base_class.pyaas.dba.getMessageCount()[0]+1),
                                    "SenderAASID" : self.base_class.aasID,
                                    "SenderRolename" : self.base_class.skillName,
                                    "conversationId" : message["frame"]["conversationId"],
                                    "replyBy" :  self.base_class.pyaas.lia_env_variable["LIA_PREFEREDI40ENDPOINT"],
                                    "replyTo" :  message["frame"]["replyBy"],
                                    "ReceiverAASID" :  receiverId,
                                    "ReceiverRolename" : receiverRole
                                }
        
            self.frame = self.gen.createFrame(I40FrameData)
    
            #oMessage_Out = {"frame": self.frame}
            # Usually the interaction Elements are the submodels fro that particualar skill
            # the relevant submodel could be retrieved using
            # interactionElements
            
            submodel,status,statuscode = self.base_class.pyaas.dba.GetSubmodelById("submodelIdentifier")
            oMessage_Out ={"frame": self.frame,
                                    "interactionElements":submodel}
            self.instanceId = str(uuid.uuid1())
            self.base_class.pyaas.dataManager.pushInboundMessage({"functionType":3,"instanceid":self.instanceId,
                                                            "conversationId":oMessage_Out["frame"]["conversationId"],
                                                            "messageType":oMessage_Out["frame"]["type"],
                                                            "messageId":oMessage_Out["frame"]["messageId"],
                                                            "direction" : "outbound",
                                                            "SenderAASID" : self.base_class.aasID,
                                                            "message":oMessage_Out})
            outboundMessages.append(oMessage_Out)
        return outboundMessages
    
    def run(self) -> None:
        """
            This method is first called form the base class after instantiating the
            class. The method executes the entire of the state.
        """
        self.base_class.skillLogger.info("\n #############################################################################")
        # StartState
        self.base_class.skillLogger.info("StartState: GenerateNegativeResponse")
        # InputDocumentType"
        InputDocument = "NA"
        self.base_class.skillLogger.info("InputDocument : " + InputDocument)
        
        self.GenerateNegativeResponse_Logic()
        
    def next(self) -> object:
        """
            This methods returns the object to the next state the needs
            to be executed by the base class
        """
        OutputDocument = "negativefeedback"
        self.base_class.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        if (OutputDocument != "NA"):
            self.outboundMessages = self.create_Outbound_Message()
            for outbMessage in self.outboundMessages:
                self.base_class.sendMessage(outbMessage)
        
        if (self.NotifyFeedBacktoMnO_Enabled):
            self.base_class.skillLogger.info("Condition :" + "true")
            ts = NotifyFeedBacktoMnO(self.base_class)
            self.base_class.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.base_class.skillLogger.info("############################################################################# \n")
            return ts
        
class Start:
    
    def __init__(self, base_class):
        """
        """
        self.base_class = base_class
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.WaitforOrder_Enabled = True
    

    def Start_Logic(self):
        """
            The actualy logic this state  goes into this method.
            It is upto the developer to add the relevant code.
        """
        
    
    def run(self) -> None:
        """
            This method is first called form the base class after instantiating the
            class. The method executes the entire of the state.
        """
        self.base_class.skillLogger.info("\n #############################################################################")
        # StartState
        self.base_class.skillLogger.info("StartState: Start")
        # InputDocumentType"
        InputDocument = "NA"
        self.base_class.skillLogger.info("InputDocument : " + InputDocument)
        
        self.Start_Logic()
        
    def next(self) -> object:
        """
            This methods returns the object to the next state the needs
            to be executed by the base class
        """
        OutputDocument = "NA"
        self.base_class.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        
        if (self.WaitforOrder_Enabled):
            self.base_class.skillLogger.info("Condition :" + "true")
            ts = WaitforOrder(self.base_class)
            self.base_class.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.base_class.skillLogger.info("############################################################################# \n")
            return ts
        
class createnSendRequest:
    
    def __init__(self, base_class):
        """
        """
        self.base_class = base_class
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.WaitforFeedBack_Enabled = True
    

    def createnSendRequest_Logic(self):
        """
            The actualy logic this state  goes into this method.
            It is upto the developer to add the relevant code.
        """
        
    def create_Outbound_Message(self) -> list:
        """
            The method is used to create the outbound I4.0 messages.
            The message type is carried from the json file.
        """
        self.oMessages = "request".split("/")
        outboundMessages = []
        for oMessage in self.oMessages:
            message = self.base_class.WaitforOrder_In
            self.gen = Generic()
            #receiverId = "" # To be decided by the developer
            #receiverRole = "" # To be decided by the developer
            
            # For broadcast message the receiverId and the 
            # receiverRole could be empty 
            
            # For the return reply these details could be obtained from the inbound Message
            receiverId = "https://example.com/ids/aas/8414_0121_2122_0339"#message["frame"]["sender"]["id"]
            receiverRole = "VOR"
            
            # For sending the message to an internal skill
            # The receiver Id should be
            
            I40FrameData =      {
                                    "semanticProtocol": self.base_class.semanticProtocol,
                                    "type" : oMessage,
                                    "messageId" : oMessage+"_"+str(self.base_class.pyaas.dba.getMessageCount()[0]+1),
                                    "SenderAASID" : self.base_class.aasID,
                                    "SenderRolename" : self.base_class.skillName,
                                    "conversationId" : message["frame"]["conversationId"],
                                    "replyBy" :  self.base_class.pyaas.lia_env_variable["LIA_PREFEREDI40ENDPOINT"],
                                    "replyTo" :  message["frame"]["replyBy"],
                                    "ReceiverAASID" :  receiverId,
                                    "ReceiverRolename" : receiverRole
                                }
        
            self.frame = self.gen.createFrame(I40FrameData)
    
            #oMessage_Out = {"frame": self.frame}
            # Usually the interaction Elements are the submodels fro that particualar skill
            # the relevant submodel could be retrieved using
            # interactionElements
            orderDetails = (self.base_class.WaitforOrder_In["interactionElements"][0])
            request_collection,status,statuscode = self.base_class.pyaas.dba.GetSubmodelElementByPath_SRI(orderDetails[0],orderDetails[2])
            oMessage_Out ={"frame": self.frame,
                                    "interactionElements":[request_collection]}
            self.instanceId = str(uuid.uuid1())
            self.base_class.pyaas.dataManager.pushInboundMessage({"functionType":3,"instanceid":self.instanceId,
                                                            "conversationId":oMessage_Out["frame"]["conversationId"],
                                                            "messageType":oMessage_Out["frame"]["type"],
                                                            "messageId":oMessage_Out["frame"]["messageId"],
                                                            "direction" : "outbound",
                                                            "SenderAASID" : self.base_class.aasID,
                                                            "message":oMessage_Out})
            outboundMessages.append(oMessage_Out)
        return outboundMessages
    
    def run(self) -> None:
        """
            This method is first called form the base class after instantiating the
            class. The method executes the entire of the state.
        """
        self.base_class.skillLogger.info("\n #############################################################################")
        # StartState
        self.base_class.skillLogger.info("StartState: createnSendRequest")
        # InputDocumentType"
        InputDocument = "NA"
        self.base_class.skillLogger.info("InputDocument : " + InputDocument)
        
        self.createnSendRequest_Logic()
        
    def next(self) -> object:
        """
            This methods returns the object to the next state the needs
            to be executed by the base class
        """
        OutputDocument = "request"
        self.base_class.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        if (OutputDocument != "NA"):
            self.outboundMessages = self.create_Outbound_Message()
            for outbMessage in self.outboundMessages:
                self.base_class.sendMessage(outbMessage)
        
        if (self.WaitforFeedBack_Enabled):
            self.base_class.skillLogger.info("Condition :" + "true")
            ts = WaitforFeedBack(self.base_class)
            self.base_class.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.base_class.skillLogger.info("############################################################################# \n")
            return ts
        
class RequesterMNO:
    '''
    classdocs
    '''

        
    def initstate_specific_queue_internal(self) -> None:
        """
        """
        self.QueueDict = {}
        
        self.WaitforOrder_Queue = Queue.Queue()
        self.ExamineFeedback_Queue = Queue.Queue()
        self.GeneratePositiveResponse_Queue = Queue.Queue()
        self.WaitforFeedBack_Queue = Queue.Queue()
        self.NotifyFeedBacktoMnO_Queue = Queue.Queue()
        self.GenerateNegativeResponse_Queue = Queue.Queue()
        self.Start_Queue = Queue.Queue()
        self.createnSendRequest_Queue = Queue.Queue()
        
                
        self.QueueDict = {
              "Order": self.WaitforOrder_Queue,
              "feedback": self.WaitforFeedBack_Queue,
            }
    
    def init_inbound_messages(self) -> None:
        self.WaitforOrder_In = {}
        self.WaitforFeedBack_In = {}
        pass
    
    def empty_all_queues(self) -> None:
        for queueName,queue in self.QueueDict.items():
            queueList = list(self.queue.queue)
            for elem in range(0,len(queueList)):
                queue.get()
    
    def create_status_message(self) -> None:
        self.StatusDataFrame =      {
                                "semanticProtocol": self.semanticProtocol,
                                "type" : "StausChange",
                                "messageId" : "StausChange_1",
                                "SenderAASID" : self.aasID,
                                "SenderRolename" : self.skillName,
                                "conversationId" : "AASNetworkedBidding",
                                "replyBy" :  "",
                                "replyTo" :"",
                                "ReceiverAASID" :  self.aasID + "/"+self.skillName,
                                "ReceiverRolename" : "SkillStatusChange"
                            }
        self.statusframe = self.gen.createFrame(self.StatusDataFrame)
        self.statusInElem = self.pyaas.aasConfigurer.getStatusResponseSubmodel()
        self.statusMessage ={"frame": self.statusframe,
                                "interactionElements":[self.statusInElem]}
 
    
    def __init__(self,pyaas):
        '''
        Constructor
        '''
        
        self.SKILL_STATES = {
                          "WaitforOrder": "WaitforOrder",  "ExamineFeedback": "ExamineFeedback",  "GeneratePositiveResponse": "GeneratePositiveResponse",  "WaitforFeedBack": "WaitforFeedBack",  "NotifyFeedBacktoMnO": "NotifyFeedBacktoMnO",  "GenerateNegativeResponse": "GenerateNegativeResponse",  "Start": "Start",  "createnSendRequest": "createnSendRequest",
                       }
        
        self.pyaas = pyaas
        self.skillName = "StateMachine_Requester_MnO"
        self.initstate_specific_queue_internal()
        self.init_inbound_messages()
        self.currentConversationId = "temp"
        
        self.enabledStatus = {"Y":True, "N":False}
        self.enabledState = "Y"
        
        self.semanticProtocol = "www.admin-shell.io/interaction/servicerequistion"
        self.initialState = "Start"
        self.skill_service = "Maintenance"
        self.gen = Generic()
        self.productionStepSeq = []
        self.responseMessage = {}
        self.StatusResponseSM = [self.pyaas.aasConfigurer.getStatusResponseSubmodel()]
        
    def start(self, msgHandler,shellObject,_uid) -> None:
        """
            Starting of the Skill state machine
        """
        self.msgHandler = msgHandler
        self.shellObject = shellObject
        self.aasID = shellObject.aasELement["id"]
        self.uuid  = _uid
        self.create_status_message()
        self.skillLogger = logging.getLogger(self.aasID+"."+self.skillName)
        self.skillLogger.setLevel(logging.DEBUG)
        
        self.commandLogger_handler = logging.StreamHandler(stream=sys.stdout)
        self.commandLogger_handler.setLevel(logging.DEBUG)

        bString = base64.b64encode(bytes(self.aasID,'utf-8'))
        base64_string= bString.decode('utf-8')
        
        self.fileLogger_Handler = logging.FileHandler(self.pyaas.base_dir+"/logs/"+"_"+str(base64_string)+"_"+self.skillName+".LOG")
        self.fileLogger_Handler.setLevel(logging.DEBUG)
        
        self.listHandler = ServiceLogHandler(LogList())
        self.listHandler.setLevel(logging.DEBUG)
        
        self.Handler_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%m/%d/%Y %I:%M:%S %p')
        
        self.listHandler.setFormatter(self.Handler_format)
        self.commandLogger_handler.setFormatter(self.Handler_format)
        self.fileLogger_Handler.setFormatter(self.Handler_format)
        
        self.skillLogger.addHandler(self.listHandler)
        self.skillLogger.addHandler(self.commandLogger_handler)
        self.skillLogger.addHandler(self.fileLogger_Handler)
        
        Start_1 = Start(self)
        self.stateChange("Start")
        currentState = Start_1
        
        
        while (True):
            if ((currentState.__class__.__name__) == "Start"):
                if(self.enabledState):
                    currentState.run()
                    ts = currentState.next()
                    self.stateChange(ts.__class__.__name__)
                    currentState = ts
                else:
                    time.sleep(1)
            else:
                currentState.run()
                ts = currentState.next()
                if not (ts):
                    break
                else:
                    self.stateChange(ts.__class__.__name__)
                    currentState = ts
    
    def geCurrentSKILLState(self) -> str:
        return self.SKILL_STATE
    
    def getListofSKILLStates(self) -> list:
        return self.SKILL_STATES
    
    
    def stateChange(self, STATE) -> None:
        self.statusMessage["interactionElements"][0]["submodelElements"][0]["value"] = "I"
        self.statusMessage["interactionElements"][0]["submodelElements"][1]["value"] = "A006. internal-status-change"
        self.statusMessage["interactionElements"][0]["submodelElements"][2]["value"] = str(datetime.now()) +" "+STATE
        #self.sendMessage(self.statusMessage)
    
    def sendMessage(self, sendMessage) -> None:
        self.msgHandler.putIbMessage(sendMessage)
    
    def receiveMessage(self,inMessage) -> None:
        try:    
            _conversationId = str(inMessage['frame']['conversationId'])
            senderRole = str(inMessage["frame"]['sender']['role']["name"])
            _messageType = str(inMessage['frame']['type'])
            self.QueueDict[_messageType].put(inMessage)
        except Exception as E:
            pass#self.skillLogger.info("Raise an Exception " + str(E))



if __name__ == '__main__':
    
    lm2 = RequesterMNO()
    lm2.Start('msgHandler')
