'''
Copyright (c) 2021-2022 OVGU LIA
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
'''
from flask_restful import Resource,request
from flask import render_template,Response,redirect,flash,make_response,send_file,send_from_directory,jsonify
from urllib.parse import unquote
import base64
import json
import os
import uuid
import copy
import urllib
from werkzeug.utils import secure_filename
try:
    from utils.utils import ExecuteDBModifier,ProductionStepOrder,ExecuteDBRetriever,AASMetaModelValidator,Generate_AAS_Shell,UUIDGenerator,AIDProperty,AssetInterfaceDescription
except ImportError:
    from src.main.utils.utils import ExecuteDBModifier,ProductionStepOrder,ExecuteDBRetriever,AASMetaModelValidator,Generate_AAS_Shell,UUIDGenerator,AIDProperty,AssetInterfaceDescription
#from jwkest.jws import JWSig, SIGNER_ALGS, JWS
#from jwkest.jwk import rsa_load, RSAKey,pem_cert2rsa,der_cert2rsa,der2rsa
#from jwkest.jwt import b64encode_item

#AssetAdministrationShells,AssetAdministrationShellById,AssetAdministrationShellsByAssetId

#
fileformat = dict()
fileformat = {"txt":"text/plain","xml":"text/xml","html":"text/html","josn":"application/json",
"rdf":"application/rdf+xml","pdf":"application/pdf","jpeg":"image/jpeg",
"png":"image/png","gif":"image/gif","igs":"application/iges",
"iges":"application/iges","stp":"application/step"}

##################################################
'''
Shell Repository Interface Start
'''


class AssetAdministrationShells(Resource):
    def __init__(self,pyaas):
        self.pyaas = pyaas
        
    def get(self):
        """
        """
        try:
            reqData = {}
            if (request.data.decode("utf-8") != ""):
                try:
                    data = json.loads(reqData.decode("utf-8"))
                    if ("assetids" in reqData.keys()):
                        data, status,statuscode = self.pyaas.dba.GetAllAssetAdministrationShellsByAssetId()          
                        return make_response(data,statuscode)
                    elif ("idShorts" in reqData.keys()):
                        data, status,statuscode = self.pyaas.dba.GetAllAssetAdministrationShellsByIdShort()            
                        return make_response(data,statuscode)
                except:
                    pass           
            else:
                data, status,statuscode = self.pyaas.dba.GetAllAssetAdministrationShells()            
                return make_response(jsonify(data),statuscode)
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at getAssetAdministrationShells Rest" + str(E))
            return make_response("Internal Server Error",500)
        
    def post(self):
        """
        """
        try:
            data = request.json
            if "interactionElements" in data:
                pass
                #return self.pyaas.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyaas)           
                if(aasValid.validateAASShell(data)):
                    edm = ExecuteDBModifier(self.pyaas)
                    data,status,statuscode = edm.execute({"data":data, "method": "PostAssetAdministrationShell",
                                                                 "instanceId" : str(uuid.uuid1())})
                    return make_response(data,statuscode)
                else :
                    return make_response("The syntax of the passed Asset Administration Shell is not valid or malformed request",400)
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at postAssetAdministrationShells Rest" + str(E))
            return make_response("Internal Server Error",500)

class AssetAdministrationShellById(Resource):
    def __init__(self,pyaas):
        self.pyaas = pyaas
    
    def get(self,aasIdentifier):
        try:
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            data,status,statuscode = self.pyaas.dba.GetAssetAdministrationShellById(aasIdentifier)            
            return make_response(jsonify(data),statuscode)
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at getAssetAdministrationShellById  REST API" + str(E))
            return make_response("Internal Server Error",500)
        
    def put(self,aasIdentifier):
        try:
            data = request.json
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            if "interactionElements" in data:
                pass
                #return self.pyaas.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyaas)           
                if(aasValid.validateAASShell(data)):
                    if (aasIdentifier == data["id"] or aasIdentifier == ["idShort"]):
                        edm = ExecuteDBModifier(self.pyaas)
                        data,status,statuscode = edm.execute({"data": {"_shellId":aasIdentifier, "_aasShell":data}, "method": "PutAssetAdministrationShellById",
                                                                     "instanceId" : str(uuid.uuid1())})
                        return make_response(data,statuscode)
                    else:
                        return make_response("The aas-identifier in the uri and in AAS Shell do not match",400)
                else :
                    return make_response("The syntax of the passed Asset Administration Shell is not valid or malformed request",400)
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at PutAssetAdministrationShellById Rest" + str(E))
            return make_response("Internal Server Error",500)

    def delete(self,aasIdentifier):
        try:
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            edm = ExecuteDBModifier(self.pyaas)
            data,status,statuscode = edm.execute({"data":aasIdentifier, "method": "DeleteAssetAdministrationShellById",
                                                         "instanceId" : str(uuid.uuid1())})
            return make_response(data,statuscode)          
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at DeleteAssetAdministrationShellById REST API" + str(E))
            return make_response("Internal Server Error",500)

'''
Shell Repository Interface End
'''

##################################################
'''
Asset Administration Shell Interface start

'''
class AssetAdministrationShell(Resource):
    def __init__(self,pyaas):
        self.pyaas = pyaas
    
    def get(self,aasIdentifier):
        try:
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            data,status,statuscode = self.pyaas.dba.GetAssetAdministrationShell(aasIdentifier)            
            return make_response(jsonify(data),statuscode)
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at GetAssetAdministrationShell  REST API" + str(E))
            return make_response("Internal Server Error",500)
        
    def put(self,aasIdentifier):
        try:
            data = request.json
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            if "interactionElements" in data:
                pass
                #return self.pyaas.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyaas)           
                if(aasValid.validateAASShell(data)):
                    if (aasIdentifier == data["id"] or aasIdentifier == ["idShort"]):
                        edm = ExecuteDBModifier(self.pyaas)
                        data,status,statuscode = edm.execute({"data": {"_shellId":aasIdentifier, "_aasShell":data}, "method": "PutAssetAdministrationShell",
                                                                     "instanceId" : str(uuid.uuid1())})
                        return make_response(data,statuscode)
                    else:
                        return make_response("The aas-identifier in the uri and in AAS Shell do not match",400)
                else :
                    return make_response("The syntax of the passed Asset Administration Shell is not valid or malformed request",400)
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at PutAssetAdministrationShell Rest" + str(E))
            return make_response("Internal Server Error",500)

class SubmodelReferences(Resource):
    def __init__(self,pyaas):
        self.pyaas = pyaas
    
    def get(self,aasIdentifier):
        try:
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            data,status,statuscode = self.pyaas.dba.GetAllSubmodelReferences(aasIdentifier)            
            return make_response(jsonify(data),statuscode)
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at GetAllSubmodelReferences Rest" + str(E))
            return make_response("Internal Server Error",500)

    def post(self,aasIdentifier):
        try:
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            data = request.json
            if "interactionElements" in data:
                pass
                #return self.pyaas.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyaas)           
                if(aasValid.validateAASShellSubmodelRef(data)):
                    edm = ExecuteDBModifier(self.pyaas)
                    data,status,statuscode = edm.execute({"data": {"_shellId":aasIdentifier, "_Reference":data}, "method": "PostSubmodelReference",
                                                                 "instanceId" : str(uuid.uuid1())})
                    return make_response(data,statuscode)
                else :
                    return make_response("The syntax of the passed Submodel Reference is not valid or malformed request",400)
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at postAssetAdministrationShells Rest" + str(E))
            return make_response("Internal Server Error",500)        

class DeleteSubmodelReference(Resource):
    def __init__(self,pyaas):
        self.pyaas = pyaas
    
    def delete(self,aasIdentifier,submodelIdentifier):    
        try:
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            edm = ExecuteDBModifier(self.pyaas)
            data,status,statuscode = edm.execute({"data":{"_shellId":aasIdentifier, "submodelIdentifier":submodelIdentifier}, "method": "DeleteSubmodelReference",
                                                         "instanceId" : str(uuid.uuid1())})
            return make_response(data,statuscode)            
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at DeleteSubmodelReference REST API" + str(E))
            return make_response("Internal Server Error",500)

class AssetInformation(Resource):
    def __init__(self,pyaas):
        self.pyaas = pyaas

    def get(self,aasIdentifier):
        try:
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            data,status,statuscode = self.pyaas.dba.GetAssetInformation(aasIdentifier)            
            return make_response(data,statuscode)     
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at GetAssetInformation REST API" + str(E))
            return make_response("Internal Server Error",500)
    
    def put(self,aasIdentifier):
        try:
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            data = request.json
            if "interactionElements" in data: 
                pass
                #return self.pyaas.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyaas)           
                if(aasValid.valitdateAssetInformation(data)):
                    edm = ExecuteDBModifier(self.pyaas)
                    data,status,statuscode = edm.execute({"data": {"_shellId":aasIdentifier, "_assetInformation":data}, "method": "PutAssetInformation",
                                                                 "instanceId" : str(uuid.uuid1())})
                    return make_response(data,statuscode)                    
                else :
                    return make_response("The syntax of the passed AssetInformation is not valid or malformed request",400)
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at PutAssetInformation Rest" + str(E))
            return make_response("Internal Server Error",500)

'''
Asset Administration Shell Interface End

'''

##################################################
'''
Submodel Interface Start 
'''
#extra start
class Submodels_shell(Resource):
    def __init__(self,pyaas):
        self.pyaas = pyaas
    
    def get(self,aasIdentifier): 
        try:
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            data,status,statuscode = self.pyaas.dba.GetSubmodels_shell(aasIdentifier)  
            return make_response(data,statuscode)
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at GetSubmodel Rest" + str(E))
            return make_response("Internal Server Error",500)

#extra end
class Submodel(Resource):
    def __init__(self,pyaas):
        self.pyaas = pyaas
    
    def get(self,aasIdentifier,submodelIdentifier): 
        try:
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            data,status,statuscode = self.pyaas.dba.GetSubmodel(aasIdentifier,submodelIdentifier)  
            return make_response(data,statuscode)
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at GetSubmodel Rest" + str(E))
            return make_response("Internal Server Error",500)

        
    def put(self,aasIdentifier,submodelIdentifier): 
        try:
            data = request.json
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            if "interactionElements" in data:
                pass
                #return self.pyaas.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyaas)           
                if(aasValid.valitdateSubmodel(data)):
                    edm = ExecuteDBModifier(self.pyaas)
                    data,status,statuscode = edm.execute({"data":{"submodelIdentifier":submodelIdentifier, "_shellId":aasIdentifier,
                                                                "submodelData":data},"method":"PutSubmodel","instanceId" : str(uuid.uuid1())})
                    return make_response(data,statuscode)
                else :
                    return make_response("The syntax of the passed Submodel is not valid or malformed request",400)
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at PutSubmodel Rest" + str(E))
            return make_response("Internal Server Error",500)

class SubmodelElements(Resource):
    def __init__(self,pyaas):
        self.pyaas = pyaas
    
    def get(self,aasIdentifier,submodelIdentifier):
        try:
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            data,status,statuscode = self.pyaas.dba.GetAllSubmodelElements(aasIdentifier,submodelIdentifier)            
            return make_response(jsonify(data),statuscode)
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at GetAllSubmodelElements Rest" + str(E))
            return make_response("Internal Server Error",500)


    def post(self,aasIdentifier,submodelIdentifier):
        try:
            data = request.json
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            if "interactionElements" in data:
                pass
                #return self.pyaas.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyaas)           
                if(aasValid.validateSubmodelElement(data)):
                    edm = ExecuteDBModifier(self.pyaas)
                    data,status,statuscode = edm.execute({"data":{"elemData":data,
                                            "submodelIdentifier" : submodelIdentifier,"_shellId": aasIdentifier
                                                                  },"method":"PostSubmodelElement","instanceId" : str(uuid.uuid1())})
                    return make_response(data,statuscode)
                else :
                    return make_response("The syntax of the passed Submodel ELement is not valid or malformed request",400)                
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at PostSubmodelElement Rest" + str(E))
            return make_response("Internal Server Error",500)              

class SubmodelElementByPath(Resource):
    def __init__(self,pyaas):
        self.pyaas = pyaas
        
    def get(self,aasIdentifier,submodelIdentifier,idShortPath):
        try:
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            idShortPath = unquote(idShortPath)
            data,status,statuscode = self.pyaas.dba.GetSubmodelElementByPath(aasIdentifier,submodelIdentifier,idShortPath)            
            return make_response(data,statuscode)
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at GetSubmodelElementByPath Rest" + str(E))
            return make_response("Internal Server Error",500)

    def post(self,aasIdentifier,submodelIdentifier,idShortPath):
        try:
            data = request.json
            idShortPath = unquote(idShortPath)
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            if "interactionElements" in data:
                pass
                #return self.pyaas.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else:
                aasValid = AASMetaModelValidator(self.pyaas)           
                if(aasValid.validateSubmodelElement(data)):
                    edm = ExecuteDBModifier(self.pyaas)
                    data,status,statuscode = edm.execute({"data":{"_shellId":aasIdentifier, "submodelIdentifier":submodelIdentifier,
                                                   "idShortPath":idShortPath,"elemData":data},"method":"PostSubmodelElementByPath","instanceId" : str(uuid.uuid1())}) 
                    return make_response(data,statuscode)
                else :
                    return make_response("The syntax of the passed Submodel ELement is not valid or malformed request",400)                
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at PostSubmodelElementByPath Rest" + str(E))
            return make_response("Internal Server Error",500)        

    def put(self,aasIdentifier,submodelIdentifier,idShortPath):
        try:
            data = request.json
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            idShortPath = unquote(idShortPath)
            if "interactionElements" in data:
                pass
                #return self.pyaas.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyaas)           
                if(aasValid.validateSubmodelElement(data)):
                    edm = ExecuteDBModifier(self.pyaas)
                    data,status,statuscode = edm.execute({"data":{"_shellId":aasIdentifier, "submodelIdentifier":submodelIdentifier,
                                               "idShortPath":idShortPath,"elemData":data},"method":"PutSubmodelElementByPath","instanceId" : str(uuid.uuid1())}) 
                    return make_response(data,statuscode)
                else :
                    return make_response("The syntax of the passed Submodel ELement is not valid or malformed request",400)                
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at PutSubmodelElementByPath Rest" + str(E))
            return make_response("Internal Server Error",500)  

    def delete(self,aasIdentifier,submodelIdentifier,idShortPath):
        try:
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            idShortPath = unquote(idShortPath)
            edm = ExecuteDBModifier(self.pyaas)
            data,status,statuscode = edm.execute({"data":{"_shellId":aasIdentifier, "submodelIdentifier":submodelIdentifier,
                                               "idShortPath":idShortPath},"method":"DeleteSubmodelElementByPath","instanceId" : str(uuid.uuid1())})            
            return make_response(data,statuscode)
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at DeleteSubmodelElementByPath Rest" + str(E))
            return make_response("Internal Server Error",500)   

#SubmodelElementByPath_history,SubmodelElementByPath_SRI_history
class SubmodelElementByPath_history(Resource):
    def __init__(self,pyaas):
        self.pyaas = pyaas
        
    def get(self,aasIdentifier,submodelIdentifier,idShortPath):
        try:
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            idShortPath = unquote(idShortPath)
            data,status,statuscode = self.pyaas.dba.GetSubmodelElementByPath_History(aasIdentifier,submodelIdentifier,idShortPath)
            return make_response(data,statuscode)
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at GetSubmodelElementByPath_histtory Rest" + str(E))
            return make_response("Internal Server Error",500)

class FileByPath(Resource):
    def __init__(self,pyaas):
        self.pyaas = pyaas

    def get(self,aasIdentifier,submodelIdentifier,idShortPath):
        try:
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            idShortPath = unquote(idShortPath)            
            data, status,statuscode = self.pyaas.dba.GetFileByPath(aasIdentifier,submodelIdentifier,idShortPath)            
            if status:
                fileExtension = (data.split(".")[-1]).lower()
                filename = (data.split("/"))[-1]
                if fileExtension in fileformat:
                    file_path = os.path.join(self.pyaas.downlaod_repository,*(data).split("/"))
                    sendfile = send_file(file_path,attachment_filename=filename, as_attachment=True,mimetype= fileformat[fileExtension])
                else:
                    file_path = os.path.join(self.pyaas.downlaod_repository,*(data).split("/"))
                    sendfile = send_file(file_path,attachment_filename=filename, as_attachment=True,mimetype="text/plain")
                return  sendfile
            else:
                return make_response(data,status)
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at GetFileByPath  REST API" + str(E))
            return make_response("Internal Server Error",500)
        
    def put(self,aasIdentifier,submodelIdentifier,idShortPath):
        try:
            if False:
                pass
                #return self.pyaas.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
                submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
                if 'file' not in request.files:
                    return make_response("Internal Server Error",500)
                file = request.files['file']
                if file.filename == '':
                    return make_response("Internal Server Error",500)
                
                filename = secure_filename(file.filename)
                fileExtension = (filename.split(".")[-1]).lower()
                mimeType = ""
                if fileExtension in fileformat:
                    mimeType= fileformat[fileExtension]
                else :
                    mimeType="text/plain"
                edm = ExecuteDBModifier(self.pyaas)
                filedata,status,statuscode = edm.execute({"data":{"_shellId":aasIdentifier, "submodelIdentifier":submodelIdentifier,
                                               "idShortPath":idShortPath,"elemData":filename,"mimeType":mimeType},"instanceId" : str(uuid.uuid1()),
                                                                         "method":"PutFileByPath"})
                if status:
                    try:
                        filename = secure_filename(file.filename)
                        file.save(os.path.join(self.pyaas.downlaod_repository, *(filedata).split("/")))
                        return make_response("Submodel element updated successfully",204)
                    except Exception as E:
                        self.pyaas.serviceLogger.info("Error at PutFileByPath Rest" + str(E))
                        return make_response("Internal Server Error",500)
                else:
                    return make_response(filedata,statuscode)
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at PutFileByPath Rest" + str(E))
            return make_response("Internal Server Error",500)        

'''
Submodel Interface End
'''


'''
Concept Description Repository Start
'''
class ConceptDescriptions(Resource):
    def __init__(self,pyaas):
        self.pyaas = pyaas

    def get(self):
        try:
            args = request.args
            if len(args) > 0:
                try:
                    if (args.get('idShort')):
                        data, status,statuscode = self.pyaas.dba.GetAllConceptDescriptionsByIdShort(args.get('idShort'))            
                        return make_response(jsonify(data),statuscode)
                    elif (args.get('isCaseOf')):
                        data, status,statuscode = self.pyaas.dba.GetAllConceptDescriptionsByIsCaseOf(args.get('isCaseOf'))            
                        return make_response(jsonify(data),statuscode)
                    elif (args.get('dataSpecificationRef')):
                        data, status,statuscode = self.pyaas.dba.GetAllConceptDescriptionsByDataSpecificationReference(args.get('dataSpecificationRef'))            
                        return make_response(jsonify(data),statuscode)
                    else:
                        return ("Bad Request",500)
                except:
                    pass           
            else:
                data, status,statuscode = self.pyaas.dba.GetAllConceptDescriptions()            
                return make_response(jsonify(data),statuscode)
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at GetConceptDescriptions Rest" + str(E))
            return make_response("Internal Server Error",500)
          
    def post(self):
        try:
            data = request.json
            if "interactionElements" in data:
                pass
                #return self.pyaas.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyaas)           
                if(aasValid.validateConceptDescription(data)):
                    edm = ExecuteDBModifier(self.pyaas)
                    data1,status1,statuscode1 = edm.execute({"data":{"_cd":data}, "method": "PostConceptDescription", "instanceId" : str(uuid.uuid1())})
                    return make_response(data1,statuscode1)
                else :
                    return make_response("The syntax of the passed Concept Description is not valid or malformed request",200)
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at PostConceptDescription Rest" + str(E))
            return make_response("Internal Server Error",500)
        
class ConceptDescriptionById(Resource):
    def __init__(self,pyaas):
        self.pyaas = pyaas
    
    def get(self,cdIdentifier):
        try:
            cdIdentifier = (base64.decodebytes(cdIdentifier.encode())).decode()
            data,status,statuscode = self.pyaas.dba.GetConceptDescriptionById(cdIdentifier)  
            return make_response(data,statuscode)
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at GetConceptDescriptionById Rest" + str(E))
            return make_response("Unexpected Internal Server Error",500)
        
    def put(self,cdIdentifier):
        try:
            data = request.json
            cdIdentifier = (base64.decodebytes(cdIdentifier.encode())).decode()
            if "interactionElements" in data:
                pass
                #return self.pyaas.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyaas)           
                if(aasValid.validateConceptDescription(data)):
                    edm = ExecuteDBModifier(self.pyaas)
                    
                    data,status,statuscode = edm.execute({"data":{"_conceptDescriptionId":cdIdentifier, "_cd":data}, "method": "PutConceptDescriptionById", "instanceId" : str(uuid.uuid1())})
                    return make_response(data,statuscode)
                else :
                    return make_response("The syntax of the passed Concept Description is not valid or malformed request",400)
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at PutConceptDescriptionById Rest" + str(E))
            return make_response("Internal Server Error",500)

    def delete(self,cdIdentifier):
        try:
            cdIdentifier = (base64.decodebytes(cdIdentifier.encode())).decode()
            edm = ExecuteDBModifier(self.pyaas)
            data,status,statuscode = edm.execute({"data":cdIdentifier, "instanceId" : str(uuid.uuid1()), "method": "DeleteConceptDescriptionById"})
            return make_response(data,statuscode)
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at DeleteConceptDescriptionById Rest" + str(E))
            return make_response("Internal Server Error",500)
 
'''
Concept Description Repository End 
'''
       
'''       
Submodel Repository Interface Start
'''
class Submodels(Resource):
    def __init__(self,pyaas):
        self.pyaas = pyaas
    
    def get(self):
        try:
            args = request.args
            if len(args) > 0:
                try:
                    if (args.get('idShort')):
                        data, status,statuscode = self.pyaas.dba.GetAllSubmodelsByIdShort(args.get('idShort'))            
                        return make_response(jsonify(data),statuscode)
                    elif (args.get('semanticId')):
                        data, status,statuscode = self.pyaas.dba.GetAllSubmodelsBySemanticId(args.get('semanticId'))            
                        return make_response(jsonify(data),statuscode)
                    else:
                        return make_response("Internal Server Error",500)
                except:
                    pass           
            else:
                data, status,statuscode = self.pyaas.dba.GetAllSubmodels()            
                return make_response(jsonify(data),statuscode)
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at GetSubmodels Rest" + str(E))
            return make_response("Internal Server Error",500)
       
    def post(self):
        try:
            data = request.json
            if "interactionElements" in data:
                pass
                #return self.pyaas.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyaas)           
                if(aasValid.valitdateSubmodel(data)):
                    edm = ExecuteDBModifier(self.pyaas)
                    data,status,statuscode = edm.execute({"data":{"_submodel":data}, "method": "PostSubmodel", "instanceId" : str(uuid.uuid1())})
                    return make_response(data,statuscode)
                else :
                    return make_response("The syntax of the passed Submodel is not valid or malformed request",400)
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at PostSubmodel Rest" + str(E))
            return make_response("Internal Server Error",500)

class SubmodelById(Resource):
    def __init__(self,pyaas):
        self.pyaas = pyaas

    def get(self,submodelIdentifier):
        try:
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            data,status,statuscode = self.pyaas.dba.GetSubmodelById(submodelIdentifier)  
            return make_response(data,statuscode)
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at GetSubmodelById Rest" + str(E))
            return make_response("Internal Server Error",500)

    def put(self,submodelIdentifier):
        try:
            data = request.json
            submodelIdentifier = unquote(submodelIdentifier)
            if "interactionElements" in data:
                pass
                #return self.pyaas.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
                aasValid = AASMetaModelValidator(self.pyaas)           
                if(aasValid.valitdateSubmodel(data)):
                    edm = ExecuteDBModifier(self.pyaas)
                    
                    data,status,statuscode = edm.execute({"data":{"submodelIdentifier":submodelIdentifier, "_submodel":data}, "method": "PutSubmodelById", "instanceId" : str(uuid.uuid1())})
                    return make_response(data,statuscode)
                else :
                    return make_response("The syntax of the passed Submodel is not valid or malformed request",400)
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at PutSubmodelById Rest" + str(E))
            return make_response("Internal Server Error",500)

    def delete(self,submodelIdentifier):
        try:
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            edm = ExecuteDBModifier(self.pyaas)
            data,status,statuscode = edm.execute({"data":submodelIdentifier, "instanceId" : str(uuid.uuid1()), "method": "DeleteSubmodelById"})
            return make_response(data,statuscode)
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at DeleteSubmodelById Rest" + str(E))
            return make_response("Internal Server Error",500)

class Submodel_SRI(Resource):
    def __init__(self,pyaas):
        self.pyaas = pyaas
    
    def get(self,submodelIdentifier): 
        try:
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            data,status,statuscode = self.pyaas.dba.GetSubmodel_SRI(submodelIdentifier)  
            return make_response(data,statuscode)
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at GetSubmodel_SRI Rest" + str(E))
            return make_response("Internal Server Error",500)
        
    def put(self,submodelIdentifier): 
        try:
            data = request.json
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            if "interactionElements" in data:
                pass
                #return self.pyaas.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyaas)           
                if(aasValid.valitdateSubmodel(data)):
                    edm = ExecuteDBModifier(self.pyaas)
                    data,status,statuscode = edm.execute({"data":{"submodelIdentifier":submodelIdentifier,
                                                                "_submodel":data},"method":"PutSubmodel_SRI","instanceId" : str(uuid.uuid1())})
                    return make_response(data,statuscode)
                else :
                    return make_response("The syntax of the passed Submodel is not valid or malformed request",400)
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at PutSubmodel_SRI Rest" + str(E))
            return make_response("Internal Server Error",500)

class SubmodelElements_SRI(Resource):
    def __init__(self,pyaas):
        self.pyaas = pyaas
    
    def get(self,submodelIdentifier):
        try:
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            data,status,statuscode = self.pyaas.dba.GetAllSubmodelElements_SRI(submodelIdentifier)            
            return make_response(jsonify(data),statuscode)
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at GetAllSubmodelElements_SRI Rest" + str(E))
            return make_response("Internal Server Error",500)

    def post(self,submodelIdentifier):
        try:
            data = request.json
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            if "interactionElements" in data:
                pass
                #return self.pyaas.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyaas)           
                if(aasValid.validateSubmodelElement(data)):
                    edm = ExecuteDBModifier(self.pyaas)
                    data,status,statuscode = edm.execute({"data":{"elemData":data,
                                            "submodelIdentifier" : submodelIdentifier
                                                                  },"method":"PostSubmodelElement_SRI","instanceId" : str(uuid.uuid1())})
                    return make_response(data,statuscode)
                else :
                    return make_response("The syntax of the passed Submodel ELement is not valid or malformed request",400)                
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at PostSubmodelElement_SRI Rest" + str(E))
            return make_response("Internal Server Error",500)              

class SubmodelElementByPath_SRI(Resource):
    def __init__(self,pyaas):
        self.pyaas = pyaas
        
    def get(self,submodelIdentifier,idShortPath):
        try:
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            idShortPath = unquote(idShortPath)
            data,status,statuscode = self.pyaas.dba.GetSubmodelElementByPath_SRI(submodelIdentifier,idShortPath)          
            return make_response(data,statuscode)
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at GetSubmodelElementByPath_SRI Rest" + str(E))
            return make_response("Internal Server Error",500)

    def post(self,submodelIdentifier,idShortPath):
        try:
            data = request.json
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            idShortPath = unquote(idShortPath)
            if "interactionElements" in data:
                pass
                #return self.pyaas.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyaas)           
                if(aasValid.validateSubmodelElement(data)):
                    edm = ExecuteDBModifier(self.pyaas)
                    data,status,statuscode = edm.execute({"data":{"submodelIdentifier":submodelIdentifier,
                                                   "idShortPath":idShortPath,"elemData":data},"method":"PostSubmodelElementByPath_SRI","instanceId" : str(uuid.uuid1())}) 
                    return make_response(data,statuscode)
                else :
                    return make_response("The syntax of the passed Submodel ELement is not valid or malformed request",400)                
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at PostSubmodelElementByPath_SRI Rest" + str(E))
            return make_response("Internal Server Error",500)        

    def put(self,submodelIdentifier,idShortPath):
        try:
            data = request.json
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            idShortPath = unquote(idShortPath)
            if "interactionElements" in data:
                pass
                #return self.pyaas.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyaas)           
                if(aasValid.validateSubmodelElement(data)):
                    edm = ExecuteDBModifier(self.pyaas)
                    data,status,statuscode = edm.execute({"data":{"submodelIdentifier":submodelIdentifier,
                                               "idShortPath":idShortPath,"elemData":data},"method":"PutSubmodelElementByPath_SRI","instanceId" : str(uuid.uuid1())}) 
                    return make_response(data,statuscode)
                else :
                    return make_response("The syntax of the passed Submodel ELement is not valid or malformed request",400)                
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at PutSubmodelElementByPath_SRI Rest" + str(E))
            return make_response("Internal Server Error",500)  

    def delete(self,submodelIdentifier,idShortPath):
        try:
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            idShortPath = unquote(idShortPath)
            edm = ExecuteDBModifier(self.pyaas)
            data,status,statuscode = edm.execute({"data":{"submodelIdentifier":submodelIdentifier,
                                               "idShortPath":idShortPath},"method":"DeleteSubmodelElementByPath_SRI","instanceId" : str(uuid.uuid1())})            
            return make_response(data,statuscode)
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at DeleteSubmodelElementByPath_SRI Rest" + str(E))
            return make_response("Internal Server Error",500)   

class FileByPath_SRI(Resource):
    def __init__(self,pyaas):
        self.pyaas = pyaas

    def get(self,submodelIdentifier,idShortPath):
        try:
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            idShortPath = unquote(idShortPath)            
            data,status,statuscode = self.pyaas.dba.GetFileByPath_SRI(submodelIdentifier,idShortPath)            
            if status:
                fileExtension = (data.split(".")[-1]).lower()
                filename = (data.split("/"))[-1]
                if fileExtension in fileformat:
                    file_path = os.path.join(self.pyaas.downlaod_repository,*(data).split("/"))
                    sendfile = send_file(file_path,attachment_filename=filename, as_attachment=True,mimetype= fileformat[fileExtension])
                else:
                    file_path = os.path.join(self.pyaas.downlaod_repository,*(data).split("/"))
                    sendfile = send_file(file_path,attachment_filename=filename, as_attachment=True,mimetype="text/plain")
                return  sendfile
            else:
                return make_response(data,status)
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at GetFileByPath_SRI  REST API" + str(E))
            return make_response("Internal Server Error",500)
        
    def put(self,submodelIdentifier,idShortPath):
        try:
            if False:
                pass
                #return self.pyaas.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
                if 'file' not in request.files:
                    return make_response("Internal Server Error",500)
                file = request.files['file']
                if file.filename == '':
                    return make_response("Internal Server Error",500)
                
                filename = secure_filename(file.filename)
                fileExtension = (filename.split(".")[-1]).lower()
                mimeType = ""
                if fileExtension in fileformat:
                    mimeType= fileformat[fileExtension]
                else :
                    mimeType="text/plain"
                edm = ExecuteDBModifier(self.pyaas)
                filedata,status,statuscode = edm.execute({"data":{"submodelIdentifier":submodelIdentifier,
                                               "idShortPath":idShortPath,"elemData":filename,"mimeType":mimeType},"instanceId" : str(uuid.uuid1()),
                                                                         "method":"PutFileByPath_SRI"})
                if status:
                    try:
                        filename = secure_filename(file.filename)
                        file.save(os.path.join(self.pyaas.downlaod_repository, *(filedata).split("/")))
                        return make_response("Submodel element updated successfully",204)
                    except Exception as E:
                        self.pyaas.serviceLogger.info("Error at PutFileByPath Rest" + str(E))
                        return make_response("Internal Server Error",500)
                else:
                    return make_response(filedata,statuscode)
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at PutFileByPath_SRI Rest" + str(E))
            return make_response("Internal Server Error",500)        



'''       
Submodel Repository Interface End
'''

class AssetAdministrationShellsSubmodelRefs(Resource):
    def __init__(self,pyaas):
        self.pyaas = pyaas
    
    def get(self,aasIdentifier):
        try:
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            data,status,statuscode = self.pyaas.dba.getShellSubmodelRefs(aasIdentifier)            
            return make_response(data,statuscode)
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at getAssetAdministrationShells Rest" + str(E))
            return make_response("Unexpected Internal Server Error",500)
        
    def post(self,aasIdentifier):
        try:
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            data = request.json
            if "interactionElements" in data:
                pass
                #return self.pyaas.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyaas)           
                if(aasValid.validateAASShellSubmodelRef(data)):
                    edm = ExecuteDBModifier(self.pyaas)
                    data,status,statuscode = edm.execute({"data":{"_shellId":aasIdentifier, "_submodelRef":data
                                                                  },"method":"postShellSubmodelRef"})
                    return make_response(data,statuscode)
                else :
                    return make_response("The syntax of the passed Asset Administration Shell Submodel Reference is not valid or malformed request",200)
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at postAssetAdministrationShells Rest" + str(E))
            return make_response("Internal Server Error",500)

class AASSubmodelElementByIdShortPath(Resource):
    def __init__(self,pyaas):
        self.pyaas = pyaas
        
    def get(self,aasIdentifier,submodelIdentifier,idShortPath):
        try:
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            idShortPath = unquote(idShortPath)
            data,status,statuscode = self.pyaas.dba.GetSubmodelElementByPath(aasIdentifier,
                                                                             submodelIdentifier,
                                                                             idShortPath)            

        except Exception as E:
            self.pyaas.serviceLogger.info("Error at GetSubmodelElementByPath Rest" + str(E))
            return make_response("Unexpected Internal Server Error",500)

    def put(self,aasIdentifier,submodelIdentifier,idShortPath):
        try:
            data = request.json
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            idShortPath = unquote(idShortPath)
            if "interactionElements" in data:
                pass
                #return self.pyaas.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyaas)           
                if(aasValid.validateSubmodelELement(data)):
                    edm = ExecuteDBModifier(self.pyaas)
                    msg,status = edm.execute({"data":{"elemData":data,
                                            "_idShortpath" : submodelIdentifier+"."+idShortPath
                                                      },"method":"putSubmodelElem","instanceId" : str(uuid.uuid1())})
                    if status:
                        return make_response(msg,201)
                    else:
                        return make_response(msg,500)
                else :
                    return make_response("The syntax of the passed Submodel ELement is not valid or malformed request",400)                
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at putSubmodelElementByIdShortPath Rest" + str(E))
            return make_response("Internal Server Error",500)

    def post(self,aasIdentifier,submodelIdentifier,idShortPath):
        try:
            data = request.json
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            idShortPath = unquote(idShortPath)
            if "interactionElements" in data:
                pass
                #return self.pyaas.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyaas)           
                if(aasValid.validateSubmodelELement(data)):
                    edm = ExecuteDBModifier(self.pyaas)
                    msg,status = edm.execute({"data":{"elemData":data,
                                            "_idShortpath" : submodelIdentifier+"."+idShortPath
                                                      },"method":"postSubmodelElem","instanceId" : str(uuid.uuid1())})
                    if status:
                        return make_response(msg,201)
                    else:
                        return make_response(msg,500)
                else :
                    return make_response("The syntax of the passed Submodel ELement is not valid or malformed request",400)                
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at postSubmodelElementByIdShortPath Rest" + str(E))
            return make_response("Internal Server Error",500)        

    def delete(self,aasIdentifier,submodelIdentifier,idShortPath):
        try:
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            idShortPath = unquote(idShortPath)
            edm = ExecuteDBModifier(self.pyaas)
            msg,status = edm.execute({"data": submodelIdentifier + "." + idShortPath, "method": "deleteSubmodelElem", "instanceId" : str(uuid.uuid1())})
            if status:
                return make_response(msg,204)
            else:
                return make_response(msg,500)
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at deleteSubmodelElementByIdShortPath Rest" + str(E))
            return make_response("Unexpected Internal Server Error",500)    
            
class AASsubmodelRefsIndentifier(Resource):
    def __init__(self,pyaas):
        self.pyaas = pyaas

    def get(self,aasId,submodelId):
        try:
            aasId = unquote(aasId)
            submodelId = unquote(submodelId)
            data,status = self.pyaas.dba.getShellSubmodelRef(aasId,submodelId)            
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
                #return self.pyaas.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else:
                if(True):
                    if (True):
                        edm = ExecuteDBModifier(self.pyaas)
                        data,status = edm.execute({"data":{"_shellId": aasId, "_submodelRef":data}
                                                               ,"method":"putShellSubmodelRef","instanceId" : str(uuid.uuid1())})            
                        if status:
                            return make_response(data,204)
                    else:
                        return make_response("The namspace SubmodelId value and the IdShort value do not match",500)
                else:
                    return make_response("The syntax of the passed submodel data is not valid or malformed request",400)
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at putAASsubmodelRefsIndentifier Rest" + str(E))
            return make_response("Unexpected Internal Server Error",500)

    def delete(self,aasId,submodelId):
        try:
            aasId = unquote(aasId),
            submodelId = unquote(submodelId)
            edm = ExecuteDBModifier(self.pyaas)
            data,status = edm.execute({"data":{"_shellId":aasId, "_submodelrefId":submodelId},
                                                   "method":"deleteShellSubmodelRef","instanceId" : str(uuid.uuid1())})
            if status:
                return make_response(data,204)     
            else:
                return make_response(data,500)
        except Exception as E:
            self.pyaas.serviceLogger.info("Error at deleteAASsubmodelRefsIndentifier Rest" + str(E))
            return make_response("Unexpected Internal Server Error",500)

class RetrieveMessage(Resource):    
    def __init__(self, pyaas):
        self.pyaas = pyaas
        
    def post(self):
        jsonMessage = request.json
        try:
            if (jsonMessage["frame"]["sender"]["identification"]["id"] == self.pyaas.AASID):
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
        if ((jsonMessage["frame"]["conversationId"] not in self.pyaas.conversationInteractionList)):
            self.pyaas.serviceLogger.info("Test1 handleBoradCastMessage")
            self.pyaas.dba.createNewConversation(jsonMessage["frame"]["conversationId"])
            self.pyaas.conversationInteractionList.append(jsonMessage["frame"]["conversationId"])
            self.instanceId = str(uuid.uuid1())
            self.pyaas.dataManager.pushInboundMessage({"functionType":3,"instanceid":self.instanceId,
                                                           "conversationId":jsonMessage["frame"]["conversationId"],
                                                           "messageType":jsonMessage["frame"]["type"],
                                                           "messageId":jsonMessage["frame"]["messageId"],
                                                           "direction":"inbound",
                                                           "SenderAASID" : "Broadcast",
                                                           "message":jsonMessage})            
            self.msgHandler.putIbMessage(jsonMessage)       


class AASStaticSource(Resource):
    def __init__(self,pyaas):
        self.pyaas = pyaas
        
    def get(self,filename):      
        try:
            return send_from_directory(self.pyaas.downlaod_repository,filename)
        except Exception as E:
            print(str(E))        

class AASStaticConfigSource(Resource):
    def __init__(self,pyaas):
        self.pyaas = pyaas
        
    def get(self,filename):      
        try:
            filename = unquote(filename)
            _type = filename.split(".")[-1]
            _filename = filename.split("/")[-1]
            filenames = {'filename': _filename}
            rv = send_from_directory((self.pyaas.repository),filename,mimetype="image/"+_type)
            rv.headers.set('Content-Disposition',_filename)
            return rv        
        
        except Exception as E:
            print(str(E))  


class AASWebInterfaceHome(Resource):
    def __init__(self,pyaas):
        self.pyaas = pyaas
    
    def process(self,shelldata):
        edm = ExecuteDBModifier(self.pyaas)
        data,status1,statuscode = edm.execute({"data":shelldata, "method": "PostAssetAdministrationShell",
                                                                 "instanceId" : str(uuid.uuid1())})    
        return status1
    
    def save_aas_information(self,data):
        gen_aas_shell = Generate_AAS_Shell(self.pyaas,data)
        shelldata,status = gen_aas_shell.execute()
        if status:
            if self.process(shelldata):
                _uuid = self.pyaas.aasHashDict.__getHashEntry__(shelldata["id"])._id
                self.pyaas.configure_skills_by_id(_uuid,shelldata["id"])
                self.pyaas.start_skills_by_id(_uuid)
                return True
            else:
                return False 
        else:
            return False
        
    def retrieve_validate_aas(self,request):
        data = dict()
        updateData = request.form
        try:
            file = request.files['file']
            data["file"] = file.filename
        except Exception as e:
            print("Error retreiving the thumbnail @retrieve_aas_information "+ str(e))
            return False, "Error retreiving the thumbnail" 
        
        try:
            idSHort = updateData["AAS-IdShort"]
            if idSHort == "":
                return False, "The IdShort is empty"
            data["idShort"] = idSHort
        except Exception as e:
            print("Error retreiving the value for idShort @retrieve_validate_aas"+ str(e))
            return False, "Error retreiving the value for idShort"

        try:
            description = updateData["AAS-description"]
            if description == "":
                return False, "The description is empty"
            data["description"] = description
            
        except Exception as e:
            print("Error while retrieving the description  @retrieve_aas_information"+ str(e))
            return False, "Error while retrieving the description"

        try:
            displayName = updateData["AAS-displayName"]
            if displayName == "":
                return False, "The displayName is empty"
            data["displayName"] = displayName
            
        except Exception as e:
            print("Error while retrieving the displayName  @retrieve_aas_information"+ str(e))
            return False, "Error while retrieving the displayName"

        try:
            globalAssetId = updateData["AAS-globalAssetId"]
            if globalAssetId == "":
                return False, "The globalAssetId is empty"
            data["globalAssetId"] = globalAssetId
            
        except Exception as e:
            print("Error while retrieving the globalAssetId  @retrieve_aas_information"+ str(e))
            return False, "Error while retrieving the globalAssetId"


        return True, data
    
    def post(self):              
        try:
            status, data = self.retrieve_validate_aas(request)
            if not status:
                flash(data,"error")             
            else:    
                status1 = self.save_aas_information(data)
                if status1:
                    file = request.files['file']
                    filename = secure_filename(file.filename)
                    (file).save(os.path.join(self.pyaas.downlaod_repository, "aasx/files",filename))
                else:
                    flash("data","error")

        except Exception as e:
            self.pyaas.serviceLogger.info("Error at Post AASWebInterfaceHome Rest" + str(e))
            flash("Error in creating the ","error")
        
        return redirect("/shells/webui", code=302)
        
    def get_aas_data(self):
        try:
            data, status, code = self.pyaas.dba.GetAllAssetAdministrationShells()
            aasList = []
            if status :
                for _shell in data:
                    bString = base64.b64encode(bytes(_shell["id"],'utf-8'))
                    base64_string= bString.decode('utf-8')
                    aasList.append(
                        { 
                         "aasIdentifier": base64_string,
                         "shellId": _shell["id"],
                          "idShort": _shell["idShort"],
                          "thumbnail": urllib.parse.quote(((_shell["assetInformation"]["defaultThumbnail"]["path"]).split("file:/"))[1],safe= "")})  
        except Exception as e:
            self.pyaas.serviceLogger.info("Error at Get AASWebInterfaceHome Rest" + str(e))
        return aasList 
                   
    def get(self) :              
        try:
            return  Response(render_template('home.html',exDomain=self.pyaas.exDomain,
                                                         aasList = self.get_aas_data()))
        except Exception as E:
            return str(E)

class AASWebInterface(Resource):
    def __init__(self,pyaas):
        self.pyaas = pyaas

    def process(self,submodel_data,_reference,_conceptDescriptions,aasIdentifier):
        edm = ExecuteDBModifier(self.pyaas)
        
        data,status,statuscode = edm.execute({"data":{"_submodel":submodel_data}, "method": "PostSubmodel",
                                                                 "instanceId" : str(uuid.uuid1())})   
        data1,status1,statuscode = edm.execute({"data": {"_shellId":aasIdentifier, "_Reference":_reference}, "method": "PostSubmodelReference",
                                                                 "instanceId" : str(uuid.uuid1())})
         
        return True
    
    def save_submodel_information(self,shellId,submodel_name,submodel_IdShort) -> bool:
        try:
            template_data = copy.deepcopy(self.pyaas.aasConfigurer.submodel_template_dict[submodel_name])
            submodel_data = template_data["submodels"][0]
            submodel_Ref = template_data["assetAdministrationShells"][0]["submodels"][0]
            concept_Descriptions =[]
            if "conceptDescriptions" in template_data.keys():
                concept_Descriptions = template_data["conceptDescriptions"]
            
            uuidG = UUIDGenerator()
            _uuid = uuidG.getnewUUID()
            submodel_Id = "ww.ovgu.de/submodel/"+str(_uuid)
            
            submodel_data["id"] = submodel_Id
            submodel_data["idShort"] = submodel_IdShort
            submodel_Ref["keys"][0]["value"] = submodel_Id
        
            self.create_submodel(submodel_data)
            self.save_submodel_ref(shellId,submodel_Ref)
            self.save_concept_descriptions(concept_Descriptions)
            return True
        except Exception as e:
            return False
    
    def create_submodel(self,submodel_data) -> bool:
        try :
            edm = ExecuteDBModifier(self.pyaas)
            data,status,statuscode = edm.execute({"data":{"_submodel":submodel_data}, "method": "PostSubmodel",
                                                                 "instanceId" : str(uuid.uuid1())})
            return status
        except Exception as e:
            return False
        
        
    def save_submodel(self,submodel_data) -> bool:
        try :
            edm = ExecuteDBModifier(self.pyaas)
            data,status,statuscode = edm.execute({"data":{"_submodel":submodel_data,"submodelIdentifier" : submodel_data["id"]}, "method": "PutSubmodelById",
                                                                 "instanceId" : str(uuid.uuid1())})
            return status
        except Exception as e:
            return False
        
    def save_submodel_ref(self,aasIdentifier,_reference) -> bool:
        try:
            edm = ExecuteDBModifier(self.pyaas)
            data,status,statuscode = edm.execute({"data": {"_shellId":aasIdentifier, "_Reference":_reference}, "method": "PostSubmodelReference",
                                                             "instanceId" : str(uuid.uuid1())})
            return status        
        except Exception as e:
            return False
 
    def save_concept_descriptions(self,_conceptDescriptions) -> bool:
        try:
            edm = ExecuteDBModifier(self.pyaas)
            for _cd in _conceptDescriptions:
                data1,status1,statuscode1 = edm.execute({"data":{"_cd":_cd}, "method": "PostConceptDescription", "instanceId" : str(uuid.uuid1())})
            return False
        except Exception as E:
            return False
        
    def create_skill_entry_sc(self,skill_details) -> dict:
        operational_data = copy.deepcopy(self.pyaas.aasConfigurer.submodel_template_dict["OperationalData"])
        sc = operational_data["submodels"][0]["submodelElements"][0]
        sc["idShort"] = skill_details["SkillName"] 
        for index,sc_feature in enumerate(sc["value"]):
            sc["value"][index]["value"] = skill_details[sc_feature["idShort"]]
        return sc
    
    def create_operational_data_entry(self,aasIdentifier,semantic_id,skill_details) -> bool:
        try :
            data, status = self.pyaas.aasConfigurer.retrieve_submodel_semantic_id(aasIdentifier,semantic_id)
            if status:
                data["submodelElements"].append(self.create_skill_entry_sc(skill_details))
                self.save_submodel(data)
            else:
                uuidG = UUIDGenerator()
                _uuid = uuidG.getnewUUID()
                submodel_Id = "www.ovgu.de/submodel/OperationaData/"+str(_uuid)
                operational_data_aas = copy.deepcopy(self.pyaas.aasConfigurer.submodel_template_dict["OperationalData"])
                operational_data_submodel = operational_data_aas["submodels"][0]
                operational_data_submodel["submodelElements"].clear()
                operational_data_submodel["submodelElements"].append(self.create_skill_entry_sc(skill_details))
                operational_data_submodel["id"] = submodel_Id
                submodel_Ref = operational_data_aas["assetAdministrationShells"][0]["submodels"][0]
                submodel_Ref["keys"][0]["value"] = submodel_Id
                
                self.create_submodel(operational_data_submodel)
                self.save_submodel_ref(aasIdentifier, submodel_Ref)
            return True
        except Exception as E:
            return False
    
    def check_for_skill_existence(self,uuid,skill_name) -> bool:
        try:
            shellObject = self.pyaas.aasShellHashDict.__getHashEntry__(uuid)
            if skill_name in shellObject.skills.keys():
                return False
            else:
                return True
        except Exception as e:
            return True
    
    
    def lookup_collection_cd(self,collection):
        try:
            cds = []
            for element in collection["value"]:
                if "semanticId" in element.keys():
                    _cds,present = self.lookup_cd(element["semanticId"])
                    if present:
                        cds.extend(_cds)
                if element["modelType"] == "SubmodelElementCollection":
                    _cds1,present = (self.lookup_collection_cd(element))
                    if present:
                        cds.extend(_cds1)
            return cds,True
        except Exception as e:
            return "Error", False          
    
    def lookup_cd(self,semanticId):
        try:
            cds = []
            for key in semanticId["keys"]:
                if key["type"] == "ConceptDescription":
                    cds.append(key["value"])
            return cds,True
        except Exception as e:
            return "Error", False
    
    
    def post(self,aasIdentifier):
        try:
            operation_type = request.form["operation_type"]
            aasIdentifier1 = (base64.decodebytes(aasIdentifier.encode())).decode()
            _uuid = self.pyaas.aasHashDict.__getHashEntry__(aasIdentifier1)._id
            if operation_type == "delete_aas":
                try:
                    edm = ExecuteDBModifier(self.pyaas)
                    data,status,statuscode = edm.execute({"data":aasIdentifier1, "method": "DeleteAssetAdministrationShellByIdandSubmodels",
                                                         "instanceId" : str(uuid.uuid1())})
                except Exception as E:
                    pass
            if operation_type == "available_skills":
                if "skill_name" in list(request.form.keys()):
                    skill_name = request.form["skill_name"]
                    if self.check_for_skill_existence(_uuid,skill_name):
                        skill_details = self.pyaas.available_skills[skill_name]
                        self.create_operational_data_entry(aasIdentifier1,"www.ovgu.de/submodel/operationaldata",skill_details)
                        self.pyaas.configure_skill_by_id(_uuid,skill_name)
                        self.pyaas.start_skill_by_name(_uuid,skill_name)
                    else:
                        flash("No Skills to add","error")
                else:
                    flash("No Skills to add","error")
                    
            elif operation_type == "std_submodel":
                submodel_name = request.form["submodel-name"]
                submodel_IdShort = request.form["submodel-IdShort"]
                data,status1 = self.pyaas.dba.get_aas_information(aasIdentifier1)
                self.save_submodel_information(data["_aasShell"].aasELement["id"],submodel_name,submodel_IdShort)
            
            elif operation_type == "new_submodel":
                _reference = json.loads(request.form["_reference"])
                submodel_data =  json.loads(request.form["submodel-data"])
                submodel_Id = "ww.ovgu.de/submodel/"+str(submodel_data["idShort"])
                submodel_data["id"] = submodel_Id
                _reference["keys"][0]["value"] = submodel_Id
                self.create_submodel(submodel_data)
                self.save_submodel_ref(aasIdentifier1, _reference)
            
            elif operation_type == "download_json":
                conceptDescriptions = []
                packageData =  {
                                    "assetAdministrationShells" :[],
                                    "submodels" : [],
                                    "conceptDescriptions" : []
                                }                
                edbR = ExecuteDBRetriever(self.pyaas)
                data,status,statuscode = edbR.execute({"data":aasIdentifier1,"method":"GetAssetAdministrationShellById"})                
                if status:
                    packageData["assetAdministrationShells"].append(data)
                    data,status,statuscode = edbR.execute({"data":aasIdentifier1,"method":"GetSubmodels_shell"})
                    if status:
                        for _submodel in data:
                            if "semanticId" in _submodel.keys():
                                cd,present = self.lookup_cd(_submodel["semanticId"])
                                if present:
                                    conceptDescriptions.extend(cd)
                                cds = []
                                for element in _submodel["submodelElements"]:
                                    if "semanticId" in element.keys():
                                        cds,present = self.lookup_cd(element["semanticId"])
                                    if present:
                                        conceptDescriptions.extend(cds)
                                    if element["modelType"] == "SubmodelElementCollection":
                                        cds,present = self.lookup_collection_cd(element)
                                        conceptDescriptions.extend(cds)
                            packageData["submodels"].append(_submodel)
                            for _cdId in conceptDescriptions:
                                data,status,statuscode = edbR.execute({"data":_cdId,"method":"GetConceptDescriptionById"})
                                if status:
                                    packageData["conceptDescriptions"].append(data)
                    else:
                        flash("Error Fetching the data","error")
                        return redirect('/shells/'+aasIdentifier+"/webui", code=302)
                else:
                    flash("Error Fetching the data","error")
                    return redirect('/shells/'+aasIdentifier+"/webui", code=302)
                return  Response(json.dumps(packageData), 
                                mimetype='application/json',
                                headers={'Content-Disposition':'attachment;filename=package.json'})
        except Exception as e:
            print(str(e))
        return redirect('/shells/'+aasIdentifier+"/webui", code=302) 
                                  
    
    def get(self,aasIdentifier):
        try:
            aasIdentifier1 = (base64.decodebytes(aasIdentifier.encode())).decode()
            data,status = self.pyaas.dba.get_aas_information(aasIdentifier1)
            if status:
                available_skills = set(self.pyaas.available_skills.keys()) - set(data["skillList"])
                rv=   Response(render_template('index.html',thumbNail= urllib.parse.quote(data["thumbnail"],safe= ""),
                                                        aasIdentifier=aasIdentifier, exDomain=self.pyaas.exDomain , 
                                                        skillList= data["skillList"],
                                                        aasIdShort = data["idShort"],
                                                        submodelList = data["submodelList"],
                                                        std_submodels = list(self.pyaas.aasConfigurer.submodel_template_dict.keys()),
                                                        available_skills = list(available_skills)))
                return rv
            else:
                return redirect("/shells/webui", code=302)
        except Exception as E:
            return redirect("/shells/webui", code=302)


class AASWebInterfaceSubmodels(Resource):
    def __init__(self,pyaas):
        self.pyaas = pyaas

    def get(self,aasIdentifier,submodelIdentifier):       
        try:
            aasIdentifier1 = (base64.decodebytes(aasIdentifier.encode())).decode()
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            data,statu1 = self.pyaas.dba.get_aas_information(aasIdentifier1)
            submodelData,status,code = self.pyaas.dba.GetSubmodel(aasIdentifier1,submodelIdentifier)
            return  Response(render_template('submodel.html',thumbNail= urllib.parse.quote(data["thumbnail"],safe= ""),
                                                        aasIdentifier=aasIdentifier, exDomain=self.pyaas.exDomain , 
                                                        skillList= data["skillList"],
                                                        aasIdShort = data["idShort"],
                                                        submodelList = data["submodelList"],
                                                        submodelD = submodelData,
                                                        submodelId = submodelData["id"],
                                                        submodelName =submodelData["idShort"] ))        
        except Exception as e:
            print(str(e))
            return redirect('/shells/'+aasIdentifier+"/webui", code=302)

class AASWebInterfaceProductionManagement(Resource):
    def __init__(self,pyaas):
        self.pyaas = pyaas

    def get(self,aasIdentifier):   
        try:
            aasIdentifier1 = (base64.decodebytes(aasIdentifier.encode())).decode()
            data,status1 = self.pyaas.dba.get_aas_information(aasIdentifier1)
            available_skills = set(self.pyaas.available_skills.keys()) - set(data["skillList"])  -set(["ProductionManager","Register"])
            productions_skills = set(data["skillList"]) -set(["ProductionManager","Register"])
            rv=   Response(render_template('productionmanager.html',thumbNail= urllib.parse.quote(data["thumbnail"],safe= ""),
                                                        aasIdentifier=aasIdentifier, exDomain=self.pyaas.exDomain , 
                                                        skillList= data["skillList"],
                                                        aasIdShort = data["idShort"],
                                                        submodelList = data["submodelList"],
                                                        available_skills = list(available_skills),
                                                        conversationIdList=data["conversationIdList"],
                                                        productionStepList=data["productionStepList"],
                                                        productions_skills = productions_skills))
            return rv  
            
        except Exception as e:
            return str(e)

    def post(self,aasIdentifier):
        updateInfo = request.form
        tag =  updateInfo["operationType"]   
        aasIdentifier1 = (base64.decodebytes(aasIdentifier.encode())).decode()
        if (tag =="home"):
            return redirect('/shells/'+aasIdentifier+"/productionmanager/webui", code=302)
        
        elif (tag == "create"):
            try:
                skill_name = request.form.get("skill_name")     
                submodel_ids = request.form.getlist("submodel_id_idshort")
                idShortPath = ""#request.form.get("idShortPath") 
                if skill_name != None:
                    if submodel_ids != None and len(submodel_ids) > 0:
                        submodel_id_idSHort_list = []
                        for _id_idSHort in submodel_ids:
                            submodel_id_idshort_encoded = _id_idSHort.split(".")
                            submodel_id = ((base64.decodebytes((submodel_id_idshort_encoded[0]).encode())).decode())
                            idShort = submodel_id_idshort_encoded[1]
                            submodel_id_idSHort_list.append([submodel_id,idShort,idShortPath])
                        _uuid = self.pyaas.aasHashDict.__getHashEntry__(aasIdentifier1)._id
                        shellObject = self.pyaas.aasShellHashDict.__getHashEntry__(_uuid)
                        data, status = shellObject.add_produtionstep(skill_name,submodel_id_idSHort_list)
                        if status:
                            flash(data,"success")
                        else:
                            flash(data,"error")
                    else:
                        flash("Please add a submodel","error")
                else:
                    flash("Please add a skill","error")
            except Exception as e:
                flash("Error in adding the production step" + str(e),"error")
            return redirect('/shells/'+aasIdentifier+"/productionmanager/webui", code=302)
        
        elif (tag == "delete_all"):
            try:
                _uuid = self.pyaas.aasHashDict.__getHashEntry__(aasIdentifier1)._id
                shellObject = self.pyaas.aasShellHashDict.__getHashEntry__(_uuid)
                status = shellObject.delete_all_production()
                if status:
                    flash("All production steps are deleted","success")
                else:
                    flash("Error deleting the production steps","error")
            except Exception as e:
                flash("Error in deleting the production step" + str(e),"error")
            return redirect('/shells/'+aasIdentifier+"/productionmanager/webui", code=302)

        elif (tag == "delete"):
            try:
                skill_name = request.form.get("skill_name")
                submodel_id = request.form.get("submodel_id")
                sequence = request.form.get("sequence")
                _uuid = self.pyaas.aasHashDict.__getHashEntry__(aasIdentifier1)._id
                shellObject = self.pyaas.aasShellHashDict.__getHashEntry__(_uuid)
                status = shellObject.delete_production_step(skill_name,submodel_id,sequence)
                if status:
                    flash("All production steps are deleted","success")
                else:
                    flash("Error deleting the production steps","error")
            except Exception as e:
                flash("Error in deleting the production step" + str(e),"error")
            return redirect('/shells/'+aasIdentifier+"/productionmanager/webui", code=302)        
        
        elif (tag == "start"):
            try:
                pso = ProductionStepOrder(self.pyaas,aasIdentifier1)
                conversationID,status = pso.createProductionStepOrder(aasIdentifier1)
                if status:
                    flash("New Order booked with Order ID " + conversationID + " is booked","info")
                else:
                    flash(conversationID,"error")
            except  Exception as e:
                flash("Error creating the conversation Id." + str(e),"error")
            return redirect('/shells/'+aasIdentifier+"/productionmanager/webui", code=302)


class AASWebInterfaceSKillLog(Resource):
    
    def __init__(self,pyaas):
        self.pyaas = pyaas

    def get(self,aasIdentifier,skillName):
        try:
            aasIdentifier1 = (base64.decodebytes(aasIdentifier.encode())).decode()
            data,status = self.pyaas.dba.get_aas_information(aasIdentifier1)        
            return Response(render_template('skill.html',thumbNail= urllib.parse.quote(data["thumbnail"],safe= ""),
                                                            aasIdentifier=aasIdentifier, exDomain=self.pyaas.exDomain , 
                                                            skillList= data["skillList"],
                                                            aasIdShort = data["idShort"],
                                                            submodelList = data["submodelList"],                                         
                                                            skillName = skillName))
        except Exception as e:
            return redirect('/shells/'+aasIdentifier+"/webui", code=302)
        
    def post(self,aasIdentifier,skillName):
        try:
            aasIdentifier1 = (base64.decodebytes(aasIdentifier.encode())).decode()
            uuid = self.pyaas.aasHashDict.__getHashEntry__(aasIdentifier1)._id
            _aasShell = self.pyaas.aasShellHashDict.__getHashEntry__(uuid)
            return _aasShell.get_skill_log(skillName)
        except Exception as e:
            return redirect('/shells/'+aasIdentifier+"/webui", code=302)

class AASWebInterfaceCFP(Resource):
    def __init__(self,pyaas):
        self.pyaas = pyaas

    def get(self,conversationId):         
        try:
            return {"cfpList" :self.pyaas.dba.getConversationCFP(conversationId)} 
        except Exception as E:
            return {"cfpList" : []}


class AASWebInterfaceSearch(Resource):
    def __init__(self,pyaas):
        self.pyaas = pyaas

    def get(self,aasIdentifier):         
        try:
            args = request.args
            query =  args["searchQuery"]
            queryList = str(unquote(query)).split("**")
            return self.pyaas.dba.getMessagebyId(queryList[0],queryList[1])
        except Exception as E:
            return str(queryList) + str(E)
            
    def post(self,aasIdentifier):
        try:
            updateInfo = request.form
            query =  updateInfo["searchQuery"]
            aasIdentifier1 = (base64.decodebytes(aasIdentifier.encode())).decode()
            conversation,status = self.pyaas.dba.getConversationsById(query,aasIdentifier1)
            data,status = self.pyaas.dba.get_aas_information(aasIdentifier1)
            if status:
                available_skills = set(self.pyaas.available_skills.keys()) - set(data["skillList"])
                rv=   Response(render_template('search.html',thumbNail= urllib.parse.quote(data["thumbnail"],safe= ""),
                                                        aasIdentifier=aasIdentifier, exDomain=self.pyaas.exDomain , 
                                                        skillList= data["skillList"],
                                                        aasIdShort = data["idShort"],
                                                        submodelList = data["submodelList"],
                                                        std_submodels = list(self.pyaas.aasConfigurer.submodel_template_dict.keys()),
                                                        available_skills = list(available_skills),
                                                        conversationId = query,
                                                        resultList = {query:conversation}))
                return rv
            else:
                count = self.pyaas.dba.getMessageCount()
                flash("The conversation Id is not found, the last count is " + str(count["message"][0]),"error")
                return redirect('/shells/'+aasIdentifier+"/webui", code=302)
                
        except Exception as E:
            flash("Error","error")
            self.pyaas.serviceLogger.info("Error at postAASWebInterfaceSearch Rest" + str(E))
            return redirect('/shells/'+aasIdentifier+"/webui", code=302)

class AASWebInterfaceRegister(Resource):
    def __init__(self,pyaas):
        self.pyaas = pyaas

    def post(self,aasIdentifier):
        try:
            aasIdentifier1 = (base64.decodebytes(aasIdentifier.encode())).decode() 
            pso = ProductionStepOrder(self.pyaas)
            conversationID = pso.createRegistrationStep(aasIdentifier1)
            flash("New Resgitration  Order with Order ID " + conversationID + " is booked","info")
            return redirect("/shells/"+str(aasIdentifier)+"/registration/webui")   
        except  Exception as E:
            print(str(E))
            flash("Registration Failed"+str(E),"error")
            return redirect("/shells/"+str(aasIdentifier)+"/registration/webui") 
    

    def get(self,aasIdentifier):
            aasIdentifier1 = (base64.decodebytes(aasIdentifier.encode())).decode()
            data,status1 = self.pyaas.dba.get_aas_information(aasIdentifier1)
            available_skills = set(self.pyaas.available_skills.keys()) - set(data["skillList"])
            productions_skills = set(data["skillList"]) - set(["ProductionManager","Register"])
            rv=   Response(render_template('registration.html',
                                                        aasIdentifier=aasIdentifier, exDomain=self.pyaas.exDomain , 
                                                        skillList= data["skillList"],
                                                        aasIdShort = data["idShort"],
                                                        submodelList = data["submodelList"],
                                                        available_skills = list(available_skills),
                                                        conversationIdList=data["conversationIdList"][-5:],
                                                        productionStepList=data["productionStepList"],
                                                        productions_skills = productions_skills))
                    
            return  rv
        
class AASWebInterfaceSubmodelElemValue(Resource):
    def __init__(self,pyaas):
        self.pyaas = pyaas

    def getSubmodelIdentificationId(self,aasIdentifier,submodelIdentifier):
        aaData = self.pyaas.aasContentData[aasIdentifier]
        for submodel in aaData["submodels"]:
            if (submodel["idShort"] == submodelIdentifier):
                return submodel["id"]
        
    
    def getRelevantElemData(self,aasIdentifier,updateValue,idShortPath,submodelName,submodelElemAdditionalInfo,submodelELemType,submodelidentificationId):
        try:
            edbR = ExecuteDBRetriever(self.pyaas)
            msg,status = edbR.execute({"data":idShortPath,"method":"getSubmodelElement",
                                       "instanceId" : str(uuid.uuid1())})            
            
            if status:
                elemType = msg["modelType"]
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
            edm = ExecuteDBModifier(self.pyaas)
            elemData,status = self.getRelevantElemData(aasIdentifier,updateValue,idShortPath,submodelName,submodelElemAdditionalInfo,
                                                submodelELemType,submodelidentificationId)
            if status :
                msg1,status1,statuscode = edm.execute({"data":{"elemData":elemData,
                                                "_idShortpath" : idShortPath
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
    def __init__(self,pyaas):
        self.pyaas = pyaas
    
    def get(self,aasId,filename):
        try:
            file_path = os.path.join(self.pyaas.downlaod_repository,filename)
            sendfile = send_file(file_path, as_attachment=True,mimetype= "application/pdf")
            return  sendfile
        except Exception as E:
            print(str(E))

class AASDocumentationDownload(Resource):
    def __init__(self,pyaas):
        self.pyaas = pyaas
    
    def get(self,filename):
        try:
            file_path = os.path.join(self.pyaas.downlaod_repository,filename)
            sendfile = send_file(file_path,attachment_filename=filename, as_attachment=True,mimetype= "application/pdf")
            return  sendfile
        except Exception as E:
            print(str(E))

class AASAssetInterfaceDescription(Resource):        
    def __init__(self,pyaas):
        self.pyaas = pyaas
    
    def check_referred_property_exists(self,submodelId,idShortPath):
        try:
            return self.pyaas.aasHashDict.__isKeyPresent__(submodelId+"."+idShortPath)
        except Exception as E:
            print(str(E))
            return False
    
    def check_aid_exists(self,aasIdentifier:str) -> bool:
        try:
            data, status = self.pyaas.aasConfigurer.retrieve_submodel_semantic_id(aasIdentifier,"https://www.w3.org/2019/wot/td#Thing")
            return status
        except Exception as E:
            print(str(E))
            return False

    def save_submodel(self,submodel_data) -> bool:
        try :
            edm = ExecuteDBModifier(self.pyaas)
            data,status,statuscode = edm.execute({"data":{"_submodel":submodel_data}, "method": "PostSubmodel",
                                                                 "instanceId" : str(uuid.uuid1())})
            
            print("status "+status + " save_submodel")
            return status
        except Exception as e:
            return False
        
    def save_submodel_ref(self,aasIdentifier,_reference) -> bool:
        try:
            edm = ExecuteDBModifier(self.pyaas)
            data,status,statuscode = edm.execute({"data": {"_shellId":aasIdentifier, "_Reference":_reference}, "method": "PostSubmodelReference",
                                                             "instanceId" : str(uuid.uuid1())})
            return status        
        except Exception as e:
            return False

    
    def add_aid_propertys(self,aasIdentifier:str,aid_data:list):
        aid_properties_aas = []
        for aid_property in aid_data:
            aid_property["aasIdentifier"] = aasIdentifier
            aidP = AIDProperty()
            aidP.from_json(aid_property)
            elem_uuid = self.pyaas.aasHashDict.__getHashEntry__(aid_property["submodelId"]
                                                            +"."+aid_property["idShortPath"])._id
                    
            aidP.elemObject = self.pyaas.submodelHashDict.__getHashEntry__(elem_uuid)
            self.pyaas.scheduler.update_scheduler(aidP)
            aid_properties_aas.append(aidP)
            
        if not self.check_aid_exists(aasIdentifier):
            aid_submodel = copy.deepcopy(self.pyaas.aasConfigurer.submodel_template_dict["asset_interface_description"]["ThingDescription"])
            aid_submodel_ref = copy.deepcopy(self.pyaas.aasConfigurer.submodel_template_dict["asset_interface_description"]["SubmodelReference"])

            for aidp in aid_properties_aas:
                aid_property_aas_json = copy.deepcopy(self.pyaas.aasConfigurer.submodel_template_dict["asset_interface_description"]["Property"])
                aid_submodel["submodelElements"][3]["value"].append(aidp.to_aas_josn(aid_property_aas_json))
        
            uuidG = UUIDGenerator()
            _uuid = uuidG.getnewUUID()
            submodel_Id = "ww.ovgu.de/submodel/"+str(_uuid)
            
            aid_submodel["id"] = submodel_Id
            aid_submodel_ref["keys"][0]["value"] = submodel_Id
            
            self.save_submodel(aid_submodel)
            self.save_submodel_ref(aasIdentifier, aid_submodel_ref)
        else:
            aid_data_submodel, status = self.pyaas.aasConfigurer.retrieve_submodel_semantic_id(aasIdentifier,"https://www.w3.org/2019/wot/td#Thing")
            i = 0 
            for aid in aid_data_submodel["submodelElements"]:
                if (aid["idShort"] == "properties"):
                    break
                i = i + 1
            for aidp in aid_properties_aas:
                aid_property_aas_json = copy.deepcopy(self.pyaas.aasConfigurer.submodel_template_dict["asset_interface_description"]["Property"])
                aid_data_submodel["submodelElements"][i]["value"].append(aidp.to_aas_josn(aid_property_aas_json))
            
            self.save_submodel(aid_data_submodel)
            
            
            aas_shell_uuid = self.pyaas.aasHashDict.__getHashEntry__(aasIdentifier)._id
                    
            aasHashObject = self.pyaas.aasShellHashDict.__getHashEntry__(aas_shell_uuid)

            for aidp in aid_properties_aas:
                elem_uuid = self.pyaas.aasHashDict.__getHashEntry__(aidp.submodelIdentifier
                                                            +"."+aidp.idshort_path)._id
                    
                aidp.elemObject = self.pyaas.submodelHashDict.__getHashEntry__(elem_uuid)
                if aasHashObject.asset_interface_description != None:
                    aasHashObject.asset_interface_description.add_property(aidp,aidp.property_name)
                else:
                    aasHashObject.asset_interface_description = AssetInterfaceDescription()
                    aasHashObject.asset_interface_description.add_property(aidp,aidp.property_name)
                    
    def get(self,aasIdentifier): 
        try:
            aasIdentifier1 = (base64.decodebytes(aasIdentifier.encode())).decode()
            data,status = self.pyaas.dba.get_aas_information(aasIdentifier1)
            if status:
                available_skills = set(self.pyaas.available_skills.keys()) - set(data["skillList"])
                rv=   Response(render_template('aid.html',thumbNail= urllib.parse.quote(data["thumbnail"],safe= ""),
                                                        aasIdentifier=aasIdentifier, exDomain=self.pyaas.exDomain , 
                                                        skillList= data["skillList"],
                                                        aasIdShort = data["idShort"],
                                                        submodelList = data["submodelList"],
                                                        std_submodels = list(self.pyaas.aasConfigurer.submodel_template_dict.keys()),
                                                        available_skills = list(available_skills),
                                                        asssetInterfaceList = data["asssetInterfaceList"]))
                return rv
            else:
                return redirect("/shells/"+aasIdentifier+"/webui", code=302)
        except Exception as E:
            return redirect("/shells/"+aasIdentifier+"/webui", code=302)
        
    def post(self,aasIdentifier):
        updateInfo = request.form
        tag =  updateInfo["operationType"]
        aasIdentifier1 = (base64.decodebytes(aasIdentifier.encode())).decode()
        if (tag =="retreive-aid-property-data"):        
            returnData = {}
            try:
                property_Name =  updateInfo["propertyName"]
                aas_shell_uuid = self.pyaas.aasHashDict.__getHashEntry__(aasIdentifier1)._id
                aasHashObject = self.pyaas.aasShellHashDict.__getHashEntry__(aas_shell_uuid)
                elemObject = aasHashObject.asset_interface_description.get_property(property_Name).elemObject
                aasHashObject.asset_interface_description.get_property('Temperature').elemObject.history[0].timestamp
                returnData[property_Name] = {'label': [(str(dt.timestamp)).split(" ")[1] for dt in elemObject.history][-19:], 'value': [dt.aasElementValue for dt in elemObject.history][-19:]}
                return returnData
            except Exception as E:
                print(str(E))
                return redirect("/shells/"+aasIdentifier+"/webui", code=302) 
        
        elif (tag == "add-aid-properties"):
            try:
                aid_csv_file = request.files["file"]
                aid_header_line = (aid_csv_file.stream.readline()).decode().strip().split(',')
                aid_data = []
                for aid_line_stream in aid_csv_file.stream.readlines():
                    aid_line = aid_line_stream.decode().strip().split(',')
                    aid_property = dict()
                    i = 0
                    for _header_elem in aid_header_line:
                        aid_property[_header_elem] = aid_line[i]
                        i = i + 1
                    if not self.check_referred_property_exists(aid_property["submodelId"],
                                                           aid_property["idShortPath"]):
                        flash("The referred property does not exist","error")
                        return redirect("/shells/"+aasIdentifier+"/aid/webui", code=302)
                    aid_data.append(aid_property)
                self.add_aid_propertys(aasIdentifier1,aid_data)
                return redirect("/shells/"+aasIdentifier+"/aid/webui", code=302)
            except Exception as E:
                print(str(E))
                flash(str(E),"error")
                return redirect("/shells/"+aasIdentifier+"/aid/webui", code=302)