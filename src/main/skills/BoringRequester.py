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
try:
    from utils.utils import ExecuteDBModifier,ProductionStepOrder
except ImportError:
    from main.utils.utils import ExecuteDBModifier,ProductionStepOrder
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
        "SenderRolename" : "BoringRequester",
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
    
class WaitforTransportOrderCompletion:
    
    def __init__(self, base_class):
        """
        """
        self.base_class = base_class
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.WaitforInformConfirm_Enabled = True
        self.sendCompletionResponse_Enabled = True
    
    def retrieve_WaitforTransportOrderCompletion_Message(self) -> None:
        """
            Method to retrieve the inbound i4.0 message from the relevant queue.
            The retrieved message is assigned to the dictionary variabel designed
            in the base clase. The Variable and the queue name are based on the 
            current state.
        """
        self.base_class.WaitforTransportOrderCompletion_In = self.base_class.WaitforTransportOrderCompletion_Queue.get()
    
    def saveMessage(self) -> None:
        """
            Method to save the message into the database
        """
        inboundQueueList = list(self.base_class.WaitforTransportOrderCompletion_Queue.queue) # in case for further processing is required
        # else creation of the new queue is not required.
        for i in range (0, self.base_class.WaitforTransportOrderCompletion_Queue.qsize()):
            message = inboundQueueList[i]
            self.instanceId = str(uuid.uuid1())
            self.base_class.pyaas.dataManager.pushInboundMessage({"functionType":3,"instanceid":self.instanceId,
                                                            "conversationId":message["frame"]["conversationId"],
                                                            "messageType":message["frame"]["type"],
                                                            "messageId":message["frame"]["messageId"],
                                                            "direction": "inbound",
                                                            "SenderAASID" : message["frame"]["sender"]["id"],
                                                            "message":message})
            

    def WaitforTransportOrderCompletion_Logic(self):
        """
            The actualy logic this state  goes into this method.
            It is upto the developer to add the relevant code.
        """
        try:
            statusMessage = self.base_class.WaitforTransportOrderCompletion_In["interactionElements"][0]
            statusResponse = statusMessage["submodelElements"][0]["value"]
            if (statusResponse == "E"):
                self.base_class.responseMessage["status"] = "E"
                self.base_class.responseMessage["code"] = statusMessage["submodelElements"][1]["value"]
                self.base_class.responseMessage["message"] =  statusMessage["submodelElements"][2]["value"]
                self.WaitforInformConfirm_Enabled = False
            else:
                self.sendCompletionResponse_Enabled = False
        except Exception as e:
            self.base_class.responseMessage["status"] = "E"
            self.base_class.responseMessage["code"] = "E.014"
            self.base_class.responseMessage["message"] =  "Error Processing the Order"
            self.WaitforInformConfirm_Enabled = False
                
    
    def run(self) -> None:
        """
            This method is first called form the base class after instantiating the
            class. The method executes the entire of the state.
        """
        self.base_class.skillLogger.info("\n #############################################################################")
        # StartState
        self.base_class.skillLogger.info("StartState: WaitforTransportOrderCompletion")
        # InputDocumentType"
        InputDocument = "OrderStatus"
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
            while (((self.base_class.WaitforTransportOrderCompletion_Queue).qsize()) == 0):
                time.sleep(1)
                i = i + 1 
                if i > 120: # Time to wait the next incoming message
                    self.messageExist = False # If the waiting time expires, the loop is broken
                    break
            if (self.messageExist):
                self.saveMessage() # in case we need to store the incoming message
                self.retrieve_WaitforTransportOrderCompletion_Message() # in case of multiple inbound messages this function should 
                                                      # not be invoked. 
        self.WaitforTransportOrderCompletion_Logic()
        
    def next(self) -> object:
        """
            This methods returns the object to the next state the needs
            to be executed by the base class
        """
        OutputDocument = "NA"
        self.base_class.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        
        if (self.WaitforInformConfirm_Enabled):
            self.base_class.skillLogger.info("Condition :" + "-")
            ts = WaitforInformConfirm(self.base_class)
            self.base_class.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.base_class.skillLogger.info("############################################################################# \n")
            return ts
        if (self.sendCompletionResponse_Enabled):
            self.base_class.skillLogger.info("Condition :" + "-")
            ts = sendCompletionResponse(self.base_class)
            self.base_class.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.base_class.skillLogger.info("############################################################################# \n")
            return ts
        
class WaitforNewOrder:
    
    def __init__(self, base_class):
        """
        """
        self.base_class = base_class
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.cfpConfiguration_Enabled = True
    
    
    def retrieve_WaitforNewOrder_Message(self) -> None:
        """
            Method to retrieve the inbound i4.0 message from the relevant queue.
            The retrieved message is assigned to the dictionary variabel designed
            in the base clase. The Variable and the queue name are based on the 
            current state.
        """
        self.base_class.WaitforNewOrder_In = self.base_class.WaitforNewOrder_Queue.get()
    
    def saveMessage(self) -> None:
        """
            Method to save the message into the database
        """
        inboundQueueList = list(self.base_class.WaitforNewOrder_Queue.queue) # in case for further processing is required
        # else creation of the new queue is not required.
        for i in range (0, self.base_class.WaitforNewOrder_Queue.qsize()):
            message = inboundQueueList[i]
            self.instanceId = str(uuid.uuid1())
            self.base_class.pyaas.dataManager.pushInboundMessage({"functionType":3,"instanceid":self.instanceId,
                                                            "conversationId":message["frame"]["conversationId"],
                                                            "messageType":message["frame"]["type"],
                                                            "messageId":message["frame"]["messageId"],
                                                            "direction": "inbound",
                                                            "SenderAASID" : message["frame"]["sender"]["id"],
                                                            "message":message})
            

    def WaitforNewOrder_Logic(self):
        """
            The actualy logic this state  goes into this method.
            It is upto the developer to add the relevant code.
        """
        startTime = datetime.now()
        self.base_class.pyaas.dba.setInitialValue(self.base_class.WaitforNewOrder_In["frame"]["conversationId"],
                             self.base_class.skillName,startTime)
    
    def run(self) -> None:
        """
            This method is first called form the base class after instantiating the
            class. The method executes the entire of the state.
        """
        self.base_class.skillLogger.info("\n #############################################################################")
        # StartState
        self.base_class.skillLogger.info("StartState: WaitforNewOrder")
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
            sys.stdout.write(" Waiting for response")
            sys.stdout.flush()
            while (((self.base_class.WaitforNewOrder_Queue).qsize()) == 0):
                time.sleep(1)
            if (self.messageExist):
                self.saveMessage() # in case we need to store the incoming message
                self.retrieve_WaitforNewOrder_Message() # in case of multiple inbound messages this function should 
                                                        # not be invoked. 
        self.WaitforNewOrder_Logic()
        
    def next(self) -> object:
        """
            This methods returns the object to the next state the needs
            to be executed by the base class
        """
        OutputDocument = "NA"
        self.base_class.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        
        if (self.cfpConfiguration_Enabled):
            self.base_class.skillLogger.info("Condition :" + "-")
            ts = cfpConfiguration(self.base_class)
            self.base_class.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.base_class.skillLogger.info("############################################################################# \n")
            return ts
        
class cfpConfiguration:
    
    def __init__(self, base_class):
        """
        """
        self.base_class = base_class
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.sendCompletionResponse_Enabled = True
        self.SendCFP_Enabled = True
    

    def cfpConfiguration_Logic(self):
        """
            The actual logic this state  goes into this method.
            It is upto the developer to add the relevant code.
        """
        if (len(self.base_class.WaitforNewOrder_In["interactionElements"]) == 2):
            Identifier1 = self.base_class.WaitforNewOrder_In["interactionElements"][0]
            Identifier2 = self.base_class.WaitforNewOrder_In["interactionElements"][1]
            submodel1,status,statuscode = self.base_class.pyaas.dba.GetSubmodelById(Identifier1[0])
            submodel2,status,statuscode = self.base_class.pyaas.dba.GetSubmodelById(Identifier2[0])
            
            if status and status:
                if (submodel1["semanticId"]["keys"][0]["value"] == "0173-1#01-AKG243#015"):
                    if (submodel2["semanticId"]["keys"][0]["value"] == "0173-1#01-ADR740#004"):
                        self.sendCompletionResponse_Enabled = False
                    else:
                        self.base_class.responseMessage["status"] = "E"
                        self.base_class.responseMessage["code"] = "E.01"
                        self.base_class.responseMessage["message"] =  "The Transport submodel is not provided."
                        self.SendCFP_Enabled = False
                elif (submodel2["semanticId"]["keys"][0]["value"] == "0173-1#01-AKG243#015"):
                    if (submodel1["semanticId"]["keys"][0]["value"] == "0173-1#01-ADR740#004"):
                        self.base_class.WaitforNewOrder_In["interactionElements"][0] = Identifier2
                        self.base_class.WaitforNewOrder_In["interactionElements"][1] = Identifier1
                        self.sendCompletionResponse_Enabled = False
                    else:
                        self.base_class.responseMessage["status"] = "E"
                        self.base_class.responseMessage["code"] = "E.01"
                        self.base_class.responseMessage["message"] =  "The Transport submodel is not provided."
                        self.SendCFP_Enabled = False
                else: 
                    self.base_class.responseMessage["status"] = "E"
                    self.base_class.responseMessage["code"] = "E.01"
                    self.base_class.responseMessage["message"] =  "The boring submodel is not provided."
                    self.SendCFP_Enabled = False
            else:
                self.base_class.responseMessage["status"] = "E"
                self.base_class.responseMessage["code"] = "E.01"
                self.base_class.responseMessage["message"] =  "Error retriving the submodels"
                self.SendCFP_Enabled = False
        else:
            self.base_class.responseMessage["status"] = "E"
            self.base_class.responseMessage["code"] = "E.01"
            self.base_class.responseMessage["message"] =  "Enough number of submodel Id's are not provided"
            self.SendCFP_Enabled = False
    
    def run(self) -> None:
        """
            This method is first called form the base class after instantiating the
            class. The method executes the entire of the state.
        """
        self.base_class.skillLogger.info("\n #############################################################################")
        # StartState
        self.base_class.skillLogger.info("StartState: cfpConfiguration")
        # InputDocumentType"
        InputDocument = "NA"
        self.base_class.skillLogger.info("InputDocument : " + InputDocument)
        
        self.cfpConfiguration_Logic()
        
    def next(self) -> object:
        """
            This methods returns the object to the next state the needs
            to be executed by the base class
        """
        OutputDocument = "NA"
        self.base_class.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        
        if (self.sendCompletionResponse_Enabled):
            self.base_class.skillLogger.info("Condition :" + "-")
            ts = sendCompletionResponse(self.base_class)
            self.base_class.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.base_class.skillLogger.info("############################################################################# \n")
            return ts
        if (self.SendCFP_Enabled):
            self.base_class.skillLogger.info("Condition :" + "-")
            ts = SendCFP(self.base_class)
            self.base_class.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.base_class.skillLogger.info("############################################################################# \n")
            return ts
        
class sendTransportOrder:
    
    def __init__(self, base_class):
        """
        """
        self.base_class = base_class
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.WaitforTransportOrderCompletion_Enabled = True
    

    def sendTransportOrder_Logic(self):
        """
            The actualy logic this state  goes into this method.
            It is upto the developer to add the relevant code.
        """
        try:
            #acceptproposalMessageList = list(self.base_class.sendacceptProposal_Queue.queue) # in case for further processing is required
            acceptproposalMessage = self.base_class.acceptProposal#acceptproposalMessageList[0]
            
            for submodelElem in acceptproposalMessage["interactionElements"][0]["submodelElements"]:
                if (submodelElem['idShort'] == 'CommercialProperties'):
                    for value in submodelElem["value"]:
                        if value['idShort'] == "workStationLocation":
                            self.TargetLocation = value["value"]               
        except Exception as e:
            print("Error ", str(e))
        i = 0
        j = 0
        k = 0
        transportIdentifier = self.base_class.WaitforNewOrder_In["interactionElements"][1][0]
        self.TransportSubmodel,status,statuscode = self.base_class.pyaas.dba.GetSubmodelById(transportIdentifier)
        for submodelElem in self.TransportSubmodel["submodelElements"]:
            if (submodelElem["idShort"] == "TechnicalProperties"):
                for valueELem in submodelElem["value"]:
                    if (valueELem["idShort"] == "FunctionalProperties"):
                        for specifierElem in valueELem["value"]:
                            if (specifierElem["idShort"] == "targetLocation"):
                                self.TransportSubmodel["submodelElements"][i]["value"][j]["value"][k]["value"] = self.TargetLocation
                            k = k + 1
                    j = j + 1
            i = i + 1
 
        try:
            edm = ExecuteDBModifier(self.base_class.pyaas)
            data,status,statuscode = edm.execute({"data":{"submodelIdentifier":self.TransportSubmodel["id"], "_submodel":self.TransportSubmodel},
                                                            "method": "PutSubmodelById",
                                                                "instanceId" : str(uuid.uuid1())})
            
        except Exception as e:
            self.base_class.skillLogger.info("Error" + str(e))   
        
    def create_Outbound_Message(self) -> list:
        """
            The method is used to create the outbound I4.0 messages.
            The message type is carried from the json file.
        """
        self.oMessages = "Order".split("/")
        outboundMessages = []
        for oMessage in self.oMessages:
            message = self.base_class.WaitforNewOrder_In
            self.gen = Generic()
            #receiverId = "" # To be decided by the developer
            #receiverRole = "" # To be decided by the developer
            
            # For broadcast message the receiverId and the 
            # receiverRole could be empty 
            psp = ProductionStepOrder(self.base_class.pyaas)
            currentConvId = message["frame"]["conversationId"]
            # For the return reply these details could be obtained from the inbound Message
            receiverId = message["frame"]["sender"]["id"]
            receiverRole = "TransportRequester"
            
            # For sending the message to an internal skill
            # The receiver Id should be
            
            I40FrameData =      {
                                    "semanticProtocol": self.base_class.semanticProtocol,
                                    "type" : oMessage,
                                    "messageId" : oMessage+"_"+str(self.base_class.pyaas.dba.getMessageCount()[0]+1),
                                    "SenderAASID" : self.base_class.aasID,
                                    "SenderRolename" : "BoringRequester",
                                    "conversationId" : psp.createTransportStepOrder(self.base_class.aasID,currentConvId),
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
            
            #submodel,status,statuscode = self.base_class.pyaas.dba.GetSubmodelById("submodelIdentifier")
            oMessage_Out ={"frame": self.frame,
                                    "interactionElements":[self.base_class.WaitforNewOrder_In["interactionElements"][1]]}
            self.instanceId = str(uuid.uuid1())
            self.base_class.pyaas.dataManager.pushInboundMessage({"functionType":3,"instanceid":self.instanceId,
                                                            "conversationId":oMessage_Out["frame"]["conversationId"],
                                                            "messageType":oMessage_Out["frame"]["type"],
                                                            "messageId":oMessage_Out["frame"]["messageId"],
                                                            "direction" : "outbound",
                                                            "SenderAASID" : message["frame"]["sender"]["id"],
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
        self.base_class.skillLogger.info("StartState: sendTransportOrder")
        # InputDocumentType"
        InputDocument = "NA"
        self.base_class.skillLogger.info("InputDocument : " + InputDocument)
        
        self.sendTransportOrder_Logic()
        
    def next(self) -> object:
        """
            This methods returns the object to the next state the needs
            to be executed by the base class
        """
        OutputDocument = "Order"
        self.base_class.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        if (OutputDocument != "NA"):
            self.outboundMessages = self.create_Outbound_Message()
            for outbMessage in self.outboundMessages:
                self.base_class.sendMessage(outbMessage)
        
        if (self.WaitforTransportOrderCompletion_Enabled):
            self.base_class.skillLogger.info("Condition :" + "-")
            ts = WaitforTransportOrderCompletion(self.base_class)
            self.base_class.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.base_class.skillLogger.info("############################################################################# \n")
            return ts
        
class noProposalReceived:
    
    def __init__(self, base_class):
        """
        """
        self.base_class = base_class
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.sendCompletionResponse_Enabled = True
    

    def noProposalReceived_Logic(self):
        """
            The actualy logic this state  goes into this method.
            It is upto the developer to add the relevant code.
        """
        self.base_class.responseMessage["status"] = "E"
        self.base_class.responseMessage["code"] = "E.06"
        self.base_class.responseMessage["message"] =  "No proposals received from any of the Service Providers"
    
    def run(self) -> None:
        """
            This method is first called form the base class after instantiating the
            class. The method executes the entire of the state.
        """
        self.base_class.skillLogger.info("\n #############################################################################")
        # StartState
        self.base_class.skillLogger.info("StartState: noProposalReceived")
        # InputDocumentType"
        InputDocument = "NA"
        self.base_class.skillLogger.info("InputDocument : " + InputDocument)
        
        self.noProposalReceived_Logic()
        
    def next(self) -> object:
        """
            This methods returns the object to the next state the needs
            to be executed by the base class
        """
        OutputDocument = "NA"
        self.base_class.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        
        if (self.sendCompletionResponse_Enabled):
            self.base_class.skillLogger.info("Condition :" + "-")
            ts = sendCompletionResponse(self.base_class)
            self.base_class.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.base_class.skillLogger.info("############################################################################# \n")
            return ts
        
class sendrejectProposal:
    
    def __init__(self, base_class):
        """
        """
        self.base_class = base_class
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.sendCompletionResponse_Enabled = True
        self.sendacceptProposal_Enabled = True
    

    def sendrejectProposal_Logic(self):
        """
            The actualy logic this state  goes into this method.
            It is upto the developer to add the relevant code.
        """
        if (self.base_class.sendacceptProposal_Queue.qsize() == 0):
            self.sendacceptProposal_Enabled = False
            self.base_class.responseMessage["status"] = "E"
            self.base_class.responseMessage["code"] = "E.06"
            self.base_class.responseMessage["message"] =  "None of the provider is selected."           
        else:
            self.sendCompletionResponse_Enabled = False
        
    def create_Outbound_Message(self) -> list:
        """
            The method is used to create the outbound I4.0 messages.
            The message type is carried from the json file.
        """
        self.oMessages = "rejectProposal".split("/")
        outboundMessages = []
        for oMessage in self.oMessages:
            message = self.base_class.sendrejectProposal_Queue.get()
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
    
            oMessage_Out = {"frame": self.frame,"interactionElements":[]}
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
                                                            "SenderAASID" : message["frame"]["sender"]["id"],
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
        self.base_class.skillLogger.info("StartState: sendrejectProposal")
        # InputDocumentType"
        InputDocument = "NA"
        self.base_class.skillLogger.info("InputDocument : " + InputDocument)
        
        self.sendrejectProposal_Logic()
        
    def next(self) -> object:
        """
            This methods returns the object to the next state the needs
            to be executed by the base class
        """
        OutputDocument = "rejectProposal"
        self.base_class.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        if (OutputDocument != "NA"):
            if (self.base_class.sendrejectProposal_Queue).qsize() > 0:
                self.outboundMessages = self.create_Outbound_Message()
                for outbMessage in self.outboundMessages:
                    self.base_class.sendMessage(outbMessage)
        
        if (self.sendCompletionResponse_Enabled):
            self.base_class.skillLogger.info("Condition :" + "-")
            ts = sendCompletionResponse(self.base_class)
            self.base_class.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.base_class.skillLogger.info("############################################################################# \n")
            return ts
        if (self.sendacceptProposal_Enabled):
            self.base_class.skillLogger.info("Condition :" + "-")
            ts = sendacceptProposal(self.base_class)
            self.base_class.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.base_class.skillLogger.info("############################################################################# \n")
            return ts
        
class sendacceptProposal:
    
    def __init__(self, base_class):
        """
        """
        self.base_class = base_class
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.sendTransportOrder_Enabled = True

    def sendacceptProposal_Logic(self):
        """
            The actualy logic this state  goes into this method.
            It is upto the developer to add the relevant code.
        """
        pass
    
    def create_Outbound_Message(self) -> list:
        """
            The method is used to create the outbound I4.0 messages.
            The message type is carried from the json file.
        """
        self.oMessages = "acceptProposal".split("/")
        outboundMessages = []
        for oMessage in self.oMessages:
            message = self.base_class.sendacceptProposal_Queue.get()
            self.base_class.acceptProposal = message
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
    
            oMessage_Out = {"frame": self.frame,"interactionElements":[]}
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
                                                            "SenderAASID" : message["frame"]["sender"]["id"],
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
        self.base_class.skillLogger.info("StartState: sendacceptProposal")
        # InputDocumentType"
        InputDocument = "NA"
        self.base_class.skillLogger.info("InputDocument : " + InputDocument)
        
        self.sendacceptProposal_Logic()
        
    def next(self) -> object:
        """
            This methods returns the object to the next state the needs
            to be executed by the base class
        """
        OutputDocument = "acceptProposal"
        self.base_class.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        if (OutputDocument != "NA"):
            self.outboundMessages = self.create_Outbound_Message()
            for outbMessage in self.outboundMessages:
                self.base_class.sendMessage(outbMessage)
        
        if (self.sendTransportOrder_Enabled):
            self.base_class.skillLogger.info("Condition :" + "-")
            ts = sendTransportOrder(self.base_class)
            self.base_class.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.base_class.skillLogger.info("############################################################################# \n")
            return ts
        
class WaitForSPProposal:
    
    def __init__(self, base_class):
        """
        """
        self.base_class = base_class
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.noProposalReceived_Enabled = True
        self.EvaluateProposal_Enabled = True
    
    def retrieve_WaitForSPProposal_Message(self) -> None:
        """
            Method to retrieve the inbound i4.0 message from the relevant queue.
            The retrieved message is assigned to the dictionary variabel designed
            in the base clase. The Variable and the queue name are based on the 
            current state.
        """
        self.base_class.WaitForSPProposal_In = self.base_class.WaitForSPProposal_Queue.get()
    
    def saveMessage(self) -> None:
        """
            Method to save the message into the database
        """
        inboundQueueList = list(self.base_class.WaitForSPProposal_Queue.queue) # in case for further processing is required
        # else creation of the new queue is not required.
        for i in range (0, self.base_class.WaitForSPProposal_Queue.qsize()):
            message = inboundQueueList[i]
            self.instanceId = str(uuid.uuid1())
            self.base_class.pyaas.dataManager.pushInboundMessage({"functionType":3,"instanceid":self.instanceId,
                                                            "conversationId":message["frame"]["conversationId"],
                                                            "messageType":message["frame"]["type"],
                                                            "messageId":message["frame"]["messageId"],
                                                            "direction": "inbound",
                                                            "SenderAASID" : message["frame"]["sender"]["id"],
                                                            "message":message})
            

    def WaitForSPProposal_Logic(self):
        """
            The actualy logic this state  goes into this method.
            It is upto the developer to add the relevant code.
        """
        if (self.messageExist):
            self.noProposalReceived_Enabled = False
        else:
            self.EvaluateProposal_Enabled = False
    
    
    def run(self) -> None:
        """
            This method is first called form the base class after instantiating the
            class. The method executes the entire of the state.
        """
        self.base_class.skillLogger.info("\n #############################################################################")
        # StartState
        self.base_class.skillLogger.info("StartState: WaitForSPProposal")
        # InputDocumentType"
        InputDocument = "proposal"
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
            while (((self.base_class.WaitForSPProposal_Queue).qsize()) == 0):
                time.sleep(1)
                i = i + 1 
                if i > 30: # Time to wait the next incoming message
                    self.messageExist = False # If the waiting time expires, the loop is broken
                    break
            if (self.messageExist):
                self.saveMessage() # in case we need to store the incoming message
                #self.retrieve_WaitForSPProposal_Message() # in case of multiple inbound messages this function should 
                                                      # not be invoked. 
        self.WaitForSPProposal_Logic()
        
    def next(self) -> object:
        """
            This methods returns the object to the next state the needs
            to be executed by the base class
        """
        OutputDocument = "NA"
        self.base_class.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        
        if (self.noProposalReceived_Enabled):
            self.base_class.skillLogger.info("Condition :" + "-")
            ts = noProposalReceived(self.base_class)
            self.base_class.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.base_class.skillLogger.info("############################################################################# \n")
            return ts
        if (self.EvaluateProposal_Enabled):
            self.base_class.skillLogger.info("Condition :" + "-")
            ts = EvaluateProposal(self.base_class)
            self.base_class.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.base_class.skillLogger.info("############################################################################# \n")
            return ts
        
class EvaluateProposal:
    
    def __init__(self, base_class):
        """
        """
        self.base_class = base_class
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.sendrejectProposal_Enabled = True

    def getItem(self,submodelElement,Item_Name) -> int:
        for value in submodelElement["value"]:
            if value['idShort'] == Item_Name:
                return int(value['value'])     

    def EvaluateProposal_Logic(self):
        """
            The actualy logic this state  goes into this method.
            It is upto the developer to add the relevant code.
        """
        try:
            proposlList = []
            ListPrice_CFP = [] 
            qsize = self.base_class.WaitForSPProposal_Queue.qsize()
            for i in range (0,qsize):
                proposlList.append(self.base_class.WaitForSPProposal_Queue.get())
            for eachPorposal in proposlList:
                for submodelElement in eachPorposal['interactionElements'][0]['submodelElements']:
                    if (submodelElement['idShort'] == 'CommercialProperties'):
                        ListPrice_CFP.append([self.getItem(submodelElement,"cfp"),self.getItem(submodelElement,"listprice")])
            
            qoutes = []
            
            for lsp in ListPrice_CFP:
                qoutes.append(lsp[0] + lsp[1])
                
            bestPrice = min(qoutes)
            bestPriceIndex = qoutes.index(bestPrice)  
            self.base_class.CFP = ListPrice_CFP[bestPriceIndex][0]        
            for i  in range(0,len(proposlList)):
                if (i == bestPriceIndex):
                    self.base_class.sendacceptProposal_Queue.put(proposlList[i])
                else:
                    self.base_class.sendrejectProposal_Queue.put(proposlList[i])
        except Exception as e:
            self.base_class.skillLogger.info("Evaluate Proposal Error" + str(e))
        
    
    def run(self) -> None:
        """
            This method is first called form the base class after instantiating the
            class. The method executes the entire of the state.
        """
        self.base_class.skillLogger.info("\n #############################################################################")
        # StartState
        self.base_class.skillLogger.info("StartState: EvaluateProposal")
        # InputDocumentType"
        InputDocument = "NA"
        self.base_class.skillLogger.info("InputDocument : " + InputDocument)
        
        self.EvaluateProposal_Logic()
        
    def next(self) -> object:
        """
            This methods returns the object to the next state the needs
            to be executed by the base class
        """
        OutputDocument = "NA"
        self.base_class.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        
        if (self.sendrejectProposal_Enabled):
            self.base_class.skillLogger.info("Condition :" + "-")
            ts = sendrejectProposal(self.base_class)
            self.base_class.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.base_class.skillLogger.info("############################################################################# \n")
            return ts
        
class WaitforInformConfirm:
    
    def __init__(self, base_class):
        """
        """
        self.base_class = base_class
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.sendCompletionResponse_Enabled = True
    
    def retrieve_WaitforInformConfirm_Message(self) -> None:
        """
            Method to retrieve the inbound i4.0 message from the relevant queue.
            The retrieved message is assigned to the dictionary variabel designed
            in the base clase. The Variable and the queue name are based on the 
            current state.
        """
        self.base_class.WaitforInformConfirm_In = self.base_class.WaitforInformConfirm_Queue.get()
    
    def saveMessage(self) -> None:
        """
            Method to save the message into the database
        """
        inboundQueueList = list(self.base_class.WaitforInformConfirm_Queue.queue) # in case for further processing is required
        # else creation of the new queue is not required.
        for i in range (0, self.base_class.WaitforInformConfirm_Queue.qsize()):
            message = inboundQueueList[i]
            self.instanceId = str(uuid.uuid1())
            self.base_class.pyaas.dataManager.pushInboundMessage({"functionType":3,"instanceid":self.instanceId,
                                                            "conversationId":message["frame"]["conversationId"],
                                                            "messageType":message["frame"]["type"],
                                                            "messageId":message["frame"]["messageId"],
                                                            "direction": "inbound",
                                                            "SenderAASID" : message["frame"]["sender"]["id"],
                                                            "message":message})
            

    def WaitforInformConfirm_Logic(self):
        """
            The actualy logic this state  goes into this method.
            It is upto the developer to add the relevant code.
        """
        self.base_class.responseMessage["status"] = "S"
        self.base_class.responseMessage["code"] = "A.013"
        self.base_class.responseMessage["message"] =  "The Order is Succesfully Executed."        
            
    
    def run(self) -> None:
        """
            This method is first called form the base class after instantiating the
            class. The method executes the entire of the state.
        """
        self.base_class.skillLogger.info("\n #############################################################################")
        # StartState
        self.base_class.skillLogger.info("StartState: WaitforInformConfirm")
        # InputDocumentType"
        InputDocument = "informConfirm"
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
            while (((self.base_class.WaitforInformConfirm_Queue).qsize()) == 0):
                time.sleep(1)
                i = i + 1 
                if i > 60: # Time to wait the next incoming message
                    self.messageExist = False # If the waiting time expires, the loop is broken
                    break
            if (self.messageExist):
                self.saveMessage() # in case we need to store the incoming message
                self.retrieve_WaitforInformConfirm_Message() # in case of multiple inbound messages this function should 
                                                      # not be invoked. 
        self.WaitforInformConfirm_Logic()
        
    def next(self) -> object:
        """
            This methods returns the object to the next state the needs
            to be executed by the base class
        """
        OutputDocument = "NA"
        self.base_class.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        
        if (self.sendCompletionResponse_Enabled):
            self.base_class.skillLogger.info("Condition :" + "-")
            ts = sendCompletionResponse(self.base_class)
            self.base_class.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.base_class.skillLogger.info("############################################################################# \n")
            return ts
        
class sendCompletionResponse:
    
    def __init__(self, base_class):
        """
        """
        self.base_class = base_class
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.WaitforNewOrder_Enabled = True
    
    def set_cfp_properties(self,conversationId,_cfp):
        endTime = datetime.now()
        self.base_class.pyaas.dba.setFinalProperties(conversationId,
                             endTime,_cfp)


    def sendCompletionResponse_Logic(self):
        """
            The actualy logic this state  goes into this method.
            It is upto the developer to add the relevant code.
        """
        self.InElem = self.base_class.StatusResponseSM
        self.InElem[0]["submodelElements"][0]["value"] = self.base_class.responseMessage["status"]
        self.InElem[0]["submodelElements"][1]["value"] = self.base_class.responseMessage["code"]
        self.InElem[0]["submodelElements"][2]["value"] = self.base_class.responseMessage["message"]
        self.set_cfp_properties(self.base_class.WaitforNewOrder_In["frame"]["conversationId"],
                                self.base_class.CFP)
        self.base_class.responseMessage = {}
        
    def create_Outbound_Message(self) -> list:
        """
            The method is used to create the outbound I4.0 messages.
            The message type is carried from the json file.
        """
        self.oMessages = "OrderStatus".split("/")
        outboundMessages = []
        for oMessage in self.oMessages:
            message = self.base_class.WaitforNewOrder_In
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
            
            #submodel,status,statuscode = self.base_class.pyaas.dba.GetSubmodelById("submodelIdentifier")
            oMessage_Out = {"frame": self.frame,
                                "interactionElements":self.InElem}
            self.instanceId = str(uuid.uuid1())
            self.base_class.pyaas.dataManager.pushInboundMessage({"functionType":3,"instanceid":self.instanceId,
                                                            "conversationId":oMessage_Out["frame"]["conversationId"],
                                                            "messageType":oMessage_Out["frame"]["type"],
                                                            "messageId":oMessage_Out["frame"]["messageId"],
                                                            "direction" : "outbound",
                                                            "SenderAASID" : message["frame"]["sender"]["id"],
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
        self.base_class.skillLogger.info("StartState: sendCompletionResponse")
        # InputDocumentType"
        InputDocument = "NA"
        self.base_class.skillLogger.info("InputDocument : " + InputDocument)
        
        self.sendCompletionResponse_Logic()
        
    def next(self) -> object:
        """
            This methods returns the object to the next state the needs
            to be executed by the base class
        """
        OutputDocument = "OrderStatus"
        self.base_class.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        if (OutputDocument != "NA"):
            self.outboundMessages = self.create_Outbound_Message()
            for outbMessage in self.outboundMessages:
                self.base_class.sendMessage(outbMessage)
        
        if (self.WaitforNewOrder_Enabled):
            self.base_class.skillLogger.info("Condition :" + "-")
            ts = WaitforNewOrder(self.base_class)
            self.base_class.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.base_class.skillLogger.info("############################################################################# \n")
            return ts
        
class SendCFP:
    
    def __init__(self, base_class):
        """
        """
        self.base_class = base_class
        
        #Transition to the next state is enabled using the targetState specific Boolen Variable
        # for each target there will be a separate boolean variable
                
        self.WaitForSPProposal_Enabled = True
    

    def SendCFP_Logic(self):
        """
            The actualy logic this state  goes into this method.
            It is upto the developer to add the relevant code.
        """
        
    def create_Outbound_Message(self) -> list:
        """
            The method is used to create the outbound I4.0 messages.
            The message type is carried from the json file.
        """
        self.oMessages = "callForProposal".split("/")
        outboundMessages = []
        for oMessage in self.oMessages:
            message = self.base_class.WaitforNewOrder_In
            self.gen = Generic()
            receiverId = "" # To be decided by the developer
            receiverRole = "" # To be decided by the developer
            
            # For broadcast message the receiverId and the 
            # receiverRole could be empty 
            
            # For the return reply these details could be obtained from the inbound Message
            #receiverId = message["frame"]["sender"]["id"]
            #receiverRole = "BoringProvider"#message["frame"]["sender"]["role"]["name"]
            
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
            
            submodelIdentifier = message["interactionElements"][0][0]
            submodel,status,statuscode = self.base_class.pyaas.dba.GetSubmodelById(submodelIdentifier)
            oMessage_Out ={"frame": self.frame,
                                    "interactionElements":[submodel]}
            self.instanceId = str(uuid.uuid1())
            self.base_class.pyaas.dataManager.pushInboundMessage({"functionType":3,"instanceid":self.instanceId,
                                                            "conversationId":oMessage_Out["frame"]["conversationId"],
                                                            "messageType":oMessage_Out["frame"]["type"],
                                                            "messageId":oMessage_Out["frame"]["messageId"],
                                                            "direction" : "outbound",
                                                            "SenderAASID" : message["frame"]["sender"]["id"],
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
        self.base_class.skillLogger.info("StartState: SendCFP")
        # InputDocumentType"
        InputDocument = "NA"
        self.base_class.skillLogger.info("InputDocument : " + InputDocument)
        
        self.SendCFP_Logic()
        
    def next(self) -> object:
        """
            This methods returns the object to the next state the needs
            to be executed by the base class
        """
        OutputDocument = "callForProposal"
        self.base_class.skillLogger.info("OutputDocumentType : " + OutputDocument)
        
        if (OutputDocument != "NA"):
            self.outboundMessages = self.create_Outbound_Message()
            for outbMessage in self.outboundMessages:
                self.base_class.sendMessage(outbMessage)
        
        if (self.WaitForSPProposal_Enabled):
            self.base_class.skillLogger.info("Condition :" + "-")
            ts = WaitForSPProposal(self.base_class)
            self.base_class.skillLogger.info("TargettState: " + ts.__class__.__name__)
            self.base_class.skillLogger.info("############################################################################# \n")
            return ts
        



class BoringRequester:
    '''
    classdocs
    '''

        
    def initstate_specific_queue_internal(self) -> None:
        """
        """
        self.QueueDict = {}
        
        self.WaitforTransportOrderCompletion_Queue = Queue.Queue()
        self.WaitforNewOrder_Queue = Queue.Queue()
        self.cfpConfiguration_Queue = Queue.Queue()
        self.sendTransportOrder_Queue = Queue.Queue()
        self.noProposalReceived_Queue = Queue.Queue()
        self.sendrejectProposal_Queue = Queue.Queue()
        self.sendacceptProposal_Queue = Queue.Queue()
        self.WaitForSPProposal_Queue = Queue.Queue()
        self.EvaluateProposal_Queue = Queue.Queue()
        self.WaitforInformConfirm_Queue = Queue.Queue()
        self.sendCompletionResponse_Queue = Queue.Queue()
        self.SendCFP_Queue = Queue.Queue()
        
                
        self.QueueDict = {
              "OrderStatus": self.WaitforTransportOrderCompletion_Queue,
              "Order": self.WaitforNewOrder_Queue,
              "proposal": self.WaitForSPProposal_Queue,
              "informConfirm": self.WaitforInformConfirm_Queue,
            }
    
    def init_inbound_messages(self) -> None:
        self.WaitforInformConfirm_In = {}
        self.WaitforNewOrder_In = {}
        self.WaitForSPProposal_In = {}
        self.WaitforTransportOrderCompletion_In = {}
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
                          "WaitforTransportOrderCompletion": "WaitforTransportOrderCompletion",  "WaitforNewOrder": "WaitforNewOrder",  "cfpConfiguration": "cfpConfiguration",  "sendTransportOrder": "sendTransportOrder",  "noProposalReceived": "noProposalReceived",  "sendrejectProposal": "sendrejectProposal",  "sendacceptProposal": "sendacceptProposal",  "WaitForSPProposal": "WaitForSPProposal",  "EvaluateProposal": "EvaluateProposal",  "WaitforInformConfirm": "WaitforInformConfirm",  "sendCompletionResponse": "sendCompletionResponse",  "SendCFP": "SendCFP",
                       }
        
        self.pyaas = pyaas
        self.skillName = "BoringRequester"
        self.initstate_specific_queue_internal()
        self.init_inbound_messages()
        self.currentConversationId = "temp"
        
        self.enabledStatus = {"Y":True, "N":False}
        self.enabledState = "Y"
        
        self.semanticProtocol = "www.admin-shell.io/interaction/bidding"
        self.initialState = "WaitforNewOrder"
        self.skill_service = "Boring Requisition"
        self.gen = Generic()
        self.productionStepSeq = []
        self.responseMessage = {}
        self.StatusResponseSM = [self.pyaas.aasConfigurer.getStatusResponseSubmodel()]
        self.acceptProposal = {}
        self.CFP = 0
        self.cfp_uid = ""
        
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
        
        WaitforNewOrder_1 = WaitforNewOrder(self)
        #self.stateChange("WaitforNewOrder")
        currentState = WaitforNewOrder_1
        
        
        while (True):
            if ((currentState.__class__.__name__) == "WaitforNewOrder"):
                if(self.enabledState):
                    currentState.run()
                    ts = currentState.next()
                    #self.stateChange(ts.__class__.__name__)
                    currentState = ts
                else:
                    time.sleep(1)
            else:
                currentState.run()
                ts = currentState.next()
                if not (ts):
                    break
                else:
                    #self.stateChange(ts.__class__.__name__)
                    currentState = ts
    
    def geCurrentSKILLState(self) -> str:
        return self.SKILL_STATE
    
    def getListofSKILLStates(self) -> list:
        return self.SKILL_STATES
    
    
    def stateChange(self, STATE) -> None:
        #self.statusMessage["interactionElements"][0]["submodelElements"][0]["value"] = "I"
        #self.statusMessage["interactionElements"][0]["submodelElements"][1]["value"] = "A006. internal-status-change"
        #self.statusMessage["interactionElements"][0]["submodelElements"][2]["value"] = str(datetime.now()) +" "+STATE
        pass#self.sendMessage(self.statusMessage)
    
    def sendMessage(self, sendMessage) -> None:
        self.msgHandler.putObMessage(sendMessage)
    
    def receiveMessage(self,inMessage) -> None:
        try:    
            _conversationId = str(inMessage['frame']['conversationId'])
            senderRole = str(inMessage["frame"]['sender']['role']["name"])
            _messageType = str(inMessage['frame']['type'])
            if (_messageType == "proposal"):
                self.QueueDict[_messageType].put(inMessage)
            else:
                self.QueueDict[_messageType].put(inMessage)
        except Exception as E:
            pass#self.skillLogger.info("Raise an Exception " + str(E))



if __name__ == '__main__':
    
    lm2 = BoringRequester()
    lm2.Start('msgHandler')
