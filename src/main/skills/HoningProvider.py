"""
Copyright (c) 2023 Otto-von-Guericke-Universitaet Magdeburg, Lehrstuhl Integrierte Automation
Author: Harish Kumar Pakala
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
    
    The base_class is responsible for collecting the documents from the external
    world (either from other skill that is part of the AAS or a skill part of 
    of another AAS). For this the base_class maintains a queue one for each class. 
    
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
    
    A class specific inbound queue is defined in the base_class for the classes defined in this
    source-code. A dictionary is also manitained, with key representing the messagetype and the
    value being the class specific inboundqueue.
    
    Every inbound message to the skill, is routed to the specific class based on its message type
    from the base CLaas.  
    
    For operational purposes, a dictionary variable is defined for each message type that this skill
    expects. 

    StateName_In         
    StateName_Queue 
        
    The sendMessage method in the base_class submits an outbound message to the message handler so that
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
        self.plcHandler = self.base_class.pyaas.asset_access_handlers[MODULE_NAME] # 1
        
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
        "SenderRolename" : "HoningProvider",
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
    
    example Honing (should be same as the one specified in AASX file.)
    submodel,status,statuscode = self.base_class.pyaas.dba.GetSubmodelById("submodelIdentifier")
    Here status is a boolean variable and when it is False submodel is not returned.
    statuscode can be ignored in this context 
    # result is list
    I40OutBoundMessage = {
                            "frame" : frame,
                            "interactionElements" : HoningSubmodel
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
                                                            "message":message})
        
    
'''
    
class sendingRefuse:
    
    def __init__(self, base_class):
        """
        """
        self.base_class = base_class
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.WaitForCallForProposal_Enabled = True
    

    def sendingRefuse_Logic(self):
        """
            The actualy logic this state  goes into this method.
            It is upto the developer to add the relevant code.
        """
        
    def create_Outbound_Message(self) -> list:
        """
            The method is used to create the outbound I4.0 messages.
            The message type is carried from the json file.
        """
        self.oMessages = "refuseProposal".split("/")
        outboundMessages = []
        for oMessage in self.oMessages:
            message = self.base_class.WaitForCallForProposal_In
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
                                    "replyBy" :  "",
                                    "replyTo" :  message["frame"]["replyBy"],
                                    "ReceiverAASID" :  receiverId,
                                    "ReceiverRolename" : receiverRole
                                }
        
            self.frame = self.gen.createFrame(I40FrameData)
    
            oMessage_Out = {"frame": self.frame}
            # Usually the interaction Elements are the submodels fro that particualar skill
            # the relevant submodel could be retrieved using
            # interactionElements
            
            #submodel,status,statuscode = self.base_class.pyaas.dba.GetSubmodelById("submodelIdentifier")
            #oMessage_Out ={"frame": self.frame,
            #                        "interactionElements":submodel}
            self.instanceId = str(uuid.uuid1())
            self.base_class.pyaas.dataManager.pushInboundMessage({"functionType":3,"instanceid":self.instanceId,
                                                            "conversationId":oMessage_Out["frame"]["conversationId"],
                                                            "messageType":oMessage_Out["frame"]["type"],
                                                            "messageId":oMessage_Out["frame"]["messageId"],
                                                            "direction" : "outbound",
                                                            "SenderAASID" : oMessage_Out["frame"]["sender"]["id"],
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
        self.base_class.skillLogger.info("StartState: sendingRefuse")
        # InputDocumentType"
        InputDocument = "NA"
        self.base_class.skillLogger.info("InputDocument : " + InputDocument)
        
        self.sendingRefuse_Logic()
        
    def next(self) -> object:
        """
            This methods returns the object to the next state the needs
            to be executed by the base class
        """
        OutputDocument = "refuseProposal"
        self.base_class.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        if (OutputDocument != "NA"):
            self.outboundMessages = self.create_Outbound_Message()
            for outbMessage in self.outboundMessages:
                self.base_class.sendMessage(outbMessage)
        
        if (self.WaitForCallForProposal_Enabled):
            self.base_class.skillLogger.info("Condition :" + "-")
            ts = WaitForCallForProposal(self.base_class)
            self.base_class.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.base_class.skillLogger.info("############################################################################# \n")
            return ts
        
class sendinPropoposalporvisionConfirm:
    
    def __init__(self, base_class):
        """
        """
        self.base_class = base_class
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.WaitForCallForProposal_Enabled = True
    

    def sendinPropoposalporvisionConfirm_Logic(self):
        """
            The actualy logic this state  goes into this method.
            It is upto the developer to add the relevant code.
        """
        
    def create_Outbound_Message(self) -> list:
        """
            The method is used to create the outbound I4.0 messages.
            The message type is carried from the json file.
        """
        self.oMessages = "informConfirm".split("/")
        outboundMessages = []
        for oMessage in self.oMessages:
            message = self.base_class.waitingforServiceRequesterAnswer_In
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
                                    "replyBy" :  "",
                                    "replyTo" :  message["frame"]["replyBy"],
                                    "ReceiverAASID" :  receiverId,
                                    "ReceiverRolename" : receiverRole
                                }
        
            self.frame = self.gen.createFrame(I40FrameData)
    
            oMessage_Out = {"frame": self.frame}
            # Usually the interaction Elements are the submodels fro that particualar skill
            # the relevant submodel could be retrieved using
            # interactionElements
            
            #submodel,status,statuscode = self.base_class.pyaas.dba.GetSubmodelById("submodelIdentifier")
            #oMessage_Out ={"frame": self.frame,
            #                        "interactionElements":submodel}
            self.instanceId = str(uuid.uuid1())
            self.base_class.pyaas.dataManager.pushInboundMessage({"functionType":3,"instanceid":self.instanceId,
                                                            "conversationId":oMessage_Out["frame"]["conversationId"],
                                                            "messageType":oMessage_Out["frame"]["type"],
                                                            "messageId":oMessage_Out["frame"]["messageId"],
                                                            "direction" : "outbound",
                                                            "SenderAASID" : oMessage_Out["frame"]["sender"]["id"],
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
        self.base_class.skillLogger.info("StartState: sendinPropoposalporvisionConfirm")
        # InputDocumentType"
        InputDocument = "NA"
        self.base_class.skillLogger.info("InputDocument : " + InputDocument)
        
        self.sendinPropoposalporvisionConfirm_Logic()
        
    def next(self) -> object:
        """
            This methods returns the object to the next state the needs
            to be executed by the base class
        """
        OutputDocument = "informConfirm"
        self.base_class.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        if (OutputDocument != "NA"):
            self.outboundMessages = self.create_Outbound_Message()
            for outbMessage in self.outboundMessages:
                self.base_class.sendMessage(outbMessage)
        
        if (self.WaitForCallForProposal_Enabled):
            self.base_class.skillLogger.info("Condition :" + "-")
            ts = WaitForCallForProposal(self.base_class)
            self.base_class.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.base_class.skillLogger.info("############################################################################# \n")
            return ts
        
class sendingNotUnderstood:
    
    def __init__(self, base_class):
        """
        """
        self.base_class = base_class
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.WaitForCallForProposal_Enabled = True
    

    def sendingNotUnderstood_Logic(self):
        """
            The actualy logic this state  goes into this method.
            It is upto the developer to add the relevant code.
        """
        
    def create_Outbound_Message(self) -> list:
        """
            The method is used to create the outbound I4.0 messages.
            The message type is carried from the json file.
        """
        self.oMessages = "notUnderstood".split("/")
        outboundMessages = []
        for oMessage in self.oMessages:
            message = self.base_class.WaitForCallForProposal_In
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
                                    "replyBy" :  "",
                                    "replyTo" :  message["frame"]["replyBy"],
                                    "ReceiverAASID" :  receiverId,
                                    "ReceiverRolename" : receiverRole
                                }
        
            self.frame = self.gen.createFrame(I40FrameData)
    
            oMessage_Out = {"frame": self.frame}
            # Usually the interaction Elements are the submodels fro that particualar skill
            # the relevant submodel could be retrieved using
            # interactionElements
            
            #submodel,status,statuscode = self.base_class.pyaas.dba.GetSubmodelById("submodelIdentifier")
            #oMessage_Out ={"frame": self.frame,
            #                        "interactionElements":submodel}
            self.instanceId = str(uuid.uuid1())
            self.base_class.pyaas.dataManager.pushInboundMessage({"functionType":3,"instanceid":self.instanceId,
                                                            "conversationId":oMessage_Out["frame"]["conversationId"],
                                                            "messageType":oMessage_Out["frame"]["type"],
                                                            "messageId":oMessage_Out["frame"]["messageId"],
                                                            "direction" : "outbound",
                                                            "SenderAASID" : oMessage_Out["frame"]["sender"]["id"],
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
        self.base_class.skillLogger.info("StartState: sendingNotUnderstood")
        # InputDocumentType"
        InputDocument = "NA"
        self.base_class.skillLogger.info("InputDocument : " + InputDocument)
        
        self.sendingNotUnderstood_Logic()
        
    def next(self) -> object:
        """
            This methods returns the object to the next state the needs
            to be executed by the base class
        """
        OutputDocument = "notUnderstood"
        self.base_class.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        if (OutputDocument != "NA"):
            self.outboundMessages = self.create_Outbound_Message()
            for outbMessage in self.outboundMessages:
                self.base_class.sendMessage(outbMessage)
        
        if (self.WaitForCallForProposal_Enabled):
            self.base_class.skillLogger.info("Condition :" + "-")
            ts = WaitForCallForProposal(self.base_class)
            self.base_class.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.base_class.skillLogger.info("############################################################################# \n")
            return ts
        
class feasibilityCheck:
    
    def __init__(self, base_class):
        """
        """
        self.base_class = base_class
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.sendingRefuse_Enabled = True
        self.checkingSchedule_Enabled = True
    

    def feasibilityCheck_Logic(self):
        """
            The actualy logic this state  goes into this method.
            It is upto the developer to add the relevant code.
        """
        self.itemsCheck = {"MaterialOfWorkpiece":"Property","Height":"Range",
         "Depth":"Range","Width":"Range","ReferencedStandartOfMaterialShortName":"Property",
         "TensileStrengthOfMaterial":"Range","WeightOfWorkpiece":"Range","Hardness":"TRange",
         "honingDiameter":"Range","honingDepth":"Range",
         "RoughnessAverageOfBore":"Range","ISOToleranceClass":"Range"}
        
        feasibilityLen = 0
        for key in list(self.itemsCheck):
            item = self.itemsCheck[key]
            if  item == "Property":
                if (key == "MaterialOfWorkpiece"):
                    feasibilityLen = feasibilityLen + 1 
                elif ( self.base_class.proposalSubmodelTypes[key] == self.base_class.subModelTypes[key] ):
                    feasibilityLen = feasibilityLen + 1
                else :
                    print(key,self.base_class.proposalSubmodelTypes[key],self.base_class.subModelTypes[key])
            elif item == "Range":
                value = self.base_class.proposalSubmodelTypes[key]
                min = float(self.base_class.subModelTypes[key]["min"])
                max = float(self.base_class.subModelTypes[key]["max"])
                if float(value) >= min and float(value) <= max :
                    feasibilityLen = feasibilityLen + 1
                else :
                    print(key,value,self.base_class.subModelTypes[key])                    
            elif item == "TRange":
                value = self.base_class.proposalSubmodelTypes[key]
                _min = float((self.base_class.subModelTypes[key]["min"]).split(" ")[1])
                _max = float((self.base_class.subModelTypes[key]["max"]).split(" ")[1])
                tempValue = value.split(" ")[1]
                if float(tempValue) >= _min and float(tempValue) <= _max :
                    feasibilityLen = feasibilityLen + 1
                else :
                    print(key,value,self.base_class.subModelTypes[key])                    
                    
        if feasibilityLen == 12:
            self.sendingRefuse_Enabled = False
        else:
            self.checkingSchedule_Enabled = False
        
    
    def run(self) -> None:
        """
            This method is first called form the base class after instantiating the
            class. The method executes the entire of the state.
        """
        self.base_class.skillLogger.info("\n #############################################################################")
        # StartState
        self.base_class.skillLogger.info("StartState: feasibilityCheck")
        # InputDocumentType"
        InputDocument = "NA"
        self.base_class.skillLogger.info("InputDocument : " + InputDocument)
        
        self.feasibilityCheck_Logic()
        
    def next(self) -> object:
        """
            This methods returns the object to the next state the needs
            to be executed by the base class
        """
        OutputDocument = "NA"
        self.base_class.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        
        if (self.sendingRefuse_Enabled):
            self.base_class.skillLogger.info("Condition :" + "-")
            ts = sendingRefuse(self.base_class)
            self.base_class.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.base_class.skillLogger.info("############################################################################# \n")
            return ts
        if (self.checkingSchedule_Enabled):
            self.base_class.skillLogger.info("Condition :" + "-")
            ts = checkingSchedule(self.base_class)
            self.base_class.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.base_class.skillLogger.info("############################################################################# \n")
            return ts
        
class WaitForCallForProposal:
    
    def __init__(self, base_class):
        """
        """
        self.base_class = base_class
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.capabilitycheck_Enabled = True
    
    def retrieve_WaitForCallForProposal_Message(self) -> None:
        """
            Method to retrieve the inbound i4.0 message from the relevant queue.
            The retrieved message is assigned to the dictionary variabel designed
            in the base clase. The Variable and the queue name are based on the 
            current state.
        """
        self.base_class.WaitForCallForProposal_In = self.base_class.WaitForCallForProposal_Queue.get()
        self.base_class.subModelTypes = {}
        self.base_class.proposalSubmodelTypes = {}

    
    def saveMessage(self) -> None:
        """
            Method to save the message into the database
        """
        inboundQueueList = list(self.base_class.WaitForCallForProposal_Queue.queue) # in case for further processing is required
        # else creation of the new queue is not required.
        for i in range (0, self.base_class.WaitForCallForProposal_Queue.qsize()):
            message = inboundQueueList[i]
            self.instanceId = str(uuid.uuid1())
            self.base_class.pyaas.dataManager.pushInboundMessage({"functionType":3,"instanceid":self.instanceId,
                                                            "conversationId":message["frame"]["conversationId"],
                                                            "messageType":message["frame"]["type"],
                                                            "messageId":message["frame"]["messageId"],
                                                            "direction": "inbound",
                                                            "SenderAASID" : message["frame"]["sender"]["id"],
                                                            "message":message})
            

    def WaitForCallForProposal_Logic(self):
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
        self.base_class.skillLogger.info("StartState: WaitForCallForProposal")
        # InputDocumentType"
        InputDocument = "callForProposal"
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
            while (((self.base_class.WaitForCallForProposal_Queue).qsize()) == 0):
                time.sleep(1)
                
            self.base_class.WaitForCallForProposal_In = {}
            self.base_class.proposalSubmodelTypes = {}
            self.base_class.subModelTypes = {}
            self.base_class.emptyAllQueues()
            self.base_class.initInBoundMessages()               

            self.saveMessage() # in case we need to store the incoming message
            self.retrieve_WaitForCallForProposal_Message() # in case of multiple inbound messages this function should 
                                                      # not be invoked. 
        self.WaitForCallForProposal_Logic()
        
    def next(self) -> object:
        """
            This methods returns the object to the next state the needs
            to be executed by the base class
        """
        OutputDocument = "NA"
        self.base_class.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        
        if (self.capabilitycheck_Enabled):
            self.base_class.skillLogger.info("Condition :" + "-")
            ts = capabilitycheck(self.base_class)
            self.base_class.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.base_class.skillLogger.info("############################################################################# \n")
            return ts
        
class waitingforServiceRequesterAnswer:
    
    def __init__(self, base_class):
        """
        """
        self.base_class = base_class
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.WaitForCallForProposal_Enabled = True
        self.serviceProvision_Enabled = True
    
    def retrieve_waitingforServiceRequesterAnswer_Message(self) -> None:
        """
            Method to retrieve the inbound i4.0 message from the relevant queue.
            The retrieved message is assigned to the dictionary variabel designed
            in the base clase. The Variable and the queue name are based on the 
            current state.
        """
        self.base_class.waitingforServiceRequesterAnswer_In = self.base_class.waitingforServiceRequesterAnswer_Queue.get()
    
    def saveMessage(self) -> None:
        """
            Method to save the message into the database
        """
        inboundQueueList = list(self.base_class.waitingforServiceRequesterAnswer_Queue.queue) # in case for further processing is required
        # else creation of the new queue is not required.
        for i in range (0, self.base_class.waitingforServiceRequesterAnswer_Queue.qsize()):
            message = inboundQueueList[i]
            self.instanceId = str(uuid.uuid1())
            self.base_class.pyaas.dataManager.pushInboundMessage({"functionType":3,"instanceid":self.instanceId,
                                                            "conversationId":message["frame"]["conversationId"],
                                                            "messageType":message["frame"]["type"],
                                                            "messageId":message["frame"]["messageId"],
                                                            "direction": "inbound",
                                                            "SenderAASID" : message["frame"]["sender"]["id"],
                                                            "message":message})
            

    def waitingforServiceRequesterAnswer_Logic(self):
        """
            The actualy logic this state  goes into this method.
            It is upto the developer to add the relevant code.
        """
        if (self.messageExist):
            if (self.base_class.waitingforServiceRequesterAnswer_In["frame"]["type"] =="rejectProposal"):
                self.serviceProvision_Enabled = False
            else:
                self.WaitForCallForProposal_Enabled = False
        else:
            self.serviceProvision_Enabled = False
        
    
    def run(self) -> None:
        """
            This method is first called form the base class after instantiating the
            class. The method executes the entire of the state.
        """
        self.base_class.skillLogger.info("\n #############################################################################")
        # StartState
        self.base_class.skillLogger.info("StartState: waitingforServiceRequesterAnswer")
        # InputDocumentType"
        InputDocument = "acceptProposal / rejectProposal"
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
            while (((self.base_class.waitingforServiceRequesterAnswer_Queue).qsize()) == 0):
                time.sleep(1)
                i = i + 1 
                if i > 60: # Time to wait the next incoming message
                    self.messageExist = False # If the waiting time expires, the loop is broken
                    break
            if (self.messageExist):
                self.saveMessage() # in case we need to store the incoming message
                self.retrieve_waitingforServiceRequesterAnswer_Message() # in case of multiple inbound messages this function should 
                                                      # not be invoked. 
        self.waitingforServiceRequesterAnswer_Logic()
        
    def next(self) -> object:
        """
            This methods returns the object to the next state the needs
            to be executed by the base class
        """
        OutputDocument = "NA"
        self.base_class.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        
        if (self.WaitForCallForProposal_Enabled):
            self.base_class.skillLogger.info("Condition :" + "-")
            ts = WaitForCallForProposal(self.base_class)
            self.base_class.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.base_class.skillLogger.info("############################################################################# \n")
            return ts
        if (self.serviceProvision_Enabled):
            self.base_class.skillLogger.info("Condition :" + "-")
            ts = serviceProvision(self.base_class)
            self.base_class.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.base_class.skillLogger.info("############################################################################# \n")
            return ts
        
class sendingProposal:
    
    def __init__(self, base_class):
        """
        """
        self.base_class = base_class
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.waitingforServiceRequesterAnswer_Enabled = True

    
    def getPropertyElem(self,iSubmodel,propertyName):
        for submodelELem in iSubmodel["submodelElements"]:
            if submodelELem["idShort"] =="CommercialProperties":
                for sproperty in submodelELem["value"]:
                    if sproperty["idShort"] == propertyName:
                        return sproperty
             
             
    def addPropertyElems(self,oSubmodel1,iSubmodel1):
        self.oSubmodel1 = oSubmodel1
        self.iSubmodel1 = iSubmodel1
        i = 0
        listPrice = self.getPropertyElem(self.iSubmodel1,"listprice")
        CFP = self.getPropertyElem(self.iSubmodel1,"cfp")
        workStationLocation = self.getPropertyElem(self.iSubmodel1,"workStationLocation")
        for submodelELem in self.oSubmodel1["submodelElements"]:
            if submodelELem["idShort"] =="CommercialProperties":
                self.oSubmodel1["submodelElements"][i]["value"].append(listPrice)
                self.oSubmodel1["submodelElements"][i]["value"].append(workStationLocation)
                self.oSubmodel1["submodelElements"][i]["value"].append(CFP)
                break
            i = i + 1
        return self.oSubmodel1
                

    def sendingProposal_Logic(self):
        """
            The actualy logic this state  goes into this method.
            It is upto the developer to add the relevant code.
        """
        
    def create_Outbound_Message(self) -> list:
        """
            The method is used to create the outbound I4.0 messages.
            The message type is carried from the json file.
        """
        self.oMessages = "proposal".split("/")
        outboundMessages = []
        for oMessage in self.oMessages:
            import copy
            message = copy.deepcopy(self.base_class.WaitForCallForProposal_In)

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
                                    "replyBy" :  "",
                                    "replyTo" :  message["frame"]["replyBy"],
                                    "ReceiverAASID" :  receiverId,
                                    "ReceiverRolename" : receiverRole
                                }
        
            self.frame = self.gen.createFrame(I40FrameData)
    
            #oMessage_Out = {"frame": self.frame}
            # Usually the interaction Elements are the submodels fro that particualar skill
            # the relevant submodel could be retrieved using
            # interactionElements
            
            self.InElem,status,statuscode = self.base_class.pyaas.dba.GetSubmodelById("https://example.com/ids/sm/4084_7040_1122_9091")
            
            self.HoningSubmodel1 = self.addPropertyElems(message["interactionElements"][0],self.InElem)
            oMessage_Out ={"frame": self.frame,
                                   "interactionElements":[self.HoningSubmodel1]}
            
            self.instanceId = str(uuid.uuid1())
            self.base_class.pyaas.dataManager.pushInboundMessage({"functionType":3,"instanceid":self.instanceId,
                                                            "conversationId":oMessage_Out["frame"]["conversationId"],
                                                            "messageType":oMessage_Out["frame"]["type"],
                                                            "messageId":oMessage_Out["frame"]["messageId"],
                                                            "direction" : "outbound",
                                                            "SenderAASID" : oMessage_Out["frame"]["sender"]["id"],
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
        self.base_class.skillLogger.info("StartState: sendingProposal")
        # InputDocumentType"
        InputDocument = "NA"
        self.base_class.skillLogger.info("InputDocument : " + InputDocument)
        
        self.sendingProposal_Logic()
        
    def next(self) -> object:
        """
            This methods returns the object to the next state the needs
            to be executed by the base class
        """
        OutputDocument = "proposal"
        self.base_class.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        if (OutputDocument != "NA"):
            self.outboundMessages = self.create_Outbound_Message()
            for outbMessage in self.outboundMessages:
                self.base_class.sendMessage(outbMessage)
        
        if (self.waitingforServiceRequesterAnswer_Enabled):
            self.base_class.skillLogger.info("Condition :" + "-")
            ts = waitingforServiceRequesterAnswer(self.base_class)
            self.base_class.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.base_class.skillLogger.info("############################################################################# \n")
            return ts
        
class checkingSchedule:
    
    def __init__(self, base_class):
        """
        """
        self.base_class = base_class
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.sendingRefuse_Enabled = True
        self.PriceCalculation_Enabled = True
    

    def checkingSchedule_Logic(self):
        """
            The actualy logic this state  goes into this method.
            It is upto the developer to add the relevant code.
        """
        self.plcHandler = self.base_class.pyaas.asset_access_handlers["OPCUA"]
        self.tdPropertiesList = self.base_class.shellObject.thing_description
        try:
            sPermissionVariable = ""#self.plcHandler.read(self.tdPropertiesList["sPermission"].href)
            if sPermissionVariable =="error":
                self.PriceCalculation_Enabled = False
            else:
                self.sendingRefuse_Enabled = False
        except Exception as E:
            self.PriceCalculation_Enabled = False
    
    def run(self) -> None:
        """
            This method is first called form the base class after instantiating the
            class. The method executes the entire of the state.
        """
        self.base_class.skillLogger.info("\n #############################################################################")
        # StartState
        self.base_class.skillLogger.info("StartState: checkingSchedule")
        # InputDocumentType"
        InputDocument = "NA"
        self.base_class.skillLogger.info("InputDocument : " + InputDocument)
        
        self.checkingSchedule_Logic()
        
    def next(self) -> object:
        """
            This methods returns the object to the next state the needs
            to be executed by the base class
        """
        OutputDocument = "NA"
        self.base_class.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        
        if (self.sendingRefuse_Enabled):
            self.base_class.skillLogger.info("Condition :" + "-")
            ts = sendingRefuse(self.base_class)
            self.base_class.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.base_class.skillLogger.info("############################################################################# \n")
            return ts
        if (self.PriceCalculation_Enabled):
            self.base_class.skillLogger.info("Condition :" + "-")
            ts = PriceCalculation(self.base_class)
            self.base_class.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.base_class.skillLogger.info("############################################################################# \n")
            return ts
        
class capabilitycheck:
    
    def __init__(self, base_class):
        """
        """
        self.base_class = base_class
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.sendingNotUnderstood_Enabled = True
        self.feasibilityCheck_Enabled = True

    def getProperty(self,submodelElem):
        if submodelElem["modelType"] =="Property":
            return submodelElem["value"] 
        elif submodelElem["modelType"] =="Range":
            return  {"min":submodelElem["min"],"max":submodelElem["max"]} 
    
    def getPropertyList(self,submodel):
        tempDict = {}
        for submodelElem in submodel["submodelElements"]:
            if submodelElem["idShort"] =="CommercialProperties":
                for elem in submodelElem["value"]:
                    tempDict[elem["idShort"]] = self.getProperty(elem)
                    
            elif submodelElem["idShort"] =="TechnicalProperties": 
                for elem in submodelElem["value"]:
                    if elem["idShort"] =="FunctionalProperties" or elem["idShort"] =="EnvironmentalProperties": 
                        for ele in elem["value"]:
                            tempDict[ele["idShort"]] = self.getProperty(ele)
                    elif elem["idShort"] =="WorkpieceProperties": 
                        for ele in elem["value"]:
                            if ele["idShort"] =="Dimensions":
                                for el in ele["value"]:
                                    tempDict[el["idShort"]] = self.getProperty(el)
                            else:
                                tempDict[ele["idShort"]] = self.getProperty(ele)      
        return tempDict                  
                    
    def capabilitycheck_Logic(self):
        """
            The actualy logic this state  goes into this method.
            It is upto the developer to add the relevant code.
        """
        self.submodel,status,statuscode = self.base_class.pyaas.dba.GetSubmodelById("https://example.com/ids/sm/4084_7040_1122_9091")
        tempDict1 = self.getPropertyList(self.submodel)
        tempDict = self.getPropertyList(self.base_class.WaitForCallForProposal_In['interactionElements'][0])

        try:
            if (tempDict["env"] !="live"):
                self.feasibilityCheck_Enabled = False
                self.base_class.skillLogger.info("Environment Error")
            else:       
                for key in list(tempDict1.keys()):
                    self.base_class.subModelTypes[key] = tempDict1[key]        
                
                for key in list(tempDict.keys()):
                    self.base_class.proposalSubmodelTypes[key] = tempDict[key]     
                    
                submodelTypeList = list(self.base_class.subModelTypes.keys())
                if len(list(self.base_class.proposalSubmodelTypes.keys())) == 0:
                    self.feasibilityCheck_Enabled = False
                    self.base_class.skillLogger.info("Not Equal number of property types")
                    
                for key in list(self.base_class.proposalSubmodelTypes.keys()):
                    if (key in ["MaxDistanceToPreferredVenueOfProvision","PreferredVenueOfProvision","deliveryTime"]):
                        pass                
                    elif key not in submodelTypeList:
                        self.feasibilityCheck_Enabled = False
                        self.base_class.skillLogger.info("one of the property missing" + str(key))
                        break
        except Exception as E:
            self.feasibilityCheck_Enabled = False
        
        if self.feasibilityCheck_Enabled:
            self.sendingNotUnderstood_Enabled = False
        else:
            self.feasibilityCheck_Enabled = False
        
    
    def run(self) -> None:
        """
            This method is first called form the base class after instantiating the
            class. The method executes the entire of the state.
        """
        self.base_class.skillLogger.info("\n #############################################################################")
        # StartState
        self.base_class.skillLogger.info("StartState: capabilitycheck")
        # InputDocumentType"
        InputDocument = "NA"
        self.base_class.skillLogger.info("InputDocument : " + InputDocument)
        
        self.capabilitycheck_Logic()
        
    def next(self) -> object:
        """
            This methods returns the object to the next state the needs
            to be executed by the base class
        """
        OutputDocument = "NA"
        self.base_class.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        
        if (self.sendingNotUnderstood_Enabled):
            self.base_class.skillLogger.info("Condition :" + "-")
            ts = sendingNotUnderstood(self.base_class)
            self.base_class.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.base_class.skillLogger.info("############################################################################# \n")
            return ts
        if (self.feasibilityCheck_Enabled):
            self.base_class.skillLogger.info("Condition :" + "-")
            ts = feasibilityCheck(self.base_class)
            self.base_class.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.base_class.skillLogger.info("############################################################################# \n")
            return ts
        
class serviceProvision:
    
    def __init__(self, base_class):
        """
        """
        self.base_class = base_class
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.sendinPropoposalporvisionConfirm_Enabled = True
        self.WaitForCallForProposal_Enabled = True
        self.plcHandler = self.base_class.pyaas.asset_access_handlers["OPCUA"]
        self.tdPropertiesList = self.base_class.shellObject.thing_description  
                

    def serviceProvision_Logic(self):
        """
            The actualy logic this state  goes into this method.
            It is upto the developer to add the relevant code.
        """
        try :
            #self.plcHandler.write(self.tdPropertiesList["sPermission"]["href"],"true")
            plcBoool = True
            while (plcBoool):
                time.sleep(20)
                sPermissionVariable = "FALSE"#self.plcHandler.read(self.tdPropertiesList["sPermission"]["href"])
                if  (sPermissionVariable.upper() =="FALSE"):
                    plcBoool = False
            self.WaitForCallForProposal_Enabled = False
        except Exception as E:
            self.sendinPropoposalporvisionConfirm_Enabled = False
            
    
    def run(self) -> None:
        """
            This method is first called form the base class after instantiating the
            class. The method executes the entire of the state.
        """
        self.base_class.skillLogger.info("\n #############################################################################")
        # StartState
        self.base_class.skillLogger.info("StartState: serviceProvision")
        # InputDocumentType"
        InputDocument = "NA"
        self.base_class.skillLogger.info("InputDocument : " + InputDocument)
        
        self.serviceProvision_Logic()
        
    def next(self) -> object:
        """
            This methods returns the object to the next state the needs
            to be executed by the base class
        """
        OutputDocument = "NA"
        self.base_class.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        
        if (self.sendinPropoposalporvisionConfirm_Enabled):
            self.base_class.skillLogger.info("Condition :" + "-")
            ts = sendinPropoposalporvisionConfirm(self.base_class)
            self.base_class.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.base_class.skillLogger.info("############################################################################# \n")
            return ts
        if (self.WaitForCallForProposal_Enabled):
            self.base_class.skillLogger.info("Condition :" + "-")
            ts = WaitForCallForProposal(self.base_class)
            self.base_class.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.base_class.skillLogger.info("############################################################################# \n")
            return ts
        
class PriceCalculation:
    
    def __init__(self, base_class):
        """
        """
        self.base_class = base_class
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.sendingProposal_Enabled = True
    

    def PriceCalculation_Logic(self):
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
        self.base_class.skillLogger.info("StartState: PriceCalculation")
        # InputDocumentType"
        InputDocument = "NA"
        self.base_class.skillLogger.info("InputDocument : " + InputDocument)
        
        self.PriceCalculation_Logic()
        
    def next(self) -> object:
        """
            This methods returns the object to the next state the needs
            to be executed by the base class
        """
        OutputDocument = "NA"
        self.base_class.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        
        if (self.sendingProposal_Enabled):
            self.base_class.skillLogger.info("Condition :" + "-")
            ts = sendingProposal(self.base_class)
            self.base_class.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.base_class.skillLogger.info("############################################################################# \n")
            return ts
        



class HoningProvider:
    '''
    classdocs
    '''

        
    def initstate_specific_queue_internal(self) -> None:
        """
        """
        self.QueueDict = {}
        
        self.sendingRefuse_Queue = Queue.Queue()
        self.sendinPropoposalporvisionConfirm_Queue = Queue.Queue()
        self.sendingNotUnderstood_Queue = Queue.Queue()
        self.feasibilityCheck_Queue = Queue.Queue()
        self.WaitForCallForProposal_Queue = Queue.Queue()
        self.waitingforServiceRequesterAnswer_Queue = Queue.Queue()
        self.sendingProposal_Queue = Queue.Queue()
        self.checkingSchedule_Queue = Queue.Queue()
        self.capabilitycheck_Queue = Queue.Queue()
        self.serviceProvision_Queue = Queue.Queue()
        self.PriceCalculation_Queue = Queue.Queue()
        
                
        self.QueueDict = {
              "callForProposal": self.WaitForCallForProposal_Queue,
              "acceptProposal": self.waitingforServiceRequesterAnswer_Queue,
              "rejectProposal": self.waitingforServiceRequesterAnswer_Queue,
            }
    
    def init_inbound_messages(self) -> None:
        self.waitingforServiceRequesterAnswer_In = {}
        self.WaitForCallForProposal_In = {}
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
                          "sendingRefuse": "sendingRefuse",  "sendinPropoposalporvisionConfirm": "sendinPropoposalporvisionConfirm",  "sendingNotUnderstood": "sendingNotUnderstood",  "feasibilityCheck": "feasibilityCheck",  "WaitForCallForProposal": "WaitForCallForProposal",  "waitingforServiceRequesterAnswer": "waitingforServiceRequesterAnswer",  "sendingProposal": "sendingProposal",  "checkingSchedule": "checkingSchedule",  "capabilitycheck": "capabilitycheck",  "serviceProvision": "serviceProvision",  "PriceCalculation": "PriceCalculation",
                       }
        
        self.pyaas = pyaas
        self.skillName = "HoningProvider"
        self.initstate_specific_queue_internal()
        self.init_inbound_messages()
        self.currentConversationId = "temp"
        
        self.enabledStatus = {"Y":True, "N":False}
        self.enabledState = "Y"
        
        self.semanticProtocol = ""
        self.initialState = ""
        self.skill_service = ""
        self.gen = Generic()
        self.productionStepSeq = []
        self.responseMessage = {}

        self.subModelTypes = {}
        self.proposalSubmodelTypes = {}


    def emptyAllQueues(self):
        waitingforServiceRequesterAnswerList = list(self.waitingforServiceRequesterAnswer_Queue.queue)
        for elem in range(0,len(waitingforServiceRequesterAnswerList)):
            self.waitingforServiceRequesterAnswer_Queue.get()

    def initInBoundMessages(self):
            self.WaitForCallForProposal_In = {}
            self.waitingforServiceRequesterAnswer_In = {}
        
    def start(self, msgHandler,shellObject,_uid) -> None:
        """
            Starting of the Skill state machine
        """
        self.msgHandler = msgHandler
        self.shellObject = shellObject
        self.aasID = shellObject.aasELement["id"]
        self._uid  = _uid
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
        
        WaitForCallForProposal_1 = WaitForCallForProposal(self)
        self.stateChange("WaitForCallForProposal")
        currentState = WaitForCallForProposal_1
        
        
        while (True):
            if ((currentState.__class__.__name__) == "WaitForCallForProposal"):
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
        self.msgHandler.putObMessage(sendMessage)
    
    def receiveMessage(self,inMessage) -> None:
        try:    
            _conversationId = str(inMessage['frame']['conversationId'])
            senderRole = str(inMessage["frame"]['sender']['role']["name"])
            _messageType = str(inMessage['frame']['type'])
            self.QueueDict[_messageType].put(inMessage)
        except Exception as E:
            pass#self.skillLogger.info("Raise an Exception " + str(E))



if __name__ == '__main__':
    
    lm2 = HoningProvider()
    lm2.Start('msgHandler')
