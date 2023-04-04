'''
Copyright (c) 2021-2022 Otto-von-Guericke-Universiat Magdeburg, Lehrstuhl Integrierte Automation
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
'''
import base64
import os
import uuid
from datetime import datetime
try:
    from utils.utils import AASHashObject,UUIDGenerator,AASElementObject,ConversationObject,HistoryObject,SubscriptionMessage,ShellObject,CarbonFootPrintObject
except ImportError:
    from src.main.utils.utils import AASHashObject,UUIDGenerator,AASElementObject,ConversationObject,HistoryObject,SubscriptionMessage,ShellObject,CarbonFootPrintObject

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
        _aasElementObject.modelType = _element["modelType"]
        _aasElementObject.idShort = _element["idShort"]
        self.submodelHashDict.__insertHashEntry__(_uuid, _aasElementObject)
        return _uuid
    
    def updatePropertyElement(self,_submodelElement,_newId):
        hashObject = self.aasHashDict.__getHashEntry__(_newId)
        _uuid = hashObject.__getId__()
        aasElementObject = self.submodelHashDict.__getHashEntry__(_uuid)
        _history = aasElementObject.getElement()
        aasElementObject.aasELement = _submodelElement
        aasElementObject.modelType = _submodelElement["modelType"]
        if (_submodelElement["modelType"] == "Property"):
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
            if (_submodelElement["modelType"] != "SubmodelElementCollection"):
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
        submodelId = submodel["id"]
        submodelElements = []
        if "submodelElements" in submodel.keys():
            for _submodelElement in submodel["submodelElements"]:
                if (_submodelElement["modelType"] != "SubmodelElementCollection"):
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
        _cdId = _cD["id"]
        return self.registerElement(_cdId,_cD)

class AASShellParser(object):
    def __init__(self,aasHashDict,submodelHashDict,aasShellHashDict):
        self.aasHashDict = aasHashDict
        self.aasShellHashDict = aasShellHashDict
        self.submodelHashDict = submodelHashDict
        self.uuidG = UUIDGenerator()    
        
    def register(self,_newId,_element):
        _uuid = self.uuidG.getnewUUID()
        aasHashObj = AASHashObject(_uuid)
        shellIndex = self.aasHashDict.getElementCount() + 1
        self.aasHashDict.__insertHashEntry__(_newId, aasHashObj)
        _aasElementObject = ShellObject(_element,_newId,shellIndex)
        self.aasShellHashDict.__insertHashEntry__(_uuid, _aasElementObject)
        
        return _uuid

    def parse(self,_assShell):
        return self.register(_assShell["id"],_assShell)

class AAS_Database_Server(object):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
        self.jsonData = self.pyAAS.aasConfigurer.jsonData
        self.aasHashDict = self.pyAAS.aasHashDict
        self.submodelHashDict = self.pyAAS.submodelHashDict
        self.assetHashDict = self.pyAAS.assetHashDict
        self.cdHashDict = self.pyAAS.cdHashDict
        self.conversHashDict = self.pyAAS.converseHashDict
        self.cfpHashDict = self.pyAAS.cfpHashDict
        self.aasShellHashDict = self.pyAAS.aasShellHashDict
        self.dbServerStatus = self.__initAASPackage__()
        
    def __initAASPackage__(self):
        try:
            self.parseSubmodels(self.jsonData["submodels"])
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

    def parseConceptDescription(self,conceptDescriptions):
        for _conceptDescription in conceptDescriptions:
            cdParse = ConceptionDescriptionParser(self.aasHashDict,self.cdHashDict)
            cdParse.parse(_conceptDescription)
    
    def parseAssetAdministrationShells(self,assetAdministrationShells):
        for _aasShell in assetAdministrationShells:
            aasShellObject = AASShellParser(self.aasHashDict,self.submodelHashDict,self.aasShellHashDict)
            aasShellObject.parse(_aasShell)    
            
    def processCollectionElements(self,collectionElem):
        values = []
        for _subid in collectionElem["value"]:
            subelem = (self.submodelHashDict.__getHashEntry__(_subid)).getElement()
            if (subelem["modelType"] != "SubmodelElementCollection"):
                values.append(subelem)
            else:
                values.append(self.processCollectionElements(subelem))
        collectionElem["value"] = values
        return collectionElem
        
    def deleteCollectionElems(self,collectionElem):
        for _subid in collectionElem["value"]:
            _aasElementObject = (self.submodelHashDict.__getHashEntry__(_subid))
            subelem = _aasElementObject.getElement()
            if (subelem["modelType"] == "SubmodelElementCollection"):
                self.deleteCollectionElems(subelem)
            self.submodelHashDict.__deleteHashEntry__(_subid)
            self.aasHashDict.__deleteHashEntry__(_aasElementObject.getIdShortPath())
        
    def postSubmodelElem(self,data):
        try:
            _idShortpath = data["_idShortpath"]
            elemData = data["elemData"]
            aasSmParser = AASSubmodelParser(self.aasHashDict,self.submodelHashDict)
            _parentId = (_idShortpath.split("."))
            del _parentId[-1]
            if (elemData["modelType"] == "SubmodelElementCollection"):
                aasSmParser.parseSubmodelCollection(elemData, ".".join(_parentId))
            else:
                aasSmParser.parseDataElement(elemData, _parentId)
            return "Submodel element created successfully", True,201
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at postSubmodelElem DB" + str(E))
            return  "Internal Server Error", False,500
  
    def putSubmodelElem(self,data):
        try:
            _idShortpath = data["_idShortpath"]
            if self.aasHashDict.__isKeyPresent__(_idShortpath):
                data,status,statuscode = self.deleteSubmodelElem(_idShortpath)
                if status:
                    return self.PostSubmodelElement(data)
                    #aasHashObject = self.pyaas.aasHashDict.__getHashEntry__(_idShortpath)
                    #if len(aasHashObject.subscribers) > 0 and elemData["modelType"] == "Property":
                    #    subForword = SubscriptionMessage(_idShortpath,"dd",elemData["modelType"],aasHashObject.subscribers,elemData)
                    #    subForword.subscriptiondata = elemData
                    #    self.pyaas.listnerSockets["AAS_PUBSUB"].subscription_forward_messages.put(subForword)
                else:
                    return data,status,statuscode
            else:
                return "The Submodel element not found", False, 404
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at putSubmodelElem DB" + str(E))
            return  "Internal Server Error", False,500
    
    def deleteSubmodelElem(self,_idShortPath):
        try:
            if self.aasHashDict.__isKeyPresent__(_idShortPath):
                _id = (self.aasHashDict.__getHashEntry__(_idShortPath).__getId__())
                self.aasHashDict.__deleteHashEntry__(_idShortPath)
                elem = (self.submodelHashDict.__getHashEntry__(_id)).getElement()
                if (elem["modelType"] != "SubmodelElementCollection"):
                    self.submodelHashDict.__deleteHashEntry__(_id)
                else:
                    self.deleteCollectionElems(elem)
                return "Submodel element deleted successfully", True, 204
            else:
                return "The Submodel element not found", False, 404
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at deleteSubmodelElem DB" + str(E))
            return  "Internal Server Error", False,500

    def getSubmodelElement(self,_idShortPath):
        try:
            _id = (self.aasHashDict.__getHashEntry__(_idShortPath).__getId__())
            elem = (self.submodelHashDict.__getHashEntry__(_id)).getElement()
            if (elem["modelType"] != "SubmodelElementCollection"):
                return elem, True,200
            else:
                return self.processCollectionElements(elem), True,200
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at getSubmodelElement DB" + str(E))
            return  "Internal Server Error", False,500
      
    def GetAllSubmodelElements(self,aasIdentifier,submodelIdentifier):
        try:
            _submodel,status,statuscode = self.GetSubmodel(aasIdentifier,submodelIdentifier)
            if (status):
                if "submodelElements" in _submodel.keys():
                    return _submodel["submodelElements"], True,200
                else:
                    return [], True,200
            else:
                return _submodel,status,statuscode
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at GetAllSubmodelElements DB" + str(E))            
            return  "Internal Server Error", False,500

    def PostSubmodelElement(self,data):
        try:
            _shellId = data ["_shellId"]
            _submodelIdentifier = data["submodelIdentifier"]
            _elemData = data["elemData"]
            referencePresent = False
            if self.aasHashDict.__isKeyPresent__(_shellId):
                _id = (self.aasHashDict.__getHashEntry__(_shellId).__getId__())
                _shell = (self.aasShellHashDict.__getHashEntry__(_id)).getElement()
                for _reference in _shell["submodels"]:
                    if _reference["keys"][0]["value"] == _submodelIdentifier:
                        referencePresent = True
                        break
                if (referencePresent):
                    if self.aasHashDict.__isKeyPresent__(_submodelIdentifier):
                        idShortPath = _submodelIdentifier +"."+_elemData["idShort"]
                        if self.aasHashDict.__isKeyPresent__(idShortPath):
                            return "The submodel element is already present please try put",False,400                   
                        else:
                            aasSmParser = AASSubmodelParser(self.aasHashDict,self.submodelHashDict)
                            _newuuid = ""
                            if (_elemData["modelType"] == "SubmodelElementCollection"):
                                _newuuid = aasSmParser.parseSubmodelCollection(_elemData, _submodelIdentifier)
                            else:
                                _newuuid = aasSmParser.parseDataElement(_elemData, _submodelIdentifier)
                            _sid = (self.aasHashDict.__getHashEntry__(_submodelIdentifier).__getId__())
                            (self.submodelHashDict.__getHashEntry__(_sid)).aasELement["submodelElements"].append(_newuuid)
                            return "Submodel element created successfully", True,201                                 
                    else:
                        return "The submodel is not found", True,404             
                else:
                    return "The Asset administration shell does not refer to the submodel", False, 404
            else:
                return "The Asset administration shell not found", False, 404
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at PostSubmodelElement DB" + str(E))
            return  "Internal Server Error", False,500

    def GetSubmodelElementByPath(self,_shellId,_submodelIdentifier,idShortPath):
        try:
            referencePresent = False
            if self.aasHashDict.__isKeyPresent__(_shellId):
                _id = (self.aasHashDict.__getHashEntry__(_shellId).__getId__())
                _shell = (self.aasShellHashDict.__getHashEntry__(_id)).getElement()
                for _reference in _shell["submodels"]:
                    if _reference["keys"][0]["value"] == _submodelIdentifier:
                        referencePresent = True
                        break
                if (referencePresent):
                    if self.aasHashDict.__isKeyPresent__(_submodelIdentifier):
                        _idSHortPath = _submodelIdentifier +"." +idShortPath
                        if self.aasHashDict.__isKeyPresent__(_idSHortPath):
                            _sid = (self.aasHashDict.__getHashEntry__(_idSHortPath).__getId__())
                            submodelElem = (self.submodelHashDict.__getHashEntry__(_sid)).getElement()
                            if (submodelElem["modelType"] == "SubmodelElementCollection"):
                                return self.processCollectionElements(submodelElem), True,200
                            else:
                                return submodelElem,True,200
                        else:
                            return "The submodel element not found",False,404   
                    else:
                        return "The submodel is not found", False,404             
                else:
                    return "The Asset administration shell does not refer to the submodel", False, 404
            else:
                return "The Asset administration shell not found", False, 404
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at GetSubmodelElementByPath DB" + str(E))
            return  "Internal Server Error", False,500

    def DeleteSubmodelElementByPath(self,data):
        try:
            _shellId = data ["_shellId"]
            _submodelIdentifier = data ["submodelIdentifier"]
            referencePresent = False
            if self.aasHashDict.__isKeyPresent__(_shellId):
                _id = (self.aasHashDict.__getHashEntry__(_shellId).__getId__())
                _shell = (self.aasShellHashDict.__getHashEntry__(_id)).getElement()
                for _reference in _shell["submodels"]:
                    if _reference["keys"][0]["value"] == _submodelIdentifier:
                        referencePresent = True
                        break
                if (referencePresent):
                    if self.aasHashDict.__isKeyPresent__(_submodelIdentifier):
                        if self.aasHashDict.__isKeyPresent__(_submodelIdentifier+"."+data["idShortPath"]):
                            idShortSplit = (data["idShortPath"]).split(".")
                            if (len(idShortSplit) == 1):
                                _submodel_id = (self.aasHashDict.__getHashEntry__(_submodelIdentifier).__getId__())
                                _submodel = (self.submodelHashDict.__getHashEntry__(_submodel_id)).getElement()
                                _sumodelElemId =  (self.aasHashDict.__getHashEntry__(_submodelIdentifier+"."+data["idShortPath"]).__getId__())
                                _submodelElem = (self.submodelHashDict.__getHashEntry__(_sumodelElemId)).getElement()
                                if _sumodelElemId in _submodel["submodelElements"]:
                                    _submodel["submodelElements"].remove(_sumodelElemId)
                                    self.submodelHashDict.__getHashEntry__(_submodel_id).setElement(_submodel)
                                    if (_submodelElem["modelType"] == "SubmodelElementCollection"):
                                        self.deleteCollectionElems(_submodelElem)    
                                    self.submodelHashDict.__deleteHashEntry__(_sumodelElemId)
                                    self.aasHashDict.__deleteHashEntry__(_submodelIdentifier+"."+data["idShortPath"])
                                    return "Submodel element deleted successfully", True, 204
                                else:
                                    return "THe Submodel element is not found in the submodel", False,404
                            else:
                                _parentId = _submodelIdentifier+"."+".".join(idShortSplit[:-1])
                                if self.aasHashDict.__isKeyPresent__(_parentId):
                                    _pid = (self.aasHashDict.__getHashEntry__(_parentId).__getId__())
                                    parentElement = (self.submodelHashDict.__getHashEntry__(_pid)).getElement()
                                    if (parentElement["modelType"] == "SubmodelElementCollection"):
                                        _sumodelElemId =  (self.aasHashDict.__getHashEntry__(_submodelIdentifier+"."+data["idShortPath"]).__getId__())
                                        _submodelElem = (self.submodelHashDict.__getHashEntry__(_sumodelElemId)).getElement()
                                        if (_submodelElem["modelType"] == "SubmodelElementCollection"):
                                            self.deleteCollectionElems(_submodelElem)
                                        self.submodelHashDict.__deleteHashEntry__(_sumodelElemId)
                                        self.aasHashDict.__deleteHashEntry__(_submodelIdentifier+"."+data["idShortPath"])
                                        parentElement["value"].remove(_sumodelElemId)
                                        self.submodelHashDict.__getHashEntry__(_pid).setElement(parentElement)
                                        return "Submodel element deleted successfully", True, 204                                    
                                    else:
                                        return "The submodel element is not valid at this location", False, 400
                                else:
                                    return "The parent element does not exist",False,400
                        else:
                            return "The submodel element is not found",False,404                   
                    else:
                        return "The submodel is not found", False,404             
                else:
                    return "The Asset administration shell does not refer to the submodel", False, 404
            else:
                return "The Asset administration shell not found", False, 404
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at DeleteSubmodelElementByPath DB" + str(E))
            return  "Internal Server Error", False,500

    def PostSubmodelElementByPath(self,data):
        try:
            _shellId = data ["_shellId"]
            _submodelIdentifier = data ["submodelIdentifier"]
            _elemData = data["elemData"]
            referencePresent = False
            if self.aasHashDict.__isKeyPresent__(_shellId):
                _id = (self.aasHashDict.__getHashEntry__(_shellId).__getId__())
                _shell = (self.aasShellHashDict.__getHashEntry__(_id)).getElement()
                for _reference in _shell["submodels"]:
                    if _reference["keys"][0]["value"] == _submodelIdentifier:
                        referencePresent = True
                        break
                if (referencePresent):
                    if self.aasHashDict.__isKeyPresent__(_submodelIdentifier):
                        _idSHortPath = _submodelIdentifier +"." +data["idShortPath"] + _elemData["idShort"]
                        if self.aasHashDict.__isKeyPresent__(_idSHortPath):
                            return "The submodel element is already present please try put",False,400
                        else:
                            idShortSplit = (data["idShortPath"]).split(".")
                            aasSmParser = AASSubmodelParser(self.aasHashDict,self.submodelHashDict)
                            _newuuid = ""
                            if len(idShortSplit) == 1:
                                if (_elemData["modelType"] == "SubmodelElementCollection"):
                                    _newuuid = aasSmParser.parseSubmodelCollection(_elemData, _submodelIdentifier)
                                else:
                                    _newuuid = aasSmParser.parseDataElement(_elemData, _submodelIdentifier)
                                _sid = (self.aasHashDict.__getHashEntry__(_submodelIdentifier).__getId__())
                                (self.submodelHashDict.__getHashEntry__(_sid)).aasELement["submodelElements"].append(_newuuid)
                                return "Submodel element created successfully", True,201
                            else:
                                _parentId = _submodelIdentifier +"." + data["idShortPath"]
                                if  self.aasHashDict.__isKeyPresent__(_parentId):
                                    _pid = (self.aasHashDict.__getHashEntry__(_parentId).__getId__())
                                    parentElement = (self.submodelHashDict.__getHashEntry__(_pid)).getElement()
                                    _newuuid = ""
                                    if (parentElement["modelType"] == "SubmodelElementCollection"):
                                        if (_elemData["modelType"] == "SubmodelElementCollection"):
                                            _newuuid = aasSmParser.parseSubmodelCollection(_elemData, _parentId)
                                        else:
                                            _newuuid = aasSmParser.parseDataElement(_elemData, _parentId)
                                        (self.submodelHashDict.__getHashEntry__(_pid)).aasELement["value"].append(_newuuid)
                                        return "Submodel element created successfully", True,201                                    
                                    else:
                                        return "The new element cannot be created at this place",False,400
                                else:
                                    return "The parent element does not exist",False,400 
                                
                    else:
                        return "The submodel is not found", False,404             
                else:
                    return "The Asset administration shell does not refer to the submodel", False, 404
            else:
                return "The Asset administration shell not found", False, 404
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at PostSubmodelElementByPath DB" + str(E))
            return  "Internal Server Error", False,500

    def PutSubmodelElementByPath(self,data):
        try:
            _idShortpath = data["idShortPath"]
            if self.aasHashDict.__isKeyPresent__(data["submodelIdentifier"]+"."+_idShortpath):
                data1,status1,statuscode1 = self.DeleteSubmodelElementByPath(data)
                if status1:
                    idShortSplit = _idShortpath.split(".") 
                    data["idShortPath"] = ".".join(idShortSplit[:-1])
                    if len(idShortSplit) == 1:
                        data2,status2,statuscode2 = self.PostSubmodelElement(data)
                        if status2:
                            return "Submodel element updated successfully", True,204
                        else:
                            return data2,status2,statuscode2
                    else:
                        data3,status3,statuscode3 = self.PostSubmodelElementByPath(data)
                        if status3:
                            return "Submodel element updated successfully", True,204
                        else:
                            return data3,status3,statuscode3
                else:
                    return data1,status1,statuscode1
            else:
                return "The Submodel element not found", False, 404
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at PutSubmodelElementByPath DB" + str(E))
            return  "Internal Server Error", False,500        

    def GetSubmodelElementByPath_History(self,_shellId,_submodelIdentifier,idShortPath):
        try:
            referencePresent = False
            if self.aasHashDict.__isKeyPresent__(_shellId):
                _id = (self.aasHashDict.__getHashEntry__(_shellId).__getId__())
                _shell = (self.aasShellHashDict.__getHashEntry__(_id)).getElement()
                for _reference in _shell["submodels"]:
                    if _reference["keys"][0]["value"] == _submodelIdentifier:
                        referencePresent = True
                        break
                if (referencePresent):
                    if self.aasHashDict.__isKeyPresent__(_submodelIdentifier):
                        _idSHortPath = _submodelIdentifier +"." +idShortPath
                        if self.aasHashDict.__isKeyPresent__(_idSHortPath):
                            _sid = (self.aasHashDict.__getHashEntry__(_idSHortPath).__getId__())
                            historyObjects = (self.submodelHashDict.__getHashEntry__(_sid)).getHistory()
                            historyData = {"values": [], "label" :[]}
                            labels = []
                            labels_dif = []
                            if len(historyObjects) > 0:
                                for hObject in historyObjects[-25:]:
                                    labels.append(hObject.timestamp)
                                    historyData["values"].append((hObject.aasElementValue))
                                historyData["label"].append(0)
                                labels_dif.append(0)
                            for i in range(1,len(labels)):
                                labels_dif.append((labels[i]-labels[i-1]).seconds)
                                
                            for i in range(0,len(labels_dif)-1):
                                historyData["label"].append((labels_dif[i]+labels_dif[i+1]))                                
                            
                            print(historyData)
                            return historyData,True,200
                        else:
                            return "The submodel element not found",False,404   
                    else:
                        return "The submodel is not found", False,404             
                else:
                    return "The Asset administration shell does not refer to the submodel", False, 404
            else:
                return "The Asset administration shell not found", False, 404
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at GetSubmodelElementByPath_History DB" + str(E))
            return  "Internal Server Error", False,500

    def GetFileByPath(self,_shellId,_submodelIdentifier,idShortPath):
        try:
            referencePresent = False
            if self.aasHashDict.__isKeyPresent__(_shellId):
                _id = (self.aasHashDict.__getHashEntry__(_shellId).__getId__())
                _shell = (self.aasShellHashDict.__getHashEntry__(_id)).getElement()
                for _reference in _shell["submodels"]:
                    if _reference["keys"][0]["value"] == _submodelIdentifier:
                        referencePresent = True
                        break
                if (referencePresent):
                    if self.aasHashDict.__isKeyPresent__(_submodelIdentifier):
                        _idSHortPath = _submodelIdentifier +"." +idShortPath
                        if self.aasHashDict.__isKeyPresent__(_idSHortPath):
                            _sid = (self.aasHashDict.__getHashEntry__(_idSHortPath).__getId__())
                            submodelElem = (self.submodelHashDict.__getHashEntry__(_sid)).getElement()
                            if (submodelElem["modelType"] != "File"):
                                return "A file is not associated at the specified path", False,404
                            else:
                                return submodelElem["value"], True,200
                        else:
                            return "The submodel element not found",False,404   
                    else:
                        return "The submodel is not found", False,404             
                else:
                    return "The Asset administration shell does not refer to the submodel", False, 404
            else:
                return "The Asset administration shell not found", False, 404
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at GetFileByPath DB" + str(E))
            return  "Internal Server Error", False,500

    def PutFileByPath(self,data):
        try:
            _idShortpath = data["idShortPath"]
            if self.aasHashDict.__isKeyPresent__(data["submodelIdentifier"]+"."+_idShortpath):
                _sid = (self.aasHashDict.__getHashEntry__(data["submodelIdentifier"]+"."+_idShortpath).__getId__())
                submodelElem = (self.submodelHashDict.__getHashEntry__(_sid)).getElement()
                if (submodelElem["modelType"] != "File"):
                    return "A file is not associated at the specified path", False,404
                else:
                    filePath = (submodelElem["value"]).split("/")[:-1]
                    _newPathValue = "/".join(filePath) + "/" + data["elemData"]
                    submodelElem["value"] = _newPathValue
                    submodelElem["contentType"] = data["mimeType"]
                    data["elemData"] = submodelElem
                    data1,status1,statuscode1 = self.DeleteSubmodelElementByPath(data)
                    if status1:
                        data2,status2,statuscode2 = self.PostSubmodelElementByPath(data)
                        if status2:
                            return _newPathValue, True,204
                        else:
                            return data2,status2,statuscode2
                    else:
                        return data1,status1,statuscode1
            else:
                return "The Submodel element not found", False, 404
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at PutFileByPath DB" + str(E))
            return  "Internal Server Error", False,500 
    
  
    '''
        Concept Description Repository Interface start
    '''
  
    def  GetAllConceptDescriptions(self):
        try:
            _conceptDescriptions = []
            for _id in self.cdHashDict._getKeys():
                _conceptDescriptions.append(self.cdHashDict.__getHashEntry__(_id).getElement())
            return _conceptDescriptions,True,200
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at GetAllConceptDescriptions DB" + str(E))
            return  "Internal Server Error", False,500

    def  GetAllConceptDescriptionsByIdShort(self,idShort):
        try:
            _conceptDescriptions = []
            for _id in self.cdHashDict._getKeys():
                _cD = self.cdHashDict.__getHashEntry__(_id).getElement()
                try:
                    if idShort == _cD["idShort"]:
                        _conceptDescriptions.append(_cD)
                except:
                    pass
            return _conceptDescriptions,True,200
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at GetAllConceptDescriptionsByIdShort DB" + str(E))
            return  "Internal Server Error", False,500

    def  GetAllConceptDescriptionsByIsCaseOf(self,isCaseValue):
        try:
            _conceptDescriptions = []
            for _id in self.cdHashDict._getKeys():
                _cD = self.cdHashDict.__getHashEntry__(_id).getElement()
                try:    
                    keys = []
                    for _ref in _cD["isCaseOf"]:
                        keys.extend([key["value"] for key in _ref["keys"]])
                    if isCaseValue in keys:
                        _conceptDescriptions.append(_cD)
                except:
                    pass
            return _conceptDescriptions,True,200
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at GetAllConceptDescriptionsByIsCaseOf DB" + str(E))
            return  "Internal Server Error", False,500

    def  GetAllConceptDescriptionsByDataSpecificationReference(self,dataSpecificationRef):
        try:
            _conceptDescriptions = []
            for _id in self.cdHashDict._getKeys():
                _cD = self.cdHashDict.__getHashEntry__(_id).getElement()
                try:
                    keys = []
                    for _ref in _cD["dataSpecifications"]:
                        keys.extend([key["value"] for key in _ref["keys"]])
                    if dataSpecificationRef in keys:
                        _conceptDescriptions.append(_cD)
                except:
                    pass
            return _conceptDescriptions,True,200
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at GetAllConceptDescriptionsByDataSpecificationReference DB" + str(E))
            return  "Internal Server Error", False,500

    def PostConceptDescription(self,data):
        try:
            _newId = data["_cd"]["id"]
            if self.aasHashDict.__isKeyPresent__(_newId):
                return "The conception already already exist please try put",False,400
            else:
                cdParse = ConceptionDescriptionParser(self.aasHashDict,self.cdHashDict)
                cdParse.parse(data["_cd"])
            return "Concept Description created successfully",True,201
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at PostConceptDescription DB" + str(E))
            return  "Internal Server Error", False,500

    def GetConceptDescriptionById(self,_conceptDescriptionId):
        try:
            if self.aasHashDict.__isKeyPresent__(_conceptDescriptionId):
                _id = self.aasHashDict.__getHashEntry__(_conceptDescriptionId).__getId__()
                _conceptDescription= self.cdHashDict.__getHashEntry__(_id).getElement()
                return _conceptDescription,True,200
            else:
                return "The conception description is not found",False,404
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at GetConceptDescriptionById DB" + str(E))
            return  "Internal Server Error", False,500

    def DeleteConceptDescriptionById(self,_conceptDescriptionId):
        try:
            if self.aasHashDict.__isKeyPresent__(_conceptDescriptionId):
                _id = (self.aasHashDict.__getHashEntry__(_conceptDescriptionId).__getId__())
                self.cdHashDict.__deleteHashEntry__(_id)
                self.aasHashDict.__deleteHashEntry__(_conceptDescriptionId)
                return "Concept Description deleted successfully", True,204
            else:
                return "The Concept Description not found",False,404
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at getAASShells DB" + str(E))
            return  "Internal Server Error", False,500    

    def PutConceptDescriptionById(self,data):
        try:
            msg,status,statuscode = self.DeleteConceptDescriptionById(data["_conceptDescriptionId"])
            if (status):
                msg1,status1,statuscode1 = self.PostConceptDescription(data)
                if (status1):
                    return "Concept Description updated successfully", True,204
                else:
                    return msg1,status1,statuscode1
            else:
                return msg,status,statuscode
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at PutConceptDescriptionById DB" + str(E))
            return  "Internal Server Error", False,500
  
    '''
        Concept Description Repository Interface End
    '''



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
            self.pyAAS.serviceLogger.info("Error at getInformations DB" + str(E))
            return  str(E) + "Unexpected Error", False     
 
    '''
        Asset Administration Shell Interface start
    '''
    def GetAssetAdministrationShell(self,_shellId):
        try:
            if not self.aasHashDict.__isKeyPresent__(_shellId):
                return "The Asset administration shell not found", False, 404
            else:
                _id = self.aasHashDict.__getHashEntry__(_shellId)._id
                _aasShell = self.aasShellHashDict.__getHashEntry__(_id).getElement()
                return _aasShell,True,200
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at GetAssetAdministrationShell DB" + str(E))
            return  "Internal Server Error", False,500 

    def PutAssetAdministrationShell(self,data):
        try:
            msg,status,statuscode = self.DeleteAssetAdministrationShellById(data["_shellId"])
            if (status):
                msg1,status1,statuscode1 =  self.PostAssetAdministrationShell(data["_aasShell"])
                if (status1):
                    return "Asset Administration Shell updated successfully",True,204
                else:
                    return msg1,status1,statuscode1
            else:
                return msg,status,statuscode
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at PutAssetAdministrationShell DB" + str(E))
            return  "Internal Server Error", False,500
 
    def GetAllSubmodelReferences(self,_shellId):
        try:
            if not self.aasHashDict.__isKeyPresent__(_shellId):
                return "The Asset administration shell not found", False, 404
            else:
                submodelRefs = []
                _id = self.aasHashDict.__getHashEntry__(_shellId)._id
                _aasShell = self.aasShellHashDict.__getHashEntry__(_id).getElement()
                for _submodelRef in _aasShell["submodels"]:
                    submodelRefs.append(_submodelRef)
                return submodelRefs, True,200                
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at GetAllSubmodelReferences DB" + str(E))
            return  "Internal Server Error", False,500         
   
    def PostSubmodelReference(self,data):
        try:
            _shellId = data ["_shellId"]
            if not self.aasHashDict.__isKeyPresent__(_shellId):
                return "The Asset administration shell not found", False, 404
            else:
                _submodelRef = data["_Reference"]
                _id = self.aasHashDict.__getHashEntry__(_shellId).__getId__()
                _aasShell = self.aasShellHashDict.__getHashEntry__(_id).getElement()
                _aasShell["submodels"].append(_submodelRef)
                self.aasShellHashDict.__getHashEntry__(_id).setElement(_aasShell)
                return "Submodel reference created successfully", True,201
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at PostSubmodelReference DB" + str(E))
            return  "Internal Server Error", False,500

    def DeleteSubmodelReference(self,data):
        try:
            if self.aasHashDict.__isKeyPresent__(data["_shellId"]):
                _id = (self.aasHashDict.__getHashEntry__(data["_shellId"]).__getId__())
                _aasShell = self.aasShellHashDict.__getHashEntry__(_id).getElement()
                for index, submodelRef in  enumerate(_aasShell["submodels"]):
                    if submodelRef["keys"][0]["value"] == data["submodelIdentifier"]:
                        del _aasShell["submodels"][index]
                        return "Submodel reference deleted successfully", True,204
                return "The submodel reference not found",False,404
            else:
                return "Asset Administration shell not found",False,404
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at DeleteSubmodelReference DB" + str(E))
            return  "Internal Server Error", False,500  

    def GetAssetInformation(self,_shellId):
        try:
            if self.aasHashDict.__isKeyPresent__(_shellId):
                _id = self.aasHashDict.__getHashEntry__(_shellId).__getId__()
                _aasShell = self.aasShellHashDict.__getHashEntry__(_id).getElement()
                return _aasShell["assetInformation"], True,200
            else:
                return "Asset Administration shell not found",False,404
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at GetAssetInformation DB" + str(E))
            return  "Internal Server Error", False,500

    def PutAssetInformation(self,data):
        try:
            if self.aasHashDict.__isKeyPresent__(data["_shellId"]):
                _id = self.aasHashDict.__getHashEntry__(data["_shellId"]).__getId__()
                _aasShell = self.aasShellHashDict.__getHashEntry__(_id).getElement()
                _aasShell["assetInformation"] = data["_assetInformation"]
                self.aasShellHashDict.__getHashEntry__(_id).aasELement  = _aasShell
                return "Asset Information updated successfully",True,204
            else:
                return "Asset Administration shell not found",False,404
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at PutAssetInformation DB" + str(E))
            return  "Internal Server Error", False,500
    
    '''
       Shell Repository Interface Begin
    '''
    def GetAllAssetAdministrationShells(self):
        try:
            _aasShells = []
            for _id in self.aasShellHashDict._getKeys():
                _aasShells.append(self.aasShellHashDict.__getHashEntry__(_id).getElement())
            return _aasShells, True,200
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at GetAllAssetAdministrationShells DB" + str(E))
            return  "Internal Server Error", False,500

    def GetAllAssetAdministrationShellsByAssetId(self,_shellId):
        try:
            _aasShells = []
            for _id in self.aasShellHashDict.__getKeys():
                shell = self.aasShellHashDict.__getHashEntry__(_id)
                for assetRef in shell["asset"]["keys"]:
                    if assetRef["value"] == _shellId:
                        _aasShells.append(shell)  
            return _aasShells, True,200
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at getAASShells DB" + str(E))
            return  "Internal Server Error", False,500  
    
    def GetAllAssetAdministrationShellsByIdShort(self,_shellId):
        try:
            _aasShells = []
            for _id in self.aasShellHashDict.__getKeys():
                shell = self.aasShellHashDict.__getHashEntry__(_id)
                if shell["idShort"] == _shellId:
                    _aasShells.append(shell)  
            return _aasShells, True,200
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at getAASShells DB" + str(E))
            return  "Internal Server Error", False,500                   

    def GetAssetAdministrationShellById(self,_shellId):
        try:
            if not self.aasHashDict.__isKeyPresent__(_shellId):
                return "The Asset administration shell not found", False, 404
            else:
                _id = self.aasHashDict.__getHashEntry__(_shellId)._id
                _aasShell = self.aasShellHashDict.__getHashEntry__(_id).getElement()
                return _aasShell,True,200
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at GetAssetAdministrationShellById DB" + str(E))
            return  "Internal Server Error", False,500 
        
    def PostAssetAdministrationShell(self,_aasShell):
        try:
            aasShellParser = AASShellParser(self.aasHashDict,self.submodelHashDict,self.aasShellHashDict)
            aasShellParser.parse(_aasShell)
            return "Asset Administration Shell created successfully", True,201
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at PostAssetAdministrationShell DB" + str(E))
            return  "Internal Server Error", False,500    
    
    def PutAssetAdministrationShellById(self,data):
        try:
            msg,status,statuscode = self.DeleteAssetAdministrationShellById(data["_shellId"])
            if (status):
                msg1,status1,statuscode1 =  self.PostAssetAdministrationShell(data["_aasShell"])
                if (status1):
                    return "Asset Administration Shell updated successfully",True,204
                else:
                    return msg1,status1,statuscode1
            else:
                return msg,status,statuscode
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at PutAssetAdministrationShellById DB" + str(E))
            return  "Internal Server Error", False,500

    def DeleteAssetAdministrationShellById(self,_shellId):
        try:
            if _shellId not in self.aasHashDict._getKeys():
                return "The Asset administration shell not found", False, 404
            else:
                _id = (self.aasHashDict.__getHashEntry__(_shellId).__getId__())
                self.aasShellHashDict.__deleteHashEntry__(_id)
                self.aasHashDict.__deleteHashEntry__(_shellId)
            return "Asset Administration Shell deleted successfully", True, 204
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at DeleteAssetAdministrationShellById DB" + str(E))
            return  "Internal Server Error", False,500      

    '''
       Shell Repository Interface End
    '''

#additiona start
    def GetSubmodels_shell(self,aasIdentifier1):
        try:
            submodels = []
            _shellId = aasIdentifier1
            if self.aasHashDict.__isKeyPresent__(_shellId):
                _id = (self.aasHashDict.__getHashEntry__(_shellId).__getId__())
                _shell = (self.aasShellHashDict.__getHashEntry__(_id)).getElement()
                for _reference in _shell["submodels"]:
                    _submodelIdentifier = _reference["keys"][0]["value"]
                    if self.aasHashDict.__isKeyPresent__(_submodelIdentifier):
                        _id = (self.aasHashDict.__getHashEntry__(_submodelIdentifier).__getId__())
                        _submodel = (self.submodelHashDict.__getHashEntry__(_id)).getElement() 
                        i = 0
                        if "submodelElements" in _submodel.keys():            
                            for submodelElem in _submodel["submodelElements"]:
                                _submodelid = (self.submodelHashDict.__getHashEntry__(submodelElem)).getIdShortPath()
                                data, status,statuscode = self.getSubmodelElement(_submodelid)
                                if (status):
                                    _submodel["submodelElements"][i] = data
                                    i = i + 1
                                else:
                                    return data, status,statuscode
                            submodels.append(_submodel)
                    else:
                        return "The submodel is not found", False,404             
                return submodels,True,200
            else:
                return "The Asset administration shell not found", False, 404
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at GetSubmodel DB" + str(E))
            return  "Internal Server Error", False,500

#additional end

    def GetSubmodel(self,_shellId,_submodelIdentifier):
        try:
            referencePresent = False
            if self.aasHashDict.__isKeyPresent__(_shellId):
                _id = (self.aasHashDict.__getHashEntry__(_shellId).__getId__())
                _shell = (self.aasShellHashDict.__getHashEntry__(_id)).getElement()
                for _reference in _shell["submodels"]:
                    if _reference["keys"][0]["value"] == _submodelIdentifier:
                        referencePresent = True
                        break
                if (referencePresent):
                    if self.aasHashDict.__isKeyPresent__(_submodelIdentifier):
                        _id = (self.aasHashDict.__getHashEntry__(_submodelIdentifier).__getId__())
                        _submodel = (self.submodelHashDict.__getHashEntry__(_id)).getElement() 
                        i = 0
                        if "submodelElements" in _submodel.keys():                   
                            for submodelElem in _submodel["submodelElements"]:
                                _submodelid = (self.submodelHashDict.__getHashEntry__(submodelElem)).getIdShortPath()
                                data, status,statuscode = self.getSubmodelElement(_submodelid)
                                if (status):
                                    _submodel["submodelElements"][i] = data
                                    i = i + 1
                                else:
                                    return data, status,statuscode
                        return _submodel, True,200   
                    else:
                        return "The submodel is not found", True,404             
                else:
                    return "The Asset administration shell does not refer to the submodel", False, 404
            else:
                return "The Asset administration shell not found", False, 404
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at GetSubmodel DB" + str(E))
            return  "Internal Server Error", False,500
       
    def PutSubmodel(self,data):
        try:
            _shellId = data ["_shellId"]
            _submodelIdentifier = data ["submodelIdentifier"]
            referencePresent = False
            if self.aasHashDict.__isKeyPresent__(_shellId):
                _id = (self.aasHashDict.__getHashEntry__(_shellId).__getId__())
                _shell = (self.aasShellHashDict.__getHashEntry__(_id)).getElement()
                for _reference in _shell["submodels"]:
                    if _reference["keys"][0]["value"] == _submodelIdentifier:
                        referencePresent = True
                if (referencePresent):
                    data1,status1,statuscode1 =  self.DeleteSubmodelById(_submodelIdentifier)
                    if status1:
                        aasSmParser = AASSubmodelParser(self.aasHashDict,self.submodelHashDict)
                        aasSmParser.parse(data["submodelData"])
                        return "Submodel updated successfully", True,204
                    else:
                        return data1,status1,statuscode1
                else:
                    return "The Asset administration shell does not refer to the submodel", False, 404
            else:
                return "The Asset administration shell not found", False, 404
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at GetSubmodel DB" + str(E))
            return  "Internal Server Error", False,500
        
    def getSubmodel(self,_submodelid):
        try:
            if self.aasHashDict.__isKeyPresent__(_submodelid):
                _submodel = dict()
                _id = (self.aasHashDict.__getHashEntry__(_submodelid).__getId__())
                _submodel = (self.submodelHashDict.__getHashEntry__(_id)).getElement()
                i = 0
                if "submodelElements" in _submodel.keys():
                    for submodelElem in _submodel["submodelElements"]:
                        _submodelid = (self.submodelHashDict.__getHashEntry__(submodelElem)).getIdShortPath()
                        data, status,statuscode = self.getSubmodelElement(_submodelid)
                        if (status):
                            _submodel["submodelElements"][i] = data
                        else:
                            return data, status,statuscode
                        i = i + 1
                return _submodel, True,200
            else:
                return "The submodel not found", False, 404
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at getSubmodel DB" + str(E))
            return  "Internal Server Error", False,500  
                 

    '''
   Submodel Repository Interface Start
    '''

    def GetAllSubmodels(self):
        try:
            _submodels = []
            for _id in self.submodelHashDict._getKeys():
                if self.submodelHashDict.__getHashEntry__(_id).modelType == "Submodel":
                    _submodelId = self.aasHashDict.__getkey__(_id)
                    submodel,status,statuscode = self.getSubmodel(_submodelId)
                    if status:
                        _submodels.append(submodel)
                    else:
                        return submodel,status,statuscode
            return _submodels, True,200
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at GetAllSubmodels DB" + str(E))
            return  "Internal Server Error", False,500

    def GetAllSubmodelsByIdShort(self,idShort):
        try:
            _submodels = []
            for _id in self.submodelHashDict._getKeys():
                hashEntry = self.submodelHashDict.__getHashEntry__(_id)
                if hashEntry.modelType == "Submodel" and hashEntry.idShort == idShort:
                    _submodelId = self.aasHashDict.__getkey__(_id)
                    submodel,status,statuscode = self.getSubmodel(_submodelId)
                    if status:
                        _submodels.append(submodel)
                    else:
                        return submodel,status,statuscode
            return _submodels, True,200
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at GetAllSubmodelsByIdShort DB" + str(E))
            return  "Internal Server Error", False,500

    def GetAllSubmodelsBySemanticId(self,semanticId):
        try:
            _submodels = []
            for _id in self.submodelHashDict._getKeys():
                hashEntry = self.submodelHashDict.__getHashEntry__(_id)
                if hashEntry.modelType == "Submodel":
                    _submodelTemp = hashEntry.getElement()
                    _keys = []
                    for key in _submodelTemp["semanticId"]["keys"]:
                        _keys.append(key["value"])
                    if semanticId in _keys: 
                        _submodelId = self.aasHashDict.__getkey__(_id)
                        submodel,status,statuscode = self.getSubmodel(_submodelId)
                        if status:
                            _submodels.append(submodel)
                        else:
                            return submodel,status,statuscode
            return _submodels, True,200
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at GetAllSubmodelsBySemanticId DB" + str(E))
            return  "Internal Server Error", False,500

    def PostSubmodel(self,submodelData):
        try:
            if self.aasHashDict.__isKeyPresent__(submodelData["_submodel"]["id"]):
                return "The submodel is already present please try put",False,400
            else:
                aasSmParser = AASSubmodelParser(self.aasHashDict,self.submodelHashDict)
                aasSmParser.parse(submodelData["_submodel"])
            return "Submodel created successfully",True,201
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at PostSubmodel DB" + str(E))
            return  "Internal Server Error", False,500     

    def GetSubmodelById(self,submodelIdentifier):
        try:
            submodel,status,statuscode = self.getSubmodel(submodelIdentifier)
            if status:
                return submodel,status,statuscode
            else:   
                return submodel,status,statuscode
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at GetSubmodelById DB" + str(E))
            return  "Internal Server Error", False,500

    def PutSubmodelById(self,data):
        try:
            msg,status,statuscode = self.DeleteSubmodelById(data["submodelIdentifier"])
            if (status):
                msg1,status1,statuscode1 = self.PostSubmodel(data)
                if status1:
                    return  "Submodel updated successfully", True,201
                else:
                    return msg1,status1,statuscode1
            else:
                return msg,status,statuscode
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at PutSubmodelById DB" + str(E))
            return  "Internal Server Error", False,500

    def DeleteSubmodelById(self,_submodelid):
        try:
            if self.aasHashDict.__isKeyPresent__(_submodelid):
                _id = (self.aasHashDict.__getHashEntry__(_submodelid).__getId__())
                _submodel = (self.submodelHashDict.__getHashEntry__(_id)).getElement()
                if "submodelElements" in _submodel.keys():
                    for uuid in _submodel["submodelElements"]:
                        _key = self.aasHashDict.__getkey__(uuid)
                        self.deleteSubmodelElem(_key)
                    self.submodelHashDict.__deleteHashEntry__(_id)
                    self.aasHashDict.__deleteHashEntry__(_submodelid)
                return "Submodel deleted Successfully", True,204
            else:
                return "Submodel not found", False,404
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at DeleteSubmodelById DB" + str(E))
            return  "Internal Server Error", False,500    

    def GetSubmodel_SRI(self,_submodelIdentifier):
        try:
            if self.aasHashDict.__isKeyPresent__(_submodelIdentifier):
                _id = (self.aasHashDict.__getHashEntry__(_submodelIdentifier).__getId__())
                _submodel = (self.submodelHashDict.__getHashEntry__(_id)).getElement() 
                i = 0
                if "submodelElements" in _submodel.keys():                   
                    for submodelElem in _submodel["submodelElements"]:
                        _submodelid = (self.submodelHashDict.__getHashEntry__(submodelElem)).getIdShortPath()
                        data, status,statuscode = self.getSubmodelElement(_submodelid)
                        if (status):
                            _submodel["submodelElements"][i] = data
                            i = i + 1
                        else:
                            return data, status,statuscode
                return _submodel, True,200   
            else:
                        return "The submodel is not found", True,404             
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at GetSubmodel_SRI DB" + str(E))
            return  "Internal Server Error", False,500

    def PutSubmodel_SRI(self,data):
        try:
            data1,status1,statuscode1 =  self.DeleteSubmodelById(data["submodelIdentifier"])
            if status1:
                aasSmParser = AASSubmodelParser(self.aasHashDict,self.submodelHashDict)
                aasSmParser.parse(data["_submodel"])
                return "Submodel updated successfully", True,204
            else:
                return data1,status1,statuscode1 
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at PutSubmodel_SRI DB" + str(E))
            return  "Internal Server Error", False,500

    def GetAllSubmodelElements_SRI(self,data):
        try:
            if self.aasHashDict.__isKeyPresent__(data["submodelIdentifier"]):
                _submodelElements = []
                _id = (self.aasHashDict.__getHashEntry__(data["submodelIdentifier"]).__getId__())
                _submodel = (self.submodelHashDict.__getHashEntry__(_id)).getElement() 
                i = 0   
                if "submodelElements" in _submodel.keys():                
                    for submodelElem in _submodel["submodelElements"]:
                        _submodelid = (self.submodelHashDict.__getHashEntry__(submodelElem)).getIdShortPath()
                        data1, status,statuscode = self.getSubmodelElement(_submodelid)
                        if (status):
                            _submodelElements.append(data1)
                            i = i + 1
                        else:
                            return data1, status,statuscode
                return _submodelElements, True,200   
            else:
                return "The submodel is not found", True,404   
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at GetAllSubmodelElements_SRI DB" + str(E))            
            return  "Internal Server Error", False,500

    def PostSubmodelElement_SRI(self,data):
        try:
            _submodelIdentifier = data["submodelIdentifier"]
            _elemData = data["elemData"]
            if self.aasHashDict.__isKeyPresent__(_submodelIdentifier):
                idShortPath = _submodelIdentifier +"."+_elemData["idShort"]
                if self.aasHashDict.__isKeyPresent__(idShortPath):
                    return "Submodel element is already present please try put",False,400
                else:
                    aasSmParser = AASSubmodelParser(self.aasHashDict,self.submodelHashDict)
                    _newuuid = ""
                    if (_elemData["modelType"] == "SubmodelElementCollection"):
                        _newuuid = aasSmParser.parseSubmodelCollection(_elemData, _submodelIdentifier)
                    else:
                        _newuuid = aasSmParser.parseDataElement(_elemData, _submodelIdentifier)
                    _sid = (self.aasHashDict.__getHashEntry__(_submodelIdentifier).__getId__())
                    (self.submodelHashDict.__getHashEntry__(_sid)).aasELement["submodelElements"].append(_newuuid)
                    return "Submodel Element is created Successfully",True,201
            else:
                return "The submodel is not found", True,404             
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at PostSubmodelElement_SRI DB" + str(E))
            return  "Internal Server Error", False,500

    def GetSubmodelElementByPath_SRI(self,_submodelIdentifier,idShortPath):
        try:
            if self.aasHashDict.__isKeyPresent__(_submodelIdentifier):
                _idSHortPath = _submodelIdentifier +"." + idShortPath
                if self.aasHashDict.__isKeyPresent__(_idSHortPath):
                    _sid = (self.aasHashDict.__getHashEntry__(_idSHortPath).__getId__())
                    submodelElem = (self.submodelHashDict.__getHashEntry__(_sid)).getElement()
                    if (submodelElem["modelType"] == "SubmodelElementCollection"):
                        return self.processCollectionElements(submodelElem), True,200
                    else:
                        return submodelElem,True,200
                else:
                    return "The submodel element not found",False,404   
            else:
                return "The submodel is not found", False,404             
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at GetSubmodelElementByPath_SRI DB" + str(E))
            return  "Internal Server Error", False,500

    def DeleteSubmodelElementByPath_SRI(self,data):
        try:
            _submodelIdentifier = data ["submodelIdentifier"]
            if self.aasHashDict.__isKeyPresent__(_submodelIdentifier):
                if self.aasHashDict.__isKeyPresent__(_submodelIdentifier+"."+data["idShortPath"]):
                    idShortSplit = (data["idShortPath"]).split(".")
                    if (len(idShortSplit) == 1):
                        _submodel_id = (self.aasHashDict.__getHashEntry__(_submodelIdentifier).__getId__())
                        _submodel = (self.submodelHashDict.__getHashEntry__(_submodel_id)).getElement()
                        _sumodelElemId =  (self.aasHashDict.__getHashEntry__(_submodelIdentifier+"."+data["idShortPath"]).__getId__())
                        _submodelElem = (self.submodelHashDict.__getHashEntry__(_sumodelElemId)).getElement()
                        if "submodelElements" in _submodel.keys():
                            if _sumodelElemId in _submodel["submodelElements"]:
                                _submodel["submodelElements"].remove(_sumodelElemId)
                                self.submodelHashDict.__getHashEntry__(_submodel_id).setElement(_submodel)
                                if (_submodelElem["modelType"] == "SubmodelElementCollection"):
                                    self.deleteCollectionElems(_submodelElem)    
                                self.submodelHashDict.__deleteHashEntry__(_sumodelElemId)
                                self.aasHashDict.__deleteHashEntry__(_submodelIdentifier+"."+data["idShortPath"])
                                return "Submodel element deleted successfully", True, 204
                            else:
                                return "THe Submodel element is not found in the submodel", False,404
                        else:
                            return "THe Submodel element is not found in the submodel", False,404
                    else:
                        _parentId = _submodelIdentifier+"."+".".join(idShortSplit[:-1])
                        if self.aasHashDict.__isKeyPresent__(_parentId):
                            _pid = (self.aasHashDict.__getHashEntry__(_parentId).__getId__())
                            parentElement = (self.submodelHashDict.__getHashEntry__(_pid)).getElement()
                            if (parentElement["modelType"] == "SubmodelElementCollection"):
                                _sumodelElemId =  (self.aasHashDict.__getHashEntry__(_submodelIdentifier+"."+data["idShortPath"]).__getId__())
                                _submodelElem = (self.submodelHashDict.__getHashEntry__(_sumodelElemId)).getElement()
                                if (_submodelElem["modelType"] == "SubmodelElementCollection"):
                                    self.deleteCollectionElems(_submodelElem)
                                parentElement["value"].remove(_sumodelElemId)
                                self.submodelHashDict.__getHashEntry__(_pid).setElement(parentElement)
                                self.submodelHashDict.__deleteHashEntry__(_sumodelElemId)
                                self.aasHashDict.__deleteHashEntry__(_submodelIdentifier+"."+data["idShortPath"])
                                return "Submodel element deleted successfully", True, 204                                    
                            else:
                                return "The submodel element is not valid at this location", False, 400                        
                        else:
                            return "The parent element does not exist",False,400
                else:
                    return "The submodel element is not found",False,404                   
            else:
                return "The submodel is not found", False,404             
                
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at DeleteSubmodelElementByPath_SRI DB" + str(E))
            return  "Internal Server Error", False,500

    def PostSubmodelElementByPath_SRI(self,data):
        try:
            _submodelIdentifier = data ["submodelIdentifier"]
            _elemData = data["elemData"]
            if self.aasHashDict.__isKeyPresent__(_submodelIdentifier):
                _idSHortPath = _submodelIdentifier +"." +data["idShortPath"] +"." +_elemData["idShort"]
                if self.aasHashDict.__isKeyPresent__(_idSHortPath):
                    return "The submodel element is already present please try put",False,400
                else:
                    idShortSplit = (_idSHortPath).split(".")
                    aasSmParser = AASSubmodelParser(self.aasHashDict,self.submodelHashDict)
                    _newuuid = ""
                    if len(idShortSplit) == 1:
                        if (_elemData["modelType"] == "SubmodelElementCollection"):
                            _newuuid = aasSmParser.parseSubmodelCollection(_elemData, _submodelIdentifier)
                        else:
                            _newuuid = aasSmParser.parseDataElement(_elemData, _submodelIdentifier)
                        _sid = (self.aasHashDict.__getHashEntry__(_submodelIdentifier).__getId__())
                        (self.submodelHashDict.__getHashEntry__(_sid)).aasELement["submodelElements"].append(_newuuid)
                        return "Submodel element created successfully", True,201
                    else:
                        _parentId = _submodelIdentifier +"." +data["idShortPath"]
                        if  self.aasHashDict.__isKeyPresent__(_parentId):
                            _pid = (self.aasHashDict.__getHashEntry__(_parentId).__getId__())
                            parentElement = (self.submodelHashDict.__getHashEntry__(_pid)).getElement()
                            _newuuid = ""
                            if (parentElement["modelType"] == "SubmodelElementCollection"):
                                if (_elemData["modelType"] == "SubmodelElementCollection"):
                                    _newuuid = aasSmParser.parseSubmodelCollection(_elemData, _parentId)
                                else:
                                    _newuuid = aasSmParser.parseDataElement(_elemData, _parentId)
                                (self.submodelHashDict.__getHashEntry__(_pid)).aasELement["value"].append(_newuuid)
                                return "Submodel element created successfully", True,201                                    
                            else:
                                return "The new element cannot be created at this place",False,400                        
                        else: 
                            return "The parent element does not exist",False,400
            else:
                return "The submodel is not found", False,404             
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at PostSubmodelElementByPath_SRI DB" + str(E))
            return  "Internal Server Error", False,500

    def PutSubmodelElementByPath_SRI(self,data):
        try:
            _idShortpath = data["idShortPath"]
            if self.aasHashDict.__isKeyPresent__(data["submodelIdentifier"]+"."+_idShortpath):
                data1,status1,statuscode1 = self.DeleteSubmodelElementByPath_SRI(data)
                if status1:
                    idShortSplit = _idShortpath.split(".")
                    data["idShortPath"] = ".".join(idShortSplit[:-1])
                    if len(idShortSplit) == 1:
                        data2,status2,statuscode2 = self.PostSubmodelElement_SRI(data)
                        if status2:
                            return "Submodel element updated successfully", True,204
                        else:
                            return data2,status2,statuscode2
                    else:
                        data3,status3,statuscode3 = self.PostSubmodelElementByPath_SRI(data)
                        if status3:
                            return "Submodel element updated successfully", True,204
                        else:
                            return data3,status3,statuscode3
                else:
                    return data1,status1,statuscode1
            else:
                return "The Submodel element not found", False, 404
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at PutSubmodelElementByPath_SRI DB" + str(E))
            return  "Internal Server Error", False,500        

    def GetFileByPath_SRI(self,_submodelIdentifier,idShortPath):
        try:
            if self.aasHashDict.__isKeyPresent__(_submodelIdentifier):
                _idSHortPath = _submodelIdentifier +"." +idShortPath
                if self.aasHashDict.__isKeyPresent__(_idSHortPath):
                    _sid = (self.aasHashDict.__getHashEntry__(_idSHortPath).__getId__())
                    submodelElem = (self.submodelHashDict.__getHashEntry__(_sid)).getElement()
                    if (submodelElem["modelType"] != "File"):
                        return "A file is not associated at the specified path", False,404
                    else:
                        return submodelElem["value"], True,200
                else:
                    return "The submodel element not found",False,404   
            else:
                return "The submodel is not found", False,404             
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at GetFileByPath_SRI DB" + str(E))
            return  "Internal Server Error", False,500

    def PutFileByPath_SRI(self,data):
        try:
            _idShortpath = data["idShortPath"]
            if self.aasHashDict.__isKeyPresent__(data["submodelIdentifier"]+"."+_idShortpath):
                _sid = (self.aasHashDict.__getHashEntry__(data["submodelIdentifier"]+"."+_idShortpath).__getId__())
                submodelElem = (self.submodelHashDict.__getHashEntry__(_sid)).getElement()
                if (submodelElem["modelType"] != "File"):
                    return "A file is not associated at the specified path", False,404
                else:
                    filePath = (submodelElem["value"]).split("/")[:-1]
                    _newPathValue = "/".join(filePath) + "/" + data["elemData"]
                    submodelElem["value"] = _newPathValue
                    submodelElem["contentType"] = data["mimeType"]
                    data["elemData"] = submodelElem
                    data1,status1,statuscode1 = self.PutSubmodelElementByPath_SRI(data)
                    if status1:
                        return _newPathValue, True,204
                    else:
                        return data1,status1,statuscode1
            else:
                return "The Submodel element not found", False, 404
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at PutFileByPath_SRI DB" + str(E))
            return  "Internal Server Error", False,500 
    

    '''
    Submodel Repository Interface end
    '''

    def getShellSubmodelRefs(self,_shellId):
        try:
            _id = (self.aasHashDict.__getHashEntry__(_shellId).__getId__())
            _aasShell = self.aasShellHashDict.__getHashEntry__(_id)
            return _aasShell["submodels"], True 
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at getShellSubmodelRef DB" + str(E))
            return  str(E) + "Unexpected Error", False 
      

    def getShellSubmodelRef(self,_shellId,_submodelrefId):
        try:
            _id = (self.aasHashDict.__getHashEntry__(_shellId).__getId__())
            _aasShell = self.aasShellHashDict.__getHashEntry__(_id)
            for index, submodelRef in  enumerate(_aasShell["submodels"]):
                if submodelRef["keys"][0]["value"] == _submodelrefId:
                    return _aasShell["submodels"][index], True
            return "No data", False 
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at getShellSubmodelRef DB" + str(E))
            return  str(E) + "Unexpected Error", False 
      
    def putShellSubmodelRef(self,data):
        try:
            data,status,statuscode = self.deleteShellSubmodelRef(data["_shellId"])
            if (status):
                data1,status1,statuscode1 =  self.postShellSubmodelRef(data["_submodelRef"])
                if (status1):
                    return "Asset Administration Shell updated successfully",True,201
                else:
                    return data1,status1,statuscode1
            else:
                data,status,statuscode
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at putShellSubmodelRef DB" + str(E))
            return  "Internal Server Error", False,500
        
    def getSubmodelsbyShell(self,_shellId):
        try:
            _id = self.aasHashDict.__getHashEntry__(_shellId).__getId__()
            _aasShell = self.aasShellHashDict.__getHashEntry__(_id).getElement()
            _submodels = []
            i = 0
            for _submodelRef in _aasShell["submodels"]:
                _submodelid = _submodelRef["keys"][0]["value"]
                _submodel,status,statuscode = self.getSubmodel(_submodelid)
                if status:
                    _submodels.append(_submodel)
                else:
                    return _submodel,status,statuscode
                i = i + 1
            return _submodels,True,200
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at putShellSubmodelRef DB" + str(E))
            return  "Internal Server Error", False,500
                
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

    def createNewCFPObject(self,_coversationId):
        try:
            uuidG = UUIDGenerator()
            _uuid = uuidG.getnewUUID()
            cfpo = CarbonFootPrintObject(_coversationId,_uuid)
            self.cfpHashDict.__insertHashEntry__(_coversationId, cfpo)
        except Exception as E:
            return  str(E) + "Unexpected Error", False
    
    def setInitialValue(self,coversationId,_skillName,startTime):
        try:
            cfpo = self.cfpHashDict.__getHashEntry__(coversationId)
            cfpo.setInitialValue(_skillName,startTime)
        except Exception as E:
            return  str(E) + "Unexpected Error", False

    def setFinalProperties(self,coversationId,endTime,_cfp):
        try:
            cfpo = self.cfpHashDict.__getHashEntry__(coversationId)
            cfpo.setFinalProperties(endTime,_cfp)
        except Exception as E:
            return  str(E) + "Unexpected Error", False    
    
    def getCFPObject(self,coversationId):
        cfpo = self.cfpHashDict.__getHashEntry__(coversationId)
        return cfpo.getProperties()
    
    def getConversationCFP(self,coversationId):
        try:
            _uuid = self.aasHashDict.__getHashEntry__(coversationId).__getId__()
            converseObject = self.conversHashDict.__getHashEntry__(_uuid)
            if len(converseObject.sub_coversationIds) == 0:
                return [self.getCFPObject(coversationId)]
            else:
                tes = []
                subList = [self.getCFPObject(sci) for sci in converseObject.sub_coversationIds]
                baseObject = self.getCFPObject(coversationId)
                baseObject[3] = sum([int(obj[3]) for obj in subList])
                baseObject[4] = sum([int(obj[4]) for obj in subList])
                tes.append(baseObject)
                tes.extend(subList)
                return tes
        except Exception as E:
            return [] 
    
    def getMessageCount(self):
        try:
            uuids = self.conversHashDict._getKeys()
            messageCount = sum(   self.conversHashDict.__getHashEntry__(uuid)._getMessageCount() for uuid in uuids)   
            return messageCount, "Success"    
        except Exception as E:
            return  0, False
    
    def insertSubCovsersationIds(self,sci_list,coversationId):
        try:
            _uuid = self.aasHashDict.__getHashEntry__(coversationId).__getId__()
            converseObject = self.conversHashDict.__getHashEntry__(_uuid)
            converseObject.extend_sub_conversation_ids(sci_list)
            return True
        except Exception as E:
            return False
           
    def getConversationsById(self,coversationId,aasIdentifier):
        try:
            _uuid = self.aasHashDict.__getHashEntry__(coversationId).__getId__()
            converseObject = self.conversHashDict.__getHashEntry__(_uuid)
            conversation = converseObject._getMessages(aasIdentifier)
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
        if submodelElement["modelType"] == "SubmodelElementCollection":
            elemCollection = {}
            for elem in submodelElement["value"]:
                if elem["modelType"] == "SubmodelElementCollection":
                    elemCollection[elem["idShort"]] = self.processEachSubmodelElement(elem)
                else:
                    if (elem["modelType"] == "Property"):
                        elemCollection[elem["idShort"]] = elem["value"] 
                    elif (elem["modelType"] == "Range"):
                        elemCollection[elem["idShort"]] = {"min" :elem["min"] ,"max":elem["max"]}
                        
            return elemCollection
        else: 
            return submodelElement["value"]
    
    def getSubmodePropertyDict(self,submodel):
        submodelProperetyDict = {}
        for eachProperty in submodel["submodelElements"]:
            submodelProperetyDict[eachProperty["idShort"]] = self.processEachSubmodelElement(eachProperty)
        return submodelProperetyDict
    
    def get_aas_information(self,aasIdentifier) -> dict():
        returnDict = dict()
        try:
            uuid = self.aasHashDict.__getHashEntry__(aasIdentifier)._id
            _aasShell = self.aasShellHashDict.__getHashEntry__(uuid)
            submodelList = []
    
            for submodelRef in _aasShell.aasELement["submodels"]:
                submodelId = submodelRef["keys"][0]["value"]
                _suid = (self.aasHashDict.__getHashEntry__(submodelId).__getId__())
                submodelidShort = self.submodelHashDict.__getHashEntry__(_suid).idShort            
                bString = base64.b64encode(bytes(submodelId,'utf-8'))
                base64_string= bString.decode('utf-8')
                submodelList.append({base64_string:submodelidShort})
                
            returnDict["submodelList"] = submodelList
            returnDict["skillList"] = list(_aasShell.skills.keys())
            returnDict["thumbnail"] = ((_aasShell.aasELement["assetInformation"]["defaultThumbnail"]["path"]).split("file:/"))[1]    
            returnDict["idShort"] = _aasShell.aasELement["idShort"]
            returnDict["aasIndex"] = _aasShell.elementIndex
            returnDict["_aasShell"] = _aasShell
            returnDict["productionStepList"] = _aasShell.productionStepList
            returnDict["conversationIdList"] = _aasShell.conversationIdList
            
        except Exception as e:
            return returnDict,False 
        return returnDict,True
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