"""
Copyright (c) 2023 Otto-von-Guericke-Universitaet Magdeburg, Lehrstuhl Integrierte Automation
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
"""

from importlib import import_module
import copy
import logging
import os
import platform
import sys
import threading
import time

from dotenv import load_dotenv
from dotenv.main import find_dotenv

try:
    from schedulers.propertiesScheduler import Scheduler
except ImportError:
    from src.main.schedulers.propertiesScheduler import Scheduler

try:
    from datastore.datamanager import DataManager
except ImportError:
    from src.main.datastore.datamanager import DataManager

try:
    from datastore.databaseutils import AAS_Database_UtilServer
except ImportError:
    from src.main.datastore.databaseutils import AAS_Database_UtilServer

# try:
#     from pubsub.pubsubmanager import PubSubManager
# except ImportError:
#     from main.pubsub.pubsubmanager import PubSubManager

try:
    from handlers.messagehandler import MessageHandler
except ImportError:
    from src.main.handlers.messagehandler import MessageHandler

try:
    from config.aasxconfig import ConfigParser
except ImportError:
    from src.main.config.aasxconfig import ConfigParser

try:
    from datastore.databaseserver import AAS_Database_Server
except ImportError:
    from src.main.datastore.databaseserver import AAS_Database_Server

try:
    from utils.aaslog import ServiceLogHandler, LogList
except ImportError:
    from src.main.utils.aaslog import ServiceLogHandler, LogList

try:
    from utils.utils import HashDict, SecurityAccess
except ImportError:
    from src.main.utils.utils import HashDict, SecurityAccess


class PyAASxServer:
    def __init__(self):
        self.AASendPointHandlerObjects = None
        self.aasConfigurer = None
        self.exDomain = None
        self.port = None
        self.extHost = None
        self.scheduler = None
        self.io_adapters = None
        self.registryAPI = ""
        self.listeners_config = dict()
        
        self.aasHashDict = HashDict()
        
        self.submodelHashDict = HashDict()
        self.cdHashDict = HashDict()
        self.converseHashDict = HashDict()
        self.cfpHashDict = HashDict()
        self.aasShellHashDict = HashDict()
        self.assetHashDict = HashDict()
        
        self.listenerSockets = dict()

        self.available_skills = dict()

        self.reset()
        self.end_point_modules = {}
        self.AASendPointHandles = {}
        self.asset_access_handlers = {}
        
        self.commList = []  # List of communication drivers
        self.msgHandler = MessageHandler(self)
        self.skillInstanceDictAASId = {}
        self.platform = platform.system()
        self.base_dir = os.path.dirname(os.path.realpath(__file__))

        self.lia_env_variable = {}
        self.conversationInteractionList = []
        
        self.heartBeatHandlerList = set()

        self.aasContentData = {}
        self.AASData = []
        self.tdProperties = {}
        self.tdPropertiesList = {}

        if self.platform == "Windows":
            self.script_dir = self.base_dir.split("src\main")[0]
        elif self.platform == "Linux":
            self.script_dir = self.base_dir + "/../../"

        self.src_repository = os.path.join(self.script_dir, "src/main")
        self.repository = os.path.join(self.script_dir, "config")
        self.dataRepository = os.path.join(self.script_dir, "data")
        self.template_repository = os.path.join(self.script_dir, "config/templates")
        self.downlaod_repository = os.path.join(self.script_dir, "config")

        self.img_repository = os.path.join(self.script_dir, "data/web/images")
        self.js_repository = os.path.join(self.script_dir, "data/web/js")
        self.js_aaselements_repository = os.path.join(self.script_dir, "data/web/js/aaselements")
        self.css_repository = os.path.join(self.script_dir, "data/web/css")

        self.src_skills_repository = os.path.join(self.src_repository, "skills")

        self.dba = None
        self.derAuthCert = None
        
        self.AASXupdate = False
        self.conversationUpdate = False
        
    def reset(self):
        self.io_adapters = {}
        self.AASendPointHandles = {}
        self.scheduler = None

    def reconfigure(self):
        self.stop()
        self.reset()
        self.configure()
        self.start()

    # Configure Service Entities

    def configure_logger(self) -> None:
        try:
            self.ServiceLogList = LogList()
            self.ServiceLogList.setMaxSize(maxSize=200)

            self.serviceLogger = logging.getLogger(
                str(self.__class__.__name__) + " Service Instance"
            )
            self.serviceLogger.setLevel(logging.DEBUG)

            self.commandLogger_handler = logging.StreamHandler()
            self.commandLogger_handler.setLevel(logging.DEBUG)

            self.fileLogger_Handler = logging.FileHandler(
                self.base_dir + "/logs/LIAPyAAS.LOG"
            )
            self.fileLogger_Handler.setLevel(logging.DEBUG)

            self.listHandler_Handler = ServiceLogHandler(self.ServiceLogList)
            self.listHandler_Handler.setLevel(logging.DEBUG)

            self.Handler_format = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%m/%d/%Y %I:%M:%S %p",
            )

            self.commandLogger_handler.setFormatter(self.Handler_format)
            self.listHandler_Handler.setFormatter(self.Handler_format)
            self.fileLogger_Handler.setFormatter(self.Handler_format)

            self.serviceLogger.addHandler(self.commandLogger_handler)
            self.serviceLogger.addHandler(self.listHandler_Handler)
            self.serviceLogger.addHandler(self.fileLogger_Handler)

            self.serviceLogger.info("The service Logger is Configured.")

        except Exception as E:
            self.serviceLogger.info("Error configuring the Logger." + str(E))
            self.shutDown()

    def set_external_variables(self, environ) -> bool:
        """

        """
        try:
            for env_variable in environ.keys():
                if env_variable.split("_")[0] == "LIA":
                    self.lia_env_variable[env_variable] = os.environ[env_variable]
        except Exception as E:
            self.serviceLogger.info("Error at setExternalVariables" + str(E))
            return False
        return True

    def configure_external_variables(self) -> None:
        """
        """
        try:
            load_dotenv(find_dotenv())
            if self.set_external_variables(os.environ):
                self.extHost = self.lia_env_variable["LIA_AAS_RESTAPI_DOMAIN_EXTERN"]
                self.port = self.lia_env_variable["LIA_AAS_RESTAPI_PORT_INTERN"]
                if  self.pyaas.lia_env_variable["LIA_SECURITY_ENABLED"] == "Y":
                    self.exDomain = "https://" + self.extHost + ":" + self.port + "/"
                else:
                    self.exDomain = "http://" + self.extHost + ":" + self.port + "/"
                self.serviceLogger.info("External Variables are configured.")
            else:
                self.serviceLogger.info("Error configuring the external variables.")
                self.shutDown()
        except Exception as E:
            self.serviceLogger.info(
                "Error configuring the external variables. " + str(E)
            )

    def configure_aas_configure_parser(self) -> None:
        """
        """
        try:
            packageFile = self.lia_env_variable["LIA_AAS_PACKAGE"]
            self.aasConfigurer = ConfigParser(self, packageFile)
            if self.aasConfigurer.reposStatus:
                pass
            else:
                self.serviceLogger.info("Error configuring the AASX parser.")
                self.shutDown()
        except Exception as E:
            self.serviceLogger.info("Error configuring the AASX parser." + str(E))
            self.shutDown()

    def configure_data_adaptor(self) -> None:
        try:
            self.dba = AAS_Database_Server(self)
            self.utilsServer = AAS_Database_UtilServer(self)
            if not self.dba.dbServerStatus:
                self.serviceLogger.info(
                    "Error while initializing the Database server. "
                )
                self.shutDown()
        except Exception as E:
            self.serviceLogger.info(
                "Error while configuring the Database Server. " + str(E)
            )
            self.shutDown()

    def configure_data_manager(self) -> None:
        try:
            self.dataManager = DataManager(self)
        except Exception as E:
            self.serviceLogger.info(
                "Error while configuring the Database manager. " + str(E)
            )
            self.shutDown()

    def configure_end_points(self) -> None:
        try:
            aasEndPoints = self.aasConfigurer.getAASEndPoints()
            for endPoint in aasEndPoints:
                name = endPoint["Name"]
                module = endPoint["Module"]
                if module not in sys.modules:
                    self.end_point_modules[module] = import_module(
                        "aasendpointhandlers" + module
                    )

                endPoint0 = self.end_point_modules[module].AASEndPointHandler(
                    self, self.msgHandler
                )
                self.AASendPointHandles[name] = endPoint0

                endPoint0.configure()

            self.serviceLogger.info("The AAS I40 End Points are configured")
        except Exception as E:
            self.serviceLogger.info("Error configuring the EndPoints. " + str(E))
            self.shutDown()
    
    def configure_asset_end_points_by_id(self,_uuid,aasIdentifier) -> None:
        """
        """
        try:
            _submodel,status = self.aasConfigurer.retrieve_submodel_semantic_id(aasIdentifier,"https://www.w3.org/2019/wot/td#Thing")
            if status :
                shellObject = self.aasShellHashDict.__getHashEntry__(_uuid)
                shellObject.asset_interface_description = self.aasConfigurer.get_asset_interface_description(_submodel,aasIdentifier,_uuid) 
        except Exception as E:
            self.serviceLogger.info(
                "Error configuring the Asset end point. " + str(E)
            )
            self.shutDown()
            
    def configure_asset_end_points(self) -> None:
        """
        """
        try:
            for _uid in self.aasShellHashDict._getKeys():
                self.configure_asset_end_points_by_id(_uid,self.aasShellHashDict.__getHashEntry__(_uid).aasELement["id"])
        except Exception as E:
            self.serviceLogger.info(
                "Error configuring the Asset end pointss. " + str(E)
            )
            self.shutDown()
            
    def configure_asset_access_adaptors(self) -> None:
        try:
            # configure the IOAdapters
            assetAccessEndPoints = self.aasConfigurer.getAssetAccessEndPoints()
            for key in assetAccessEndPoints.keys():
                module = assetAccessEndPoints[key]
                if module not in sys.modules:
                    self.assetmodule = import_module("assetaccessadapters" + module)
                    endPoint0 = self.assetmodule.AsssetEndPointHandler(self)
                    self.asset_access_handlers[key] = endPoint0

            self.serviceLogger.info("The Asset Access points are configured")
        except Exception as E:
            self.serviceLogger.info(
                "Error configuring the Asset access points. " + str(E)
            )
            self.shutDown()

    def configure_register_sKill(self) -> None:
        try:
            registerModule = import_module("." + "Register", package="skills")
            registerBaseCLass = getattr(registerModule, "Register")
            return registerBaseCLass()
        except Exception as E:
            self.serviceLogger.info("Error configuring the register skill " + str(E))

    def configure_pm_skill(self) -> None:
        try:
            pManagerModule = import_module("." + "ProductionManager", package="skills")
            pmBaseCLass = getattr(pManagerModule, "ProductionManager")
            return pmBaseCLass()
        except Exception as E:
            self.serviceLogger.info(
                "Error configuring the production management skill. " + str(E)
            )
            sys.exit(0)

    def configure_available_skills(self) -> None:
        self.available_skills = self.aasConfigurer.get_available_skills()
        
    def configure_skill_by_id(self,_uid,skill_name):
        try:
            shellObject = self.aasShellHashDict.__getHashEntry__(_uid)
            skillDetails = copy.deepcopy(self.available_skills[skill_name])
            skill_module = import_module("." + skill_name, package="skills")
            skill_base_class = getattr(skill_module, skill_name)
            skillDetails["SkillHandler"] = skill_base_class()
            skillDetails["SkillHandler"].set_base(self)
            shellObject.add_skill(skill_name, skillDetails)
        except Exception as e:
            self.serviceLogger.info("Error configuring skill @configure_skill_by_id " + str(e))
    
    def configure_skills_by_id(self,_uid,aasId) -> None:
        try:
            skill_List = self.aasConfigurer.get_skills(aasId)
            for skill_name in skill_List:
                self.configure_skill_by_id(_uid,skill_name)
            
            shellObject = self.aasShellHashDict.__getHashEntry__(_uid)
                
            pm_skillDetails = copy.deepcopy(self.available_skills["ProductionManager"])
            pm_skillDetails["SkillHandler"] = self.configure_pm_skill()
            pm_skillDetails["SkillHandler"].set_base(self)
            shellObject.add_skill("ProductionManager", pm_skillDetails)

            rg_skillDetails = copy.deepcopy(self.available_skills["Register"])
            rg_skillDetails["SkillHandler"] = self.configure_register_sKill()
            rg_skillDetails["SkillHandler"].set_base(self)
            shellObject.add_skill("Register", rg_skillDetails)
            
            
        except Exception as E:
            self.serviceLogger.info("Error configuring skills @configure_skills_by_id " + str(E))

    def configure_skills(self) -> None:
        try:
            for _uid in self.aasShellHashDict._getKeys():
                self.configure_skills_by_id(_uid,self.aasShellHashDict.__getHashEntry__(_uid).aasELement["id"])
        except Exception as E:
            self.serviceLogger.info("Error configuring skills. " + str(E))
        

        
    def configureSecurityMeasure(self) -> None:
        self.pySA = SecurityAccess(self)

    def getSubmodelPropertyListDict(self, aasIdentifier) -> None:
        self.submodelPropertyListDict = self.aasConfigurer.getSubmodelPropertyListDict(
            aasIdentifier
        )
        return self.submodelPropertyListDict

    def getSubmodelList(self, aasIdentifier) -> None:
        self.submodelList = self.aasConfigurer.getSubmodelPropertyList(aasIdentifier)
        return self.submodelList

    # Start Service Entities ################
    # Start Service Entities ################

    def start_end_points(self) -> None:
        try:
            self.AASendPointHandlerObjects = {}
            for module_name, endPointHandler in self.AASendPointHandles.items():
                endPointHandler.start()
                self.AASendPointHandlerObjects[module_name] = endPointHandler

            self.serviceLogger.info("The AAS end Points are Started")
        except Exception as E:
            self.serviceLogger.info(
                "Error while starting the AAS End points. " + str(E)
            )

    def start_asset_end_points(self) -> None:
        self.serviceLogger.info("The Asset end Points are Started")

    def start_msg_handler_thread(self) -> None:
        try:
            msgHandlerThread = threading.Thread(
                target=self.msgHandler.start,
                name="msgHandler",
                args=(
                    self.skillInstanceDictAASId,
                    self.AASendPointHandlerObjects,
                ),
            )
            msgHandlerThread.start()

            self.serviceLogger.info("The message handler started")
        except Exception as E:
            self.serviceLogger.info(
                "Error while starting the message handler thread. " + str(E)
            )

    def start_scheduler(self) -> None:
        try:
            self.scheduler.start()
            self.serviceLogger.info("The Job Scheduler is Started")
        except Exception as E:
            self.serviceLogger.info(
                "Error while starting the scheduler thread. " + str(E)
            )

    def start_skill_by_name(self,_uid,skill_name) -> None:
        try:
            shellObject = self.aasShellHashDict.__getHashEntry__(_uid)
            skill = shellObject.skills[skill_name]
            skill_thread = threading.Thread(
                        target=skill["SkillHandler"]._start,
                        args=(
                            self.msgHandler,
                            shellObject,_uid,),
                        name=str(_uid) + skill_name
                    )
            skill_thread.start()
        
        except Exception as e:
            self.serviceLogger.info("Error while starting the skills. " + str(e))

    def start_skills_by_id(self,_uid) -> None:
        try:
            shellObject = self.aasShellHashDict.__getHashEntry__(_uid)
            for skill_name,skill in shellObject.skills.items():
                threading.Thread(
                        target=skill["SkillHandler"]._start,
                        args=(
                            self.msgHandler,
                            shellObject,_uid,),
                        name=str(_uid) + skill_name
                    ).start()
        
        except Exception as e:
            self.serviceLogger.info("Error while starting the skills. " + str(e))

    def start_skills(self) -> None:
        try:
            # Start remaining skills that are part of the skill instance list
            for _uid in self.aasShellHashDict._getKeys():
                self.start_skills_by_id(_uid)
            self.serviceLogger.info("The Skills are Started")
        except Exception as E:
            self.serviceLogger.info("Error while starting the skills. " + str(E))

    def start_data_manager(self) -> None:
        try:
            dataManagerThread = threading.Thread(
                target=self.dataManager.start, args=(), name="DataManager"
            )
            dataManagerThread.start()
            dataUtilsServer = threading.Thread(
                target=self.utilsServer.start, args=(), name="Data Utils Server"
            )
            dataUtilsServer.start()
            self.serviceLogger.info("The message handler started")
        except Exception as E:
            self.serviceLogger.info(
                "Error while starting the DataManager thread. " + str(E)
            )

    def startPubsubListners(self) -> None:
        try:
            # self.pubsubManager.start_listners()
            self.serviceLogger.info("PubSub listners are sucessfully started")
        except Exception as E:
            self.serviceLogger.info(
                "Error while starting the pubsub listners. " + str(E)
            )

    def startHeartBeatHandler(self) -> None:
        try:
            heartBeatThread = threading.Thread(target=self.msgHandler.trigggerHeartBeat)
            heartBeatThread.start()
        except Exception as E:
            self.serviceLogger.info(
                "Error while starting the HeartBeat handler thread. " + str(E)
            )

    def configure(self) -> None:

        # configure Service Logger
        self.configure_logger()
        self.serviceLogger.info("Configuring the Service Entities.")

        self.configure_external_variables()
        self.serviceLogger.info("Configuration Parameters are Set.")

        self.configure_aas_configure_parser()
        self.configure_data_adaptor()

        self.configure_data_manager()

        # config PubSubManager
        #         if not self.aasConfigurer.extract_pubsublistner_config():
        #             self.serviceLogger.info(
        #                 "Error extracting the pubsub listner configuration."
        #             )
        #             self.shutDown()
        #
        #         self.pubsubManager = PubSubManager(self)
        #         if not self.pubsubManager.configure_listner():
        #             self.serviceLogger.info("Error configuring the listners. ")
        #             self.shutDown()
        #
        #         if not self.pubsubManager.configure_listner_sockets():
        #             self.serviceLogger.info("Error configuring the listner sockets. ")
        #             self.shutDown()

        # configure EndPoints
        self.configure_end_points()
        # configure IA Adaptors
        self.configure_asset_end_points()
        self.configure_asset_access_adaptors()
        # configure Skill

        self.configure_available_skills()
        self.configure_skills()
        # configure the scheduler
        self.scheduler = Scheduler(self)
        self.scheduler.configure()

        self.configureSecurityMeasure()

    def start(self) -> None:

        self.serviceLogger.info("Starting the Service Entities")

        self.cdrivers = {}
        self.cdrv_mqtt = None
        # start the Data Manager
        self.start_data_manager()
        # start the pubsub listners
        self.startPubsubListners()
        # start the communication drivers
        self.start_end_points()
        # start the message handler thread
        self.start_msg_handler_thread()
        # start the scheduler
        self.start_scheduler()
        # start the skills
        self.start_skills()
        # heartBeatHandler
        self.startHeartBeatHandler()

    def stop(self) -> None:
        self.scheduler.stop()
        for module_name, cdrv in self.AASendPointHandles.items():
            cdrv.stop()

    def shutDown(self) -> None:
        self.serviceLogger.info("The Service Logger is shutting down.")
        os._exit(0)


if __name__ == "__main__":
    pyAAS = PyAASxServer()
    pyAAS.configure()
    pyAAS.start()
    print("Press Ctrl+{0} to exit".format("C"))
    try:
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        pyAAS.stop()
