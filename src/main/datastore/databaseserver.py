'''
Copyright (c) 2021-2022 Otto-von-Guericke-Universiat Magdeburg, Lehrstuhl Integrierte Automation
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
'''
import os
import uuid
from datetime import datetime
try:
    from utils.utils import AASHashObject,UUIDGenerator,AASElementObject,ConversationObject,HistoryObject,SubscriptionMessage
except ImportError:
    from main.utils.utils import AASHashObject,UUIDGenerator,AASElementObject,ConversationObject,HistoryObject,SubscriptionMessage

base_dir = os.path.dirname(os.path.realpath(__file__))

    
class AASSubmodelParser(object):
    def __init__(self,aasHashDict,submodelHashDict):
        self.aasHashDict = aasHashDict
        self.submodelHashDict = submodelHashDict
        self.uuidG = UUIDGenerator()
    
    def registerElement(self,_newId,_element):
        _uuid = self.uuidG.getnewUUID()
        aasHashObj = AASHashObject(_uuid)
        self.aasHashDict.__insertHashEntry__(_newId, aasHashObj)
        _aasElementObject = AASElementObject(_element,_newId)
        self.submodelHashDict.__insertHashEntry__(_uuid, _aasElementObject)
        return _uuid
    
    def updatePropertyElement(self,_submodelElement,_newId):
        hashObject = self.aasHashDict.__getHashEntry__(_newId)
        _uuid = hashObject.__getId__()
        aasElementObject = self.submodelHashDict.__getHashEntry__(_uuid)
        _history = aasElementObject.aasELement
        aasElementObject.aasELement = _submodelElement
        if (_submodelElement["modelType"]["name"] == "Property"):
            hobject = HistoryObject(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S")),_history["value"])
            aasElementObject.history.append(hobject)
        hashObject.newUpdate = True
        return _uuid        
    
    def parseDataElement(self,_submodelElement,_parentId,_update=False):
        _newId = _parentId +"."+ _submodelElement["idShort"]
        if (_update):
            return  self.updatePropertyElement(_submodelElement,_newId)
        else:
            return self.registerElement(_newId,_submodelElement)

    def parseSubmodelCollection(self,submodelColl,_parentId,_update=False):
        _newId =_parentId +"."+ submodelColl["idShort"]
        collectionElemIds =  []
        for _submodelElement in submodelColl["value"]:
            if (_submodelElement["modelType"]["name"] != "SubmodelElementCollection"):
                collectionElemIds.append(self.parseDataElement(_submodelElement, _newId,_update))
            else:
                collectionElemIds.append(self.parseSubmodelCollection(_submodelElement,_newId,_update))
        submodelColl["value"].clear()
        for _uid in collectionElemIds:
            submodelColl["value"].append(_uid)
        if (_update):
            return  self.updatePropertyElement(_submodelElement,_newId)
        else:
            return self.registerElement(_newId,submodelColl)
    
    def parse(self,submodel):
        submodelId = submodel["identification"]["id"]
        submodelElements = []
        for _submodelElement in submodel["submodelElements"]:
            if (_submodelElement["modelType"]["name"] != "SubmodelElementCollection"):
                submodelElements.append(self.parseDataElement(_submodelElement,submodelId))                    
            else:
                submodelElements.append(self.parseSubmodelCollection(_submodelElement,submodelId))
        submodel["submodelElements"].clear()
        for _uuid in submodelElements:
            submodel["submodelElements"].append(_uuid)
        
        return self.registerElement(submodelId, submodel)
        
        
class ConceptionDescriptionParser(object):
    def __init__(self,aasHashDict,cdHashDict):
        self.aasHashDict = aasHashDict
        self.cdHashDict = cdHashDict
        self.uuidG = UUIDGenerator()    

    def registerElement(self,_newId,_element):
        _uuid = self.uuidG.getnewUUID()
        aasHashObj = AASHashObject(_uuid)
        self.aasHashDict.__insertHashEntry__(_newId, aasHashObj)
        _aasElementObject = AASElementObject(_element,_newId)
        self.cdHashDict.__insertHashEntry__(_uuid, _aasElementObject)
        return _uuid

    def parse(self,_cD):
        _cdId = _cD["identification"]["id"]
        return self.registerElement(_cdId,_cD)

class AssetInformationParser(object):
    def __init__(self,aasHashDict,assetHashDict):
        self.aasHashDict = aasHashDict
        self.assetHashDict = assetHashDict
        self.uuidG = UUIDGenerator()    

    def registerElement(self,_newId,_element):
        _uuid = self.uuidG.getnewUUID()
        aasHashObj = AASHashObject(_uuid)
        self.aasHashDict.__insertHashEntry__(_newId, aasHashObj)
        _aasElementObject = AASElementObject(_element,_newId)
        self.assetHashDict.__insertHashEntry__(_uuid, _aasElementObject)
        return _uuid

    def parse(self,_asset):
        _assetId = _asset["identification"]["id"]
        return self.registerElement(_assetId,_asset)

class AASShellParser(object):
    def __init__(self,aasHashDict,aasShellHashDict):
        self.aasHashDict = aasHashDict
        self.aasShellHashDict = aasShellHashDict
        self.uuidG = UUIDGenerator()    

    def registerElement(self,_newId,_element):
        _uuid = self.uuidG.getnewUUID()
        aasHashObj = AASHashObject(_uuid)
        _elementCount = self.aasHashDict.getElementCount()
        self.aasHashDict.__insertHashEntry__(_newId, aasHashObj)
        _aasElementObject = AASElementObject(_element,_newId,_elementCount+1)
        self.aasShellHashDict.__insertHashEntry__(_uuid, _aasElementObject)
        return _uuid

    def parse(self,_assShell):
        _assShellId = _assShell["identification"]["id"]
        return self.registerElement(_assShellId,_assShell)

class AAS_Database_Server(object):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
        self.jsonData = self.pyAAS.aasConfigurer.jsonData
        self.aasHashDict = self.pyAAS.aasHashDict
        self.submodelHashDict = self.pyAAS.submodelHashDict
        self.assetHashDict = self.pyAAS.assetHashDict
        self.cdHashDict = self.pyAAS.cdHashDict
        self.conversHashDict = self.pyAAS.conversHashDict
        self.aasShellHashDict = self.pyAAS.aasShellHashDict
        self.dbServerStatus = self.__initAASPackage__()
        
    def __initAASPackage__(self):
        try:
            self.parseSubmodels(self.jsonData["submodels"])
            self.parseAssets(self.jsonData["assets"])
            self.parseConceptDescription(self.jsonData["conceptDescriptions"])
            self.parseAssetAdministrationShells(self.jsonData["assetAdministrationShells"])
            return True
        except Exception as E:
            self.pyAAS.serviceLogger.info('Error Initializing the AASX package. ' +  str(E))
            return False
        
    def parseSubmodels(self,_submodels):
        for _submodel in _submodels:
            aasSmParser = AASSubmodelParser(self.aasHashDict,self.submodelHashDict)
            aasSmParser.parse(_submodel)
        
    def parseAssets(self,_assets):
        for _asset in _assets:
            assetParser = AssetInformationParser(self.aasHashDict,self.assetHashDict)
            assetParser.parse(_asset)

    def parseConceptDescription(self,conceptDescriptions):
        for _conceptDescription in conceptDescriptions:
            cdParse = ConceptionDescriptionParser(self.aasHashDict,self.cdHashDict)
            cdParse.parse(_conceptDescription)
    
    def parseAssetAdministrationShells(self,assetAdministrationShells):
        for _aasShell in assetAdministrationShells:
            aasShellObject = AASShellParser(self.aasHashDict,self.aasShellHashDict)
            aasShellObject.parse(_aasShell)
        
            
    def processCollectionElements(self,collectionElem):
        values = []
        for _subid in collectionElem["value"]:
            subelem = (self.submodelHashDict.__getHashEntry__(_subid)).getElement()
            if (subelem["modelType"]["name"] != "SubmodelElementCollection"):
                values.append(subelem)
            else:
                values.append(self.processCollectionElements(subelem))
        collectionElem["value"] = values
        return collectionElem
        
    def deleteCollectionElems(self,collectionElem):
        for _subid in collectionElem["value"]:
            _aasElementObject = (self.submodelHashDict.__getHashEntry__(_subid))
            subelem = _aasElementObject.getElement()
            if (subelem["modelType"]["name"] != "SubmodelElementCollection"):
                self.deleteCollectionElems(subelem)
            self.submodelHashDict.__deleteHashEntry__(_subid)
            self.aasHashDict.__deleteHashEntry__(_aasElementObject.__getIdShortPath())

    def deleteSubmodel(self,_submodelid):
        try:
            _id = (self.aasHashDict.__getHashEntry__(_submodelid).__getId__())
            _submodel = (self.submodelHashDict.__getHashEntry__(_id)).getElement()
            for submodelElem in _submodel["submodelElements"]:
                self.deleteSubmodelElem(submodelElem["idShort"])
            self.submodelHashDict.__deleteHashEntry__(_id)
            self.aasHashDict.__deleteHashEntry__(_submodelid)
            return "Submodel deleted Successfully", True 
        except Exception as E:
            return  str(E) + "Unexpected Error", False
    
    def deleteSubmodelElem(self,_idShortPath):
        try:
            _id = (self.aasHashDict.__getHashEntry__(_idShortPath).__getId__())
            self.aasHashDict.__deleteHashEntry__(_idShortPath)
            elem = (self.submodelHashDict.__getHashEntry__(_id)).getElement()
            if (elem["modelType"]["name"] != "SubmodelElementCollection"):
                self.submodelHashDict.__deleteHashEntry__(_id)
            else:
                self.deleteCollectionElems(elem)
            return "Submodel element deleted successfully", True
        except Exception as E:
            return  str(E) + "Unexpected Error", False
        
    def postSubmodelElem(self,data):
        try:
            _idShortpath = data["_idShortpath"]
            elemData = data["requestData"]
            aasSmParser = AASSubmodelParser(self.aasHashDict,self.submodelHashDict)
            _parentId = (_idShortpath.split("."))
            del _parentId[-1]
            if (elemData["modelType"]["name"] != "SubmodelElementCollection"):
                aasSmParser.parseSubmodelCollection(elemData, ".".join(_parentId))
            else:
                aasSmParser.parseDataElement(elemData, _parentId)
            return "Submodel element created successfully", True
        except Exception as E:
            return  str(E) + "Unexpected Error", False
    
    def putSubmodelElem(self,data):
        try:
            _idShortpath = data["_idShortpath"]
            elemData = data["requestData"]            
            aasSmParser = AASSubmodelParser(self.aasHashDict,self.submodelHashDict)
            _parentId = (_idShortpath.split("."))
            del _parentId[-1]
            if (elemData["modelType"]["name"] == "SubmodelElementCollection"):
                aasSmParser.parseSubmodelCollection(elemData, ".".join(_parentId),True)
            else:
                aasSmParser.parseDataElement(elemData, ".".join(_parentId),True)
                
            aasHashObject = self.pyAAS.aasHashDict.__getHashEntry__(_idShortpath)
            if len(aasHashObject.subscribers) > 0 and elemData["modelType"]["name"] == "Property":
                subForword = SubscriptionMessage(_idShortpath,"dd",elemData["modelType"]["name"],aasHashObject.subscribers,elemData)
                subForword.subscriptiondata = elemData
                self.pyAAS.listnerSockets["AAS_PUBSUB"].subscription_forward_messages.put(subForword)
                                 
            return "Submodel element created successfully", True
        except Exception as E:
            return  str(E) + "Unexpected Error", False

    def getSubmodelElement(self,_idShortPath):
        try:
            _id = (self.aasHashDict.__getHashEntry__(_idShortPath).__getId__())
            elem = (self.submodelHashDict.__getHashEntry__(_id)).getElement()
            if (elem["modelType"]["name"] != "SubmodelElementCollection"):
                return elem, True
            else:
                return self.processCollectionElements(elem), True
        except Exception as E:
            return  str(E) + "Unexpected Error", False
    
    def getSubmodelElements(self,_submodelId):
        try:
            _submodel,status = self.getSubmodel(_submodelId)
            if (status):
                i = 0
                submodelElements = dict()
                for _submodelElem in _submodel["submodelElements"]:
                    submodelElements[i] = _submodelElem
                    i = i + 1
                return submodelElements, True
            else:
                return _submodel,status 
        except Exception as E:
            return  str(E) + "Unexpected Error", False

    def postSubmodel(self,submodelData):
        try:
            aasSmParser = AASSubmodelParser(submodelData,self.aasHashDict,self.submodelHashDict)
            aasSmParser.parse(submodelData)
            return "Submodel created successfully", True
        except Exception as E:
            return  str(E) + "Unexpected Error", False

    def putSubmodel(self,data):
        try:
            msg,status = self.deleteSubmodel(data["_submodelid"])
            if (status):
                msg1,status1 = self.postSubmodel(data["requestData"])
                if status1:
                    return  "Submodel updated successfully", "Unexpected Error"
                else:
                    return msg1,status1
            else:
                return msg,status
        except Exception as E:
            return  str(E) + "Unexpected Error", False
                        
    def getSubmodel(self,_submodelid):
        try:
            _submodel = dict()
            _id = (self.aasHashDict.__getHashEntry__(_submodelid).__getId__())
            _submodel = (self.submodelHashDict.__getHashEntry__(_id)).getElement()
            i = 0
            for submodelElem in _submodel["submodelElements"]:
                _submodelid = (self.submodelHashDict.__getHashEntry__(submodelElem)).getIdShortPath()
                data, status = self.getSubmodelElement(_submodelid)
                if (status):
                    _submodel["submodelElements"][i] = data
                else:
                    return "Error",False
                i = i + 1
            return _submodel, True
        except Exception as E:
            return  str(E) + "Unexpected Error", False     
                        
    def getSubmodels(self):
        try:
            j = 0
            _submodels = dict()
            for _id in self.submodelHashDict.__getKeys():
                i = 0
                _submodel = self.submodelHashDict.__getHashEntry__(_id)
                for submodelElem in _submodel["submodelElements"]:
                    _submodelid = (self.submodelHashDict.__getHashEntry__(submodelElem)).getIdShortPath()
                    submodelElem[i] = self.getSubmodelElement(_submodelid)
                    i = i + 1
                _submodels[j]  = _submodel
                i = j + 1
            return _submodels, True
        except Exception as E:
            return  str(E) + "Unexpected Error", False

    def deleteConceptDescription(self,_conceptDescriptionId):
        try:
            _id = (self.aasHashDict.__getHashEntry__(_conceptDescriptionId).__getId__())
            self.cdHashDict.__deleteHashEntry__(_id)
            self.aasHashDict.__deleteHashEntry__(_conceptDescriptionId)
            return "Concept Description deleted successfully", True 
        except Exception as E:
            return  str(E) + "Unexpected Error", False     
    
    def putConceptDescription(self,_conceptDescriptionId,data):
        try:
            msg,status = self.deleteConceptDescription(data["_conceptDescriptionId"])
            if (status):
                msg1,status1 = self.postConceptDescription(data["requestData"])
                if (status1):
                    return "Concept Description updated successfully", True
                else:
                    return msg1,status1
            else:
                return msg,status
        except Exception as E:
            return  str(E) + "Unexpected Error", False
    
    def postConceptDescription(self,_conceptDescription):
        try:
            cdParse = ConceptionDescriptionParser(self.aasHashDict,self.cdHashDict)
            cdParse.parse(_conceptDescription)
            return "Concept Description created successfully",True
        except Exception as E:
            return  str(E) + "Unexpected Error", False
    
    def getConceptDescription(self,_conceptDescriptionId):
        try:
            _id = self.aasHashDict.__getHashEntry__(_conceptDescriptionId)
            _conceptDescription = self.cdHashDict.__getHashEntry__(_id)
            return _conceptDescription, "Success"
        except Exception as E:
            return  str(E) + "Unexpected Error", False
    
    def  getConceptDescriptions(self):
        try:
            _conceptDescriptions = dict()
            i = 0
            for _id in self.cdHashDict.__getKeys():
                _conceptDescriptions[i] =  self.cdHashDict.__getHashEntry__(_id)
                i = i + 1
            return _conceptDescriptions, "Success"
        except Exception as E:
            return  str(E) + "Unexpected Error", False

    def deleteAsset(self,_aasetId):
        try:
            _id = (self.aasHashDict.__getHashEntry__(_aasetId).__getId__())
            self.assetHashDict.__deleteHashEntry__(_id)
            self.aasHashDict.__deleteHashEntry__(_aasetId)
            return "Asset Information Succesfully", True
        except Exception as E:
            return  str(E) + "Unexpected Error", False       
    
    def putAsset(self,_id,_assetInformation):
        try:
            msg,status = self.deleteAsset(_id)
            if status:
                msg1,status1 = self.postAsset(_assetInformation)
                if status1:
                    return "Asset Information updated succesfully", True
                else:
                    return msg1,False
            else:
                msg,status
        except Exception as E:
            return  str(E) + "Unexpected Error", False
    
    def postAsset(self,_assetInformation):
        try:
            assetParse = AssetInformationParser(self.aasHashDict,self.assetHashDict)
            assetParse.parse(_assetInformation)
            return "Asset Information created successfully", True
        except Exception as E:
            return  str(E) + "Unexpected Error", False        

    def getAssetInformation(self,_assetId):
        try:
            _id = self.aasHashDict.__getHashEntry__(_assetId)
            _assetInformation = self.assetHashDict.__getHashEntry__(_id)
            return _assetInformation, True
        except Exception as E:
            return  str(E) + "Unexpected Error", False
    
    def  getAssetInformations(self):
        try:
            _assetInformations = dict()
            i = 0
            for _id in self.assetHashDict.__getKeys():
                _assetInformations[i] =  self.assetHashDict.__getHashEntry__(_id)
                i = i + 1
            return _assetInformations, "Success"
        except Exception as E:
            return  str(E) + "Unexpected Error", False     

    def deleteAASShell(self,_shellId):
        try:
            _id = (self.aasHashDict.__getHashEntry__(_shellId).__getId__())
            self.aasShellHashDict.__deleteHashEntry__(_id)
            self.aasHashDict.__deleteHashEntry__(_shellId)
            return "Asset Administration Shell deleted successfully", True 
        except Exception as E:
            return  str(E) + "Unexpected Error", False      
    
    def putAASShell(self,data):
        try:
            msg,status = self.deleteAASShell(data["_shellId"])
            if (status):
                msg1,status1 =  self.postAASShell(data["requestData"])
                if (status1):
                    return "Asset Administration Shell updated successfully",True
                else:
                    return msg1, False
            else:
                msg,status
        except Exception as E:
            return  str(E) + "Unexpected Error", False
    
    def postAASShell(self,_aasShell):
        try:
            aasShellParser = AASShellParser(self.aasHashDict,self.aasShellHashDict)
            aasShellParser.parse(_aasShell)
            return "Asset Administration Shell created successfully", True
        except Exception as E:
            return  str(E) + "Unexpected Error", False        

    def getAASShell(self,_shellId):
        try:
            _id = self.aasHashDict.__getHashEntry__(_shellId)
            _aasShell = self.aasShellHashDict.__getHashEntry__(_id)
            return _aasShell,True
        except Exception as E:
            return  str(E) + "Unexpected Error", False
    
    def getAASShells(self):
        try:
            _aasShells = dict()
            i = 0
            for _id in self.aasShellHashDict.__getKeys():
                _aasShells[i] =  self.aasShellHashDict.__getHashEntry__(_id)
                i = i + 1
            return _aasShells, True
        except Exception as E:
            return  str(E) + "Unexpected Error", False

    def getShellSubmodelRef(self,data):
        try:
            _id = (self.aasHashDict.__getHashEntry__(data["_shellId"]).__getId__())
            _aasShell = self.aasShellHashDict.__getHashEntry__(_id)
            for index, submodelRef in  enumerate(_aasShell["submodels"]):
                if submodelRef["keys"][0]["value"] == data["_submodelrefId"]:
                    return _aasShell["submodels"][index], True
            return "No data", False 
        except Exception as E:
            return  str(E) + "Unexpected Error", False 
        
    def getShellSubmodelRefs(self,_shellId):
        try:
            submodelRefs = {}
            i = 0
            _id = self.aasHashDict.__getHashEntry__(_shellId)
            _aasShell = self.aasShellHashDict.__getHashEntry__(_id)
            for _submodelRef in _aasShell["submodels"]:
                submodelRefs[i] = _submodelRef
                i = i + 1
            return submodelRefs, True
        except Exception as E:
            return  str(E) + "Unexpected Error", False
    
    def postShellSubmodelRef(self,_shellId,_submodelRef):
        try:
            _id = self.aasHashDict.__getHashEntry__(_shellId).__getId__()
            _aasShell = self.aasShellHashDict.__getHashEntry__(_id)
            _aasShell["submodels"].append(_submodelRef)
            return "Submodel reference created successfully", True
        except Exception as E:
            return  str(E) + "Unexpected Error", False

    def deleteShellSubmodelRef(self,data):
        try:
            _id = (self.aasHashDict.__getHashEntry__(data["_shellId"]).__getId__())
            _aasShell = self.aasShellHashDict.__getHashEntry__(_id)
            for index, submodelRef in  enumerate(_aasShell["submodels"]):
                if submodelRef["keys"][0]["value"] == data["_submodelrefId"]:
                    del _aasShell["submodels"][index]
            return "Asset Administration Shell deleted successfully", True 
        except Exception as E:
            return  str(E) + "Unexpected Error", False   
        
    def putShellSubmodelRef(self,data):
        try:
            msg,status = self.deleteShellSubmodelRef(data["_shellId"])
            if (status):
                msg1,status1 =  self.postShellSubmodelRef(data["requestData"])
                if (status1):
                    return "Asset Administration Shell updated successfully",True
                else:
                    return msg1, False
            else:
                msg,status
        except Exception as E:
            return  str(E) + "Unexpected Error", False        

    def getSubmodelsbyShell(self,_shellId):
        try:
            _id = self.aasHashDict.__getHashEntry__(_shellId).__getId__()
            _aasShell = self.aasShellHashDict.__getHashEntry__(_id).aasELement
            _submodels = dict()
            i = 0
            for _submodelRef in _aasShell["submodels"]:
                _submodelid = _submodelRef["keys"][0]["value"]
                _submodel,status = self.getSubmodel(_submodelid)
                if status:
                    _submodels[i] = _submodel
                else:
                    return _submodel,status
                i = i + 1
            return _submodels,True
        except Exception as E:
            return  str(E) + "Unexpected Error", False
                
    def createNewConversation(self,coversationId):
        try:
            uuidG = UUIDGenerator()
            _uuid = uuidG.getnewUUID()
            hashObject = AASHashObject(_uuid)
            self.aasHashDict.__insertHashEntry__(coversationId, hashObject)
            conversationObject = ConversationObject(coversationId)
            self.conversHashDict.__insertHashEntry__(_uuid, conversationObject)
        except Exception as E:
            return  str(E) + "Unexpected Error", False
    
    def saveNewConversationMessage(self,coversationId,messageType,messageId,direction,message,entryTime,SenderAASID):
        try:
            _uuid = self.aasHashDict.__getHashEntry__(coversationId).__getId__()
            converseObject = self.conversHashDict.__getHashEntry__(_uuid)
            converseObject._insertMessage(messageType,messageId,direction,message,entryTime,SenderAASID)
        except Exception as E:
            return  str(E) + "Unexpected Error", False

    def getMessageCount(self):
        try:
            uuids = self.conversHashDict._getKeys()
            messageCount = sum(   self.conversHashDict.__getHashEntry__(uuid)._getMessageCount() for uuid in uuids)   
            return messageCount, "Success"    
        except Exception as E:
            return  str(E) + "Unexpected Error", False
           
    def getConversationsById(self,coversationId,identificationId):
        try:
            _uuid = self.aasHashDict.__getHashEntry__(coversationId).__getId__()
            converseObject = self.conversHashDict.__getHashEntry__(_uuid)
            conversation = converseObject._getMessages(identificationId)
            return conversation, True
        except Exception as E:
            return  str(E) + "Unexpected Error", False
    
    def getMessagebyId(self,messageId,conversationId):
        try:
            _uuid = self.aasHashDict.__getHashEntry__(conversationId).__getId__()
            converseObject = self.conversHashDict.__getHashEntry__(_uuid)
            message,status = converseObject._getMessage(messageId)
            if (status):
                return self.processMessage(message["message"]), True
            else:
                return "Message Not found", False
        except Exception as E:
            return  str(E) + "Unexpected Error", False
    
    def processMessage(self,message):
        i = 0
        if(message["frame"]["type"] != "register"):
            for iM in message["interactionElements"]:
                if ("submodelElements" in list(iM.keys())):
                    message["interactionElements"][i] = self.getSubmodePropertyDict(iM)
                elif ("assetAdministrationShells" in list(iM.keys())):
                    message["interactionElements"][i] = str(iM)
                else:
                    message["interactionElements"][i] = iM
                i = i + 1
        return message
    
    def processEachSubmodelElement(self,submodelElement):
        if submodelElement["modelType"]["name"] == "SubmodelElementCollection":
            elemCollection = {}
            for elem in submodelElement["value"]:
                if elem["modelType"]["name"] == "SubmodelElementCollection":
                    elemCollection[elem["idShort"]] = self.processEachSubmodelElement(elem)
                else:
                    if (elem["modelType"]["name"] == "Property"):
                        elemCollection[elem["idShort"]] = elem["value"] 
                    elif (elem["modelType"]["name"] == "Range"):
                        elemCollection[elem["idShort"]] = {"min" :elem["min"] ,"max":elem["max"]}
                        
            return elemCollection
        else: 
            return submodelElement["value"]
    
    def getSubmodePropertyDict(self,submodel):
        submodelProperetyDict = {}
        for eachProperty in submodel["submodelElements"]:
            submodelProperetyDict[eachProperty["idShort"]] = self.processEachSubmodelElement(eachProperty)
        return submodelProperetyDict
#     
#     
# if (platform.system() == "Windows"):
#     script_dir = (base_dir).split("src\main")[0]
#     repository = os.path.join(script_dir, "config") 
#     print(repository)    
#     with open(os.path.join(repository, "PicknPlace.json"), encoding='utf-8') as json_file:
#         jsonData = json.load(json_file)
#         aasDBServer = AAS_Database_Server(jsonData)
#         aasDBServer.__initAASPackage__()
#         eData = aasDBServer.getSubmodelElement("https://example.com/ids/sm/1544_0232_5022_8396.GeneralInformation")
#         print(eData)