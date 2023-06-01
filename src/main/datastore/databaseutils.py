'''
Copyright (c) 2021-2022 Otto-von-Guericke-Universiat Magdeburg, Lehrstuhl Integrierte Automation
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
'''
import json 
import os
import time
import threading
try:
    import queue as Queue
except ImportError:
    import Queue as Queue
    
class AAS_Database_UtilServer(object):
    def __init__(self,pyaas):
        self.pyaas = pyaas
        self.AASRegistryDatabase = self.pyaas.aasConfigurer.dataBaseFile
        self.aasxDataQueue = Queue.Queue()
        self.dataFileDataQueue = Queue.Queue()
    
    def start(self): 
        self.POLL = True
        while self.POLL:
            time.sleep(1)
            self.saveToDatabase()

    def serialize_shells(self) -> list:
        """
            
        """
        shells_list = []
        try:
            for _uuid in self.pyaas.aasShellHashDict._getKeys():
                shells_list.append(self.pyaas.aasShellHashDict.__getHashEntry__(_uuid).getElement())
        except Exception as E:
            pass
        return  shells_list
    
    def serialize_submodels(self) -> list:
        """
        """
        try:
            data,status,statuscode = self.pyaas.dba.GetAllSubmodels()
            if status :
                return data
            else:
                return []
        except Exception as E:
            return []
    
    def serialize_concept_descriptions(self) -> list:
        """
        """
        concept_descriptions_list = []
        try:
            for _uuid in self.pyaas.cdHashDict._getKeys():
                concept_descriptions_list.append(self.pyaas.cdHashDict.__getHashEntry__(_uuid).getElement())
        except Exception as E:
            pass
        return  concept_descriptions_list
    
    
    def serialize_conversations(self) -> list:
        """
        """
        conversations_list = []
        try:
            for _uuid in self.pyaas.converseHashDict._getKeys():
                conversations_list.append(self.pyaas.converseHashDict.__getHashEntry__(_uuid).getElement())
        except Exception as E:
            pass
        return  conversations_list
    
    def serialize_environment(self) -> dict:
        _environment = dict()
        try:
            _environment["assetAdministrationShells"] = self.serialize_shells()
            _environment["submodels"] =  self.serialize_submodels()
            _environment["conceptDescriptions"] = self.serialize_concept_descriptions() 
        
        except Exception as E:
            pass
        return _environment
            
    def saveToAASXFile(self,dataC) -> bool:
        """
        """
        try:
            with open(os.path.join(self.pyaas.repository,self.pyaas.aasConfigurer.base_file), 'w', encoding='utf-8') as databaseFile1:
                json.dump(dataC, databaseFile1, ensure_ascii=False, indent=4)
            return True
        except Exception as E:
            return  False
         
    def savetoDataBaseFile(self,dataJ) -> bool:
        try:
            with open(os.path.join(self.pyaas.dataRepository,"database.json"), 'w', encoding='utf-8') as databaseFile2:
                json.dump(dataJ, databaseFile2, ensure_ascii=False, indent=4)            
            return True
        except Exception as E:
            return False
        
    def savetoMongoDB(self,dataJ) -> bool:
        """
        """
        pass
    
    def saveToDatabase(self) -> bool:
        try:
            if (self.pyaas.AASXupdate):
                if len(list((self.pyaas.dataManager.outBoundProcessingDict.keys()))) == 0:
                    environment_data = self.serialize_environment()
                    self.saveToAASXFile(environment_data)
                    self.pyaas.AASXupdate = False
            if (self.pyaas.conversationUpdate):
                pass
                #conversations_data = self.deserialize_conversations()
                #self.savetoDataBaseFile(conversations_data)
            return True
        except Exception as E: 
            self.pyaas.serviceLogger.info("Error at saveToDatabase"+ str(E))
            return False
    