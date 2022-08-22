'''
Copyright (c) 2021-2022 OVGU LIA
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
'''
import json
import os.path

try:
    from utils.utils import AASDescriptor
except ImportError:
    from main.utils.aaslog import AASDescriptor

try:
    from config.TemplateCapture import NameplateCapture,IdentificationCapture,DocumentCapture,TechnicalDataCapture
except ImportError:
    from main.config.TemplateCapture import NameplateCapture,IdentificationCapture,DocumentCapture,TechnicalDataCapture
    

enabledState = {"Y":True, "N":False}

class ConfigParser(object):
    def __init__(self,pyAAS,packageFile):
        self.pyAAS = pyAAS
        self.jsonData = {}
        self.templateData = {}
        self.baseFile = packageFile 
        self.reposStatus = self.__init_repositories()
        
    def __init_repositories(self):
        try :    
            with open(os.path.join(self.pyAAS.repository, self.baseFile), encoding='utf-8') as json_file:
                self.jsonData = json.load(json_file)
            with open(os.path.join(self.pyAAS.template_repository, "documentationInfo.json"), encoding='utf-8') as json_file_document:
                self.templateData["Documentation"] = json.load(json_file_document)
            with open(os.path.join(self.pyAAS.template_repository, "namplateInfo.json"), encoding='utf-8') as json_file_nameplate:
                self.templateData["Nameplate"] = json.load(json_file_nameplate)
            with open(os.path.join(self.pyAAS.repository,"ass_JsonSchema.json"), encoding='utf-8') as json_file_aas:
                self.aasJsonSchema  = json.load(json_file_aas)
            with open(os.path.join(self.pyAAS.repository,"aasShell_JsonSchema.json"), encoding='utf-8') as json_file_aasShell:
                self.aasShell_JsonSchema  = json.load(json_file_aasShell)
            with open(os.path.join(self.pyAAS.repository,"asset_JsonSchema.json"), encoding='utf-8') as json_file_asset:
                self.assetJsonSchema  = json.load(json_file_asset)
            with open(os.path.join(self.pyAAS.repository,"submodel_JsonSchema.json"), encoding='utf-8') as json_file_submodel:
                self.submodelJsonSchema  = json.load(json_file_submodel)
            with open(os.path.join(self.pyAAS.repository,"conceptDescription_JsonSchema.json"), encoding='utf-8') as json_file_submodel:
                self.conceptDescription_JsonSchema  = json.load(json_file_submodel)
            with open(os.path.join(self.pyAAS.base_dir,"config/status.json"), encoding='utf-8') as statusFile:
                self.submodel_statusResponse  = json.load(statusFile)
            with open(os.path.join(self.pyAAS.base_dir,"config/SrSp.json"), encoding='utf-8') as SrSp_Path:
                self.SrSp  = json.load(SrSp_Path)    
                del self.SrSp["temp"]
            with open(os.path.join(self.pyAAS.dataRepository,"database.json"), encoding='utf-8') as json_file_dataBase:
                self.dataBaseFile  = json.load(json_file_dataBase)
            return True
        except Exception as E:
            self.pyAAS.serviceLogger.info('Error configuring the data respositories' + str(E))
            return False
            
    def getStatusResponseSubmodel(self):
        return self.submodel_statusResponse
        
    def configureAASJsonData(self):
        try:
            self.getStandardSubmodels()
            self.aasIdList()
            self.getAASList()
            return True    
        except Exception as E:
            self.pyAAS.serviceLogger.info('Error configuring the database' + str(E))
            return False        
    
    def extract_pubsublistner_config(self):
        try:
            listnerConfig = dict()
            listnerConfig["host"] = self.pyAAS.lia_env_variable["LIA_PUBSUB_LISTNER_HOST"] 
            listnerConfig["port"] = self.pyAAS.lia_env_variable["LIA_PUBSUB_LISTNER_PORT"]
            self.pyAAS.listnersConfig["AAS_PUBSUB"] = listnerConfig
            return True
        except Exception as E:
            return False
            self.pyAAS.serviceLogger.info("Error while extracting. " + str(E))
    
    def setThumbNails(self):
        self.pyAAS.thumbNailList[0] = "sr.png"
        
    def getStandardSubmodels(self):
        #self.setThumbNails()
        for _uuid in (self.pyAAS.aasShellHashDict._getKeys()):
            aasElementObject = self.pyAAS.aasShellHashDict.__getHashEntry__(_uuid)
            _shell = aasElementObject.aasELement
            _shellIndex = aasElementObject.elementIndex
            _shellId = _shell["identification"]["id"]
            self.stdSubmodelData = {}
            self.stdSubmodelList = []
            submodels,status = self.pyAAS.dba.getSubmodelsbyShell(_shellId)
            for _index,submodel in (submodels).items():
                _submodelId = submodel["identification"]["id"]
                if (submodel["idShort"]).upper() == "NAMEPLATE":
                    self.stdSubmodelData["NAMEPLATE"]  = [_submodelId,self.getNamePlateData(submodel,_submodelId)]
                    self.stdSubmodelList.append("NAMEPLATE")
                
                elif (submodel["idShort"]).upper() in ["DOCUMENTATION" ,"MANUFACTURERDOCUMENTATION"]:        
                    self.stdSubmodelData["DOCUMENTATION"]  = [_submodelId,self.getDcumentationData(submodel,_submodelId)]
                    self.stdSubmodelList.append("DOCUMENTATION")
                
                elif (submodel["idShort"]).upper() in ["TECHNICAL_DATA","TECHNICALDATA"]:
                    self.stdSubmodelData["TECHNICAL_DATA"]  = [_submodelId,self.getTechnicalData(submodel,_submodelId)]
                    self.stdSubmodelList.append("TECHNICAL_DATA")
                
                elif (submodel["idShort"]).upper() in ["IDENTIFICATION"]:
                    self.stdSubmodelData["IDENTIFICATION"]  = [_submodelId,self.getIdentificationData(submodel,_submodelId)]
                    self.stdSubmodelList.append("IDENTIFICATION")
                
                elif (submodel["idShort"]).upper() in ["ASSETINTERFACEDESCRIPTION","THINGDESCRIPTION"]:
                    self.stdSubmodelData["AssetInterfaceDescription"]  = [_submodelId,self.configureThingDescriptionProperties(submodel,_shellId,_shellIndex,_submodelId)]
                    self.stdSubmodelList.append("AssetInterfaceDescription")
            try :
                if (self.stdSubmodelData["IDENTIFICATION"]["TypThumbnail"] != ""):
                    self.pyAAS.thumbNailList[_shellIndex] = (self.stdSubmodelData["IDENTIFICATION"]["TypThumbnail"])
                else:
                    extHost = self.pyAAS.lia_env_variable["LIA_AAS_RESTAPI_DOMAIN_EXTERN"]
                    port = self.pyAAS.lia_env_variable["LIA_AAS_RESTAPI_PORT_INTERN"]                    
                    self.pyAAS.thumbNailList[_shellIndex] = "http://"+extHost+":"+str(port)+"/static/"+"DHT22_9adf2b76.jpg"
            except Exception as E:
                extHost = self.pyAAS.lia_env_variable["LIA_AAS_RESTAPI_DOMAIN_EXTERN"]
                port = self.pyAAS.lia_env_variable["LIA_AAS_RESTAPI_PORT_INTERN"]                    
                self.pyAAS.thumbNailList[_shellIndex] = "http://"+extHost+":"+str(port)+"/static/"+"DHT22_9adf2b76.jpg"
                            
            self.pyAAS.aasStandardSubmodelData[_shellIndex] = self.stdSubmodelData
            self.pyAAS.aasStandardSubmodelList[_shellIndex] = self.stdSubmodelList

    def aasIdList(self):
        for index,_uuid in enumerate(self.pyAAS.aasShellHashDict._getKeys()):
            aasElementObject = self.pyAAS.aasShellHashDict.__getHashEntry__(_uuid)
            _shell = aasElementObject.aasELement
            _shellIndex = aasElementObject.elementIndex
            _shellId = _shell["identification"]["id"]
            _shellidShort = _shell["idShort"]
            self.pyAAS.aasIndexidShortDict[_shellIndex] = {"idShort":_shellidShort,"identificationId" : _shellId,"_uuid":_uuid}
            self.pyAAS.aasIdentificationIdList[_shellId] = _shellIndex    
            if _shellIndex not in list(self.pyAAS.conversationIdList.keys()):
                self.pyAAS.conversationIdList[_shellIndex] = []  
            if _shellIndex not in list(self.pyAAS.productionSequenceList.keys()):
                self.pyAAS.productionSequenceList[_shellIndex] = []  
            if _shellIndex not in list(self.pyAAS.thumbNailList.keys()):
                self.pyAAS.thumbNailList[_shellIndex] = ""
    
    def getAASEndPoints(self):
        aasEndpointsList = []
        moduleDict = {"MQTT":".mqtt_endpointhandler","RESTAPI":".restapi_endpointhandler"}
        for moduleName in moduleDict.keys():
            aasEndpointsList.append({"Name":moduleName,"Module":moduleDict[moduleName]})
        return aasEndpointsList

    def getAssetAccessEndPoints(self):
        return {"OPCUA":".io_opcua"}
    
    def getpropertyValue(self,submodelElement):
        check = True
        if (submodelElement["modelType"]["name"] == "MultiLanguageProperty"):
            for lang in submodelElement["value"]["langString"]: 
                if lang["language"] == "de":
                    return lang["text"]
            if (check):
                return submodelElement["langString"]["0"]["value"]
        else:
            return submodelElement["value"]
    
    def GetAAsxSkills(self):  
        skillListAAS= {}
        for _uuid in (self.pyAAS.aasShellHashDict._getKeys()):
            aasElementObject = self.pyAAS.aasShellHashDict.__getHashEntry__(_uuid)
            _shell = aasElementObject.aasELement
            _shellIndex = aasElementObject.elementIndex
            _shellId = _shell["identification"]["id"]
            _shellIdShort = _shell["idShort"] 
            self.stdSubmodelData = {}
            self.stdSubmodelList = []
            skillsDict = {}
            stepList = []
            submodels,status = self.pyAAS.dba.getSubmodelsbyShell(_shellId)
            for _index,submodel in (submodels).items():
                if (submodel["idShort"]).upper() == "OperationalData":
                    for eachskill in submodel["submodelElements"]:
                        skillName = ""
                        skill = {}
                        for skillDetails in eachskill["value"]: 
                            if (skillDetails["idShort"] == "SkillName"):
                                skill[skillDetails["idShort"]] = skillDetails["value"]
                                skillName = skillDetails["value"]
                            elif (skillDetails["idShort"] == "SkillService"):
                                skill[skillDetails["idShort"]] = skillDetails["value"]
                            elif (skillDetails["idShort"] == "InitialState"):
                                skill[skillDetails["idShort"]] = skillDetails["value"]
                            elif (skillDetails["idShort"] == "enabled"):
                                skill[skillDetails["idShort"]] = enabledState[skillDetails["value"]] 
                        skill["aasIdentificationId"] = _shellId
                        skill["_shellIdShort"] = _shellIdShort
                        skillsDict[skillName] = skill
                        if (self.checkForOrderExistence(skill)):
                            stepList.append(skillName)
            else:
                pass                   

            for key in self.SrSp.keys():
                skillsDict[key] = self.SrSp[key]
                if (self.checkForOrderExistence(self.SrSp[key])):
                    stepList.append(key)
                    
            skillListAAS[_shellIndex] = skillsDict
            self.pyAAS.productionStepList[_shellIndex] = stepList
        return skillListAAS 
    
    def getAASList(self):
        try:
            aasList = []
            self.pyAAS.AASData = []
            i = 0
            for index,_uuid in enumerate(self.pyAAS.aasShellHashDict._getKeys()):
                aasShellObject = self.pyAAS.aasShellHashDict.__getHashEntry__(_uuid)
                _shell = aasShellObject.aasELement
                _shellId = _shell["identification"]["id"]      
                aasList.append({"aasId":aasShellObject.elementIndex,"_shellId":_shellId,"idShort":_shell["idShort"],"uuid":_uuid})      
            numberofAAS = len(aasList)
            if numberofAAS == 0:
                self.pyAAS.AASData.append([])
            elif numberofAAS == 1:
                self.pyAAS.AASData.append(aasList)
            else:
                if ((numberofAAS % 2) == 0):
                    for i in range(1,int(numberofAAS/2)+1):
                        tempList = []
                        tempList.append(aasList[2*i-2])
                        tempList.append(aasList[2*i-1])
                        self.pyAAS.AASData.append(tempList)
                else: 
                    numberofRows = int( (numberofAAS + 1)/ 2)
                    for i in range(1,numberofRows):
                        tempList = []
                        tempList.append(aasList[2*i-2])
                        tempList.append(aasList[2*i-1])
                        self.pyAAS.AASData.append(tempList)
                    self.pyAAS.AASData.append([aasList[numberofAAS-1]])

        except Exception as E: 
            print(str(E))        
            return self.pyAAS.AASData
        
    def getRelevantSubModel(self,submodelId):
        checkVar = False
        for submodel in self.jsonData["submodels"]:         
            if (submodel["identification"]["id"] == submodelId):
                checkVar = True
                return {"data" : submodel, "check" : True}
        if(not checkVar):
            return {"check" : False}
        
    def GetAAS(self):
        return self.jsonData
       
    def getQualifiersList(self,submodelElem):
        qualiferList = {}
        if "constraints" in list(submodelElem.keys()):
            for qualifier in submodelElem["constraints"]:
                qualiferList[qualifier["type"]] = qualifier["value"]
        return (qualiferList)
    
    def getSemanticIdList(self,submodelElem):
        semanticIdList = {}
        if "semanticId" in list(submodelElem.keys()):        
            for semId in submodelElem["semanticId"]["keys"]:
                semanticIdList[semId["type"]]  = semId["value"]
        return (semanticIdList)
    
    def parseBlobData(self,mimeType,data):
        if (mimeType == "application/json"):
            jData =  json.loads(data)
            return jData
        else: 
            return data
        
    def processSubmodelELement(self,submodelElement,submodelProperetyDict,idShortPath,identificationId):
            if submodelElement["modelType"]["name"] == "SubmodelElementCollection":
                collectionDict = {}
                for elem in submodelElement["value"]: 
                    collectionDict = self.processSubmodelELement(elem,collectionDict,idShortPath + "."+elem["idShort"],identificationId)
                submodelProperetyDict[submodelElement["idShort"]] =  { "data" :  collectionDict,"qualifierList":self.getQualifiersList(submodelElement),"semanticIdList":self.getSemanticIdList(submodelElement), "type" : "collection" }
            elif (submodelElement["modelType"]["name"] == "Property"):
                submodelProperetyDict[submodelElement["idShort"]] =  {"data" : submodelElement["value"],"qualifierList":self.getQualifiersList(submodelElement),"semanticIdList":self.getSemanticIdList(submodelElement),"type" :"Property","idShortPath":idShortPath,"identificationId":identificationId}
            elif (submodelElement["modelType"]["name"] == "Range"):
                submodelProperetyDict[submodelElement["idShort"]] =  {"data" : {"min" : submodelElement["min"],"max" : submodelElement["max"] },"qualifierList":self.getQualifiersList(submodelElement),"semanticIdList":self.getSemanticIdList(submodelElement),"type" :"Range","idShortPath":idShortPath,"identificationId":identificationId}
            elif (submodelElement["modelType"]["name"] == "MultiLanguageProperty"):
                submodelProperetyDict[submodelElement["idShort"]] =  {"data" : submodelElement["value"],"qualifierList":self.getQualifiersList(submodelElement),"semanticIdList":self.getSemanticIdList(submodelElement),"type" :"MultiLanguageProperty","idShortPath":idShortPath,"identificationId":identificationId}
            elif (submodelElement["modelType"]["name"] == "File"):
                submodelProperetyDict[submodelElement["idShort"]] =  {"data" : submodelElement["value"],"qualifierList":self.getQualifiersList(submodelElement),"semanticIdList":self.getSemanticIdList(submodelElement),"type" :"File","idShortPath":idShortPath,"identificationId":identificationId}
            elif (submodelElement["modelType"]["name"] == "Blob"):
                submodelProperetyDict[submodelElement["idShort"]] =  {"data" : self.parseBlobData(submodelElement["mimeType"], submodelElement["value"]), "mimeType" :submodelElement["mimeType"], "qualifierList":self.getQualifiersList(submodelElement),"semanticIdList":self.getSemanticIdList(submodelElement),"type" :"Blob","idShortPath":idShortPath,"identificationId":identificationId}
            elif (submodelElement["modelType"]["name"] == "ReferenceElement"):
                submodelProperetyDict[submodelElement["idShort"]] =  {"data" : submodelElement["value"],"qualifierList":self.getQualifiersList(submodelElement),"semanticIdList":self.getSemanticIdList(submodelElement),"type" :"ReferenceElement","idShortPath":idShortPath,"identificationId":identificationId}
            elif (submodelElement["modelType"]["name"] == "RelationshipElement"):
                submodelProperetyDict[submodelElement["idShort"]] =  {"data" : {"first" : submodelElement["first"],"second" : submodelElement["second"]},"qualifierList":self.getQualifiersList(submodelElement),"semanticIdList":self.getSemanticIdList(submodelElement),"type" :"RelationshipElement","idShortPath":idShortPath,"identificationId":identificationId}
            elif (submodelElement["modelType"]["name"] == "AnnotatedRelationshipElement"):
                submodelProperetyDict[submodelElement["idShort"]] =  {"data" : {"first" : submodelElement["first"],"second" : submodelElement["second"]},"qualifierList":self.getQualifiersList(submodelElement),"semanticIdList":self.getSemanticIdList(submodelElement),"type" :"AnnotatedRelationshipElement","idShortPath":idShortPath,"identificationId":identificationId}
            elif (submodelElement["modelType"]["name"] == "Capability"):
                submodelProperetyDict[submodelElement["idShort"]] =  {"data" : "Capability","qualifierList":self.getQualifiersList(submodelElement),"semanticIdList":self.getSemanticIdList(submodelElement),"type" :"Capability","idShortPath":idShortPath,"identificationId":identificationId}
            elif (submodelElement["modelType"]["name"] == "Operation"):
                submodelProperetyDict[submodelElement["idShort"]] =  {"data" : {"inputVariable" : submodelElement["inputVariable"],"outputVariable" : submodelElement["outputVariable"],"inoutputVariable" : submodelElement["inoutputVariable"]},"qualifierList":self.getQualifiersList(submodelElement),"semanticIdList":self.getSemanticIdList(submodelElement),"type" :"Operation","idShortPath":idShortPath,"identificationId":identificationId}
            elif (submodelElement["modelType"]["name"] == "BasicEvent"):
                submodelProperetyDict[submodelElement["idShort"]] =  {"data" : submodelElement["observed"],"qualifierList":self.getQualifiersList(submodelElement),"semanticIdList":self.getSemanticIdList(submodelElement),"type" :"BasicEvent","idShortPath":idShortPath,"identificationId":identificationId}
            elif (submodelElement["modelType"]["name"] == "Entity"):     
                submodelProperetyDict[submodelElement["idShort"]] =  {"data" : submodelElement["asset"],"qualifierList":self.getQualifiersList(submodelElement),"semanticIdList":self.getSemanticIdList(submodelElement),"type" :"Entity","idShortPath":idShortPath,"identificationId":identificationId}    
            return submodelProperetyDict
            
    def getSubmodePropertyDict(self,submodel):
        submodelProperetyDict = {}
        identificationId = submodel["identification"]["id"]
        for eachSubmodelElem in submodel["submodelElements"]:
            self.processSubmodelELement(eachSubmodelElem,submodelProperetyDict,eachSubmodelElem["idShort"],identificationId)
        return submodelProperetyDict
    
    def getSubmodelPropertyList(self,aasIdentifier):
        submodelNameList = []
        for submodel in self.pyAAS.aasContentData[aasIdentifier]["submodels"]:
            submodelNameList.append(submodel)
        return submodelNameList
    
    def getSubmodelPropertyListDict(self,aasIdentifier):
        submodelPropertyListDict = {}
        i = 0
        submodels,status = self.pyAAS.dba.getSubmodelsbyShell(aasIdentifier)
        for key,submodel in submodels.items():
            submodelName =  submodel["idShort"]
            if not (submodelName in ["Mechanical break down","Nameplate","TechnicalData","ManufacturerDocumentation",
                                     "Documentation","ThingDescription","Identification"]):
                submodelProperetyDict = self.getSubmodePropertyDict(submodel)    
                if (i == 0):
                    status = " fade show active"
                    i = 1        
                else:
                    status = " fade show"
                submodelPropertyListDict[submodelName] = {"status" : status,
                                                          "data" : submodelProperetyDict,
                                                          "type" : "collection"
                                                         }
        return submodelPropertyListDict
    
    def configureDescriptor(self,identifier):
        aasDesc = AASDescriptor(self.pyAAS)
        aasIndex = self.pyAAS.aasIdentificationIdList[identifier]
        return aasDesc.createDescriptor(aasIndex)

    def checkForOrderExistence(self,skill):
        if (skill["InitialState"] == "WaitforNewOrder"):
            return True
        else :
            return False

    def submodelElemeObject(self,idShortPath):
        _uuid = self.pyAAS.aasHashDict.__getHashEntry__(idShortPath).__getId__()
        return self.pyAAS.submodelHashDict.__getHashEntry__(_uuid)
    
    def configureThingDescriptionProperties(self,submodel,aasIdenId,aasIndex,_submodelId):
        tdProperties = []
        tdPropertyDict = {}
        #updateFrequency = 60
        unit = ""
        _href = ""
        _requestType = ""
        _referenceId = ""
        for tdELement in submodel["submodelElements"]:
            if (tdELement["idShort"] == "properties"):
                for tdproperty in tdELement["value"]:
                    for pConstraint in tdproperty["constraints"]:
                        if(pConstraint["type"] == "updateFrequencey"):
                            updateFrequency = pConstraint["value"]
                        if(pConstraint["type"] == "unit"):
                            unit = pConstraint["value"]
                        if(pConstraint["type"] == "refrence"):
                            _referenceId= pConstraint["value"]                             
                                            
                    for pelem in tdproperty["value"]:
                        if(pelem["idShort"] == "forms"):
                            for formConstraint in pelem["value"][0]["constraints"]:
                                if (formConstraint["type"] == "href"):
                                    _href = formConstraint["value"]
                                elif (formConstraint["type"] == "requestType"):
                                    _requestType = formConstraint["value"]

                    tddata ={"propertyName" :  tdproperty["idShort"],
                                             "href" : _href,
                                             "requestType" : _requestType,
                                             "updateFrequency": updateFrequency,
                                             "submodelName" : submodel["idShort"],
                                             "aasId" : aasIdenId,
                                             "aasIndex" : aasIndex,
                                             "unit" : unit,
                                             "_referenceId" : _referenceId,
                                             "dataElement" : self.submodelElemeObject(_referenceId),
                                             "value" : [0,0,0,0,0,0,0,0,0,0],
                                             "label" : [0,0,0,0,0,0,0,0,0,0],
                                             "idShortPath" : "properties."+tdproperty["idShort"]}
                    tdProperties.append(tddata)
                    tdPropertyDict[tdproperty["idShort"]] = tddata                                    
                        
            self.pyAAS.tdPropertiesList[aasIndex]  = tdPropertyDict
        return self.reOrderEntityList(tdProperties)

    def reOrderEntityList(self,documentationList):
        numberofDocuments =len(documentationList)
        if numberofDocuments == 0:
            return []
        elif numberofDocuments == 1:
            return  [[documentationList[0]]]
        else:
            documentDivisions = []
            if ((numberofDocuments % 2) == 0):
                for i in range(1,int(numberofDocuments/2)+1):
                    tempList = []
                    tempList.append(documentationList[2*i-2])
                    tempList.append(documentationList[2*i-1])
                    documentDivisions.append(tempList)
                return documentDivisions
            else: 
                numberofRows = int( (numberofDocuments + 1)/ 2)
                for i in range(1,numberofRows):
                    tempList = []
                    tempList.append(documentationList[2*i-2])
                    tempList.append(documentationList[2*i-1])
                    documentDivisions.append(tempList)
                documentDivisions.append([documentationList[numberofDocuments-1]])
                return documentDivisions

    def getDcumentationData(self,submodel,_submodelId):
        documentationList = []
        documentLangSet = set([])
        languageDIct = {}        
        for eachDocument in submodel["submodelElements"]:
            tc = DocumentCapture(eachDocument,"Documentation",self.pyAAS)
            documentData = tc.getTemplateInformation()
            documentationList.append(documentData)
            for lang in documentData["languageSet"]:
                documentLangSet.add(lang)
        for dLang in documentLangSet:
            languageDIct[dLang] = []
        for docData in documentationList:
            for lang in docData["languageSet"]:
                if lang in languageDIct.keys():
                    languageDIct[lang].append(docData["data"])
                        
        documentationData = {}
        i = 0
        active = "active"
        status = "true"
        showActive = " show active"
        for lang in languageDIct.keys():
            if i == 0:
                i = i + 1
            else:
                status = "false"
                active = ""
                showActive = ""
            documentationData[lang]  = {"data":self.reOrderEntityList(languageDIct[lang]),"active":active,"status":status,"showActive":showActive}              
        return documentationData
              
    def getNamePlateData(self,submodel,_submodelId):
        tc = NameplateCapture(submodel,self.pyAAS)
        return tc.getTemplateInformation(_submodelId)      
 
    def getIdentificationData(self,submodel,_submodelId):
        tc = IdentificationCapture(submodel,self.pyAAS)
        return tc.getTemplateInformation(_submodelId)
           
    def getTechnicalData(self,submodel,_submodelId):
        tc = TechnicalDataCapture(submodel,self.pyAAS)
        return tc.getTemplateInformation(_submodelId)
