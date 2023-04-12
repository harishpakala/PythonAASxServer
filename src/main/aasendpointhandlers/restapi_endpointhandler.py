'''
Copyright (c) 2021-2022 OVGU LIA
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
'''
import json
import logging
import os
import requests
import threading
from gevent.pywsgi import WSGIServer

from requests.utils import quote
from flask import Flask,send_from_directory
from flask_restful import  Api,Resource
try:
    from utils.utils import HTTPResponse
except ImportError:
    from src.main.utils.utils import HTTPResponse

try:
    from abstract.endpointhandler import AASEndPointHandler
except ImportError:
    from src.main.abstract.endpointhandler import AASEndPointHandler

try:
    from aasendpointhandlers.rstapi_endpointresources import AssetAdministrationShells,AssetAdministrationShellById,AssetAdministrationShell,SubmodelReferences,DeleteSubmodelReference,AssetInformation,Submodel,SubmodelElements,SubmodelElementByPath,FileByPath,ConceptDescriptions,ConceptDescriptionById,Submodels,SubmodelById,Submodel_SRI,SubmodelElements_SRI,SubmodelElementByPath_SRI,FileByPath_SRI,SubmodelElementByPath_history,Submodels_shell#,#AssetAdministrationShell,ConceptDescriptions,ConceptDescription,Submodels,Submodel,AssetAdministrationShellsSubmodelRefs,SubmodelELements,SubmodelElementByIdShortPath,AASSubmodelElementByIdShortPath,AASStaticSource,AASStaticWebSources,AASRTDataVisualizer,AASWebInterfaceConversationMessage,AASWebInterfaceRegister
except ImportError:
    from src.main.aasendpointhandlers.rstapi_endpointresources import AssetAdministrationShells,AssetAdministrationShellById,AssetAdministrationShell,SubmodelReferences,DeleteSubmodelReference,AssetInformation,Submodel,SubmodelElements,SubmodelElementByPath,FileByPath,ConceptDescriptions,ConceptDescriptionById,Submodels,SubmodelById,Submodel_SRI,SubmodelElements_SRI,SubmodelElementByPath_SRI,FileByPath_SRI,SubmodelElementByPath_history,Submodels_shell#,AssetAdministrationShell,ConceptDescriptions,ConceptDescription,Submodels,Submodel,AssetAdministrationShellsSubmodelRefs,SubmodelELements,SubmodelElementByIdShortPath,AASSubmodelElementByIdShortPath,AASStaticSource,AASStaticWebSources,AASRTDataVisualizer,AASWebInterfaceConversationMessage,AASWebInterfaceRegister

try:
    from aasendpointhandlers.rstapi_endpointresources import RetrieveMessage,AASWebInterfaceHome,AASWebInterface,AASWebInterfaceSearch,AASWebInterfaceSubmodels,AASWebInterfaceSubmodelElemValue,AASWebInterfaceSKillLog,AASWebInterfaceProductionManagement,AASDocumentationDownload,AASDocumentationDownload,AASDocumentationDownloadSubmodel,AASStaticConfigSource,AASStaticSource,AASRTDataVisualizer,AASWebInterfaceRegister,AASWebInterfaceCFP
except ImportError:
    from src.main.aasendpointhandlers.rstapi_endpointresources import RetrieveMessage,AASWebInterfaceHome,AASWebInterface,AASWebInterfaceSearch,AASWebInterfaceSubmodels,AASWebInterfaceSubmodelElemValue,AASWebInterfaceSKillLog,AASWebInterfaceProductionManagement,AASDocumentationDownload,AASDocumentationDownload,AASDocumentationDownloadSubmodel,AASStaticConfigSource,AASStaticSource,AASRTDataVisualizer,AASWebInterfaceRegister,AASWebInterfaceCFP
    
drv_rst_app = Flask(__name__)
drv_rst_app.secret_key = os.urandom(24)
#drv_rst_app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

drv_rst_api = Api(drv_rst_app)
drv_rst_app.logger.disabled = True
log = logging.getLogger('Python AASx Server REST API')
log.setLevel(logging.ERROR)
log.disabled = True

class AASEndPointHandler(AASEndPointHandler):
    
    def __init__(self, pyaas, msgHandler):
        self.pyaas = pyaas
        
        self.msgHandler = msgHandler
        self.registryURL = self.pyaas.lia_env_variable["LIA_REGISTRYENDPOINT"] 
        self.transportHeader = {"content-type": "application/json"}
        
    def configure(self):
        
        self.ipaddressComdrv = '0.0.0.0'#self.pyaas.lia_env_variable["LIA_AAS_RESTAPI_DOMAIN_EXTERN"]
        self.portComdrv = self.pyaas.lia_env_variable["LIA_AAS_RESTAPI_PORT_INTERN"]
        
        drv_rst_app.config['JS_REPOSITORY'] = self.pyaas.js_repository
        drv_rst_app.config['CSS_REPOSITORY'] = self.pyaas.css_repository
        drv_rst_app.config['IMG_REPOSITORY'] = self.pyaas.img_repository
        
        
        drv_rst_api.add_resource(AASWebInterfaceHome,"/shells/webui",resource_class_args=tuple([self.pyaas]))    
        drv_rst_api.add_resource(AASWebInterface,"/shells/<path:aasIdentifier>/webui",resource_class_args=tuple([self.pyaas]))
        drv_rst_api.add_resource(AASWebInterfaceSubmodels,"/shells/<path:aasIdentifier>/aas/submodels/<path:submodelIdentifier>/submodel/webui",resource_class_args=tuple([self.pyaas]))
        drv_rst_api.add_resource(AASWebInterfaceSKillLog, "/shells/<path:aasIdentifier>/log/<path:skillName>/webui", resource_class_args=tuple([self.pyaas]))
        drv_rst_api.add_resource(AASWebInterfaceProductionManagement,"/shells/<path:aasIdentifier>/productionmanager/webui",resource_class_args=tuple([self.pyaas]))
        drv_rst_api.add_resource(AASWebInterfaceRegister, "/shells/<path:aasIdentifier>/registration/webui", resource_class_args=tuple([self.pyaas]))
        
        #drv_rst_api.add_resource(AASStaticSource, "/web/<filename>",resource_class_args=tuple([self.pyaas]))
        drv_rst_api.add_resource(AASStaticConfigSource, "/config/<path:filename>",resource_class_args=tuple([self.pyaas]))
        drv_rst_api.add_resource(AASStaticWebSources, "/web/<string:webtype>/<filename>",resource_class_args=tuple([self.pyaas]))
        drv_rst_api.add_resource(AASRTDataVisualizer, "/<path:aasIdentifier>/rtdata/visualize",resource_class_args=tuple([self.pyaas]))
       
        drv_rst_api.add_resource(AASWebInterfaceSearch,"/<path:aasIdentifier>/search",resource_class_args=tuple([self.pyaas]))
        drv_rst_api.add_resource(AASWebInterfaceCFP,"/<path:conversationId>/cfp",resource_class_args=tuple([self.pyaas]))
        # REST API
        drv_rst_api.add_resource(AssetAdministrationShells, "/shells/", resource_class_args=tuple([self.pyaas]))
        drv_rst_api.add_resource(AssetAdministrationShellById, "/shells/<path:aasIdentifier>", resource_class_args=tuple([self.pyaas]))
        
        drv_rst_api.add_resource(AssetAdministrationShell,"/shells/<path:aasIdentifier>/aas", resource_class_args=tuple([self.pyaas]))
        drv_rst_api.add_resource(SubmodelReferences,"/shells/<path:aasIdentifier>/aas/submodels", resource_class_args=tuple([self.pyaas]))
        drv_rst_api.add_resource(DeleteSubmodelReference,"/shells/<path:aasIdentifier>/aas/submodels/<path:submodelIdentifier>", resource_class_args=tuple([self.pyaas]))
        drv_rst_api.add_resource(AssetInformation,"/shells/<path:aasIdentifier>/aas/asset-information", resource_class_args=tuple([self.pyaas]))

        drv_rst_api.add_resource(Submodel,"/shells/<path:aasIdentifier>/aas/submodels/<path:submodelIdentifier>/submodel", resource_class_args=tuple([self.pyaas]))
        #extra
        drv_rst_api.add_resource(Submodels_shell,"/shells/<path:aasIdentifier>/aas/submodels", resource_class_args=tuple([self.pyaas]))
        #extraa
        drv_rst_api.add_resource(SubmodelElements,"/shells/<path:aasIdentifier>/aas/submodels/<path:submodelIdentifier>/submodel/submodel-elements", resource_class_args=tuple([self.pyaas]))
        drv_rst_api.add_resource(SubmodelElementByPath,"/shells/<path:aasIdentifier>/aas/submodels/<path:submodelIdentifier>/submodel/submodel-elements/<path:idShortPath>", resource_class_args=tuple([self.pyaas]))
        drv_rst_api.add_resource(SubmodelElementByPath_history,"/shells/<path:aasIdentifier>/aas/submodels/<path:submodelIdentifier>/submodel/submodel-elements/<path:idShortPath>/history", resource_class_args=tuple([self.pyaas]))
        drv_rst_api.add_resource(FileByPath,"/shells/<path:aasIdentifier>/aas/submodels/<path:submodelIdentifier>/submodel/submodel-elements/<path:idShortPath>/attachment", resource_class_args=tuple([self.pyaas]))
        
        drv_rst_api.add_resource(ConceptDescriptions, "/concept-descriptions", resource_class_args=tuple([self.pyaas]))
        drv_rst_api.add_resource(ConceptDescriptionById, "/concept-descriptions/<path:cdIdentifier>", resource_class_args=tuple([self.pyaas]))    
        
        drv_rst_api.add_resource(Submodels, "/submodels", resource_class_args=tuple([self.pyaas]))
        drv_rst_api.add_resource(SubmodelById, "/submodels/<path:submodelIdentifier>", resource_class_args=tuple([self.pyaas]))
        

        drv_rst_api.add_resource(Submodel_SRI,"/submodels/<path:submodelIdentifier>/submodel", resource_class_args=tuple([self.pyaas]))
        drv_rst_api.add_resource(SubmodelElements_SRI,"/submodels/<path:submodelIdentifier>/submodel/submodel-elements", resource_class_args=tuple([self.pyaas]))
        drv_rst_api.add_resource(SubmodelElementByPath_SRI,"/submodels/<path:submodelIdentifier>/submodel/submodel-elements/<path:idShortPath>", resource_class_args=tuple([self.pyaas]))
        #drv_rst_api.add_resource(SubmodelElementByPath_SRI_history,"/submodels/<path:submodelIdentifier>/submodel/submodel-elements/<path:idShortPath>/history", resource_class_args=tuple([self.pyaas]))
        drv_rst_api.add_resource(FileByPath_SRI,"/submodels/<path:submodelIdentifier>/submodel/submodel-elements/<path:idShortPath>/attachment", resource_class_args=tuple([self.pyaas]))
        self.pyaas.serviceLogger.info("REST API namespaces are configured")
        
        #drv_rst_api.add_resource(SubmodelReferences,"/shells/<path:aasIdentifier>/aas/submodels", resource_class_args=tuple([self.pyaas]))
        #drv_rst_api.add_resource(SubmodelReference,"/shells/<path:aasIdentifier>/aas/submodels/<path:submodelIdentifier>", resource_class_args=tuple([self.pyaas]))
    
    #WebAPI
        
        
    '''


# /shells/<path:aasIdentifier>/submodels/<path:submodelIdentifier>/submodel/submodel-elements
#/shells/<path:aasIdentifier>/aas

        #drv_rst_api.add_resource(AAS, "/shells/<path:aasIdentifier>/aas", resource_class_args=tuple([self.pyaas]))
        
        drv_rst_api.add_resource(AASAssetInformationRefs, "/shells/<path:aasIdentifier>/aas/asset-information", resource_class_args=tuple([self.pyaas]))
        drv_rst_api.add_resource(AASassetInformation, "/assetInformation", resource_class_args=tuple([self.pyaas]))
        drv_rst_api.add_resource(AASassetInformationById, "/assetInformation/<path:assetId>", resource_class_args=tuple([self.pyaas]))
        #drv_rst_api.add_resource(Login,"/login",resource_class_args=tuple([self.pyaas]))
        # HTTP Communication
        drv_rst_api.add_resource(RetrieveMessage, "/i40commu", resource_class_args=tuple([self.pyaas]))

        #Web API

        
        

        
        drv_rst_api.add_resource(AASWebInterfaceStandardSubmodel,"/<int:aasIndex>/<string:stdsubmodelType>",resource_class_args=tuple([self.pyaas]))
        drv_rst_api.add_resource(AASWebInterfaceSubmodels,"/<int:aasIndex>/submodels",resource_class_args=tuple([self.pyaas]))
        
        
                                                                                      
        drv_rst_api.add_resource(AASWebInterfaceRegister, "/<int:aasIndex>/registration", resource_class_args=tuple([self.pyaas]))        
        
        drv_rst_api.add_resource(AASWebInterfaceConversationMessage,"/<int:aasIndex>/search/<query>",resource_class_args=tuple([self.pyaas]))        
        drv_rst_api.add_resource(AASWebInterfaceSubmodelElemValue,"/<int:aasIdentifier>/submodels/elem",resource_class_args=tuple([self.pyaas]))
        
        #Skill WEB API
        # ProductionManger
        drv_rst_api.add_resource(AASDocumentationDownload, "/documentation/document/<filename>",resource_class_args=tuple([self.pyaas]))
        drv_rst_api.add_resource(AASDocumentationDownloadSubmodel, "/<int:aasId>/document/<path:filename>",resource_class_args=tuple([self.pyaas]))
        #static folder path
        '''

        
     
    def update(self, channel):
            pass
    
    def run(self):
        #drv_rst_app.run(host=self.ipaddressComdrv, port=self.portComdrv)
        #drv_rst_app.run(host=self.ipaddressComdrv, port=self.portComdrv,ssl_context=(self.pyaas.lia_env_variable["LIA_PATH2AUTHCERT"], self.pyaas.lia_env_variable["LIA_PATH2SIGNINGKEY"]))
        drv_rst_app.run(host=self.ipaddressComdrv, port=self.portComdrv,ssl_context=('/etc/letsencrypt/live/liabroker.ddns.net/fullchain.pem', '/etc/letsencrypt/live/liabroker.ddns.net/privkey.pem'))
        #http_server = WSGIServer((self.ipaddressComdrv, int(self.portComdrv)), drv_rst_app)
        #http_server.serve_forever()
        self.pyAAS.serviceLogger.info("REST API namespaces are started")
    
    def start(self):
        restServerThread = threading.Thread(target=self.run)
        restServerThread.start()

    def stop(self):
        self.pyAAS.serviceLogger.info("REST API namespaces are stopped.")
    
    def dispatchMessage(self, send_Message): 
        try:
            if (send_Message["frame"]["type"] == "register"):
                registerURL = self.registryURL + "/api/v1/registry/" + quote(self.pyAAS.AASID, safe='')
                registerdata = (json.dumps(send_Message))
                r = requests.put(url=registerURL, data=registerdata, headers=self.transportHeader)
                data = json.loads(r.text)
                self.msgHandler.putIbMessage(data)
            elif (send_Message["frame"]["type"] == "HeartBeat"):
                publishURL = self.registryURL + "/i40commu"
                r = requests.post(publishURL, data=json.dumps(send_Message), headers=self.transportHeader)
            else:
                transportURL = self.registryURL + "/i40commu"
                requests.post(transportURL, data=json.dumps(send_Message), headers=self.transportHeader)
        except Exception as e:
            self.pyaas.serviceLogger.info("Unable to publish the message to the target http server", str(e))
            httpResponse = HTTPResponse(self.pyaas)
            self.pyaas.msgHandler.putIbMessage(httpResponse.createExceptionResponse(send_Message))

    def retrieveMessage(self, testMesage):  # todo
        pass
    
    def getData(self,accessURI):
        r = requests.get(accessURI)
        return r.text

class AASStaticWebSources(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
        
    def get(self,webtype,filename):
        try:
            if (webtype == "js"):
                filenames = {'filename': filename}
                rv = send_from_directory(os.path.join(self.pyAAS.js_repository),filename,mimetype="text/javascript")
                rv.headers.set('Content-Disposition',filenames)
                return rv 
            elif (webtype == "css"):
                filenames = {'filename': filename}
                rv = send_from_directory((self.pyAAS.css_repository),filename,mimetype="text/css")
                rv.headers.set('Content-Disposition',filenames)
                return rv
            elif (webtype == "images"):
                filenames = {'filename': filename}
                _type = filename.split(".")[1]
                if _type == "svg":
                    _type = "svg+xml"
                rv = send_from_directory(os.path.join(self.pyAAS.img_repository),filename,mimetype="image/"+_type)
                rv.headers.set('Content-Disposition',filenames)
                return rv            
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at getAASStaticWebSources Rest" + str(E))



class AASElementsJS(Resource):
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
        
    def get(self,filename):
        try:
            filenames = {'filename': filename}
            rv = send_from_directory(os.path.join(self.pyAAS.js_aaselements_repository),filename,mimetype="text/javascript")
            rv.headers.set('Content-Disposition',filenames)
            return rv 
        except Exception as E:
            self.pyAAS.serviceLogger.info("Error at getAASStaticWebSources Rest" + str(E))

        drv_rst_app.config['JS_REPOSITORY'] = self.pyaas.js_repository
        drv_rst_app.config['CSS_REPOSITORY'] = self.pyaas.css_repository
        drv_rst_app.config['IMG_REPOSITORY'] = self.pyaas.img_repository
        
