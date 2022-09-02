'''
Copyright (c) 2021-2022 OVGU LIA
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
'''
from flask_restful import Resource,request
from flask import render_template,Response,redirect,flash,make_response,send_file,send_from_directory
from requests.utils import unquote
import os
import uuid
import copy
try:
    from utils.utils import ExecuteDBModifier,ProductionStepOrder,ExecuteDBRetriever,AASMetaModelValidator,StandardSubmodelData
except ImportError:
    from main.utils.utils import ExecuteDBModifier,ProductionStepOrder,ExecuteDBRetriever,AASMetaModelValidator,StandardSubmodelData

class AssetAdministrationShells(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def get(self):
        try:
            edbR = ExecuteDBRetriever(self.pyAAS)
            data, status = edbR.execute({"data":None,"method":"getAASShells"})            
            if status:
                return make_response(data,200)
            else :
                return make_response(data,500)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at getAssetAdministrationShells Rest" + str(E))
            return make_response("Unexpected Internal Server Error",500)
        
    def post(self):
        try:
            data = request.json
            if "interactionElements" in data:
                pass
                #return self.pyAAS.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyAAS)           
                if(aasValid.validateAASShell(data)):
                    edm = ExecuteDBModifier(self.pyAAS)
                    data, status = edm.executeModifer({"data":data,"method":"postAASShell"})
                    if status:
                        return make_response(data,201)
                    else :
                        return make_response(data,500)
                else :
                    return make_response("The syntax of the passed Asset Administration Shell is not valid or malformed request",200)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at postAssetAdministrationShells Rest" + str(E))
            return make_response("Internal Server Error",500)

class ConceptDescriptions(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def get(self):
        try:
            edbR = ExecuteDBRetriever(self.pyAAS)
            data,status = edbR.execute({"data":None,"method":"getConceptDescriptions"})            
            if status:
                return make_response(data,200)
            else:
                return make_response(data,500)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at getConceptDescriptions Rest" + str(E))
            return make_response("Unexpected Internal Server Error",500)
        
    def post(self):
        try:
            data = request.json
            if "interactionElements" in data:
                pass
                #return self.pyAAS.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyAAS)           
                if(aasValid.validateConceptDescription(data)):
                    edm = ExecuteDBModifier(self.pyAAS)
                    data,status = edm.executeModifer({"data":data,"method":"postConceptDescription"})
                    if status:
                        return make_response(data,201)
                    else:
                        return make_response(data,500)
                else :
                    return make_response("The syntax of the passed Concept Description is not valid or malformed request",200)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at postConceptDescriptions Rest" + str(E))
            return make_response("Internal Server Error",500)

class Submodels(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def get(self):
        try:
            edbR = ExecuteDBRetriever(self.pyAAS)
            data, status = edbR.execute({"data":None,"method":"getSubmodels"})            
            if status:
                return make_response(data,201)
            else:
                return make_response(data,500)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at getSubmodels Rest" + str(E))
            return make_response("Unexpected Internal Server Error",500)
        
    def post(self):
        try:
            data = request.json
            if "interactionElements" in data:
                pass
                #return self.pyAAS.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyAAS)           
                if(aasValid.valitdateSubmodel(data)):
                    edm = ExecuteDBModifier(self.pyAAS)
                    data,status = edm.executeModifer({"data":data,"method":"postSubmodel"})
                    if status:
                        return make_response(data,201)
                    else:
                        return make_response(data,500)
                else :
                    return make_response("The syntax of the passed Submodel is not valid or malformed request",200)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at postSubmodels Rest" + str(E))
            return make_response("Internal Server Error",500)


class AssetAdministrationShell(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def get(self,aasIdentifier):
        try:
            aasIdentifier = unquote(aasIdentifier)
            edbR = ExecuteDBRetriever(self.pyAAS)
            data,status = edbR.execute({"data":aasIdentifier,"method":"getAASShell"})            
            if status:
                return make_response(data,201)
            else:
                return make_response(data,500)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at getAssetAdministrationShell Rest" + str(E))
            return make_response("Unexpected Internal Server Error",500)
        
    def put(self,aasIdentifier):
        try:
            data = request.json
            aasIdentifier = unquote(aasIdentifier)
            if "interactionElements" in data:
                pass
                #return self.pyAAS.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyAAS)           
                if(aasValid.validateAASShell(data)):
                    if (aasIdentifier == data["identification"]["id"] or aasIdentifier == ["idShort"]):
                        edm = ExecuteDBModifier(self.pyAAS)
                        data,status = edm.executeModifer({"data": {"_shellId":aasIdentifier,"_aasShell":data},"method":"putAASShell"})
                        if status:
                            return make_response(data,204)
                        else:
                            return make_response(data,500)
                    else:
                        return make_response("The aas-identifier in the uri and in AAS Shell do not match",200)
                else :
                    return make_response("The syntax of the passed Asset Administration Shell is not valid or malformed request",200)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at postAssetAdministrationShell Rest" + str(E))
            return make_response("Internal Server Error",500)

    def delete(self,aasIdentifier):
        try:
            aasIdentifier = unquote(aasIdentifier)
            edm = ExecuteDBModifier(self.pyAAS)
            data,status = edm.executeModifer({"data":aasIdentifier,"method":"deleteAASShell"})            
            if status:
                return make_response(data,204)
            else:
                return make_response(data,500)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at deleteAssetAdministrationShell Rest" + str(E))
            return make_response("Unexpected Internal Server Error",500)

class ConceptDescription(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def get(self,cdIdentifier):
        try:
            cdIdentifier = unquote(cdIdentifier)
            edbR = ExecuteDBRetriever(self.pyAAS)
            data,status = edbR.execute({"data":cdIdentifier,"method":"getConceptDescription"})  
            if status:
                return make_response(data,201)
            else:
                return make_response(data,500)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at getConceptionDescription Rest" + str(E))
            return make_response("Unexpected Internal Server Error",500)
        
    def put(self,cdIdentifier):
        try:
            data = request.json
            cdIdentifier = unquote(cdIdentifier)
            if "interactionElements" in data:
                pass
                #return self.pyAAS.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyAAS)           
                if(aasValid.validateConceptDescription(data)):
                    edm = ExecuteDBModifier(self.pyAAS)
                    data,status = edm.executeModifer({"data":{"_conceptDescriptionId":cdIdentifier,
                                                                "_conceptDescription":data},"method":"putConceptDescription"})
                    if status:
                        return make_response(data,204)
                else :
                    return make_response("The syntax of the passed Concept Description is not valid or malformed request",400)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at putConceptionDescription Rest" + str(E))
            return make_response("Internal Server Error",500)

    def delete(self,cdIdentifier):
        try:
            cdIdentifier = unquote(cdIdentifier)
            edm = ExecuteDBModifier(self.pyAAS)
            data,status = edm.executeModifer({"data":cdIdentifier,"method":"deleteConceptDescription"})  
            if status:
                return make_response(data,204)          
            else:
                return make_response(data,500)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at deleteConceptionDescription Rest" + str(E))
            return make_response("Unexpected Internal Server Error",500)
 
class Submodel(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def get(self,submodelIdentifier):
        try:
            submodelIdentifier = unquote(submodelIdentifier)
            edbR = ExecuteDBRetriever(self.pyAAS)
            data,status = edbR.execute({"data":submodelIdentifier,"method":"getSubmodel"})  
            if status:
                return make_response(data,200)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at getSubmodel Rest" + str(E))
            return make_response("Unexpected Internal Server Error",500)
        
    def put(self,submodelIdentifier):
        try:
            data = request.json
            submodelIdentifier = unquote(submodelIdentifier)
            if "interactionElements" in data:
                pass
                #return self.pyAAS.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyAAS)           
                if(aasValid.valitdateSubmodel(data)):
                    edm = ExecuteDBModifier(self.pyAAS)
                    data,status = edm.executeModifer({"data":{"_submodelid":submodelIdentifier,
                                                                "requestData":data},"method":"putSubmodel"})
                    if status:
                        return make_response(data,204)
                    else:
                        return make_response(data,500)
                else :
                    return make_response("The syntax of the passed Submodel is not valid or malformed request",400)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at putSubmodel Rest" + str(E))
            return make_response("Internal Server Error",500)

    def delete(self,submodelIdentifier):
        try:
            submodelIdentifier = unquote(submodelIdentifier)
            edbR = ExecuteDBRetriever(self.pyAAS)
            data,status = edbR.execute({"data":submodelIdentifier,"method":"deleteSubmodel"})  
            if status:
                return make_response(data,200)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at deleteSubmodel Rest" + str(E))
            return make_response("Unexpected Internal Server Error",500)

class AssetAdministrationShellsSubmodelRefs(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def get(self,aasIdentifier):
        try:
            edbR = ExecuteDBRetriever(self.pyAAS)
            data,status = edbR.execute({"data":aasIdentifier,"method":"getShellSubmodelRefs"})            
            if status:
                return make_response(data,200)
            else:
                return make_response(data,500)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at getAssetAdministrationShells Rest" + str(E))
            return make_response("Unexpected Internal Server Error",500)
        
    def post(self,aasIdentifier):
        try:
            data = request.json
            if "interactionElements" in data:
                pass
                #return self.pyAAS.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyAAS)           
                if(aasValid.validateAASShellSubmodelRef(data)):
                    edm = ExecuteDBModifier(self.pyAAS)
                    data,status = edm.executeModifer({"data":{"_shellId":aasIdentifier,"requestData":data
                                            },"method":"postShellSubmodelRef"})                      
                    if status:
                        return make_response(data,201)
                    else:
                        return make_response(data,500)
                else :
                    return make_response("The syntax of the passed Asset Administration Shell Submodel Reference is not valid or malformed request",200)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at postAssetAdministrationShells Rest" + str(E))
            return make_response("Internal Server Error",500)

class SubmodelELements(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def get(self,submodelIdentifier):
        try:
            edbR = ExecuteDBRetriever(self.pyAAS)
            data,status = edbR.execute({"data":submodelIdentifier,"method":"getSubmodelElements"})            
            if status:
                return make_response(data,200)
            else:
                return make_response(data,500)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at getSubmodelELements Rest" + str(E))
            return make_response("Unexpected Internal Server Error",500)
        
    def post(self,submodelIdentifier):
        try:
            data = request.json
            if "interactionElements" in data:
                pass
                #return self.pyAAS.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyAAS)           
                if(aasValid.validateSubmodelElement(data)):
                    edm = ExecuteDBModifier(self.pyAAS)
                    data,status = edm.executeModifer({"data":{"_idShortpath":submodelIdentifier,"requestData":data
                                            },"method":"postSubmodelElem"})                      
                    if status:
                        return make_response(data,201)
                    else:
                        return make_response(data,500)
                else :
                    return make_response("The syntax of the passed SubmodelElement is not valid or malformed request",200)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at postSubmodelELements Rest" + str(E))
            return make_response("Internal Server Error",500)

class SubmodelElementByIdShortPath(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
        
    def get(self,submodelIdentifier,idShortPath):
        try:
            submodelIdentifier = unquote(submodelIdentifier)
            idShortPath = unquote(idShortPath)
            edbR = ExecuteDBRetriever(self.pyAAS)
            data,status = edbR.execute({"data":submodelIdentifier+"."+idShortPath,"method":"getSubmodelElement",
                                            "instanceId" : str(uuid.uuid1())})            
            if status:
                return make_response(data,200)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at getSubmodelElementByIdShortPath Rest" + str(E))
            return make_response("Unexpected Internal Server Error",500)

    def put(self,submodelIdentifier,idShortPath):
        try:
            data = request.json
            submodelIdentifier = unquote(submodelIdentifier)
            idShortPath = unquote(idShortPath)
            if "interactionElements" in data:
                pass
                #return self.pyAAS.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyAAS)           
                if(aasValid.validateSubmodelELement(data)):
                    edm = ExecuteDBModifier(self.pyAAS)
                    msg,status = edm.executeModifer({"data":{"requestData":data,
                                            "_idShortpath" : submodelIdentifier+"."+idShortPath,
                                            },"method":"putSubmodelElem","instanceId" : str(uuid.uuid1())}) 
                    if status:
                        return make_response(msg,204)
                else :
                    return make_response("The syntax of the passed Submodel ELement is not valid or malformed request",400)                
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at putSubmodelElementByIdShortPath Rest" + str(E))
            return make_response("Internal Server Error",500)

    def post(self,submodelIdentifier,idShortPath):
        try:
            data = request.json
            submodelIdentifier = unquote(submodelIdentifier)
            idShortPath = unquote(idShortPath)
            if "interactionElements" in data:
                pass
                #return self.pyAAS.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyAAS)           
                if(aasValid.validateSubmodelELement(data)):
                    edm = ExecuteDBModifier(self.pyAAS)
                    msg,status = edm.executeModifer({"data":{"requestData":data,
                                            "_idShortpath" : submodelIdentifier+"."+idShortPath,
                                            },"method":"postSubmodelElem","instanceId" : str(uuid.uuid1())}) 
                    if status:
                        return make_response(msg,201)
                    else:
                        return make_response(msg,500)
                else :
                    return make_response("The syntax of the passed Submodel ELement is not valid or malformed request",400)                
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at postSubmodelElementByIdShortPath Rest" + str(E))
            return make_response("Internal Server Error",500)        


    def delete(self,submodelIdentifier,idShortPath):
        try:
            submodelIdentifier = unquote(submodelIdentifier)
            idShortPath = unquote(idShortPath)
            edm = ExecuteDBModifier(self.pyAAS)
            msg,status = edm.executeModifer({"data":submodelIdentifier+"."+idShortPath,"method":"deleteSubmodelElem","instanceId" : str(uuid.uuid1())})            
            if status:
                return make_response(msg,204)
            else:
                return make_response(msg,500)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at deleteSubmodelElementByIdShortPath Rest" + str(E))
            return make_response("Unexpected Internal Server Error",500)    

class AASSubmodelElementByIdShortPath(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
        
    def get(self,aasIdentifier,submodelIdentifier,idShortPath):
        try:
            submodelIdentifier = unquote(submodelIdentifier)
            idShortPath = unquote(idShortPath)
            edbR = ExecuteDBRetriever(self.pyAAS)
            msg,status = edbR.execute({"data":submodelIdentifier+"."+ idShortPath,"method":"getSubmodelElement","instanceId" : str(uuid.uuid1())})            
            if status:
                return make_response(msg,201)
            else:
                return make_response(msg,500)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at getSubmodelElementByIdShortPath Rest" + str(E))
            return make_response("Unexpected Internal Server Error",500)

    def put(self,aasIdentifier,submodelIdentifier,idShortPath):
        try:
            data = request.json
            submodelIdentifier = unquote(submodelIdentifier)
            idShortPath = unquote(idShortPath)
            if "interactionElements" in data:
                pass
                #return self.pyAAS.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyAAS)           
                if(aasValid.validateSubmodelELement(data)):
                    edm = ExecuteDBModifier(self.pyAAS)
                    msg,status = edm.executeModifer({"data":{"requestData":data, 
                                            "_idShortpath" : submodelIdentifier+"."+idShortPath
                                            },"method":"putSubmodelElem","instanceId" : str(uuid.uuid1())}) 
                    if status:
                        return make_response(msg,201)
                    else:
                        return make_response(msg,500)
                else :
                    return make_response("The syntax of the passed Submodel ELement is not valid or malformed request",400)                
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at putSubmodelElementByIdShortPath Rest" + str(E))
            return make_response("Internal Server Error",500)

    def post(self,aasIdentifier,submodelIdentifier,idShortPath):
        try:
            data = request.json
            submodelIdentifier = unquote(submodelIdentifier)
            idShortPath = unquote(idShortPath)
            if "interactionElements" in data:
                pass
                #return self.pyAAS.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyAAS)           
                if(aasValid.validateSubmodelELement(data)):
                    edm = ExecuteDBModifier(self.pyAAS)
                    msg,status = edm.executeModifer({"data":{"requestData":data, 
                                            "_idShortpath" : submodelIdentifier+"."+idShortPath
                                            },"method":"postSubmodelElem","instanceId" : str(uuid.uuid1())}) 
                    if status:
                        return make_response(msg,201)
                    else:
                        return make_response(msg,500)
                else :
                    return make_response("The syntax of the passed Submodel ELement is not valid or malformed request",400)                
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at postSubmodelElementByIdShortPath Rest" + str(E))
            return make_response("Internal Server Error",500)        

    def delete(self,aasIdentifier,submodelIdentifier,idShortPath):
        try:
            submodelIdentifier = unquote(submodelIdentifier)
            idShortPath = unquote(idShortPath)
            edm = ExecuteDBModifier(self.pyAAS)
            msg,status = edm.executeModifer({"data":submodelIdentifier+"."+idShortPath,"method":"deleteSubmodelElem","instanceId" : str(uuid.uuid1())})             
            if status:
                return make_response(msg,204)
            else:
                return make_response(msg,500)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at deleteSubmodelElementByIdShortPath Rest" + str(E))
            return make_response("Unexpected Internal Server Error",500)    
            
class AASassetInformation(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def get(self):
        try:
            edbR = ExecuteDBRetriever(self.pyAAS)
            msg,status = edbR.execute({"data":None,"method":"getAssetInformations"})            
            if status:
                return make_response(msg,200)
            else:
                return make_response(msg,500)
        except:
            return make_response("Unexpected Internal Server Error",500)

class AASassetInformationById(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS

    def get(self,assetId):
        try:
            assetId = unquote(assetId)
            edbR = ExecuteDBRetriever(self.pyAAS)
            msg,status = edbR.execute({"data":assetId,"method":"getAssetInformation"})            
            if status:
                return make_response(msg,200)
            else:
                return make_response(msg,500)
        except:
            return make_response("Unexpected Internal Server Error",500)
    
    def put(self,assetId):
        try:
            assetId = unquote(assetId)
            data = request.json
            if "interactionElements" in data: 
                pass
                #return self.pyAAS.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyAAS)           
                if(aasValid.valitdateAsset(data)):
                    edm = ExecuteDBModifier(self.pyAAS),
                    msg,status = edm.executeModifer({"data":{"requestData":data,"_id":assetId},"method":"putAsset","instanceId" : str(uuid.uuid1())})
                    if status:
                        return make_response(msg,201)
                    else:
                        return make_response(msg,500)
                else :
                    return make_response("The syntax of the passed Asset Administration Shell is not valid or malformed request",400)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at putAASassetInformationById Rest" + str(E))
            return make_response("Internal Server Error",500)

    def delete(self,aasetId):
        try:
            assetId = unquote(aasetId)
            edm = ExecuteDBModifier(self.pyAAS)
            msg,status = edm.executeModifer({"data":assetId,"method":"deleteAsset","instanceId" : str(uuid.uuid1())})
            if status:
                return make_response(msg,204)
            else:
                return make_response(msg,500)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at deleteAASassetInformationById Rest" + str(E))
            return make_response("Unexpected Internal Server Error",500)

class AASsubmodelRefs(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def get(self,aasId):
        try:
            aasId = unquote(aasId)
            edbR = ExecuteDBRetriever(self.pyAAS)
            msg,status = edbR.execute({"data":aasId,"method":"getShellSubmodelRefs"})            
            if status:
                return make_response(msg,201)
            else:
                return make_response(msg,500)
        except:
            return make_response("Unexpected Internal Server Error",500)
        

class AASsubmodelRefsIndentifier(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS

    def get(self,aasId,submodelId):
        try:
            aasId = unquote(aasId)
            submodelId = unquote(submodelId)
            edbR = ExecuteDBRetriever(self.pyAAS)
            data,status = edbR.execute({"data":{"_shellId": aasId,"_submodelrefId":submodelId},"method":"getShellSubmodelRef"})            
            if status:
                return make_response(data,200)
            else:
                return make_response(data,500)
        except:
            return make_response("Unexpected Internal Server Error",500)
      
    def put(self,aasId,submodelId):
        try:
            aasId = unquote(aasId)
            submodelId = unquote(submodelId)
            data = request.json
            if "interactionElements" in data:
                pass
                #return self.pyAAS.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else:
                if(True):
                    if (True):
                        edm = ExecuteDBModifier(self.pyAAS)
                        data,status = edm.executeModifer({"data":{"_shellId": aasId,"requestData":data}
                                                               ,"method":"putShellSubmodelRef","instanceId" : str(uuid.uuid1())})            
                        if status:
                            return make_response(data,204)
                    else:
                        return make_response("The namspace SubmodelId value and the IdShort value do not match",500)
                else:
                    return make_response("The syntax of the passed submodel data is not valid or malformed request",400)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at putAASsubmodelRefsIndentifier Rest" + str(E))
            return make_response("Unexpected Internal Server Error",500)

    def delete(self,aasId,submodelId):
        try:
            aasId = unquote(aasId),
            submodelId = unquote(submodelId)
            edm = ExecuteDBModifier(self.pyAAS)
            data,status = edm.executeModifer({"data":{"_shellId":aasId,"_submodelrefId":submodelId},
                                                   "method":"deleteShellSubmodelRef","instanceId" : str(uuid.uuid1())})
            if status:
                return make_response(data,204)     
            else:
                return make_response(data,500)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at deleteAASsubmodelRefsIndentifier Rest" + str(E))
            return make_response("Unexpected Internal Server Error",500)

class RetrieveMessage(Resource):    
    def __init__(self, pyAAS):
        self.pyAAS = pyAAS
        
    def post(self):
        jsonMessage = request.json
        try:
            if (jsonMessage["frame"]["sender"]["identification"]["id"] == self.pyAAS.AASID):
                pass
            else:
                try:
                    receExists = jsonMessage["frame"]["receiver"]["identification"]["id"]
                    self.msgHandler.putIbMessage(jsonMessage)
                except Exception as E:
                    self.handleBoradCastMessage(jsonMessage)
        except:
            pass
        
    def handleBoradCastMessage(self,jsonMessage):
        if ((jsonMessage["frame"]["conversationId"] not in self.pyAAS.conversationInteractionList)):
            self.pyAAS.serviceLogger.info("Test1 handleBoradCastMessage")
            self.pyAAS.dba.createNewConversation(jsonMessage["frame"]["conversationId"])
            self.pyAAS.conversationInteractionList.append(jsonMessage["frame"]["conversationId"])
            self.instanceId = str(uuid.uuid1())
            self.pyAAS.dataManager.pushInboundMessage({"functionType":3,"instanceid":self.instanceId,
                                                           "conversationId":jsonMessage["frame"]["conversationId"],
                                                           "messageType":jsonMessage["frame"]["type"],
                                                           "messageId":jsonMessage["frame"]["messageId"],
                                                           "direction":"inbound",
                                                           "SenderAASID" : "Broadcast",
                                                           "message":jsonMessage})            
            self.msgHandler.putIbMessage(jsonMessage)       


class AASStaticSource(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
        
    def get(self,filename):      
        try:
            return send_from_directory(self.pyAAS.downlaod_repository,filename)
        except Exception as E:
            print(str(E))        

class AASStaticWebSources(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
        
    def get(self,webtype,filename):
        try:
            if (webtype == "js"):
                return send_from_directory(self.pyAAS.js_repository,filename) 
            elif (webtype == "css"):
                return send_from_directory(self.pyAAS.css_repository,filename) 
            elif (webtype == "images"):
                return send_from_directory(self.pyAAS.img_repository,filename)            
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at getAASStaticWebSources Rest" + str(E))

class AASWebInterfaceHome(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS

    def get(self):              
        try:
            return  Response(render_template('home.html',thumbNailList = self.pyAAS.thumbNailList,
                                                         exDomain=self.pyAAS.exDomain,
                                                         aasList = self.pyAAS.AASData))
        except Exception as E:
            return str(E)

class AASWebInterface(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS

    def get(self,aasIndex):
        try:
            
            return  Response(render_template('index.html',thumbNail= self.pyAAS.thumbNailList[aasIndex],
                                                        aasIndex=aasIndex, exDomain=self.pyAAS.exDomain , 
                                                        skillList= self.pyAAS.skillListWeb[aasIndex],
                                                        aasIdShort = self.pyAAS.aasIndexidShortDict[aasIndex]["idShort"],
                                                        stdSubmodelList = self.pyAAS.aasStandardSubmodelList[aasIndex]))
        except Exception as E:
            return str(E)

class AASWebInterfaceStandardSubmodel(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
        self.standardSubmodelWebPageDict = {"NAMEPLATE" : "nameplate.html", "DOCUMENTATION" : "documentation.html" ,
                                            "TECHNICAL_DATA" : "technicaldata.html" , "IDENTIFICATION": "identification.html"}
    def get(self,aasIndex,stdsubmodelType):    
        try:
            _stdSubmodel = self.pyAAS.aasStandardSubmodelData[aasIndex][stdsubmodelType]
            stdSubmodel = copy.deepcopy(_stdSubmodel)
            stdSubmodelData = stdSubmodel[1]
            stdData = StandardSubmodelData(self.pyAAS)
            if stdsubmodelType == "NAMEPLATE":
                stdSubmodelData["DE"]["data"] = stdData.execute(stdSubmodelData["DE"]["data"], "DE")
                stdSubmodelData["EN"]["data"] = stdData.execute(stdSubmodelData["EN"]["data"], "EN")
            elif stdsubmodelType in ["TECHNICAL_DATA","IDENTIFICATION"]:
                stdSubmodelData =  stdData.execute(stdSubmodelData, None)
                
            return  Response(render_template(self.standardSubmodelWebPageDict[stdsubmodelType],
                                                 aasIndex=aasIndex,exDomain=self.pyAAS.exDomain,
                                                 skillList= self.pyAAS.skillListWeb[aasIndex],
                                                 stdSubmodelList = self.pyAAS.aasStandardSubmodelList[aasIndex],
                                                 aasIdShort = self.pyAAS.aasIndexidShortDict[aasIndex]["idShort"],
                                                 submodelidentificationId = stdSubmodel[0],
                                                 stdSubmodelData = stdSubmodelData))
        except Exception as E:
            return str(E)    

class AASWebInterfaceSKillLog(Resource):
    
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS

    def get(self,aasIndex,skillName):
        return  Response(render_template('skill.html',
                                             aasIndex=aasIndex, exDomain=self.pyAAS.exDomain, 
                                             skillList= self.pyAAS.skillListWeb[aasIndex],
                                             stdSubmodelList = self.pyAAS.aasStandardSubmodelList[aasIndex],
                                            aasIdShort = self.pyAAS.aasIndexidShortDict[aasIndex]["idShort"],
                                            skillName = skillName))

    def post(self,aasIndex,skillName):
        try:
            if (skillName == "Production Manager"):
                skillName = "ProductionManager"
            return self.pyAAS.skilllogListDict[aasIndex][unquote(skillName)].getCotent()
        except Exception as E:
            return str(E)

class AASWebInterfaceSubmodels(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS

    def get(self,aasIndex):       
        try:
            propertyListDict=(self.pyAAS.getSubmodelPropertyListDict(self.pyAAS.aasIndexidShortDict[aasIndex]["identificationId"]))
            return  Response(render_template('submodels.html',
                                                 aasIndex=aasIndex,exDomain=self.pyAAS.exDomain,
                                                 skillList= self.pyAAS.skillListWeb[aasIndex],
                                                 stdSubmodelList = self.pyAAS.aasStandardSubmodelList[aasIndex],
                                                 aasIdShort = self.pyAAS.aasIndexidShortDict[aasIndex]["idShort"],
                                                 propertyListDict=propertyListDict ))
        except Exception as e:
            return str(e)


class AASWebInterfaceSearch(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def post(self,aasIndex):
        try:
            updateInfo = request.form
            query =  updateInfo["searchQuery"]
            identificationId  = self.pyAAS.aasIndexidShortDict[aasIndex]["identificationId"]
            conversaation,status = self.pyAAS.dba.getConversationsById(query,identificationId)
            if status:
                return  Response(render_template('search.html',
                                                  aasIndex=aasIndex,exDomain=self.pyAAS.exDomain,
                                                 skillList= self.pyAAS.skillListWeb[aasIndex],
                                                 stdSubmodelList = self.pyAAS.aasStandardSubmodelList[aasIndex],
                                                 aasIdShort = self.pyAAS.aasIndexidShortDict[aasIndex]["idShort"],
                                                 resultList = {query:conversaation}))
            else:
                count = self.pyAAS.dba.getMessageCount()
                flash("The conversation Id is not found, the last count is " + str(count["message"][0]),"error")
                return redirect("/"+str(aasIndex)+"/home")
                
        except Exception as E:
            flash("Error","error")
            self.pyAAS.serviceLogger.info("Error at postAASWebInterfaceSearch Rest" + str(E))
            return redirect("/"+str(aasIndex)+"/home")


class AASWebInterfaceConversationMessage(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def get(self,aasIndex,query):         
        try:
            queryList = str(unquote(query)).split("**")
            return self.pyAAS.dba.getMessagebyId(queryList[0],queryList[1])
        except Exception as E:
            return str(queryList) + str(E)

class AASWebInterfaceProductionManagement(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS

    def get(self,aasIndex):   
        try:
            productionSequenceList =  []
            if (aasIndex in self.pyAAS.productionSequenceList):
                productionSequenceList = self.pyAAS.productionSequenceList[aasIndex]
            else:
                self.pyAAS.productionSequenceList[aasIndex] = []
            return Response(render_template('productionmanager.html',
                                                aasIndex=aasIndex,exDomain=self.pyAAS.exDomain,
                                                 skillList= self.pyAAS.skillListWeb[aasIndex],
                                                 stdSubmodelList = self.pyAAS.aasStandardSubmodelList[aasIndex],
                                                 aasIdShort = self.pyAAS.aasIndexidShortDict[aasIndex]["idShort"],
                                                productionStepList=self.pyAAS.productionStepList[aasIndex],
                                                conversationIdList=self.pyAAS.conversationIdList[aasIndex][-5:],
                                                productionSequenceList=productionSequenceList))
        except Exception as e:
            return str(e)

    def post(self,aasIndex):
        updateInfo = request.form
        tag =  updateInfo["operationType"]   
        
        if (tag =="home"):
            return redirect("/"+str(aasIndex)+"/productionmanager")
        
        elif (tag == "create"):
            productionStep = request.form.get("productionStep")
            self.pyAAS.productionSequenceList[aasIndex].append(productionStep)
            flash("New Production step is added","success")
            return redirect("/"+str(aasIndex)+"/productionmanager")
        
        elif (tag == "delete"):
            self.pyAAS.productionSequenceList[aasIndex] = []
            flash("New Production step is added","success")
            return redirect("/"+str(aasIndex)+"/productionmanager")
        
        elif (tag == "start"):
            try:
                pso = ProductionStepOrder(self.pyAAS)
                conversationID = pso.createProductionStepOrder(aasIndex)
                flash("New Order booked with Order ID " + conversationID + " is booked","info")
                return redirect("/"+str(aasIndex)+"/productionmanager")   
            except  Exception as E:
                print(str(E))
                flash("Error creating the conversation Id.","error")
                return redirect("/"+str(aasIndex)+"/productionmanager")

class AASWebInterfaceRegister(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS

    def post(self,aasIndex):
        try: 
            pso = ProductionStepOrder(self.pyAAS)
            conversationID = pso.createRegistrationStep(aasIndex)
            flash("New Resgitration  Order with Order ID " + conversationID + " is booked","info")
            return redirect("/"+str(aasIndex)+"/registration")   
        except  Exception as E:
            flash("Registration Failed"+str(E),"error")
            return redirect("/"+str(aasIndex)+"/registration") 
    

    def get(self,aasIndex):
        return  Response(render_template('registration.html',
                                         aasIndex=aasIndex,exDomain=self.pyAAS.exDomain,
                                         skillList= self.pyAAS.skillListWeb[aasIndex],
                                         stdSubmodelList = self.pyAAS.aasStandardSubmodelList[aasIndex],
                                         aasIdShort = self.pyAAS.aasIndexidShortDict[aasIndex]["idShort"]))

class AASWebInterfaceSubmodelElemValue(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS

    def getSubmodelIdentificationId(self,aasIdentifier,submodelIdentifier):
        aaData = self.pyAAS.aasContentData[aasIdentifier]
        for submodel in aaData["submodels"]:
            if (submodel["idShort"] == submodelIdentifier):
                return submodel["identification"]["id"]
        
    
    def getRelevantElemData(self,aasIdentifier,updateValue,idShortPath,submodelName,submodelElemAdditionalInfo,submodelELemType,submodelidentificationId):
        try:
            edbR = ExecuteDBRetriever(self.pyAAS)
            msg,status = edbR.execute({"data":submodelidentificationId+"."+ idShortPath,"method":"getSubmodelElement",
                                       "instanceId" : str(uuid.uuid1())})            
            
            if status:
                elemType = msg["modelType"]["name"]
                if (elemType == "Property"):
                    msg["value"] = updateValue
                elif (elemType == "Range"):
                    msg[submodelElemAdditionalInfo] = updateValue
                elif (elemType == "MultiLanguageProperty"):
                    for index,langString in enumerate(msg["value"]["langString"]):
                        if langString ["language"].upper() == submodelElemAdditionalInfo.upper():
                            msg["value"]["langString"][index] = updateValue
                            return msg,True
                    langString = {"language": submodelElemAdditionalInfo,"text": updateValue}
                    msg["value"]["langString"].append(langString)
                return msg,True             
            else:
                return msg,status

        except Exception as E:  
            print(str(E))         
            return "Error", False
    
    def performDBUpdate(self,aasIdentifier,updateValue,submodelELemType,submodelName,idShortPath,submodelElemAdditionalInfo,submodelidentificationId):
        try:
            edm = ExecuteDBModifier(self.pyAAS)
            elemData,status = self.getRelevantElemData(aasIdentifier,updateValue,idShortPath,submodelName,submodelElemAdditionalInfo,
                                                submodelELemType,submodelidentificationId)
            if status :
                msg1,status1 = edm.executeModifer({"data":{"elemData":elemData, 
                                                "_idShortpath" : submodelidentificationId+"."+idShortPath
                                                },"method":"putSubmodelElem","instanceId" : str(uuid.uuid1())})     
                return  msg1,status1  
                
        except Exception as E:
            print(str(E)) 

    def put(self,aasIdentifier):
        try:    
            updateData = request.form
            submodelName = updateData["submodelName"]
            submodelELemType = updateData["submodelElemType"]
            idShortPath = updateData["submodelElemidShortPath"]
            updateValue = updateData["newValue"]
            submodelElemAdditionalInfo = updateData["submodelElemAdditionalInfo"]
            submodelidentificationId = updateData["submodelidentificationId"]
            print(self.performDBUpdate(aasIdentifier,updateValue,submodelELemType,submodelName,idShortPath,submodelElemAdditionalInfo,submodelidentificationId))
        except Exception as E:
            print(str(E))
        
class AASDocumentationDownloadSubmodel(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def get(self,aasId,filename):
        try:
            file_path = os.path.join(self.pyAAS.downlaod_repository,filename)
            sendfile = send_file(file_path,attachment_filename=filename, as_attachment=True)
            return  sendfile
        except Exception as E:
            print(str(E))

class AASDocumentationDownload(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def get(self,filename):
        try:
            file_path = os.path.join(self.pyAAS.downlaod_repository,filename)
            sendfile = send_file(file_path,attachment_filename=filename, as_attachment=True,mimetype= "application/pdf")
            return  sendfile
        except Exception as E:
            print(str(E))

class AASRTDataVisualizer(Resource):        
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS

    def get(self,aasId):          
        return  Response(render_template('rtdata.html',aasIndex=aasId,exDomain=self.pyAAS.exDomain ,
                                         tdProperties = self.pyAAS.aasStandardSubmodelData[aasId]["AssetInterfaceDescription"][1],
                                         skillList= self.pyAAS.skillListWeb[aasId],
                                         stdSubmodelList = self.pyAAS.aasStandardSubmodelList[aasId],
                                         aasIdShort = self.pyAAS.aasIndexidShortDict[aasId]["idShort"]))
    def post(self,aasId):
        returnData = {}
        try:
            for key,tdPData in self.pyAAS.tdPropertiesList[aasId].items(): 
                dataElement = tdPData["dataElement"]
                returnData[key] = {'label': [(dt.timestamp).split(" ")[1] for dt in dataElement.history][-19:], 'value': [dt.aasELemObject for dt in dataElement.history][-19:]}
            return returnData
        except Exception as E:
            print(E)
            return {}