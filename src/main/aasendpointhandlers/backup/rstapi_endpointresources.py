'''
Copyright (c) 2021-2022 OVGU LIA
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
'''
import base64
from flask_restful import Resource,request
from flask import render_template,Response,redirect,flash,make_response,send_file,send_from_directory,jsonify
from urllib.parse import unquote
import io
import json
import os
import uuid
import copy
from werkzeug.utils import secure_filename
try:
    from utils.utils import ExecuteDBModifier,ProductionStepOrder,ExecuteDBRetriever,AASMetaModelValidator,StandardSubmodelData,Generate_AAS_Shell
except ImportError:
    from src.main.utils.utils import ExecuteDBModifier,ProductionStepOrder,ExecuteDBRetriever,AASMetaModelValidator,StandardSubmodelData,Generate_AAS_Shell
from jwkest.jws import JWSig, SIGNER_ALGS, JWS
from jwkest.jwk import rsa_load, RSAKey,pem_cert2rsa,der_cert2rsa,der2rsa
from jwkest.jwt import b64encode_item

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
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
        
    def get(self):
        try:
            reqData = {}
            edbR = ExecuteDBRetriever(self.pyAAS)
            if (request.data.decode("utf-8") != ""):
                try:
                    data = json.loads(reqData.decode("utf-8"))
                    if ("assetids" in reqData.keys()):
                        data, status,statuscode = edbR.execute({"data":None,"method":"GetAllAssetAdministrationShellsByAssetId"})            
                        return make_response(data,statuscode)
                    elif ("idShorts" in reqData.keys()):
                        data, status,statuscode = edbR.execute({"data":None,"method":"GetAllAssetAdministrationShellsByIdShort"})            
                        return make_response(data,statuscode)
                except:
                    pass           
            else:
                data, status,statuscode = edbR.execute({"data":None,"method":"GetAllAssetAdministrationShells"})            
                return make_response(jsonify(data),statuscode)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at getAssetAdministrationShells Rest" + str(E))
            return make_response("Internal Server Error",500)
        
    def post(self):
        try:
            data = request.json
            if "interactionElements" in data:
                pass
                #return self.pyaas.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyAAS)           
                if(aasValid.validateAASShell(data)):
                    edm = ExecuteDBModifier(self.pyAAS)
                    data,status,statuscode = edm.execute({"data":data, "method": "PostAssetAdministrationShell",
                                                                 "instanceId" : str(uuid.uuid1())})
                    return make_response(data,statuscode)
                else :
                    return make_response("The syntax of the passed Asset Administration Shell is not valid or malformed request",400)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at postAssetAdministrationShells Rest" + str(E))
            return make_response("Internal Server Error",500)

class AssetAdministrationShellById(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def get(self,aasIdentifier):
        try:
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            edbR = ExecuteDBRetriever(self.pyAAS)
            data,status,statuscode = edbR.execute({"data":aasIdentifier,"method":"GetAssetAdministrationShellById"})            
            return make_response(jsonify(data),statuscode)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at getAssetAdministrationShellById  REST API" + str(E))
            return make_response("Internal Server Error",500)
        
    def put(self,aasIdentifier):
        try:
            data = request.json
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            if "interactionElements" in data:
                pass
                #return self.pyaas.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyAAS)           
                if(aasValid.validateAASShell(data)):
                    if (aasIdentifier == data["id"] or aasIdentifier == ["idShort"]):
                        edm = ExecuteDBModifier(self.pyAAS)
                        data,status,statuscode = edm.execute({"data": {"_shellId":aasIdentifier, "_aasShell":data}, "method": "PutAssetAdministrationShellById",
                                                                     "instanceId" : str(uuid.uuid1())})
                        return make_response(data,statuscode)
                    else:
                        return make_response("The aas-identifier in the uri and in AAS Shell do not match",400)
                else :
                    return make_response("The syntax of the passed Asset Administration Shell is not valid or malformed request",400)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at PutAssetAdministrationShellById Rest" + str(E))
            return make_response("Internal Server Error",500)

    def delete(self,aasIdentifier):
        try:
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            edm = ExecuteDBModifier(self.pyAAS)
            data,status,statuscode = edm.execute({"data":aasIdentifier, "method": "DeleteAssetAdministrationShellById",
                                                         "instanceId" : str(uuid.uuid1())})
            return make_response(data,statuscode)          
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at DeleteAssetAdministrationShellById REST API" + str(E))
            return make_response("Internal Server Error",500)

'''
Shell Repository Interface End
'''

##################################################
'''
Asset Administration Shell Interface start

'''
class AssetAdministrationShell(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def get(self,aasIdentifier):
        try:
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            edbR = ExecuteDBRetriever(self.pyAAS)
            data,status,statuscode = edbR.execute({"data":aasIdentifier,"method":"GetAssetAdministrationShell"})            
            return make_response(jsonify(data),statuscode)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at GetAssetAdministrationShell  REST API" + str(E))
            return make_response("Internal Server Error",500)
        
    def put(self,aasIdentifier):
        try:
            data = request.json
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            if "interactionElements" in data:
                pass
                #return self.pyaas.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyAAS)           
                if(aasValid.validateAASShell(data)):
                    if (aasIdentifier == data["id"] or aasIdentifier == ["idShort"]):
                        edm = ExecuteDBModifier(self.pyAAS)
                        data,status,statuscode = edm.execute({"data": {"_shellId":aasIdentifier, "_aasShell":data}, "method": "PutAssetAdministrationShell",
                                                                     "instanceId" : str(uuid.uuid1())})
                        return make_response(data,statuscode)
                    else:
                        return make_response("The aas-identifier in the uri and in AAS Shell do not match",400)
                else :
                    return make_response("The syntax of the passed Asset Administration Shell is not valid or malformed request",400)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at PutAssetAdministrationShell Rest" + str(E))
            return make_response("Internal Server Error",500)

class SubmodelReferences(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def get(self,aasIdentifier):
        try:
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            edbR = ExecuteDBRetriever(self.pyAAS)      
            data,status,statuscode = edbR.execute({"data":aasIdentifier,"method":"GetAllSubmodelReferences"})            
            return make_response(jsonify(data),statuscode)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at GetAllSubmodelReferences Rest" + str(E))
            return make_response("Internal Server Error",500)

    def post(self,aasIdentifier):
        try:
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            data = request.json
            if "interactionElements" in data:
                pass
                #return self.pyaas.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyAAS)           
                if(aasValid.validateAASShellSubmodelRef(data)):
                    edm = ExecuteDBModifier(self.pyAAS)
                    data,status,statuscode = edm.execute({"data": {"_shellId":aasIdentifier, "_Reference":data}, "method": "PostSubmodelReference",
                                                                 "instanceId" : str(uuid.uuid1())})
                    return make_response(data,statuscode)
                else :
                    return make_response("The syntax of the passed Submodel Reference is not valid or malformed request",400)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at postAssetAdministrationShells Rest" + str(E))
            return make_response("Internal Server Error",500)        

class DeleteSubmodelReference(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def delete(self,aasIdentifier,submodelIdentifier):    
        try:
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            edm = ExecuteDBModifier(self.pyAAS)
            data,status,statuscode = edm.execute({"data":{"_shellId":aasIdentifier, "submodelIdentifier":submodelIdentifier}, "method": "DeleteSubmodelReference",
                                                         "instanceId" : str(uuid.uuid1())})
            return make_response(data,statuscode)            
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at DeleteSubmodelReference REST API" + str(E))
            return make_response("Internal Server Error",500)

class AssetInformation(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS

    def get(self,aasIdentifier):
        try:
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            edbR = ExecuteDBRetriever(self.pyAAS)
            data,status,statuscode = edbR.execute({"data":aasIdentifier,"method":"GetAssetInformation"})            
            return make_response(data,statuscode)     
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at GetAssetInformation REST API" + str(E))
            return make_response("Internal Server Error",500)
    
    def put(self,aasIdentifier):
        try:
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            data = request.json
            if "interactionElements" in data: 
                pass
                #return self.pyaas.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyAAS)           
                if(aasValid.valitdateAssetInformation(data)):
                    edm = ExecuteDBModifier(self.pyAAS)
                    data,status,statuscode = edm.execute({"data": {"_shellId":aasIdentifier, "_assetInformation":data}, "method": "PutAssetInformation",
                                                                 "instanceId" : str(uuid.uuid1())})
                    return make_response(data,statuscode)                    
                else :
                    return make_response("The syntax of the passed AssetInformation is not valid or malformed request",400)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at PutAssetInformation Rest" + str(E))
            return make_response("Internal Server Error",500)

'''
Asset Administration Shell Interface End

'''

##################################################
'''
Submodel Interface Start 
'''

class Submodel(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def get(self,aasIdentifier,submodelIdentifier): 
        try:
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            edbR = ExecuteDBRetriever(self.pyAAS)
            data,status,statuscode = edbR.execute({"data":{"submodelIdentifier":submodelIdentifier,"_shellId":aasIdentifier},"method":"GetSubmodel"})  
            return make_response(data,statuscode)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at GetSubmodel Rest" + str(E))
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
                aasValid = AASMetaModelValidator(self.pyAAS)           
                if(aasValid.valitdateSubmodel(data)):
                    edm = ExecuteDBModifier(self.pyAAS)
                    data,status,statuscode = edm.execute({"data":{"submodelIdentifier":submodelIdentifier, "_shellId":aasIdentifier,
                                                                "submodelData":data},"method":"PutSubmodel","instanceId" : str(uuid.uuid1())})
                    return make_response(data,statuscode)
                else :
                    return make_response("The syntax of the passed Submodel is not valid or malformed request",400)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at PutSubmodel Rest" + str(E))
            return make_response("Internal Server Error",500)

class SubmodelElements(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def get(self,aasIdentifier,submodelIdentifier):
        try:
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            edbR = ExecuteDBRetriever(self.pyAAS)
            data,status,statuscode = edbR.execute({"data":{"submodelIdentifier":submodelIdentifier,"_shellId":aasIdentifier},"method":"GetAllSubmodelElements"})            
            return make_response(jsonify(data),statuscode)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at GetAllSubmodelElements Rest" + str(E))
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
                aasValid = AASMetaModelValidator(self.pyAAS)           
                if(aasValid.validateSubmodelElement(data)):
                    edm = ExecuteDBModifier(self.pyAAS)
                    data,status,statuscode = edm.execute({"data":{"elemData":data,
                                            "submodelIdentifier" : submodelIdentifier,"_shellId": aasIdentifier
                                                                  },"method":"PostSubmodelElement","instanceId" : str(uuid.uuid1())})
                    return make_response(data,statuscode)
                else :
                    return make_response("The syntax of the passed Submodel ELement is not valid or malformed request",400)                
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at PostSubmodelElement Rest" + str(E))
            return make_response("Internal Server Error",500)              

class SubmodelElementByPath(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
        
    def get(self,aasIdentifier,submodelIdentifier,idShortPath):
        try:
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            idShortPath = unquote(idShortPath)
            edbR = ExecuteDBRetriever(self.pyAAS)
            data,status,statuscode = edbR.execute({"data":{"_shellId":aasIdentifier,"submodelIdentifier":submodelIdentifier,
                                               "idShortPath":idShortPath},"method":"GetSubmodelElementByPath",
                                            "instanceId" : str(uuid.uuid1())})            
            return make_response(data,statuscode)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at GetSubmodelElementByPath Rest" + str(E))
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
                aasValid = AASMetaModelValidator(self.pyAAS)           
                if(aasValid.validateSubmodelElement(data)):
                    edm = ExecuteDBModifier(self.pyAAS)
                    data,status,statuscode = edm.execute({"data":{"_shellId":aasIdentifier, "submodelIdentifier":submodelIdentifier,
                                                   "idShortPath":idShortPath,"elemData":data},"method":"PostSubmodelElementByPath","instanceId" : str(uuid.uuid1())}) 
                    return make_response(data,statuscode)
                else :
                    return make_response("The syntax of the passed Submodel ELement is not valid or malformed request",400)                
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at PostSubmodelElementByPath Rest" + str(E))
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
                aasValid = AASMetaModelValidator(self.pyAAS)           
                if(aasValid.validateSubmodelElement(data)):
                    edm = ExecuteDBModifier(self.pyAAS)
                    data,status,statuscode = edm.execute({"data":{"_shellId":aasIdentifier, "submodelIdentifier":submodelIdentifier,
                                               "idShortPath":idShortPath,"elemData":data},"method":"PutSubmodelElementByPath","instanceId" : str(uuid.uuid1())}) 
                    return make_response(data,statuscode)
                else :
                    return make_response("The syntax of the passed Submodel ELement is not valid or malformed request",400)                
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at PutSubmodelElementByPath Rest" + str(E))
            return make_response("Internal Server Error",500)  

    def delete(self,aasIdentifier,submodelIdentifier,idShortPath):
        try:
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            idShortPath = unquote(idShortPath)
            edm = ExecuteDBModifier(self.pyAAS)
            data,status,statuscode = edm.execute({"data":{"_shellId":aasIdentifier, "submodelIdentifier":submodelIdentifier,
                                               "idShortPath":idShortPath},"method":"DeleteSubmodelElementByPath","instanceId" : str(uuid.uuid1())})            
            return make_response(data,statuscode)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at DeleteSubmodelElementByPath Rest" + str(E))
            return make_response("Internal Server Error",500)   

#SubmodelElementByPath_history,SubmodelElementByPath_SRI_history
class SubmodelElementByPath_history(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
        
    def get(self,aasIdentifier,submodelIdentifier,idShortPath):
        try:
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            idShortPath = unquote(idShortPath)
            edbR = ExecuteDBRetriever(self.pyAAS)
            data,status,statuscode = edbR.execute({"data":{"_shellId":aasIdentifier,"submodelIdentifier":submodelIdentifier,
                                               "idShortPath":idShortPath},"method":"GetSubmodelElementByPath_History",
                                            "instanceId" : str(uuid.uuid1())})            
            return make_response(data,statuscode)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at GetSubmodelElementByPath_histtory Rest" + str(E))
            return make_response("Internal Server Error",500)

class FileByPath(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS

    def get(self,aasIdentifier,submodelIdentifier,idShortPath):
        try:
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            idShortPath = unquote(idShortPath)            
            edbR = ExecuteDBRetriever(self.pyAAS)
            data, status,statuscode = edbR.execute({"data":{"_shellId":aasIdentifier,"submodelIdentifier":submodelIdentifier,
                                               "idShortPath":idShortPath},"method":"GetFileByPath"})            
            if status:
                fileExtension = (data.split(".")[-1]).lower()
                filename = (data.split("/"))[-1]
                if fileExtension in fileformat:
                    file_path = os.path.join(self.pyAAS.downlaod_repository,*(data).split("/"))
                    sendfile = send_file(file_path,attachment_filename=filename, as_attachment=True,mimetype= fileformat[fileExtension])
                else:
                    file_path = os.path.join(self.pyAAS.downlaod_repository,*(data).split("/"))
                    sendfile = send_file(file_path,attachment_filename=filename, as_attachment=True,mimetype="text/plain")
                return  sendfile
            else:
                return make_response(data,status)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at GetFileByPath  REST API" + str(E))
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
                edm = ExecuteDBModifier(self.pyAAS)
                filedata,status,statuscode = edm.execute({"data":{"_shellId":aasIdentifier, "submodelIdentifier":submodelIdentifier,
                                               "idShortPath":idShortPath,"elemData":filename,"mimeType":mimeType},"instanceId" : str(uuid.uuid1()),
                                                                         "method":"PutFileByPath"})
                if status:
                    try:
                        filename = secure_filename(file.filename)
                        file.save(os.path.join(self.pyAAS.downlaod_repository, *(filedata).split("/")))
                        return make_response("Submodel element updated successfully",204)
                    except Exception as E:
                        self.pyAAS.serviceLogger.info("Error at PutFileByPath Rest" + str(E))
                        return make_response("Internal Server Error",500)
                else:
                    return make_response(filedata,statuscode)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at PutFileByPath Rest" + str(E))
            return make_response("Internal Server Error",500)        

'''
Submodel Interface End
'''


'''
Concept Description Repository Start
'''
class ConceptDescriptions(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS

    def get(self):
        try:
            edbR = ExecuteDBRetriever(self.pyAAS)
            args = request.args
            if len(args) > 0:
                try:
                    if (args.get('idShort')):
                        data, status,statuscode = edbR.execute({"data":args.get('idShort'),"method":"GetAllConceptDescriptionsByIdShort"})            
                        return make_response(jsonify(data),statuscode)
                    elif (args.get('isCaseOf')):
                        data, status,statuscode = edbR.execute({"data":args.get('isCaseOf'),"method":"GetAllConceptDescriptionsByIsCaseOf"})            
                        return make_response(jsonify(data),statuscode)
                    elif (args.get('dataSpecificationRef')):
                        data, status,statuscode = edbR.execute({"data":args.get('dataSpecificationRef'),"method":"GetAllConceptDescriptionsByDataSpecificationReference"})            
                        return make_response(jsonify(data),statuscode)
                    else:
                        return ("Bad Request",500)
                except:
                    pass           
            else:
                data, status,statuscode = edbR.execute({"data":None,"method":"GetAllConceptDescriptions"})            
                return make_response(jsonify(data),statuscode)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at GetConceptDescriptions Rest" + str(E))
            return make_response("Internal Server Error",500)
          
    def post(self):
        try:
            data = request.json
            if "interactionElements" in data:
                pass
                #return self.pyaas.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyAAS)           
                if(aasValid.validateConceptDescription(data)):
                    edm = ExecuteDBModifier(self.pyAAS)
                    data1,status1,statuscode1 = edm.execute({"data":{"_cd":data}, "method": "PostConceptDescription", "instanceId" : str(uuid.uuid1())})
                    return make_response(data1,statuscode1)
                else :
                    return make_response("The syntax of the passed Concept Description is not valid or malformed request",200)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at PostConceptDescription Rest" + str(E))
            return make_response("Internal Server Error",500)
        
class ConceptDescriptionById(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def get(self,cdIdentifier):
        try:
            cdIdentifier = (base64.decodebytes(cdIdentifier.encode())).decode()
            cdIdentifier = unquote(cdIdentifier)
            edbR = ExecuteDBRetriever(self.pyAAS)
            data,status,statuscode = edbR.execute({"data":cdIdentifier,"method":"GetConceptDescriptionById"})  
            return make_response(data,statuscode)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at GetConceptDescriptionById Rest" + str(E))
            return make_response("Unexpected Internal Server Error",500)
        
    def put(self,cdIdentifier):
        try:
            data = request.json
            cdIdentifier = (base64.decodebytes(cdIdentifier.encode())).decode()
            if "interactionElements" in data:
                pass
                #return self.pyaas.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyAAS)           
                if(aasValid.validateConceptDescription(data)):
                    edm = ExecuteDBModifier(self.pyAAS)
                    
                    data,status,statuscode = edm.execute({"data":{"_conceptDescriptionId":cdIdentifier, "_cd":data}, "method": "PutConceptDescriptionById", "instanceId" : str(uuid.uuid1())})
                    return make_response(data,statuscode)
                else :
                    return make_response("The syntax of the passed Concept Description is not valid or malformed request",400)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at PutConceptDescriptionById Rest" + str(E))
            return make_response("Internal Server Error",500)

    def delete(self,cdIdentifier):
        try:
            cdIdentifier = (base64.decodebytes(cdIdentifier.encode())).decode()
            edm = ExecuteDBModifier(self.pyAAS)
            data,status,statuscode = edm.execute({"data":cdIdentifier, "instanceId" : str(uuid.uuid1()), "method": "DeleteConceptDescriptionById"})
            return make_response(data,statuscode)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at DeleteConceptDescriptionById Rest" + str(E))
            return make_response("Internal Server Error",500)
 
'''
Concept Description Repository End 
'''
       
'''       
Submodel Repository Interface Start
'''
class Submodels(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def get(self):
        try:
            edbR = ExecuteDBRetriever(self.pyAAS)
            args = request.args
            if len(args) > 0:
                try:
                    if (args.get('idShort')):
                        data, status,statuscode = edbR.execute({"data":args.get('idShort'),"method":"GetAllSubmodelsByIdShort"})            
                        return make_response(jsonify(data),statuscode)
                    elif (args.get('semanticId')):
                        data, status,statuscode = edbR.execute({"data":args.get('semanticId'),"method":"GetAllSubmodelsBySemanticId"})            
                        return make_response(jsonify(data),statuscode)
                    else:
                        return make_response("Internal Server Error",500)
                except:
                    pass           
            else:
                data, status,statuscode = edbR.execute({"data":None,"method":"GetAllSubmodels"})            
                return make_response(jsonify(data),statuscode)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at GetSubmodels Rest" + str(E))
            return make_response("Internal Server Error",500)
       
    def post(self):
        try:
            data = request.json
            if "interactionElements" in data:
                pass
                #return self.pyaas.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyAAS)           
                if(aasValid.valitdateSubmodel(data)):
                    edm = ExecuteDBModifier(self.pyAAS)
                    data,status,statuscode = edm.execute({"data":{"_submodel":data}, "method": "PostSubmodel", "instanceId" : str(uuid.uuid1())})
                    return make_response(data,statuscode)
                else :
                    return make_response("The syntax of the passed Submodel is not valid or malformed request",400)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at PostSubmodel Rest" + str(E))
            return make_response("Internal Server Error",500)

class SubmodelById(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS

    def get(self,submodelIdentifier):
        try:
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            edbR = ExecuteDBRetriever(self.pyAAS)
            data,status,statuscode = edbR.execute({"data":submodelIdentifier,"method":"GetSubmodelById"})  
            return make_response(data,statuscode)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at GetSubmodelById Rest" + str(E))
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
                aasValid = AASMetaModelValidator(self.pyAAS)           
                if(aasValid.valitdateSubmodel(data)):
                    edm = ExecuteDBModifier(self.pyAAS)
                    
                    data,status,statuscode = edm.execute({"data":{"submodelIdentifier":submodelIdentifier, "_submodel":data}, "method": "PutSubmodelById", "instanceId" : str(uuid.uuid1())})
                    return make_response(data,statuscode)
                else :
                    return make_response("The syntax of the passed Submodel is not valid or malformed request",400)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at PutSubmodelById Rest" + str(E))
            return make_response("Internal Server Error",500)

    def delete(self,submodelIdentifier):
        try:
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            edm = ExecuteDBModifier(self.pyAAS)
            data,status,statuscode = edm.execute({"data":submodelIdentifier, "instanceId" : str(uuid.uuid1()), "method": "DeleteSubmodelById"})
            return make_response(data,statuscode)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at DeleteSubmodelById Rest" + str(E))
            return make_response("Internal Server Error",500)

class Submodel_SRI(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def get(self,submodelIdentifier): 
        try:
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            edbR = ExecuteDBRetriever(self.pyAAS)
            data,status,statuscode = edbR.execute({"data":{"submodelIdentifier":submodelIdentifier},"method":"GetSubmodel_SRI"})  
            return make_response(data,statuscode)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at GetSubmodel_SRI Rest" + str(E))
            return make_response("Internal Server Error",500)
        
    def put(self,submodelIdentifier): 
        try:
            data = request.json
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            if "interactionElements" in data:
                pass
                #return self.pyaas.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyAAS)           
                if(aasValid.valitdateSubmodel(data)):
                    edm = ExecuteDBModifier(self.pyAAS)
                    data,status,statuscode = edm.execute({"data":{"submodelIdentifier":submodelIdentifier,
                                                                "_submodel":data},"method":"PutSubmodel_SRI","instanceId" : str(uuid.uuid1())})
                    return make_response(data,statuscode)
                else :
                    return make_response("The syntax of the passed Submodel is not valid or malformed request",400)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at PutSubmodel_SRI Rest" + str(E))
            return make_response("Internal Server Error",500)

class SubmodelElements_SRI(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def get(self,submodelIdentifier):
        try:
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            edbR = ExecuteDBRetriever(self.pyAAS)
            data,status,statuscode = edbR.execute({"data":{"submodelIdentifier":submodelIdentifier},"method":"GetAllSubmodelElements_SRI"})            
            return make_response(jsonify(data),statuscode)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at GetAllSubmodelElements_SRI Rest" + str(E))
            return make_response("Internal Server Error",500)

    def post(self,submodelIdentifier):
        try:
            data = request.json
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            if "interactionElements" in data:
                pass
                #return self.pyaas.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyAAS)           
                if(aasValid.validateSubmodelElement(data)):
                    edm = ExecuteDBModifier(self.pyAAS)
                    data,status,statuscode = edm.execute({"data":{"elemData":data,
                                            "submodelIdentifier" : submodelIdentifier
                                                                  },"method":"PostSubmodelElement_SRI","instanceId" : str(uuid.uuid1())})
                    return make_response(data,statuscode)
                else :
                    return make_response("The syntax of the passed Submodel ELement is not valid or malformed request",400)                
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at PostSubmodelElement_SRI Rest" + str(E))
            return make_response("Internal Server Error",500)              

class SubmodelElementByPath_SRI(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
        
    def get(self,submodelIdentifier,idShortPath):
        try:
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            idShortPath = unquote(idShortPath)
            edbR = ExecuteDBRetriever(self.pyAAS)
            data,status,statuscode = edbR.execute({"data":{"submodelIdentifier":submodelIdentifier,
                                               "idShortPath":idShortPath},"method":"GetSubmodelElementByPath_SRI",
                                            "instanceId" : str(uuid.uuid1())})            
            return make_response(data,statuscode)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at GetSubmodelElementByPath_SRI Rest" + str(E))
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
                aasValid = AASMetaModelValidator(self.pyAAS)           
                if(aasValid.validateSubmodelElement(data)):
                    edm = ExecuteDBModifier(self.pyAAS)
                    data,status,statuscode = edm.execute({"data":{"submodelIdentifier":submodelIdentifier,
                                                   "idShortPath":idShortPath,"elemData":data},"method":"PostSubmodelElementByPath_SRI","instanceId" : str(uuid.uuid1())}) 
                    return make_response(data,statuscode)
                else :
                    return make_response("The syntax of the passed Submodel ELement is not valid or malformed request",400)                
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at PostSubmodelElementByPath_SRI Rest" + str(E))
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
                aasValid = AASMetaModelValidator(self.pyAAS)           
                if(aasValid.validateSubmodelElement(data)):
                    edm = ExecuteDBModifier(self.pyAAS)
                    data,status,statuscode = edm.execute({"data":{"submodelIdentifier":submodelIdentifier,
                                               "idShortPath":idShortPath,"elemData":data},"method":"PutSubmodelElementByPath_SRI","instanceId" : str(uuid.uuid1())}) 
                    return make_response(data,statuscode)
                else :
                    return make_response("The syntax of the passed Submodel ELement is not valid or malformed request",400)                
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at PutSubmodelElementByPath_SRI Rest" + str(E))
            return make_response("Internal Server Error",500)  

    def delete(self,submodelIdentifier,idShortPath):
        try:
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            idShortPath = unquote(idShortPath)
            edm = ExecuteDBModifier(self.pyAAS)
            data,status,statuscode = edm.execute({"data":{"submodelIdentifier":submodelIdentifier,
                                               "idShortPath":idShortPath},"method":"DeleteSubmodelElementByPath_SRI","instanceId" : str(uuid.uuid1())})            
            return make_response(data,statuscode)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at DeleteSubmodelElementByPath_SRI Rest" + str(E))
            return make_response("Internal Server Error",500)   

class FileByPath_SRI(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS

    def get(self,submodelIdentifier,idShortPath):
        try:
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            idShortPath = unquote(idShortPath)            
            edbR = ExecuteDBRetriever(self.pyAAS)
            data,status,statuscode = edbR.execute({"data":{"submodelIdentifier":submodelIdentifier,
                                               "idShortPath":idShortPath},"method":"GetFileByPath_SRI"})            
            if status:
                fileExtension = (data.split(".")[-1]).lower()
                filename = (data.split("/"))[-1]
                if fileExtension in fileformat:
                    file_path = os.path.join(self.pyAAS.downlaod_repository,*(data).split("/"))
                    sendfile = send_file(file_path,attachment_filename=filename, as_attachment=True,mimetype= fileformat[fileExtension])
                else:
                    file_path = os.path.join(self.pyAAS.downlaod_repository,*(data).split("/"))
                    sendfile = send_file(file_path,attachment_filename=filename, as_attachment=True,mimetype="text/plain")
                return  sendfile
            else:
                return make_response(data,status)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at GetFileByPath_SRI  REST API" + str(E))
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
                edm = ExecuteDBModifier(self.pyAAS)
                filedata,status,statuscode = edm.execute({"data":{"submodelIdentifier":submodelIdentifier,
                                               "idShortPath":idShortPath,"elemData":filename,"mimeType":mimeType},"instanceId" : str(uuid.uuid1()),
                                                                         "method":"PutFileByPath_SRI"})
                if status:
                    try:
                        filename = secure_filename(file.filename)
                        file.save(os.path.join(self.pyAAS.downlaod_repository, *(filedata).split("/")))
                        return make_response("Submodel element updated successfully",204)
                    except Exception as E:
                        self.pyAAS.serviceLogger.info("Error at PutFileByPath Rest" + str(E))
                        return make_response("Internal Server Error",500)
                else:
                    return make_response(filedata,statuscode)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at PutFileByPath_SRI Rest" + str(E))
            return make_response("Internal Server Error",500)        



'''       
Submodel Repository Interface End
'''

class AssetAdministrationShellsSubmodelRefs(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def get(self,aasIdentifier):
        try:
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            edbR = ExecuteDBRetriever(self.pyAAS)
            data,status,statuscode = edbR.execute({"data":aasIdentifier,"method":"getShellSubmodelRefs"})            
            return make_response(data,statuscode)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at getAssetAdministrationShells Rest" + str(E))
            return make_response("Unexpected Internal Server Error",500)
        
    def post(self,aasIdentifier):
        try:
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            data = request.json
            if "interactionElements" in data:
                pass
                #return self.pyaas.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else: 
                aasValid = AASMetaModelValidator(self.pyAAS)           
                if(aasValid.validateAASShellSubmodelRef(data)):
                    edm = ExecuteDBModifier(self.pyAAS)
                    data,status,statuscode = edm.execute({"data":{"_shellId":aasIdentifier, "_submodelRef":data
                                                                  },"method":"postShellSubmodelRef"})
                    return make_response(data,statuscode)
                else :
                    return make_response("The syntax of the passed Asset Administration Shell Submodel Reference is not valid or malformed request",200)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at postAssetAdministrationShells Rest" + str(E))
            return make_response("Internal Server Error",500)



class AASSubmodelElementByIdShortPath(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
        
    def get(self,aasIdentifier,submodelIdentifier,idShortPath):
        try:
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            idShortPath = unquote(idShortPath)
            edbR = ExecuteDBRetriever(self.pyAAS)
            data,status,statuscode = edbR.execute({"data":{"_shellId":aasIdentifier,"submodelIdentifier":submodelIdentifier,
                                               "idShortPath":idShortPath},
                                       "method":"GetSubmodelElementByPath","instanceId" : str(uuid.uuid1())})            

        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at GetSubmodelElementByPath Rest" + str(E))
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
                aasValid = AASMetaModelValidator(self.pyAAS)           
                if(aasValid.validateSubmodelELement(data)):
                    edm = ExecuteDBModifier(self.pyAAS)
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
            self.pyAAS.serviceLogger.info("Error at putSubmodelElementByIdShortPath Rest" + str(E))
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
                aasValid = AASMetaModelValidator(self.pyAAS)           
                if(aasValid.validateSubmodelELement(data)):
                    edm = ExecuteDBModifier(self.pyAAS)
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
            self.pyAAS.serviceLogger.info("Error at postSubmodelElementByIdShortPath Rest" + str(E))
            return make_response("Internal Server Error",500)        

    def delete(self,aasIdentifier,submodelIdentifier,idShortPath):
        try:
            aasIdentifier = (base64.decodebytes(aasIdentifier.encode())).decode()
            submodelIdentifier = (base64.decodebytes(submodelIdentifier.encode())).decode()
            idShortPath = unquote(idShortPath)
            edm = ExecuteDBModifier(self.pyAAS)
            msg,status = edm.execute({"data": submodelIdentifier + "." + idShortPath, "method": "deleteSubmodelElem", "instanceId" : str(uuid.uuid1())})
            if status:
                return make_response(msg,204)
            else:
                return make_response(msg,500)
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at deleteSubmodelElementByIdShortPath Rest" + str(E))
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
                #return self.pyaas.skillInstanceDict["AASHandler"].restAPIHandler(data)
            else:
                if(True):
                    if (True):
                        edm = ExecuteDBModifier(self.pyAAS)
                        data,status = edm.execute({"data":{"_shellId": aasId, "_submodelRef":data}
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
            data,status = edm.execute({"data":{"_shellId":aasId, "_submodelrefId":submodelId},
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

class AASStaticConfigSource(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
        
    def get(self,filename):      
        try:
            return send_from_directory(self.pyAAS.repository,filename)
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
    def __init__(self,pyaas):
        self.pyaas = pyaas
    
    def process(self):
        status, data = self.retrieve_aas_information(request)
        if status:
            edm = ExecuteDBModifier(self.pyAAS)
            data,status1,statuscode = edm.execute({"data":data, "method": "PostAssetAdministrationShell",
                                                                 "instanceId" : str(uuid.uuid1())})
            return status1
        else:
            return status
    
    
    def save_aas_information(self,data):
        gen_aas_shell = Generate_AAS_Shell(self.pyaas,data["idShort"],data["description"],"/aasx/"+data["file"].fileName)
        data,status = gen_aas_shell.execute()
        if status:
            if self.process(): 
                (data["file"]).save(os.path.join(self.pyAAS.downlaod_repository, "/aasx/"+data["file"].fileName))
            else:
                return False
        return status
    
    def retrieve_validate_aas(self,request):
        data = dict()
        updateData = request.form
        try:
            file = request.files['file']
            data["file"] = file
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
            return True, data
        except Exception as e:
            print("Error while retrieving the description  @retrieve_aas_information"+ str(e))
            return False, "Error while retrieving the description"

    def post(self):              
        try:
            status, data = self.retrieve_validate_aas()
            if not status:
                flash(data,"error")             
            else:    
                status1,data1 = self.save_aas_information(data)
                if not status1:
                    pass
                else:
                    flash("data","error")

        except Exception as e:
            self.pyaas.serviceLogger.info("Error at Post AASWebInterfaceHome Rest" + str(e))
            flash("Error in creating the ","error")
        
        return  Response(render_template('home.html',exDomain=self.pyaas.exDomain,
                                                         aasList = self.get_aas_data()))


    def get_aas_data(self):
        try:
            data, status, code = self.pyaas.dba.GetAllAssetAdministrationShells()
            aasList = []
            if status :
                for _shell in data:
                    aasList.append(
                        {"aasIndex": self.pyaas.aasHashDict.__getHashEntry__(_shell["id"])._id, 
                         "shellId": _shell["id"],
                          "idShort": _shell["idShort"],
                          "thumbnail": _shell["assetInformation"]["defaultThumbnail"]["path"]})            
        except Exception as e:
            self.pyaas.serviceLogger.info("Error at Get AASWebInterfaceHome Rest" + str(e))
        return aasList 
                   
    

    def get(self):              
        try:
            return  Response(render_template('home.html',exDomain=self.pyaas.exDomain,
                                                         aasList = self.get_aas_data()))
        except Exception as E:
            return str(E)

class AASWebInterface(Resource):
    def __init__(self,pyaas):
        self.pyaas = pyaas

    def get(self,aasIndex):
        try:
            data = self.pyaas.dba.get_aas_information(aasIndex)
            return  Response(render_template('index.html',thumbNail= data["thumbnail"],
                                                        aasIndex=aasIndex, exDomain=self.pyaas.exDomain , 
                                                        skillList= data["skillList"],
                                                        aasIdShort = data["idShort"],
                                                        submodelList = data["submodelList"]))
        except Exception as E:
            return str(E)

class AASWebInterfaceStandardSubmodel(Resource):
    def __init__(self,pyaas):
        self.pyaas = pyaas
        self.standardSubmodelWebPageDict = {"NAMEPLATE" : ("nameplate.html","https://admin-shell.io/zvei/nameplate/1/0/Nameplate"), 
                                            "DOCUMENTATION" : ("documentation.html", "http://admin-shell.io/vdi/2770/1/0/Documentation"),
                                            "TECHNICAL_DATA" : ("technicaldata.html" ,"http://admin-shell.io/sandbox/SG2/TechnicalData/Submodel/1/1"),
                                             "IDENTIFICATION": ("identification.html","https://www.hsu-hh.de/aut/aas/identification")}
    def get(self,aasIndex,stdsubmodelType):    
        try:
            data = self.pyaas.dba.get_aas_information(aasIndex)
            submodel_information = self.standardSubmodelWebPageDict["NAMEPLATE"]
            stdSubmodel = copy.deepcopy(data["_aasShell"].standardSubmodels[submodel_information[1]][0])
            stdData = StandardSubmodelData(self.pyaas)
            if stdsubmodelType == "NAMEPLATE":
                stdSubmodel["DE"]["data"] = stdData.execute(stdSubmodel["DE"]["data"], "DE")
                stdSubmodel["EN"]["data"] = stdData.execute(stdSubmodel["EN"]["data"], "EN")
            elif stdsubmodelType in ["TECHNICAL_DATA","IDENTIFICATION"]:
                stdSubmodel =  stdData.execute(stdSubmodel, None)
            
            return  Response(render_template(self.standardSubmodelWebPageDict[stdsubmodelType][0],thumbNail= data["thumbnail"],
                                                        aasIndex=aasIndex, exDomain=self.pyaas.exDomain , 
                                                        skillList= data["skillList"],
                                                        aasIdShort = data["idShort"],
                                                        stdSubmodelList = data["stdSubmodelList"],
                                                        stdSubmodelData = stdSubmodel))
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
            return self.pyAAS.skill_logListDict[aasIndex][unquote(skillName)].getCotent()
        except Exception as E:
            return str(E)

class AASWebInterfaceSubmodels(Resource):
    def __init__(self,pyaas):
        self.pyaas = pyaas

    def get(self,aasIndex):       
        try:
            data = self.pyaas.dba.get_aas_information(aasIndex)
            submodelData,status,code = self.pyaas.dba.GetSubmodel({"submodelIdentifier":"https://example.com/ids/sm/6412_8113_1032_9697",
                                                                   "_shellId":"something_random_428f0205"})
            return  Response(render_template('cus_submodel.html',thumbNail= data["thumbnail"],
                                                        aasIndex=aasIndex, exDomain=self.pyaas.exDomain , 
                                                        skillList= data["skillList"],
                                                        aasIdShort = data["idShort"],
                                                        stdSubmodelList = data["stdSubmodelList"],
                                                        submodelD = submodelData,
                                                        submodelId = submodelData["id"],
                                                        submodelName =submodelData["idShort"] ))        
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
                return submodel["id"]
        
    
    def getRelevantElemData(self,aasIdentifier,updateValue,idShortPath,submodelName,submodelElemAdditionalInfo,submodelELemType,submodelidentificationId):
        try:
            edbR = ExecuteDBRetriever(self.pyAAS)
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
            edm = ExecuteDBModifier(self.pyAAS)
            elemData,status = self.getRelevantElemData(aasIdentifier,updateValue,idShortPath,submodelName,submodelElemAdditionalInfo,
                                                submodelELemType,submodelidentificationId)
            if status :
                msg1,status1 = edm.execute({"data":{"elemData":elemData,
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
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
    
    def get(self,aasId,filename):
        try:
            file_path = os.path.join(self.pyAAS.downlaod_repository,filename)
            sendfile = send_file(file_path, as_attachment=True,mimetype= "application/pdf")
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
        if  "AssetInterfaceDescription" in self.pyAAS.aasStandardSubmodelData[aasId].keys():      
            return  Response(render_template('rtdata.html',aasIndex=aasId,exDomain=self.pyAAS.exDomain ,
                                             tdProperties = self.pyAAS.aasStandardSubmodelData[aasId]["AssetInterfaceDescription"][1],
                                             skillList= self.pyAAS.skillListWeb[aasId],
                                             stdSubmodelList = self.pyAAS.aasStandardSubmodelList[aasId],
                                             aasIdShort = self.pyAAS.aasIndexidShortDict[aasId]["idShort"]))
        
        else:
            return  Response(render_template('rtdata.html',aasIndex=aasId,exDomain=self.pyAAS.exDomain ,
                                             tdProperties = [],
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
