'''
Copyright (c) 2021-2022 OVGU LIA
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
'''

    
class NameplateCapture(object):
    
    def __init__(self,namePlateSubmodel,pyAAS):
        self.namePlateSubmodel = namePlateSubmodel
        self.pyAAS = pyAAS
        self.nameplateData = {"EN":{},"DE":{}}
    
    def submodelElemeObject(self,idShortPath):
        _uuid = self.pyAAS.aasHashDict.__getHashEntry__(idShortPath).__getId__()
        return self.pyAAS.submodelHashDict.__getHashEntry__(_uuid)
    
    def captureNamePlateElem(self,idShort,idShortPath):
        aasELememObject = self.submodelElemeObject(idShortPath+"."+idShort)
        self.nameplateData["EN"][idShort] = aasELememObject
        self.nameplateData["DE"][idShort] = aasELememObject
    
    def captureMarkings(self,marking,idShortPath):
        markingData = {}
        extHost = self.pyAAS.lia_env_variable["LIA_AAS_RESTAPI_DOMAIN_EXTERN"]
        port = self.pyAAS.lia_env_variable["LIA_AAS_RESTAPI_PORT_INTERN"]
        for markingELem in marking["value"]:
            if markingELem["idShort"] == "MarkingName":
                aasELememObject = self.submodelElemeObject(idShortPath+marking["idShort"]+"."+markingELem["idShort"])
                markingData["MarkingName"] = aasELememObject
            elif markingELem["idShort"] == "MarkingFile":
                if markingELem["value"] != "":
                    markingData["MarkingFile"] = "http://"+extHost+":"+str(port)+"/static/"+(markingELem["value"]).split("/")[-1]
                else:
                    markingData["MarkingFile"] = ""
            else:              
                aasELememObject = self.submodelElemeObject(idShortPath+marking["idShort"]+"."+markingELem["idShort"]) 
                markingData[markingELem["idShort"]] = aasELememObject
        return markingData   
                    
    def captureCategoryELements(self,_submodelId):
        for nameplateElem in self.namePlateSubmodel["submodelElements"]:
            if nameplateElem["modelType"]["name"] ==  "SubmodelElementCollection":
                if  nameplateElem["idShort"] == "Address":
                    for addressElem in nameplateElem["value"]:
                        if addressElem["modelType"]["name"] ==  "SubmodelElementCollection":
                            for addressSubElem in addressElem["value"]:
                                self.captureNamePlateElem(addressSubElem["idShort"],_submodelId+"."+"Address"+"."+addressElem["idShort"])
                        else:
                            self.captureNamePlateElem(addressElem["idShort"],_submodelId+"."+"Address")
                elif nameplateElem["idShort"] == "AssetSpecificProperties":
                    AssetSpecificProperties = {}
                    for aspELem in nameplateElem["value"]:
                        aasELememObject = self.submodelElemeObject(_submodelId+"."+"AssetSpecificProperties"+"."+aspELem["idShort"])
                        AssetSpecificProperties[aspELem["idShort"]] = aasELememObject
                                                                      
                    self.nameplateData["EN"]["AssetSpecificProperties"] = AssetSpecificProperties
                    self.nameplateData["DE"]["AssetSpecificProperties"] = AssetSpecificProperties 
                         
                elif nameplateElem["idShort"] == "Markings":
                    markigsList = []
                    for marking in nameplateElem["value"]:
                        markigsList.append(self.captureMarkings(marking,_submodelId+".Markings."))
                    self.nameplateData["EN"]["Markings"] = markigsList
                    self.nameplateData["DE"]["Markings"] = markigsList 
     
            else:       
                self.captureNamePlateElem(nameplateElem["idShort"],_submodelId)              
    
    def reOrderNamePlate(self):
        reOrderedNamePlate = {}
        _enNamePlate = {}
        _deNamePlate = {}
        _deNamePlate["active"] = "active"
        _deNamePlate["status"] = "true"
        _deNamePlate["showActive"] = " show active"
        _deNamePlate["data"] = self.nameplateData["DE"]
       
        _enNamePlate["active"] = ""
        _enNamePlate["status"] = "false"
        _enNamePlate["showActive"] = ""
        _enNamePlate["data"] = self.nameplateData["EN"]
        
        reOrderedNamePlate["DE"] = _deNamePlate
        reOrderedNamePlate["EN"] = _enNamePlate
        
        return reOrderedNamePlate
        
    def getTemplateInformation(self,_submodelId):
        self.templateInfo = self.pyAAS.aasConfigurer.templateData["Nameplate"]
        self.captureCategoryELements(_submodelId)
        return self.reOrderNamePlate()
    

class IdentificationCapture(object):
    
    def __init__(self,identificationSubmodel,pyAAS):
        self.identificationSubmodel = identificationSubmodel
        self.pyAAS = pyAAS
        self.identificationData = {}

    def submodelElemeObject(self,idShortPath):
        _uuid = self.pyAAS.aasHashDict.__getHashEntry__(idShortPath).__getId__()
        return self.pyAAS.submodelHashDict.__getHashEntry__(_uuid)
          
    def captureIDElem(self,idShort,idShortPath):
        aasELememObject = self.submodelElemeObject(idShortPath+"."+idShort)
        self.identificationData[idShort] = aasELememObject
    
    def reOrderIdentificationDetails(self):
        returnData = dict() 
        returnData["manufacturerDetails"] = {'ManufacturerName' : "",'ManufacturerId01' : "","ManufacturerIdProvider" : "","ManufacturerTypId" : "",
                                             "ManufacturerTypName" : "","ManufacturerTypDescription" : ""}
        returnData["supplierDetails"] = {'SupplierName' : "",'SupplierId' : "","SupplierIdProvider" : "","SupplierTypId" : "","SupplierTypName" : "","SupplierTypDescription" : ""}
        returnData["productDetails"] = {'AssetId' : "",'InstanceId' : "","ChargeId" : "","TypClass" : "","ClassificationSystem" : ""}
        returnData["additionalDetails"] =  {'DeviceRevision' : "",'SoftwareRevision' : "","HardwareRevision" : "","SecondaryKeyTyp" : "","SecondaryKeyInstance" : "",
                                            "URL" : "","ManufacturingDate" : ""}
        returnData["Images"] = {"CompanyLogo" : "","QrCode" : "","TypThumbnail" : ""}
        
        for key in returnData.keys():
            for key1 in returnData[key]:
                returnData[key][key1] = self.identificationData[key1]
        returnData["contactInfo"] = self.identificationData["contactInfo"]
        return returnData
    
    def captureCategoryELements(self,_submodelId):
        contactInfos = {}
        for idELem in self.identificationSubmodel["submodelElements"]:
            if idELem["modelType"]["name"] ==  "SubmodelElementCollection":
                contact = {}
                for contactElement in idELem["value"]:
                    if contactElement["modelType"]["name"] ==  "SubmodelElementCollection":
                        #physicalAdd = {}
                        for physicalAddressElem in contactElement["value"]:
                            aasELememObject = self.submodelElemeObject(_submodelId+"."+idELem["idShort"]+"."+contactElement["idShort"]+"."+physicalAddressElem["idShort"])
                            contact[contactElement["idShort"]+"."+physicalAddressElem["idShort"]] = aasELememObject
                        #contact["PhysicalAddress"] = physicalAdd
                    else:
                        aasELememObject = self.submodelElemeObject(_submodelId+"."+idELem["idShort"]+"."+contactElement["idShort"])
                        contact[contactElement["idShort"]] = aasELememObject
                contactInfos[idELem["idShort"]] = contact
            else:       
                self.captureIDElem(idELem["idShort"],_submodelId)              
        self.identificationData["contactInfo"] = contactInfos
        
    def getTemplateInformation(self,_submodelId):
        self.captureCategoryELements(_submodelId)
        return self.reOrderIdentificationDetails()

   
class DocumentCapture(object):
    
    def __init__(self,documentSubmodel,templateName,pyAAS):
        self.documentSubmodel = documentSubmodel
        self.templateName = templateName
        self.pyAAS = pyAAS
        self.documentInstance = {}

    def captureCategoryELements(self):
        languageSet = set([])
        documentData = {}
        DocumentIdDomain = {}
        documentVersion = {}
        DocumentClassification = {}
        for docElem in self.documentSubmodel["value"]:
            if docElem["idShort"] == "DocumentVersion":
                for docSubmElem in docElem["value"]:
                    if docSubmElem["idShort"][0:8] == "Language":
                        documentVersion[docSubmElem["idShort"]] = docSubmElem["value"].upper()
                        languageSet.add(docSubmElem["value"].upper())
                    else:
                        if docSubmElem["modelType"]["name"] == "MultiLanguageProperty":
                            langString = {}
                            for _langString in  docSubmElem["value"]["langString"]:
                                langString[_langString["language"].upper()] = _langString["text"]
                            documentVersion[docSubmElem["idShort"]] = langString
                        else:
                            documentVersion[docSubmElem["idShort"]] = docSubmElem["value"]
            
            if docElem["idShort"][0:16] == "DocumentIdDomain": 
                _documentIDomain = {}
                for subElem in docElem["value"]:
                    _documentIDomain[subElem["idShort"]] = subElem["value"]
                DocumentIdDomain[docElem["idShort"]] = _documentIDomain
            
            if docElem["idShort"][0:22] == "DocumentClassification": 
                _documentClassification = {}
                for subElem in docElem["value"]:
                    _documentClassification[subElem["idShort"]] = subElem["value"]
                DocumentIdDomain[docElem["idShort"]] = _documentClassification        
        
        documentData["DocumentVersion"] =  documentVersion
        documentData["DocumentIdDomain"] =  DocumentIdDomain
        documentData["DocumentClassification"] =  DocumentClassification
        documentData["documentIdShort"] =  self.documentSubmodel["idShort"]
        
        self.documentInstance["languageSet"] = languageSet
        self.documentInstance["data"] = documentData
        
        
    def getTemplateInformation(self):
        self.templateInfo = self.pyAAS.aasConfigurer.templateData[self.templateName]
        self.captureCategoryELements()
        return self.documentInstance      
    

class TechnicalDataCapture(object):
    
    def __init__(self,technicalDataSubmodel,pyAAS):
        self.technicalDataSubmodel = technicalDataSubmodel
        self.pyAAS = pyAAS
        self.technicalData = {}

    def submodelElemeObject(self,idShortPath):
        _uuid = self.pyAAS.aasHashDict.__getHashEntry__(idShortPath).__getId__()
        return self.pyAAS.submodelHashDict.__getHashEntry__(_uuid)
    
    def captureCategoryELements(self,submodelId):
        for tdElem in self.technicalDataSubmodel["submodelElements"]:
            if tdElem["idShort"] == "GeneralInformation":      
                generalInformation = {}
                productImages = {}
                for giElem in tdElem["value"]:
                    if (giElem["idShort"])[0:12] == "ProductImage":
                        if (giElem["value"]!= ""):
                            aasELememObject = self.submodelElemeObject(submodelId+"."+tdElem["idShort"]+"."+giElem["idShort"])
                            productImages[giElem["idShort"]] = aasELememObject
                    else:
                        aasELememObject = self.submodelElemeObject(submodelId+"."+tdElem["idShort"]+"."+giElem["idShort"])
                        generalInformation[giElem["idShort"]] = aasELememObject
                generalInformation["ProductImages"] = productImages
                self.technicalData["GeneralInformation"] = generalInformation
                    
            elif tdElem["idShort"] == "ProductClassifications":      
                ProductClassifications = {}
                for pcsElem in tdElem["value"]:
                    pClassification = {}
                    for pcElem in pcsElem["value"]:
                        aasELememObject = self.submodelElemeObject(submodelId+"."+ tdElem["idShort"]+"."+pcsElem["idShort"]+"."+pcElem["idShort"])
                        pClassification[pcElem["idShort"]] = aasELememObject
                    ProductClassifications[pcsElem["idShort"]] = pClassification
                self.technicalData["ProductClassifications"] = ProductClassifications
                
            elif tdElem["idShort"] == "TechnicalProperties":      
                technicalProperties = {}
                for tcpropertyElem in tdElem["value"]:
                    if isinstance(tcpropertyElem["value"], list):
                        tcProperty = {}
                        for tpElem in tcpropertyElem["value"]:
                            aasELememObject = self.submodelElemeObject(submodelId+"."+tdElem["idShort"]+"."+
                                                                       tcpropertyElem["idShort"]+"."+tpElem["idShort"])
                            tcProperty[tpElem["idShort"]] = aasELememObject
                        technicalProperties[tcpropertyElem["idShort"]] = tcProperty
                    else:
                        aasELememObject = self.submodelElemeObject(submodelId+"."+tdElem["idShort"]+"."+tcpropertyElem["idShort"])
                        technicalProperties[tcpropertyElem["idShort"]] = aasELememObject
                self.technicalData["TechnicalProperties"] = technicalProperties
                
            elif tdElem["idShort"] == "FurtherInformation":      
                furtherInformation = {}
                for fiElem in tdElem["value"]:
                    aasELememObject = self.submodelElemeObject(submodelId+"."+tdElem["idShort"]+"."+fiElem["idShort"])
                    furtherInformation[fiElem["idShort"]] = aasELememObject
                self.technicalData["FurtherInformation"] = furtherInformation
                    
    def getTemplateInformation(self,submodelId):
        self.captureCategoryELements(submodelId)
        return self.technicalData
    