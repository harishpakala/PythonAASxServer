"""
Copyright (c) 2023 Otto-von-Guericke-Universitaet Magdeburg, Lehrstuhl Integrierte Automation
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
"""

from copy import deepcopy
from jsonschema import validate
import base64
import copy
import uuid

#from Cryptodome.PublicKey import RSA
#from Cryptodome.IO import PEM
#from jwkest.jws import JWSig, SIGNER_ALGS, JWS
#from jwkest.jwk import rsa_load, RSAKey,pem_cert2rsa,der_cert2rsa,der2rsa
#from jwkest.jwt import b64encode_item

try:
    from utils.i40data import Generic
except ImportError:
    from main.utils.i40data import Generic

try:
    from utils.aaslog import ServiceLogHandler,LogList
except ImportError:
    from main.utils.aaslog import ServiceLogHandler,LogList

try:
    from models.aastypes import Submodel,Property,SubmodelElementCollection
except ImportError:
    from main.models.aastypes import Submodel,Property,SubmodelElementCollection


class Immutable:
    def __setattr__(self, key, value):
        if not hasattr(self, key):
            super().__setattr__(key, value)
        else:
            raise RuntimeError(key + " is immutable")


class ExecuteDBModifier(object):
    def __init__(self, pyaas):
        self.pyaas = pyaas

    def execute(self, instance_data) -> tuple:
        """
            Executes the database server method specific in the arguments and returns the response
        """
        try:
            instance_id = instance_data["instanceId"]
            self.pyaas.dataManager.pushInboundMessage({"functionType": 1, "instanceid": instance_id,
                                                       "data": instance_data["data"],
                                                       "method": instance_data["method"]})
            pool = True
            while pool:
                if len(self.pyaas.dataManager.outBoundProcessingDict.keys()) != 0:
                    if instance_id in list(self.pyaas.dataManager.outBoundProcessingDict.keys()):
                        if self.pyaas.dataManager.outBoundProcessingDict[instance_id] != "":
                            modifier_response = self.pyaas.dataManager.outBoundProcessingDict[instance_id]
                            del self.pyaas.dataManager.outBoundProcessingDict[instance_id]
                            pool = False
                            return modifier_response
        except SystemError as e:
            self.serviceLogger.info(
                "Error executing the database method " + str(e)
            )
            return "Internal Server Error", False, 500



class ProductionStepOrder:
    def __init__(self, pyaas,aasIdentifier):
        self.pyaas = pyaas
        self.gen = Generic(aasIdentifier,"ProductionManager","ovgu.de/ordermanagement")

    def createTransportStepOrder(self, aasIdentifier, current_conv_id) -> str:
        """

        """
        conversation_id = current_conv_id + "_1"
        self.pyaas.dba.createNewConversation(conversation_id)
        self.pyaas.conversationInteractionList.append(conversation_id)
        
        _uuid = self.pyaas.aasHashDict.__getHashEntry__(aasIdentifier)._id
        shellObject = self.pyaas.aasShellHashDict.__getHashEntry__(_uuid)
        shellObject.add_conversationId(conversation_id)
            
        return conversation_id

    def createStepOrderConversation(self, aasId, conversation_id) -> str:
        """

        """
        _uid = self.pyaas.aasHashDict.__getHashEntry__(aasId).__getId__()
        aasShellObject = self.pyaas.aasShellHashDict.__getHashEntry__(_uid)
        
        self.pyaas.dba.createNewConversation(conversation_id)
        self.pyaas.conversationInteractionList.append(conversation_id)
        aasShellObject.add_conversationId(conversation_id)
        return conversation_id

    def createNewCFPObject(self):
        for convId in self.conversationIdList:
            self.baseClass.pyaas.dba.createNewCFPObject(convId)
    
    def addsubConversationIdsList(self,conversation_id,productionStepList):
        consList = []
        for i in range(0,len(productionStepList)):
            _conv = conversation_id+"_"+str(len(productionStepList)-i)
            consList.append(_conv)
            for j in range(0,len(productionStepList[i]["submodel_id_idSHort_list"])-1):
                __conv = _conv +"_"+str(j+1) 
                consList.append(__conv)
                
        self.pyaas.dba.insertSubCovsersationIds(consList,conversation_id)

        self.pyaas.dba.createNewCFPObject(conversation_id)
        for _id in consList:
            self.pyaas.dba.createNewCFPObject(_id)

    def createProductionStepOrder(self, aasIdentifier) -> (str,bool):
        """

        """
        
        try:
            conversation_count, status = self.pyaas.dba.getMessageCount()
            conversation_id = "ProductionOrder" + "_" + str(int(conversation_count) + 1)
            self.pyaas.dba.createNewConversation(conversation_id)
            self.pyaas.conversationInteractionList.append(conversation_id)
                
            _uuid = self.pyaas.aasHashDict.__getHashEntry__(aasIdentifier)._id
            shellObject = self.pyaas.aasShellHashDict.__getHashEntry__(_uuid)
            shellObject.add_conversationId(conversation_id)
            
            self.addsubConversationIdsList(conversation_id,shellObject.productionStepList)
            i40_message = self.gen.create_i40_message("ProductionOrder",conversation_id,aasIdentifier,"ProductionManager")
            self.pyaas.msgHandler.putIbMessage(i40_message)
            
            return conversation_id, True
        except Exception as e:
            return str(e), False
        
    def createRegistrationStep(self, aas_id) -> str:
        """

        """
        conversation_count, status = self.pyaas.dba.getMessageCount()
        conversation_id = "RegistrationOrder" + "_" + str(int(conversation_count) + 1)
        self.pyaas.dba.createNewConversation(conversation_id)
        self.pyaas.conversationInteractionList.append(conversation_id)
        i40_message = self.gen.create_i40_message("Order",conversation_id,aas_id,"Register")
        
        self.pyaas.msgHandler.putIbMessage(i40_message)
        return conversation_id
    
    def createProductionOrder(self,productionStepList):
        uuidG = UUIDGenerator()
        _uuid = uuidG.getnewUUID()
        submodelId = "ww.ovgu.de/submodel/"+str(_uuid)
        _submodel = Submodel(submodelId)
        for productionStep in productionStepList:
            _capability = SubmodelElementCollection("")
            for info in productionStep:
                _property = Property("")
                _property.value = ""
                _capability.value.append(_property)
            _submodel.submodelElements.append(_capability)
        
        return _submodel.serialize_json()

class AASDescriptor:
    def __init__(self, pyaas):
        self.pyaas = pyaas

    def get_descriptor_string(self) -> str:
        ip = str(self.pyaas.lia_env_variable["LIA_AAS_RESTAPI_DOMAIN_EXTERN"])
        port = str(self.pyaas.lia_env_variable["LIA_AAS_RESTAPI_PORT_EXTERN"])
        if  self.pyaas.lia_env_variable["LIA_SECURITY_ENABLED"] == "Y":
            return "https://" + ip + ":" + port
        else: 
            return "http://" + ip + ":" + port
        
    def createSubmodelDescriptorElementSemanticId(self, desc, submodel) -> dict():
        """

        """
        semanticList = []
        try:
            for key in submodel["semanticId"]["keys"]:
                semanticList.append(key["value"])
        except:
            pass
        desc["semanticId"] = {"value": []}
        desc["semanticId"]["value"] = semanticList

        return desc

    def createndPoint(self, desc, interface):
        endPoint = {"protocolInformation": {
            "endpointAddress": desc,
            "endpointProtocol": "http",
            "endpointProtocolVersion": "",
            "subprotocol": "",
            "subprotocolBody": "",
            "subprotocolBodyEncoding": "",
            "securityAttributes": ""
        },
            "interface": interface
        }
        if  self.pyaas.lia_env_variable["LIA_SECURITY_ENABLED"] == "Y":
            endPoint["protocolInformation"]["endpointProtocol"] = "https"

        return endPoint

    def createDescriptor(self, _shellId):
        _id = self.pyaas.aasHashDict.__getHashEntry__(_shellId).__getId__()
        _aasShell = self.pyaas.aasShellHashDict.__getHashEntry__(_id).aasELement
        aasDescriptor = dict()

        if ("id" in _aasShell.keys()):
            aasDescriptor["id"] = _aasShell["id"]
        else:
            aasDescriptor["id"] = None

        if ("idShort" in _aasShell.keys()):
            aasDescriptor["idShort"] = _aasShell["idShort"]
        else:
            aasDescriptor["id"] = None

        if ("administration" in _aasShell.keys()):
            aasDescriptor["administration"] = _aasShell["administration"]

        if ("description" in _aasShell.keys()):
            aasDescriptor["description"] = _aasShell["description"]    
        
        if ("assetInformation" in _aasShell.keys()):
            if "globalAssetId" in ( _aasShell["assetInformation"]).keys():
                aasDescriptor["globalAssetId"] = _aasShell["assetInformation"]["globalAssetId"]

            if "specificAssetIds" in ( _aasShell["assetInformation"]).keys():
                aasDescriptor["specificAssetIds"] = _aasShell["assetInformation"]["specificAssetIds"]            
        
        endpointsList = []

        endpointsList.append(self.createndPoint(self.get_descriptor_string()+ "/shells/" +  str(base64.b64encode(aasDescriptor["id"].encode()).decode()), "AAS-1.0"))
        endpointsList.append(self.createndPoint(self.get_descriptor_string()+ "/shells/" +  str(base64.b64encode(aasDescriptor["id"].encode()).decode()) +"/webui", "AAS-1.0"))
        
        if (self.pyaas.lia_env_variable["LIA_PREFEREDI40ENDPOINT"] == "MQTT"):
            pass
        else:
            endpointsList.append(self.createndPoint(self.get_descriptor_string() + "/i40commu", "communication"))

        aasDescriptor["endpoints"] = endpointsList
        
        submodelDescList = []
        submodels, status,statuscode = self.pyaas.dba.getSubmodelsbyShell(_shellId)
        for _submodel in submodels:
            sumodelDescriptor = {}
           
            if ("id" in _submodel.keys()):
                sumodelDescriptor["id"] = _submodel["id"]
            else:
                sumodelDescriptor["id"] = None
    
            #if ("administration" in _submodel.keys()):
            #    sumodelDescriptor["administration"] = _submodel["administration"]
    
            if ("description" in _submodel.keys()):
                sumodelDescriptor["description"] = _submodel["description"]    

            if ("semanticId" in _submodel.keys()):
                sumodelDescriptor["semanticId"] = _submodel["semanticId"]

            sumodelDescriptor["endpoints"] = [self.createndPoint(self.get_descriptor_string() + "/submodels/" +
                                              str(base64.b64encode(sumodelDescriptor["id"].encode()).decode())  + "/submodel", "SUBMODEL-1.0"),
                                              self.createndPoint(self.get_descriptor_string() +  "/shells/" +  str(base64.b64encode(aasDescriptor["id"].encode()).decode()) +"/aas/submodels/" +
                                              str(base64.b64encode(sumodelDescriptor["id"].encode()).decode())  + "/submodel/webui", "SUBMODEL-1.0")]
            submodelDescList.append(sumodelDescriptor)

        aasDescriptor["submodelDescriptors"] = submodelDescList
        return aasDescriptor


class AASMetaModelValidator:
    def __init__(self, pyaas):
        self.pyaas = pyaas

    def validateAASShell(self, aasShellData) -> bool:
        """
        """        
        try:
            aasShell_JsonSchema = self.pyaas.aasConfigurer.aasShell_JsonSchema
            if (not validate(instance=aasShellData, schema=aasShell_JsonSchema)):
                return True
            else:
                return False
        except Exception as e:
            # self.pyaas.serviceLogger.info("Error at AASMetaModelValidator.validateAASShell Rest" + str(E))
            return False

    def valitdateAAS(self, aasData) -> bool:
        """
        """        
        try:
            aasJsonSchema = self.pyaas.aasConfigurer.aasJsonSchema
            if (not validate(instance=aasData, schema=aasJsonSchema)):
                return True
            else:
                return False
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at AASMetaModelValidator.valitdateAAS Rest" + str(E))
            return False

    def valitdateSubmodel(self, submodelData) -> bool:
        """
        """
        try:
            submodelJsonSchema = self.pyaas.aasConfigurer.submodelJsonSchema
            if (not validate(instance=submodelData, schema=submodelJsonSchema)):
                return True
            else:
                return False
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at AASMetaModelValidator.valitdateSubmodel Rest" + str(E))
            return False

    def valitdateAssetInformation(self, assetInformation) -> bool:
        """
        """        
        try:
            assetInformation_JsonSchema = self.pyaas.aasConfigurer.assetInformation_JsonSchema
            if (not validate(instance=assetInformation, schema=assetInformation_JsonSchema)):
                return True
            else:
                return False
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at AASMetaModelValidator.valitdateAssetInformation Rest" + str(E))
            return False

    def validateConceptDescription(self, conceptDescriptionData) -> bool:
        """
        """        
        try:
            conceptDescriptionJsonSchema = self.pyaas.aasConfigurer.conceptDescription_JsonSchema
            if (not validate(instance=conceptDescriptionData, schema=conceptDescriptionJsonSchema)):
                return True
            else:
                return False
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at AASMetaModelValidator.validateConceptDescription Rest" + str(E))
            return False

    def validateSubmodelElement(self, SubmodelElementData) -> bool:
        """
        """
        try:
            if 'modelType' in list(SubmodelElementData.keys()):
                modelType = SubmodelElementData['modelType']
                if modelType not in ["Submodel", "AssetAdministrationShell", "ConceptDescription"]:
                    SubmodelElementJsonSchema = deepcopy(self.pyaas.aasConfigurer.aasJsonSchema)
                    SubmodelElementJsonSchema["allOf"][0]["$ref"] = "#/definitions/" + modelType
                    if (not validate(instance=SubmodelElementData, schema=SubmodelElementJsonSchema)):
                        return True
                    else:
                        return False
                else:
                    return False
            else:
                return False
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at AASMetaModelValidator.validateSubmodelElement Rest" + str(E))
            return False

    def validateAASShellSubmodelRef(self, AASShellSubmodelRefData) -> bool:
        """
        """        
        try:
            reference_JsonSchema = self.pyaas.aasConfigurer.reference_JsonSchema
            if (not validate(instance=AASShellSubmodelRefData, schema=reference_JsonSchema)):
                return True
            else:
                return False
        except Exception as E:
            self.pyaas.serviceLogger.info(
                "Error at AASMetaModelValidator.validatevalidateAASShellSubmodelRef Rest" + str(E))
            return False


class ExecuteDBRetriever:
    def __init__(self, pyaas):
        self.instanceId = str(uuid.uuid1())
        self.pyaas = pyaas

    def execute(self, instanceData) -> (str,bool):
        """
        """
        self.pyaas.dataManager.pushInboundMessage({"functionType": 1, "instanceid": self.instanceId,
                                                   "data": instanceData["data"],
                                                   "method": instanceData["method"]})
        vePool = True
        response = "Error",False
        while (vePool):
            if (len(self.pyaas.dataManager.outBoundProcessingDict.keys()) != 0):
                if (self.pyaas.dataManager.outBoundProcessingDict[self.instanceId] != ""):
                    response = self.pyaas.dataManager.outBoundProcessingDict[self.instanceId]
                    del self.pyaas.dataManager.outBoundProcessingDict[self.instanceId]
                    vePool = False
        return response


class HTTPResponse:
    def __init__(self, pyaas):
        self.pyaas = pyaas

    def createExceptionResponse(self, send_Message) -> dict:
        """
        """
        messageType = send_Message["frame"]["type"]
        smP = send_Message["frame"]["semanticProtocol"]["keys"][0]["value"]
        receiver = send_Message["frame"]["receiver"]["role"]["name"]
        I40FrameData = {
            "semanticProtocol": smP,
            "type": messageType + "_" + str(self.pyaas.dba.getMessageCount()["message"][0] + 1),
            "messageId": "registerAck_1",
            "SenderAASID": self.pyAAS.AASID,
            "SenderRolename": "HTTP_ENDPoint",
            "conversationId": "AASNetworkedBidding",
            "ReceiverAASID": self.pyAAS.AASID,
            "ReceiverRolename": receiver
        }
        self.gen = Generic()
        self.frame = self.gen.createFrame(I40FrameData)

        self.InElem = self.pyaas.dba.getAAsSubmodelsbyId(self.pyaas.AASID, "StatusResponse")["message"][0]

        self.InElem["submodelElements"][0]["value"] = "E"
        self.InElem["submodelElements"][1]["value"] = "E009. delivery-error"
        self.InElem["submodelElements"][2]["value"] = "Unable to send the message to the target server"

        registerAckMessage = {"frame": self.frame,
                              "interactionElements": [self.InElem]}
        return registerAckMessage


class AASHashObject:
    def __init__(self, _id):
        self._id = _id
        self.subscribers = set()
        self.lastUpdateTime = ""
        self.newUpdate = False

    def __getId__(self) -> str:
        """
        """
        return self._id

    def __addSubscriber__(self, subscriber) -> None:
        """
        """
        self.subscribers.add(subscriber)

    def __removeSubscriber__(self, subscriber)->None:
        """
        """
        self.subscribers.remove(subscriber)

    def __getSubcriberList__(self) -> None: 
        """
        """
        return self.subscribers
    
class HashDict:
    def __init__(self):
        super().__init__()
        self.hashDict = dict()
        self.elementCount = 0

    def getElementCount(self) -> int:
        """
        """
        return self.elementCount

    def __insertHashEntry__(self, key, hashObject) -> None:
        """
        """
        self.elementCount = self.elementCount + 1
        self.hashDict[key] = hashObject

    def __deleteHashEntry__(self, key) -> None:
        """
        """
        self.elementCount = self.elementCount - 1
        del self.hashDict[key]

    def __getHashEntry__(self, key) -> object:
        """
        """
        return self.hashDict[key]

    def _getKeys(self) -> list:
        """
        """
        return list(self.hashDict.keys())

    def __getkey__(self, _value) -> str:
        """
        """
        for key, value in self.hashDict.items():
            if _value == value.__getId__():
                return key

    def __isKeyPresent__(self, key) -> bool:
        """
        """
        if key in list(self.hashDict.keys()):
            return True
        else:
            return False


class HistoryObject:
    def __init__(self,aasElementValue ,timestamp):
        self.timestamp = timestamp
        self.aasElementValue = aasElementValue


class UUIDGenerator:
    def __init__(self):
        pass

    def getnewUUID(self) -> str:
        """
        """
        return str(uuid.uuid4())


class AASElementObject:
    def __init__(self, aasElement, idShortPath, elemIndex=0):
        self.aasELement = aasElement
        self.elementIdList = []
        self.history = []
        self.idShortPath = idShortPath
        self.elementIndex = elemIndex
        self.modelType = ""
        self.idShort = ""
        self.elem_lock = False

    def addhistoryElement(self, historyObject: HistoryObject) -> None:
        """
        """
        if (self.isPrimitive()):
            self.history.append(historyObject)

    def __clearHistory(self) -> None:
        """
        """
        self.history.clear()

    def __getHistory(self) -> object:
        """
        """
        return self.history

    def __getLatestHistory(self, topLen) -> list:
        """
        """
        return self.history[-topLen:]

    def __getBottomHistory(self, bottomLen) -> list:
        """
        """
        return self.history[0:bottomLen]

    def isPrimitive(self) -> bool:
        """
        """
        return True if len(self.elementIdList) == 0 and self.aasELement[
            "modelType"] != "SubmodelElementCollection" else False

    def getElement(self) -> object:
        """
        """
        _tempElement = copy.deepcopy(self.aasELement)
        return _tempElement

    def setElement(self, element) -> object:
        """
        """
        self.aasELement = copy.deepcopy(element)

    def getIdShortPath(self) -> object:
        """
        """
        return self.idShortPath

class AIDProperty:
    def __init__(self,_type="string",read_only=False,observable=False,update_frequency= 0,
                 _unit="",aasIdentifier = "",submodelIdentifier ="",idshort_path="",
                 href="",operation_type="",requestType="",elemObject = None,property_name = ""):
        self._type = _type
        self.read_only = read_only
        self.observable = observable
        self.update_frequency = update_frequency
        self._unit = _unit
        self.aasIdentifier = aasIdentifier
        self.submodelIdentifier = submodelIdentifier 
        self.idshort_path = idshort_path
        self.href = href
        self.operation_type = operation_type
        self.elemObject = elemObject
        self.requestType = requestType
        self.property_name = property_name
    
    def from_json(self,aid_json):
        '''
        '''
        try:
            self._type = aid_json['type']
            self.read_only = aid_json['readOnly']
            self.observable = aid_json['observable']
            self.update_frequency = aid_json['updateFrequency']
            self.unit = aid_json['unit']
            self.aasIdentifier = aid_json['aasIdentifier']
            self.submodelIdentifier = aid_json['submodelId'] 
            self.idshort_path = aid_json['idShortPath']
            self.href = aid_json['href']
            #self.operation_type = aid_json['requestType']
            self.requestType = aid_json['requestType']
            self.property_name = aid_json['property_name']
            return True
        except Exception as E:
            print(str(E))
            return False
    
    def to_aas_josn(self,aid_property):
        '''
            
        '''
        try:
            i = 0 
            aid_property["idShort"] = self.property_name
            for pConstraint in aid_property["qualifiers"]:
                if (pConstraint["type"] == "type"):
                    aid_property["qualifiers"][i]["value"] = self._type
                if (pConstraint["type"] == "readOnly"):
                    aid_property["qualifiers"][i]["value"] = self.read_only
                if (pConstraint["type"] == "observable"):
                    aid_property["qualifiers"][i]["value"] = self.observable       
                if pConstraint["type"] == "updateFrequency":
                    aid_property["qualifiers"][i]["value"] = self.update_frequency
                if pConstraint["type"] == "unit":
                    aid_property["qualifiers"][i]["value"] = self.unit  
                if (pConstraint["type"] == "submodelId"):
                    aid_property["qualifiers"][i]["value"] = self.submodelIdentifier
                if (pConstraint["type"] == "idShortPath"):
                    aid_property["qualifiers"][i]["value"] = self.idshort_path
                i = i + 1  
            
            i = 0
            for pelem in aid_property["value"]:
                if pelem["idShort"] == "forms":
                    for formConstraint in pelem["value"][0]["qualifiers"]:
                        j = 0
                        if formConstraint["type"] == "href":
                            aid_property["value"][i]["value"][0]["qualifiers"][j]["value"] = self.href
                        elif formConstraint["type"] == "requestType":
                            aid_property["value"][i]["value"][0]["qualifiers"][j]["value"] = self.requestType
                        j = j + 1
                i = i + 1
            
            return copy.deepcopy(aid_property)
        except Exception as E:
            print(str(E))
            return copy.deepcopy(aid_property)
        
class AssetInterfaceDescription:
    def __init__(self):
        self.properties = dict()
        self.security = None
        self.securityDefinitins = None
    
    def add_property(self,td_property,td_property_name) -> None:
        self.properties[td_property_name] = td_property
    
    def get_property(self,td_property_name) -> object:
        return self.properties[td_property_name]

class ShellObject(AASElementObject):
    def __init__(self,aasElement, idShortPath, elemIndex=0):
        AASElementObject.__init__(self, aasElement, idShortPath, elemIndex)
        self.skills = dict()
        self.asset_interface_description = None
        self.productionStepList = []
        self.conversationIdList = []
        self.assetProperties = dict()
        self.aid = dict()
    
    def get_skill(self,skill_name) -> object:
        return self.skills[skill_name]["SkillHandler"]
    
    def add_skill(self,skill_name,skill_hanler) -> None:
        """
        """        
        self.skills[skill_name] = skill_hanler
        
    def delete_skill(self,skill_name) -> None:
        """
        """        
        del self.skills[skill_name]
        
    def get_skill_log(self,skill_name) -> list:
        """
        """        
        return (self.skills[skill_name]["SkillHandler"]).listHandler.loglist.getCotent()
    
    def getpreConfiguredProductionSteps(self,submodel):
        try:
            for capability in submodel["submodelElements"]:
                capabilityInfo = []
                skillName = ""
                for step in capability["value"]:
                    if step["idShort"] == "Name":
                        skillName = step["value"]
                    elif step["idShort"] == "CapabilityContent":
                        for info in step["value"]:
                            capabilityInfo.extend([[info["value"],info["idShort"],""]])
                self.productionStepList.append({"skill_name":skillName,
                                        "submodel_id_idSHort_list":capabilityInfo})
            print(self.productionStepList)
            return True
        except Exception as E:
            return False

    
    def add_produtionCapability(self,submodel) -> (str,bool):
        """
        """
        try:
            self.getpreConfiguredProductionSteps(submodel)
            return "Sucesss", True
        except Exception as e:
            return str(e), False
        
    
    def add_produtionstep(self,skill_name,submodel_id_idSHort_list) -> (str,bool):
        """
        """        
        try:
            self.productionStepList.append({"skill_name":skill_name,
                                        "submodel_id_idSHort_list":submodel_id_idSHort_list})
            return "New Production step is added",True
        except Exception as e:
            return str(e), False
        
    def delete_production_step(self,skill_name,submodel_id,sequence) -> (str,bool):
        """
        """        
        try:
            for index,entry in enumerate(self.productionStepList):
                if skill_name  == entry["skill_name"] and submodel_id == entry["submodel_id_idSHort_list"][0][0] and int(sequence) == index + 1:
                    del self.productionStepList[index]
                    return "Production step deleted", True
            return "No Data Found", False
        except Exception as e:
            return str(e), False
    
    def delete_all_production(self) -> bool:
        try:
            self.productionStepList.clear()
            return True
        except Exception as e:
            str(e)
            return False
    
    def add_conversationId(self,conversationId):
        """
        """        
        self.conversationIdList.append(conversationId)
    
    def remove_conversationId(self,conversationId):
        """
        """        
        self.conversationIdList.remove(conversationId)
    
class SubscriptionMessage:
    def __init__(self, elementPath, updateTime, modelType, subscribers, subscriptiondata):
        self.elementPath = elementPath
        self.subscribers = subscribers
        self.updateTime = updateTime
        self.modelType = modelType
        self.subscriptiondata = subscriptiondata

class CarbonFootPrintObject:
    def __init__(self,_coversationId,_uuid):
        self._coversationId = _coversationId
        self._uuid = _uuid
        self.startTime = ""
        self.endTime = ""
        self.totalTime = 0
        self._cfp = 0
        self.skillName = ""
    
    def formatTime(self,_time):
        try:
            if (_time == "Start"):
                return self.startTime.strftime("%Y-%m-%d %H:%M:%S")
            else :
                return self.endTime.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as E:
            return ""
    
    def getTotalTime(self):
        try:
            return self.totalTime.seconds
        except Exception as E:
            return 0    
        
    def getProperties(self):
        return [self.skillName,self.formatTime("Start"),self.formatTime("End"),
                self.getTotalTime(),self._cfp]

    def setInitialValue(self,_skillName,startTime):
        self.skillName = _skillName 
        self.startTime =startTime
    
    def setFinalProperties(self,endTime,_cfp):
        self._cfp = _cfp
        self.endTime = endTime
        try:
            self.totalTime = self.endTime - self.startTime
        except Exception as e:
            self.totalTime = 0
    
    def getMessageCount(self):
        return 0    
    
class ConversationObject:
    def __init__(self, _coversationId):
        self._coversationId = _coversationId
        self.messages = []
        self.sub_coversationIds = []
    
    def extend_sub_conversation_ids(self,sub_ids):
        self.sub_coversationIds.extend(sub_ids)
    
    def _insertMessage(self, messageType, messageId, direction, message, entryTime, SenderAASID):
        _message = {
            "messageType": messageType,
            "message_Id": messageId,
            "message": message,
            "direction": direction,
            "entryTime": entryTime,
            "SenderAASID": SenderAASID
        }
        self.messages.append(copy.deepcopy(_message))

    def _getMessages(self, identificationId):
        returnData = {"inbound": [], "outbound": [], "internal": []}
        try:
            for message in self.messages:
                if True:#(message["SenderAASID"] == "Broadcast" or message["SenderAASID"] == identificationId):
                    if (message["direction"] == "inbound"):
                        returnData["inbound"].append(message["message"]["frame"]["messageId"] + ":" + message["entryTime"])
                    elif (message["direction"] == "outbound"):
                        returnData["outbound"].append(message["message"]["frame"]["messageId"] + ":" + message["entryTime"])
                    elif (message["direction"] == "internal"):
                        returnData["internal"].append(message["message"]["frame"]["messageId"] + ":" + message["entryTime"])
        except Exception as E:
            pass
        return returnData

    def _getMessage(self, messageId):
        for message in self.messages:
            if message["message_Id"] == messageId:
                return message, True
        return "Empty", "Error"

    def _getMessageCount(self):
        return len(self.messages)

    def _deleteMessage(self, messageId):
        pass  # not impelmented


class SecurityAccess:
    def __init__(self,pyaas):
        self.pyaas = pyaas
    
    def configure(self):
        self.authenticationLink = self.pyaas.lia_env_variable["LIA_AUTHENTICATION_SERVER"]
    
#     def security_check(self,accesstoken):
#         jwt= JWSig().unpack(accesstoken)
#         verifier = SIGNER_ALGS["RS256"]
#         try:
#             res = verifier.verify(jwt.sign_input(), jwt.signature(),key=der2rsa(self.pyaas.derAuthCert))
#             print(res)
#             return res
#         except Exception as E:
#             print ("Invalid Token")
#             return False
#         return False  


class Generate_AAS_Shell:
    def __init__(self,pyaas,data):
        self.pyaas = pyaas
        self.idShort = data["idShort"]
        self.description = data["description"]
        self.thumnail = "file://aasx/files/"+data["file"]
        self.displayName = data["displayName"]
        self.globalAssetId = data["globalAssetId"]
        self.assetKind = data["assetKind"]
        self.assetType = data["assetType"]
        
    def create_identification_id(self) -> str:
        """
        """        
        self.uuidG = UUIDGenerator()
        _uuid = self.uuidG.getnewUUID()
        return "ww.ovgu.de/aas/"+str(_uuid)
    
    def execute(self) -> (object,bool):
        """
        """        
        try:
            shell_data = copy.deepcopy(self.pyaas.aasConfigurer.aas_shell_template)
            shell_data["idShort"] = self.idShort
            shell_data["description"][0]["text"] = self.description
            shell_data["id"] = self.create_identification_id()
            shell_data["displayName"][0]["text"] = self.displayName
            shell_data["assetInformation"]["globalAssetId"] = self.globalAssetId
            shell_data["assetInformation"]["assetKind"] = self.assetKind
            shell_data["assetInformation"]["assetType"] = self.assetType
            shell_data["assetInformation"]["defaultThumbnail"]["path"] = self.thumnail
        except Exception as e:
            print("Error @Generate_AAS_Shell execute"+ str(e))
            return "Error generating the shell",False 
        return shell_data,True
