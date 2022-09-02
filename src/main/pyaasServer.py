'''
Copyright (c) 2021-2022 OVGU LIA
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
'''

import sys
import time
import threading
import logging
import os
import platform

from dotenv import load_dotenv
from importlib import import_module
from dotenv.main import find_dotenv

try:
    from schedulers.propertiesScheduler import Scheduler
except ImportError:
    from  main.schedulers.propertiesScheduler import Scheduler

try:
    from datastore.datamanager import DataManager
except ImportError:
    from main.datastore.datamanager import DataManager

try:
    from datastore.databaseutils import AAS_Database_UtilServer
except ImportError:
    from main.datastore.databaseutils import AAS_Database_UtilServer

try:
    from pubsub.pubsubmanager import PubSubManager
except ImportError:
    from main.pubsub.pubsubmanager import PubSubManager

try:
    from handlers.messagehandler import MessageHandler
except ImportError:
    from main.handlers.messagehandler import MessageHandler
    
try:
    from config.aasxconfig import ConfigParser
except ImportError:
    from main.config.aasxconfig  import ConfigParser

try:
    from datastore.databaseserver import AAS_Database_Server
except ImportError:
    from main.datastore.databaseserver import AAS_Database_Server 

try:
    from utils.aaslog import serviceLogHandler,LogList
except ImportError:
    from main.utils.aaslog import serviceLogHandler,LogList

try:
    from utils.utils import HashDict
except ImportError:
    from main.utils.utils import HashDict

class PyAASServer(object):
    
    def __init__(self):
        self.AASID = "PyAASServer"
        self.platform = platform.system()
        self.base_dir = os.path.dirname(os.path.realpath(__file__))
        self.lia_env_variable = {}
        
        self.initDataAccessPaths()
        
        self.aasEndPointHandlers = {}
        self.assetaccessHandlers = {}
        self.skillInstanceDictbyAASId = {}

        self.skilllogListDict = {}
        self.dba = None
    
    
    def initDataAccessVariables(self):
        if (self.platform == "Windows"):
            self.script_dir = (self.base_dir).split("src\main")[0]
        elif (self.platform == "Linux"):
            self.script_dir = (self.base_dir) + "/../../"
        
        self.repository = os.path.join(self.script_dir, "config") 
        self.dataRepository = os.path.join(self.script_dir, "data")
        self.template_repository = os.path.join(self.script_dir, "config/templateInfo")
        self.downlaod_repository = os.path.join(self.script_dir, "config/aasx/files")
        
        self.img_repository = os.path.join(self.script_dir, "data/static/images")
        self.js_repository = os.path.join(self.script_dir, "data/static/js")
        self.css_repository = os.path.join(self.script_dir, "data/static/css")
        
    
    ######## Configure Service Entities ##################
    
    def configureLogger(self):
        try:
            self.ServiceLogList = LogList()
            self.ServiceLogList.setMaxSize(maxSize= 200)
            
            self.serviceLogger = logging.getLogger(str(self.__class__.__name__) + ' Service Instance' )
            self.serviceLogger.setLevel(logging.DEBUG)
            
            self.commandLogger_handler = logging.StreamHandler()
            self.commandLogger_handler.setLevel(logging.DEBUG)
    
            self.fileLogger_Handler = logging.FileHandler(self.base_dir+"/logs/LIAPyAAS.LOG")
            self.fileLogger_Handler.setLevel(logging.DEBUG)
            
            self.listHandler_Handler = serviceLogHandler(self.ServiceLogList)
            self.listHandler_Handler.setLevel(logging.DEBUG)
            
            self.Handler_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%m/%d/%Y %I:%M:%S %p')
    
            self.commandLogger_handler.setFormatter(self.Handler_format)
            self.listHandler_Handler.setFormatter(self.Handler_format)
            self.fileLogger_Handler.setFormatter(self.Handler_format)
            
            self.serviceLogger.addHandler(self.commandLogger_handler)
            self.serviceLogger.addHandler(self.listHandler_Handler)
            self.serviceLogger.addHandler(self.fileLogger_Handler)
            
            self.serviceLogger.info('The service Logger is Configured.')
        
        except Exception as E:
            self.serviceLogger.info('Error configuring the Logger.'+str(E))
            self.shutDown()

    def configureLogList(self):
        try:
            for aasIndex in self.skillInstanceDictbyAASId.keys():
                skillLogs = {}
                for skill in self.skillInstanceDictbyAASId[aasIndex].keys():
                    skillLogs[skill] = LogList()
                self.skilllogListDict[aasIndex] = skillLogs
        except Exception as E:
            self.serviceLogger.info('Error configuring Log Lists. ' + str(E))    

    def setExternalVariables(self,environ):
        try:
            for env_variable in environ.keys():
                if (env_variable.split("_")[0] == "LIA"):
                    self.lia_env_variable[env_variable] = os.environ[env_variable]
        except Exception as E:
            self.serviceLogger.info('Error at setExternalVariables' + str(E))
            return False
        return True            
            
    def configureExternalVariables(self):
        try:
            load_dotenv(find_dotenv())
            if self.setExternalVariables(os.environ) :
                self.extHost = self.lia_env_variable["LIA_AAS_RESTAPI_DOMAIN_EXTERN"]
                self.port = self.lia_env_variable["LIA_AAS_RESTAPI_PORT_INTERN"]
                self.exDomain = "http://"+self.extHost+":"+self.port+"/"
                self.serviceLogger.info('External Variables are configured.')
            else :
                self.serviceLogger.info('Error configuring the external variables.')
                self.shutDown()
        except Exception as E:
            self.serviceLogger.info('Error configuring the external variables. ' + str(E))

    def configureDataStructures(self):
        self.aasHashDict = HashDict()
        self.submodelHashDict = HashDict()
        self.assetHashDict = HashDict()
        self.cdHashDict = HashDict()
        self.conversHashDict = HashDict()
        self.aasShellHashDict = HashDict()
    
    def configureWebInterfaceVariables(self):
        
        self.productionSequenceList = dict()
        self.productionStepList = dict()
        self.conversationIdList = dict()
        self.thumbNailList = dict()
        #  submodel template
        self.aasStandardSubmodelData = {}
        self.aasStandardSubmodelList = {}
        self.heartBeatHandlerList = set()
        self.skillListWeb = {}
        self.conversationInteractionList = []      
             
    def configureInternalVariables(self):
        self.configureDataStructures()
        self.configureWebInterfaceVariables
        self.aasList = dict()
        self.aasIdList = []
        self.aasIndexidShortDict = dict()
        self.aasIdentificationIdList = {}
        self.aasContentData = {}
        self.AASData = []
        self.tdProperties = {}
        self.tdPropertiesList = {}
            
    def configureAASConfigureParser(self):
        try:
            packageFile = self.lia_env_variable["LIA_AAS_PACKAGE"]
            self.aasConfigurer = ConfigParser(self,packageFile)
            if self.aasConfigurer.reposStatus:
                if (self.aasConfigurer.configureAASJsonData()):
                    self.serviceLogger.info('The AASX data is extracted and parsed')
                else:
                    self.serviceLogger.info('Error configuring the AAS Data. ')
                    self.shutDown()                
            else:
                self.serviceLogger.info('Error configuring the AASX parser.')
                self.shutDown()
        except Exception as E:
            self.serviceLogger.info('Error configuring the AASX parser.'+str(E))
            self.shutDown()

    def configureDataAdaptor(self):
        try:
            self.dba = AAS_Database_Server(self)
            self.utilsServer = AAS_Database_UtilServer(self)
            if (not self.dba.dbServerStatus):
                self.serviceLogger.info("Error while initializing the Database server. ")
                self.shutDown()
        except Exception as E:
            self.serviceLogger.info("Error while configuring the Database Server. " + str(E))
            self.shutDown()
     
    
    def configureMsgHandler(self):
        self.msgHandler = MessageHandler(self)
     
    def confiureDataManager(self):
        try:
            self.dataManager = DataManager(self)
        except Exception as E:
            self.serviceLogger.info("Error while configuring the Database manager. " + str(E))
            self.shutDown()        
 
    def configureAASEndPoints(self):
        try:
            # configure Industrie 4.0 communication drivers
            aasEndPoints = self.aasConfigurer.getAASEndPoints()
            for endPoint in aasEndPoints:
                name = endPoint["Name"]
                module = endPoint["Module"]
                if module not in sys.modules:
                    endPoint0 = import_module("aasendpointhandlers"+module).AASEndPointHandler(self,self.msgHandler)
                    self.aasEndPointHandlers[name] = endPoint0
                    endPoint0.configure()
                
            self.serviceLogger.info('The AAS I40 End Points are configured')        
        except Exception as E:
            self.serviceLogger.info('Error configuring the EndPoints. ' + str(E))

    def configureAssetAccessPoints(self):
        try:
            # configure the IOAdapters
            assetAccessEndPoints = self.aasConfigurer.getAssetAccessEndPoints()
            for key in assetAccessEndPoints.keys():
                module = assetAccessEndPoints[key]
                if module not in sys.modules:
                    self.assetmodule = import_module("assetaccessadapters"+module)
                    endPoint0 = self.assetmodule.AsssetEndPointHandler(self)
                    self.assetaccessHandlers[key] = endPoint0
            
            self.serviceLogger.info('The Asset Access points are configured')        
        except Exception as E:
            self.serviceLogger.info('Error configuring the Asset access points. ' + str(E))

    def configurePubSubManager(self):
        self.listnersConfig = dict()
        self.listnerSockets = dict()    
        if (not self.aasConfigurer.extract_pubsublistner_config()):
            self.serviceLogger.info("Error extracting the pubsub listner configuration.")
            self.shutDown()
            
        self.pubsubManager = PubSubManager(self)
        if (not self.pubsubManager.configure_listner()):
            self.serviceLogger.info("Error configuring the listners. ")
            self.shutDown()
            
        if (not self.pubsubManager.configure_listner_sockets()):
            self.serviceLogger.info("Error configuring the listner sockets. ")
            self.shutDown()

    def configureRegisterSKill(self):
        try:
            registerModule = import_module("." + "Register", package="skills")
            registerBaseCLass = getattr(registerModule, "Register")
            return registerBaseCLass(self)        
        except Exception as E:
            self.serviceLogger.info('Error configuring the register skill ' + str(E))
        
    def configurePMSkill(self):
        try:
            pManagerModule = import_module("." + "ProductionManager", package="skills")
            pmBaseCLass = getattr(pManagerModule, "ProductionManager")
            return pmBaseCLass(self)        
        except Exception as E:
            self.serviceLogger.info('Error configuring the production management skill. ' + str(E))
    
    def configureSkills(self): 
        try:
            #configure skills
            self.aasSkills = self.aasConfigurer.GetAAsxSkills()
            for aasIndex in self.aasSkills.keys():
                self.skillDetails = self.aasSkills[aasIndex]
                skillList = []
                self.skillInstanceDictbyAASId[aasIndex] =  {}
                for skill in self.skillDetails.keys():
                    skillModule = import_module("." + skill, package="skills")
                    skillBaseclass_ = getattr(skillModule, skill)
                    skillInstance = skillBaseclass_(self)
                    self.skillInstanceDictbyAASId[aasIndex][skill] = {"skillInstance":skillInstance,
                                                                      "skillDetails":self.skillDetails[skill]}
                    skillList.append(skill)
                skillList.append("Register")
                skillList.append("Production Manager")
                self.skillInstanceDictbyAASId[aasIndex]["ProductionManager"] = {"skillInstance":self.configurePMSkill(),"skillDetails":{"SkillName" : "Register","SkillService" : "Registration","InitialState" : "WaitforNewOrder","enabled" :"Y","shellIndex":aasIndex}}
                self.skillInstanceDictbyAASId[aasIndex]["Register"] = {"skillInstance":self.configureRegisterSKill(),"skillDetails":{"SkillName" : "ProductionManager","SkillService" : "Production Manager","InitialState" : "WaitforNewOrder","enabled" : "Y","shellIndex":aasIndex}}
                self.skillListWeb[aasIndex] = skillList
                self.serviceLogger.info('The skills are configured')            
        
        except Exception as E:
            self.serviceLogger.info('Error configuring skills. ' + str(E))
        
    def configureScheduler(self):
        self.scheduler = Scheduler(self)
        self.scheduler.configure()
        

    
    def configureSkillWebList(self):
        i = 0
        for skillWeb in self.skillListWeb:
            skillWeb
            #if skillWeb == "ProductionManager":
            #    del self.skillListWeb[i]
            #    break
            i = i + 1
  
    def getSubmodelPropertyListDict(self,aasIdentifier):
        self.submodelPropertyListDict = self.aasConfigurer.getSubmodelPropertyListDict(aasIdentifier)
        return self.submodelPropertyListDict
        
    def getSubmodelList(self,aasIdentifier):
        self.submodelList = self.aasConfigurer.getSubmodelPropertyList(aasIdentifier)
        return self.submodelList
    ####### Start Service Entities ################
        
    def startAASEndPoints(self):
        try:
            for endPointHandler in self.aasEndPointHandlers.values():
                endPointHandler.start()
            self.serviceLogger.info('The AAS end Points are Started')        
        except Exception as E:
            self.serviceLogger.info('Error while starting the AAS End points. '+str(E))
        
    def startAssetAccessPoints(self):
        self.serviceLogger.info('The Asset end Points are Started')
    
    def startMsgHandlerThread(self):
        try:
            msgHandlerThread = threading.Thread(target=self.msgHandler.start,name="msgHandler", args=(self.skillInstanceDictbyAASId,self.aasEndPointHandlers,))     
            msgHandlerThread.start()
        
            self.serviceLogger.info('The message handler started')            
        except Exception as E:
            self.serviceLogger.info('Error while starting the message handler thread. '+str(E))
        
    def startScheduler(self):
        try:
            self.scheduler.start()
            self.serviceLogger.info('The Job Scheduler is Started')        
        except Exception as E:
            self.serviceLogger.info('Error while starting the scheduler thread. '+str(E))

    def startSkills(self):      
        try:
            # Start remaining skills that are part of the skill instance list
            for aasIndex in self.skillInstanceDictbyAASId.keys():
                for skill in self.skillInstanceDictbyAASId[aasIndex]:
                    skillInfo = self.skillInstanceDictbyAASId[aasIndex][skill] 
                    skillInstance = skillInfo["skillInstance"]
                    skillDetails = skillInfo["skillDetails"]
                    threading.Thread(target=skillInstance.Start, args=(self.msgHandler, skillDetails,aasIndex,),name =str(aasIndex)+skill).start()
            
            self.serviceLogger.info('The Skills are Started')        
        except Exception as E:
            self.serviceLogger.info('Error while starting the skills. '+str(E))            
    
    def startDataManager(self):
        try:
            dataManagerThread = threading.Thread(target=self.dataManager.start, args=(),name="DataManager")     
            dataManagerThread.start()
            dataUtilsServer = threading.Thread(target=self.utilsServer.start, args=(),name="Data Utils Server")     
            dataUtilsServer.start()            
            self.serviceLogger.info('The message handler started')        
        except Exception as E:
            self.serviceLogger.info('Error while starting the DataManager thread. '+str(E))

    def startPubSubManager(self):
        try:
            self.pubsubManager.start_listners()
            self.serviceLogger.info('PubSub listners are sucessfully started')     
        except Exception as E:
            self.serviceLogger.info('Error while starting the pubsub listners. ' +str(E))

    def configure(self):
        
        self.commList = [] # List of communication drivers
        self.skilLList = [] # List of Skills
        self.skillInstanceList = {} # List consisting of instances of skills

        #configure Service Logger
        self.configureLogger()
        #configure Logs
        self.configureLogList()
        self.serviceLogger.info('Configuring the Service Entities.')
        #configure External Variables
        self.configureExternalVariables()
        #configure registryAPI
        self.configureInternalVariables()
        self.serviceLogger.info("Configuration Parameters are Set.")
        
        self.configureAASConfigureParser() 
        
        #configure Data Adaptor
        self.configureDataAdaptor()
        #configure message Handler
        self.configureMsgHandler()
        #configure the Data Manager
        self.confiureDataManager()
        #configure EndPoints
        self.configureAASEndPoints()
        #configure IA Adaptors
        self.configureAssetAccessPoints()
        #configure PubSubManager    
        self.configurePubSubManager()
        #configure Skills
        self.configureSkills()
        
        #configure skill web list
        self.configureSkillWebList()
        #configure submodel properties
        #self.configureSubmodelProperties()   
        # configure the scheduler
        self.configureScheduler()
        
    def start(self):
        
        self.serviceLogger.info('Starting the Service Entities')
        #start the Data Manager
        self.startDataManager()
        #start the pubsub listners
        self.startPubSubManager()       
        #start the communication drivers
        self.startAssetAccessPoints()
        #start the message handler thread
        self.startMsgHandlerThread()
        # start the scheduler
        self.startScheduler()
        #start the skills
        self.startSkills()
  
    def stop(self):
        self.scheduler.stop()
        for module_name, cdrv in self.cdrvs.items():
            cdrv.stop()
    
    def shutDown(self):
        self.serviceLogger.info("The Service Logger is shutting down.")
        os._exit(0)

if __name__ == "__main__":
    pyAAS = PyAASServer()
    pyAAS.configure()
    pyAAS.start()
    print('Press Ctrl+{0} to exit'.format('C'))
    try:
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        pyAAS.stop()

