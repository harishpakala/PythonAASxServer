'''
Copyright (c) 2021-2022 OVGU LIA
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
'''
import copy
import uuid
from jsonschema import validate
from requests.utils import quote
try:
    from utils.i40data import Generic
except ImportError:
    from main.utils.i40data import Generic



class Immutable(object):
    def __setattr__(self, key, value):
        if not hasattr(self, key):
            super().__setattr__(key, value)
        else:
            raise RuntimeError(key + " is immutable")

class ExecuteDBModifier(object):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
            
    def executeModifer(self,instanceData):
        self.instanceId = instanceData["instanceId"]
        self.pyAAS.dataManager.pushInboundMessage({"functionType":1,"instanceid":instanceData["instanceId"],
                                                            "data":instanceData["data"],
                                                            "method":instanceData["method"]})
        vePool = True
        while(vePool):
            if (len(self.pyAAS.dataManager.outBoundProcessingDict.keys())!= 0):
                if (self.instanceId in list(self.pyAAS.dataManager.outBoundProcessingDict.keys())):
                    if (self.pyAAS.dataManager.outBoundProcessingDict[self.instanceId] != ""):
                        modiferResponse = self.pyAAS.dataManager.outBoundProcessingDict[self.instanceId]
                        del self.pyAAS.dataManager.outBoundProcessingDict[self.instanceId]
                        vePool = False
                        return modiferResponse
                    

class ProductionStepOrder(object):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
        self.gen = Generic() 

    def createTransportStepOrder(self,aasId,currentConvId):
        conversationId = currentConvId +"_1"
        self.pyAAS.dba.createNewConversation(conversationId)
        self.pyAAS.conversationInteractionList.append(conversationId)
        self.pyAAS.conversationIdList[aasId].append(conversationId) 
        if (len(self.pyAAS.conversationIdList) > 5 ):
            del self.pyAAS.conversationIdList[0] # if length of conversation id list is greater than 0 delete an element  
        return conversationId
    
    def createStepOrderConversation(self,aasId,conversationId):
        self.pyAAS.dba.createNewConversation(conversationId)
        self.pyAAS.conversationInteractionList.append(conversationId)
        self.pyAAS.conversationIdList[aasId].append(conversationId) 
        if (len(self.pyAAS.conversationIdList) > 5 ):
            del self.pyAAS.conversationIdList[0] # if length of conversation id list is greater than 0 delete an element  
        return conversationId    
        
    def createProductionStepOrder(self,aasId):
        conversationCount,status = self.pyAAS.dba.getMessageCount()
        conversationId = "ProductionOrder" +"_"+ str(int(conversationCount) + 1)  
        self.pyAAS.dba.createNewConversation(conversationId)
        self.pyAAS.conversationInteractionList.append(conversationId)
        self.pyAAS.conversationIdList[aasId].append(conversationId) 
        if (len(self.pyAAS.conversationIdList) > 5 ):
            del self.pyAAS.conversationIdList[0] # if length of conversation id list is greater than 0 delete an element  
                
        DataFrame =      {
                                "semanticProtocol": "update",
                                "type" : "ProductionOrder",
                                "messageId" : "ProductionOrder_"+str(int(conversationCount) + 2),
                                "SenderAASID" :  self.pyAAS.aasIndexidShortDict[aasId]["identificationId"],
                                "SenderRolename" : "WebInterface",
                                "conversationId" : conversationId,
                                "ReceiverAASID" :   self.pyAAS.aasIndexidShortDict[aasId]["identificationId"],
                                "ReceiverRolename" : "ProductionManager"
                            }
        
        frame = self.gen.createFrame(DataFrame)
        self.I40OutBoundMessage = {"frame": frame,"interactionElements":[]}            
        self.pyAAS.msgHandler.putIbMessage(self.I40OutBoundMessage)
        return conversationId

    def createRegistrationStep(self,aasId):
        conversationCount,status = self.pyAAS.dba.getMessageCount()
        conversationId = "RegistrationOrder" +"_"+ str(int(conversationCount) + 1)  
        self.pyAAS.dba.createNewConversation(conversationId)
        self.pyAAS.conversationInteractionList.append(conversationId)
        #append the new conversation to the conversationId List
        self.pyAAS.conversationIdList[aasId].append(conversationId) 
        if (len(self.pyAAS.conversationIdList) > 5 ):
            del self.pyAAS.conversationIdList[0] # if length of conversation id list is greater than 0 delete an element  
                
        DataFrame =      {
                                    "semanticProtocol": "www.admin-shell.io/interaction/registerOrder",
                                    "type" : "Order",
                                    "messageId" : "Order"+"_"+str(int(conversationCount) + 2),
                                    "SenderAASID" :  self.pyAAS.aasIndexidShortDict[aasId]["identificationId"],
                                    "SenderRolename" : "RegistrationOrder",
                                    "conversationId" :conversationId,
                                    "ReceiverAASID" :   self.pyAAS.aasIndexidShortDict[aasId]["identificationId"],
                                    "ReceiverRolename" : "Register"
                                }
        
        frame = self.gen.createFrame(DataFrame)
        self.I40OutBoundMessage = {"frame": frame,"interactionElements":[]}            
        self.pyAAS.msgHandler.putIbMessage(self.I40OutBoundMessage)
        return conversationId

class AASDescriptor(object):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def createAASDescriptorElement(self,desc,aasDescriptor,aasxData):
        try:
            aasDescriptor[desc] = aasxData[desc]
        except Exception as E:
            aasDescriptor[desc] = None
            self.pyAAS.serviceLogger.info("Error at AASDescriptor.createAASDescriptorElement Rest" + str(E))
        return aasDescriptor

    def createSubmodelDescriptorElement(self,desc,sumodelDescriptor,submodel):
        try:
            sumodelDescriptor[desc] = submodel[desc]
        except:
            pass
        return sumodelDescriptor

    def createSubmodelDescriptorElementSemanticId(self,desc,submodel):
        semanticList = []
        try:
            for key in submodel["semanticId"]["keys"]:
                semanticList.append(key["value"])
        except:
            pass
        desc["semanticId"] =  {"value" : []}
        desc["semanticId"]["value"] =  semanticList
        
        return desc    
    
    def createndPoint(self,desc,interface):
        endPoint =    {"protocolInformation":{
                                "endpointAddress" : desc,
                                "endpointProtocol" : "http",
                                        "endpointProtocol": None,
                                        "endpointProtocolVersion": None,
                                        "subprotocol": None,
                                        "subprotocolBody": None,
                                        "subprotocolBodyEncoding": None
                                },
                        "interface": interface
                        }
        return endPoint
    
    
    def createDescriptor(self,aasxIndex):
        _shellId = self.pyAAS.aasIndexidShortDict[aasxIndex]["identificationId"]
        _id = self.pyAAS.aasHashDict.__getHashEntry__(_shellId).__getId__()
        _aasShell = self.pyAAS.aasShellHashDict.__getHashEntry__(_id).aasELement
        aasDescriptor = {}
        
        descList = ["idShort","description"]
        for desc in descList:
            aasDescriptor = self.createAASDescriptorElement(desc,aasDescriptor,_aasShell)
        try:
            aasDescriptor["identification"] =  _aasShell["identification"]["id"]
        except:
            aasDescriptor["identification"] = None
            
        ip = str(self.pyAAS.lia_env_variable["LIA_AAS_ADMINSHELL_CONNECT_IP"])
        port = str(self.pyAAS.lia_env_variable["LIA_AAS_RESTAPI_PORT_EXTERN"])
        descString = "http://"+ip+":"+port+"/shells/"+ quote(aasDescriptor["identification"], safe='')
        endpointsList = []

        endpointsList.append(self.createndPoint(descString, "AAS-1.0")) 
        if (self.pyAAS.lia_env_variable["LIA_PREFEREDI40ENDPOINT"] == "MQTT"):
            pass
        else:        
            endpointsList.append(self.createndPoint("http://"+ip+":"+port+"/i40commu","communication"))  
          
        aasDescriptor["endpoints"]  =  endpointsList
        submodelDescList = []
        submodels,status = self.pyAAS.dba.getSubmodelsbyShell(_shellId)
        for key,submodel in submodels.items():
            sumodelDescriptor = {}
            for desc in descList:
                sumodelDescriptor = self.createSubmodelDescriptorElement(desc, sumodelDescriptor, submodel)
            
            try:
                sumodelDescriptor["identification"]  = submodel["identification"]["id"]
            except:
                sumodelDescriptor["identification"]  = None
            sumodelDescriptor = self.createSubmodelDescriptorElementSemanticId(sumodelDescriptor,  submodel)
            submodeldescString = "http://"+ip+":"+port+"/submodels/"+str(quote(sumodelDescriptor["identification"], safe=''))+"/submodel"
            sumodelDescriptor["endpoints"]  = [self.createndPoint(submodeldescString,"SUBMODEL-1.0")] 
            submodelDescList.append(sumodelDescriptor)
        
        aasDescriptor["submodelDescriptors"] = submodelDescList
        return aasDescriptor

class DescriptorValidator(object):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def valitdateAASDescriptor(self,aasDescData):
        try :
            aasDescSchema = self.pyAAS.aasConfigurer.aasDescSchema
            if(not validate(instance = aasDescData, schema= aasDescSchema)):
                return True
            else:
                return False
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at DescriptorValidator.valitdateAASDescriptor Rest" + str(E))
            return False
    
    def valitdateSubmodelDescriptor(self,submodelDescData):
        try :
            submodelDescSchema = self.pyAAS.aasConfigurer.submodelDescSchema
            if(not validate(instance = submodelDescData, schema= submodelDescSchema)):
                return True
            else:
                return False
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at DescriptorValidator.valitdateSubmodelDescriptor Rest" + str(E))
            return False

class AASMetaModelValidator(object):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def validateAASShell(self,aasShellData):
        try :
            aasShell_JsonSchema = self.pyAAS.aasConfigurer.aasShell_JsonSchema
            if(not validate(instance = aasShellData, schema= aasShell_JsonSchema)):
                return True
            else:
                return False
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at AASMetaModelValidator.validateAASShell Rest" + str(E))
            return False

    
    def valitdateAAS(self,aasData):
        try :
            aasJsonSchema = self.pyAAS.aasConfigurer.aasJsonSchema
            if(not validate(instance = aasData, schema= aasJsonSchema)):
                return True
            else:
                return False
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at AASMetaModelValidator.valitdateAAS Rest" + str(E))
            return False
    
    def valitdateSubmodel(self,submodelData):
        try :
            submodelJsonSchema = self.pyAAS.aasConfigurer.submodelJsonSchema
            if(not validate(instance = submodelData, schema= submodelJsonSchema)):
                return True
            else:
                return False
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at AASMetaModelValidator.valitdateSubmodel Rest" + str(E))
            return False
    
    def validateProperty(self,propertData):
        pass
    
    def validateRange(self,rangeData):
        pass
    
    def validateSubmodelCollection(self,submodelCollectionData):
        pass
    
    def validateMultiLanguageProperty(self,MultiLanguagePropertyData):
        pass
    
    
    def valitdateAsset(self,assetData):
        try :
            assetJsonSchema = self.pyAAS.aasConfigurer.assetJsonSchema
            if(not validate(instance = {"assets": assetData}, schema= assetJsonSchema)):
                return True
            else:
                return False
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at AASMetaModelValidator.valitdateAsset Rest" + str(E))
            return False       
        
    def validateConceptDescription(self,conceptDescriptionData):
        try :
            conceptDescriptionJsonSchema = self.pyAAS.aasConfigurer.conceptDescriptionJsonSchema
            if(not validate(instance = conceptDescriptionData, schema= conceptDescriptionJsonSchema)):
                return True
            else:
                return False
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at AASMetaModelValidator.validateConceptDescription Rest" + str(E))
            return False         

    def validateSubmodelElement(self,SubmodelElementData):
        try :
            SubmodelElementJsonSchema = self.pyAAS.aasConfigurer.SubmodelElementJsonSchema
            if(not validate(instance = SubmodelElementData, schema= SubmodelElementJsonSchema)):
                return True
            else:
                return False
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at AASMetaModelValidator.validateSubmodelElement Rest" + str(E))
            return False  

    def validatevalidateAASShellSubmodelRef(self,AASShellSubmodelRefData):
        try :
            AASShellSubmodelRefJsonSchema = self.pyAAS.aasConfigurer.AASShellSubmodelRefJsonSchema
            if(not validate(instance = AASShellSubmodelRefData, schema= AASShellSubmodelRefJsonSchema)):
                return True
            else:
                return False
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at AASMetaModelValidator.validatevalidateAASShellSubmodelRef Rest" + str(E))
            return False    

class ExecuteDBRetriever(object):
    def __init__(self,pyAAS):
        self.instanceId = str(uuid.uuid1())
        self.pyAAS = pyAAS
            
    def execute(self,instanceData):
        self.pyAAS.dataManager.pushInboundMessage({"functionType":1,"instanceid":self.instanceId,
                                                            "data":instanceData["data"],
                                                            "method":instanceData["method"]})
        vePool = True
        while(vePool):
            if (len(self.pyAAS.dataManager.outBoundProcessingDict.keys())!= 0):
                if (self.pyAAS.dataManager.outBoundProcessingDict[self.instanceId] != ""):
                    response = self.pyAAS.dataManager.outBoundProcessingDict[self.instanceId]
                    del self.pyAAS.dataManager.outBoundProcessingDict[self.instanceId]
                    vePool = False
        return response

class HTTPResponse(object):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def createExceptionResponse(self,send_Message):
        messageType = send_Message["frame"]["type"]
        smP = send_Message["frame"]["semanticProtocol"]["keys"][0]["value"]
        receiver = send_Message["frame"]["receiver"]["role"]["name"]
        I40FrameData = {
                                "semanticProtocol": smP,
                                "type" : messageType+"_"+str(self.pyAAS.dba.getMessageCount()["message"][0]+1),
                                "messageId" : "registerAck_1",
                                "SenderAASID" : self.pyAAS.AASID,
                                "SenderRolename" : "HTTP_ENDPoint",
                                "conversationId" : "AASNetworkedBidding",                               
                                "ReceiverAASID" :  self.pyAAS.AASID,
                                "ReceiverRolename" : receiver
                        }
        self.gen = Generic()
        self.frame = self.gen.createFrame(I40FrameData)
        
        self.InElem = self.pyAAS.dba.getAAsSubmodelsbyId(self.pyAAS.AASID,"StatusResponse")["message"][0]
        
        self.InElem["submodelElements"][0]["value"] = "E"
        self.InElem["submodelElements"][1]["value"] = "E009. delivery-error"
        self.InElem["submodelElements"][2]["value"] = "Unable to send the message to the target server"
         
        registerAckMessage ={"frame": self.frame,
                                "interactionElements":[self.InElem]}
        return registerAckMessage
       
class AASHashObject(object):
    def __init__(self,_id):
        self._id = _id
        self.subscribers = set()
        self.lastUpdateTime = ""
        self.newUpdate = False
    
    def __getId__(self):
        return self._id
    
    def __addSubscriber__(self,subscriber):
        self.subscribers.add(subscriber)
    
    def __removeSubscriber__(self,subscriber):
        self.subscribers.remove(subscriber)
    
    def __getSubcriberList__(self):
        return self.subscribers
    
class HashDict(object):
    def __init__(self):
        super().__init__()
        self.hashDict = dict()
        self.elementCount = 0
    
    def getElementCount(self):
        return self.elementCount
    
    def __insertHashEntry__(self,key,hashObject):
        self.elementCount = self.elementCount + 1
        self.hashDict[key] = hashObject
    
    def __deleteHashEntry__(self,key):
        self.elementCount = self.elementCount - 1
        del self.hashDict[key]
    
    def __getHashEntry__(self,key):
        return self.hashDict[key] 
    
    def _getKeys(self):
        return list(self.hashDict.keys())


class HistoryObject(object):
    def __init__(self,timestamp,aasELemObject):
        self.timestamp = timestamp
        self.aasELemObject = aasELemObject
    
    def modfiyElemObject(self,nAasELemObject):
        self.aasELemObject = nAasELemObject


class UUIDGenerator(object):
    def __init__(self):
        pass
    def getnewUUID(self):
        return str(uuid.uuid4())  
    
class AASElementObject(object):
    def __init__(self,aasElement,idShortPath,elemIndex=0):
        self.aasELement = aasElement
        self.elementIdList = []
        self.history = []
        self.idShortPath = idShortPath
        self.elementIndex = elemIndex
        
    def __addhistoryElement(self,historyObject:HistoryObject):
        if (not self.__isPrimitive__()):
            self.history.append(historyObject)
    
    def __clearHistory(self):
        self.history = []
    
    def __getHistory(self):
        return self.history
    
    def __getLatestHistory(self,topLen):
        return self.history[-topLen:]
    
    def __getBottomHistory(self,bottomLen):
        return self.history[0:bottomLen]

    def __getChildIds(self):
        return self.elementIdList
        
    def __insertChildElem(self,childId):
        self.elementIdList.append(childId)
    
    def __getChild(self):
        return self.elementIdList
    
    def __isPrimitive__(self):
        return True if len(self.elementIdList) == 0 and self.aasELement["modelType"]["name"] != "SubmodelElementCollection" else False
    
    def getElement(self): 
        _tempElement = copy.deepcopy(self.aasELement)
        return _tempElement
    
    def getIdShortPath(self):
        return self.idShortPath

class SubscriptionMessage(object):
    def __init__(self,elementPath,updateTime,modelType,subscribers,subscriptiondata):
        self.elementPath = elementPath
        self.subscribers = subscribers
        self.updateTime = updateTime
        self.modelType = modelType
        self.subscriptiondata = subscriptiondata
    
        

class ConversationObject(object):
    def __init__(self,_coversationId):
        self._coversationId = _coversationId
        self.messages = []
    
    def _insertMessage(self,messageType,messageId,direction,message,entryTime,SenderAASID):
        _message = {
                        "messageType" : messageType,
                        "message_Id" : messageId,
                        "message" : message,
                        "direction" : direction,
                        "entryTime": entryTime,
                        "SenderAASID":SenderAASID
                    }
        self.messages.append(_message)     
        
    
    def _getMessages(self,identificationId):
        returnData = {"inbound":[],"outbound":[],"internal":[]}
        for message in self.messages:
            if (message["SenderAASID"] == "Broadcast" or message["SenderAASID"] == identificationId ):
                if (message["direction"] == "inbound"):
                    returnData["inbound"].append(message["message"]["frame"]["messageId"]+":"+message["entryTime"])
                elif(message["direction"] == "outbound"):
                    returnData["outbound"].append(message["message"]["frame"]["messageId"]+":"+message["entryTime"])
                elif(message["direction"] == "internal"):
                    returnData["internal"].append(message["message"]["frame"]["messageId"]+":"+message["entryTime"])                
        return returnData
    
    def _getMessage(self,messageId):
        for message in self.messages:
            if message["message_Id"] ==  messageId:
                return message, True
        return "Empty", "Error" 
    
    def _getMessageCount(self):
        return len(self.messages)
    
    def _deleteMessage(self,messageId):        
        pass# not impelmented

class StandardSubmodelData(object):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
        self.extHost = self.pyAAS.lia_env_variable["LIA_AAS_RESTAPI_DOMAIN_EXTERN"]
        self.port = self.pyAAS.lia_env_variable["LIA_AAS_RESTAPI_PORT_INTERN"]
    
    def parse(self,aasElement,mlp):
        if (aasElement["modelType"]["name"] == "Property"):
            return aasElement["value"]
        if (aasElement["modelType"]["name"] == "MultiLanguageProperty"):
            for langString in aasElement["value"]["langString"]:
                if langString["language"].upper() == mlp:
                    return langString["text"]
            return ""
        if (aasElement["modelType"]["name"] == "File"):
            return  "http://"+self.extHost+":"+str(self.port)+"/static/"+aasElement["value"].split("/")[-1]
        
    def execute(self,data,mlp=None):
        for key,value in data.items():
            if type(value) == dict:
                temp = self.execute(value)
                data[key] = temp
            else:
                if isinstance(value, AASElementObject):
                    data[key] = self.parse(value.aasELement,mlp)
                else:
                    data[key] = value
        return data