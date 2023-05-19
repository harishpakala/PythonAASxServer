'''
Copyright (c) 2021-2022 OVGU LIA
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
'''
from importlib import import_module

from copy import deepcopy
import json
import os.path

try:
    from utils.utils import AASDescriptor,AIDProperty,AssetInterfaceDescription
except ImportError:
    from src.main.utils.aaslog import AASDescriptor,AIDProperty,AssetInterfaceDescription

enabledState = {"Y": True, "N": False}


class ConfigParser:
    def __init__(self, pyaas, package_file):
        self.pyaas = pyaas
        self.jsonData = {}
        self.submodel_template_dict = dict()
        self.base_file = package_file
        self.reposStatus = self.__init_repositories()

    def __init_repositories(self):
        try:
            with open(os.path.join(self.pyaas.repository, self.base_file), encoding='utf-8') as json_file:
                self.jsonData = json.load(json_file)

            with open(os.path.join(self.pyaas.repository, "ass_JsonSchema.json"), encoding='utf-8') as json_file_aas:
                self.aasJsonSchema = json.load(json_file_aas)

            with open(os.path.join(self.pyaas.repository, "aas_shell_template.json"),
                      encoding='utf-8') as json_file_nameplate:
                self.aas_shell_template = json.load(json_file_nameplate)

            submodel_templates = os.listdir(self.pyaas.template_repository)
            
            for _fileName in submodel_templates:
                with open(os.path.join(self.pyaas.template_repository, _fileName),
                      encoding='utf-8') as json_file_nameplate:
                    self.submodel_template_dict[_fileName.split(".")[0]] = json.load(json_file_nameplate)

            self.pyaas.derAuthCert = open(
                os.path.join(self.pyaas.repository, self.pyaas.lia_env_variable["LIA_PATH2AUTHCERT"]), "rb").read()

            """
            with open(os.path.join(self.pyaas.repository, "ass_JsonSchema.crt")) as json_file_aas:
                self.certificateHandler = json.load(json_file_aas)
            """

            self.aasShell_JsonSchema = deepcopy(self.aasJsonSchema)
            self.aasShell_JsonSchema["allOf"][0]["$ref"] = "#/definitions/AssetAdministrationShell"

            self.assetInformation_JsonSchema = deepcopy(self.aasJsonSchema)
            self.assetInformation_JsonSchema["allOf"][0]["$ref"] = "#/definitions/AssetInformation"

            self.submodelJsonSchema = deepcopy(self.aasJsonSchema)
            self.submodelJsonSchema["allOf"][0]["$ref"] = "#/definitions/Submodel"

            self.conceptDescription_JsonSchema = deepcopy(self.aasJsonSchema)
            self.conceptDescription_JsonSchema["allOf"][0]["$ref"] = "#/definitions/ConceptDescription"

            self.reference_JsonSchema = deepcopy(self.aasJsonSchema)
            self.reference_JsonSchema["allOf"][0]["$ref"] = "#/definitions/Reference"

            with open(os.path.join(self.pyaas.base_dir, "config/status.json"), encoding='utf-8') as statusFile:
                self.submodel_statusResponse = json.load(statusFile)
            with open(os.path.join(self.pyaas.base_dir, "config/SrSp.json"), encoding='utf-8') as SrSp_Path:
                self.SrSp = json.load(SrSp_Path)
                del self.SrSp["temp"]
            with open(os.path.join(self.pyaas.dataRepository, "database.json"), encoding='utf-8') as json_file_dataBase:
                self.dataBaseFile = json.load(json_file_dataBase)
            return True
        except Exception as E:
            self.pyaas.serviceLogger.info('Error configuring the data respositories' + str(E))
            return False

    def getStatusResponseSubmodel(self):
        return self.submodel_statusResponse

    def extract_pubsublistner_config(self):
        try:
            listnerConfig = dict()
            listnerConfig["host"] = self.pyaas.lia_env_variable["LIA_PUBSUB_LISTNER_HOST"]
            listnerConfig["port"] = self.pyaas.lia_env_variable["LIA_PUBSUB_LISTNER_PORT"]
            self.pyaas.listeners_config["AAS_PUBSUB"] = listnerConfig
            return True
        except SystemError as e:
            return False
            self.pyaas.serviceLogger.info("Error while extracting. " + str(e))

    def getAASEndPoints(self):
        aasEndpointsList = []
        moduleDict = {"MQTT": ".mqtt_endpointhandler", "RESTAPI": ".restapi_endpointhandler"}
        for moduleName in moduleDict.keys():
            aasEndpointsList.append({"Name": moduleName, "Module": moduleDict[moduleName]})
        return aasEndpointsList

    def getSubmodePropertyDict(self, submodel):
        submodelProperetyDict = {}
        identificationId = submodel["id"]
        for eachSubmodelElem in submodel["submodelElements"]:
            self.processSubmodelELement(eachSubmodelElem, submodelProperetyDict,
                                        identificationId + "." + eachSubmodelElem["idShort"], identificationId)
        return submodelProperetyDict

    def getSubmodelPropertyList(self, aasIdentifier):
        submodelNameList = []
        for submodel in self.pyaas.aasContentData[aasIdentifier]["submodels"]:
            submodelNameList.append(submodel)
        return submodelNameList

    def getSubmodelPropertyListDict(self, aasIdentifier):
        submodelPropertyListDict = {}
        i = 0
        submodels, status = self.pyaas.dba.getSubmodelsbyShell(aasIdentifier)
        for key, submodel in submodels.items():
            submodelName = submodel["idShort"]
            if not (submodelName in ["Mechanical break down", "Nameplate", "TechnicalData", "ManufacturerDocumentation",
                                     "Documentation", "Identification"]):  
                submodelProperetyDict = self.getSubmodePropertyDict(submodel)
                if (i == 0):
                    status = " fade show active"
                    i = 1
                else:
                    status = " fade show"
                submodelPropertyListDict[submodelName] = {"status": status,
                                                          "data": submodelProperetyDict,
                                                          "type": "collection"
                                                          }
        return submodelPropertyListDict

    def configureDescriptor(self, _shellId):
        aasDesc = AASDescriptor(self.pyaas)
        return aasDesc.createDescriptor(_shellId)

    def checkForOrderExistence(self, skill):
        if (skill["InitialState"] == "WaitforNewOrder"):
            return True
        else:
            return False

    def submodelElemeObject(self, idShortPath):
        _uuid = self.pyaas.aasHashDict.__getHashEntry__(idShortPath).__getId__()
        return self.pyaas.submodelHashDict.__getHashEntry__(_uuid)

    def getAssetAccessEndPoints(self):
        return {"OPCUA": ".io_opcua"}

    def get_available_skills(self) -> dict:
        skill_names = [f.split(".")[0] for f in os.listdir(self.pyaas.src_skills_repository) if
                       os.path.isfile(os.path.join(self.pyaas.src_skills_repository, f))]
        skillDetails = dict()
        for skill in skill_names:
            skillModule = import_module("." + skill, package="skills")
            skillBaseclass_ = getattr(skillModule, skill)
            _tempSKillInstance = skillBaseclass_(self.pyaas)

            skill_details_dict = dict()
            skill_details_dict["SkillName"] = skill
            skill_details_dict["SkillService"] = _tempSKillInstance.skill_service
            skill_details_dict["InitialState"] = _tempSKillInstance.initialState
            skill_details_dict["enabled"] = _tempSKillInstance.enabledState
            skill_details_dict["semanticProtocol"] = _tempSKillInstance.semanticProtocol
            skill_details_dict["SkillHandler"] = None

            skillDetails[skill] = skill_details_dict

            del _tempSKillInstance

        skillDetails["ProductionManager"] = {
            "SkillName": "ProductionManager",
            "SkillService": "Production Manager",
            "InitialState": "WaitforNewOrder",
            "enabled": "Y",
            "semanticProtocol": "",
            "SkillHandler": None,
        }
        skillDetails["Register"] = {
            "SkillName": "Register",
            "SkillService": "Registration",
            "InitialState": "WaitforNewOrder",
            "enabled": "Y",
            "semanticProtocol": "",
            "SkillHandler": None,
        }

        return skillDetails

    def get_asset_interface_description(self, submodel, aasIdentifier,_uuid) -> list:
        """
        Retrieves the Asset Interface Description submodel for the specified aas_id,
        extract the properties from the submodel and returns the list.
        """
        asset_interface_description = AssetInterfaceDescription()
        for tdELement in submodel["submodelElements"]:
            if tdELement["idShort"] == "properties":
                for aid_property in tdELement["value"]:
                    td_property = AIDProperty()
                    td_property.aasIdentifier = aasIdentifier
                    td_property.submodelIdentifier = submodel["id"]
                    
                    
                    for pConstraint in aid_property["qualifiers"]:
                        if (pConstraint["type"] == "type"):
                            td_property._type =  pConstraint["value"]
                        if (pConstraint["type"] == "SerialNumber"):
                            td_property.read_only =  pConstraint["value"]
                        if (pConstraint["type"] == "observable"):
                            td_property.observable =  pConstraint["value"]                     
                        if pConstraint["type"] == "updateFrequency":
                            td_property.update_frequencey =  pConstraint["value"]
                        if pConstraint["type"] == "unit":
                            td_property._unit = pConstraint["value"]
                        if (pConstraint["type"] == "submodelId"):
                            td_property.submodel_Identifier = pConstraint["value"]
                        if (pConstraint["type"] == "idShortPath"):
                            td_property.idshort_path = pConstraint["value"]
                    
                    if (td_property.idshort_path != "" and 
                                            td_property.submodel_Identifier):
                    
                        elem_uuid = self.pyaas.aasHashDict.__getHashEntry__(td_property.submodelIdentifier
                                                            +"."+td_property.idshort_path)
                    
                        td_property.elemObject = self.pyaas.submodelHashDict.__getHashEntry__(elem_uuid)
                    
                    for pelem in aid_property["value"]:
                        if pelem["idShort"] == "forms":
                            for formConstraint in pelem["value"][0]["qualifiers"]:
                                if formConstraint["type"] == "href":
                                    td_property.href = formConstraint["value"]
                                elif formConstraint["type"] == "requestType":
                                    td_property.requestType = formConstraint["value"]
            
                    asset_interface_description.add_property(td_property,aid_property["idShort"])
        
        return asset_interface_description                   

    def get_skills(self,aasIdentifier) -> dict:
        submodel,status  = self.retrieve_submodel_semantic_id(aasIdentifier,"www.ovgu.de/submodel/operationaldata")
        skills_list = []
        if status:
            for eachskill in submodel["submodelElements"]:
                for skillDetails in eachskill["value"]: 
                    if (skillDetails["idShort"] == "SkillName"):
                        skills_list.append(skillDetails["value"])
        return skills_list

    def retrieve_submodel_semantic_id(self,aasIdentifier,_semanticId):
        try:
            uuid = self.pyaas.aasHashDict.__getHashEntry__(aasIdentifier)._id
            _element = self.pyaas.aasShellHashDict.__getHashEntry__(uuid).getElement()
            for submodel in _element["submodels"]:
                _submodelid  = submodel["keys"][0]["value"]
                if self.pyaas.aasHashDict.__isKeyPresent__(_submodelid):
                    _id = self.pyaas.aasHashDict.__getHashEntry__(_submodelid)._id
                    data,status, code = self.pyaas.dba.GetSubmodelById(_submodelid)
                    if status:
                        if type(data) == dict:
                            if "semanticId" in data.keys():
                                if data["semanticId"]["keys"][0]["value"] == _semanticId:
                                    return data,True
            return "NO Data", False
        except Exception as e:
            return "NO Data", False