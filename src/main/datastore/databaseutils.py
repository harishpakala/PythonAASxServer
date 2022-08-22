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
    def __init__(self,pyAAS):
        self.pyAAS = pyAAS
        self.AASRegistryDatabase = self.pyAAS.aasConfigurer.dataBaseFile
        self.aasxDataQueue = Queue.Queue()
        self.dataFileDataQueue = Queue.Queue()
    
    def start(self): 
        self.POLL = True
        while self.POLL:
            time.sleep(0.01)
            if (self.aasxDataQueue).qsize() != 0:
                obThread = threading.Thread(target=self.saveToAASXFile, args=(self.getaasxDataMessage(),))     
                obThread.start()
            if (self.dataFileDataQueue).qsize() != 0:
                ibThread = threading.Thread(target=self.savetoDataBaseFile, args=(self.getdataFileMessage(),))     
                ibThread.start()

    def getaasxDataMessage(self):
        return self.aasxDataQueue.get()

    def getdataFileMessage(self):
        return self.dataFileDataQueue.get()
    
    def createNewDataBaseColumn(self,colName):
        if colName in self.AASRegistryDatabase:
            return colName
        else:
            self.AASRegistryDatabase[colName] =  []
            return colName

    def updateAASDataColumn(self,aasData,mqttUpdate):
        try:
            insertResult = self.insert_one(self.col_AASX,aasData)
            if (insertResult["message"] == "failure"):
                returnMessageDict = {"message" : ["The AASX is not updated."], "status": 201}
            elif (insertResult["message"] == "success"):
                self.pyAAS.aasConfigurer.jsonData = aasData
                self.updateAASDataList()
                self.pyAAS.aasConfigurer.getStandardSubmodels()
                self.pyAAS.aasConfigurer.getAASList()
                try:
                    if (mqttUpdate == "Yes"):
                        self.pyAAS.AASendPointHandlerObjects["MQTT"].restart()
                except Exception as E:
                    self.pyAAS.serviceLogger.info("Error at dbadaptor_Custom restarting MQTT adaptors" + str(E))
                returnMessageDict = {"message" : ["The AASX is updated successfully"], "status": 200}
            else:
                returnMessageDict = {"message": ["Unexpected Internal Server Error"],"status":500}
        except Exception as E: 
            self.pyAAS.serviceLogger.info("Error at updateAASDataColumn dbadaptor_Custom" + str(E))
            returnMessageDict = {"message": ["Unexpected Internal Server Error"+str(E)],"status":500}
        return returnMessageDict
        
    def deleteUpdateAASXColumn(self,aasData,note,mqttUpdate):
        deleteResponse = self.deleteAASDataColumn()
        if (deleteResponse["status"] == 200):
            updateResponse = self.updateAASDataColumn(aasData,mqttUpdate)
            if (updateResponse["status"] == 200):
                returnMessageDict = {"message" : [note+" updated successfully"], "status": 200}
            elif (updateResponse["status"] == 201):
                returnMessageDict = {"message" : [note+" is not updated"], "status": 200}
            else:
                returnMessageDict = {"message": ["Unexpected Internal Server Error"],"status":500}    
        else:
            returnMessageDict = {"message": ["Unexpected Internal Server Error"],"status":500}
        return returnMessageDict  
    
    def checkforExistenceofColumn(self,colName):
        if colName in self.AASRegistryDatabase:
            if self.AASRegistryDatabase[colName] == []:
                return "empty column"
            else:
                return "data present"
        else:
            return "column not present"
        
    def insert_one(self,colName,insertData):
        self.AASRegistryDatabase[colName].append(insertData)
        return self.saveToDatabase(self.AASRegistryDatabase,colName)

    def delete_one(self,colName):
        self.AASRegistryDatabase[colName] = []
        return self.saveToDatabase(self.AASRegistryDatabase,colName)   
    
    def find(self,colName,query):
        try:
            databaseColumn =  self.AASRegistryDatabase[colName]
            
            if "$or" in query:
                queryTerms = query["$or"]
                for databaseRow in databaseColumn:
                    for queryTerm in queryTerms:
                        for key in queryTerm:
                            if ( queryTerm[key] == databaseRow[key] and queryTerm[key] != ""):
                                return {"data" :databaseRow, "message": "success"}
                return {"data":"Not found","message":"failure"}
            
            elif "$and" in query:
                queryTerms = query["$and"]
                checkLength = len(queryTerms)
                for databaseRow in databaseColumn:
                    i = 0
                    for queryTerm in queryTerms:
                        for key in queryTerm:
                            if (queryTerm[key] ==  databaseRow[key] and queryTerm[key] != ""):
                                i = i + 1
                    if (i == checkLength):
                        return {"data" :databaseRow, "message": "success"}            
            elif len(query.keys()) == 0:
                if (len(databaseColumn) == 0):
                    return {"data":"Not found","message":"failure"}
                else:
                    return {"message":"success","data":databaseColumn}
            
            else:
                return {"data":"Not found","message":"failure"}
        except Exception as E:
            return {"data":"Not found","message":"error"}  

    def remove(self,colName,query):
        try:
            databaseColumn =  self.AASRegistryDatabase[colName]
            if "$or" in query:
                queryTerms = query["$or"]
                i = 0 
                for databaseRow in databaseColumn:
                    for queryTerm in queryTerms:
                        for key in queryTerm:
                            if (queryTerm[key] == databaseRow[key]):
                                del self.AASRegistryDatabase[colName][i]
                                self.saveToDatabase(self.AASRegistryDatabase,"messages")
                                return { "message": "success","index":i}
                    i = i + 1
                return {"message":"failure","data":"error"}
            
            if "$and" in query:
                queryTerms = query["$and"]
                checkLength = len(queryTerms)
                k = 0
                for databaseRow in databaseColumn:
                    i = 0
                    for queryTerm in queryTerms:
                        for key in queryTerm:
                            if (queryTerm[key] == databaseRow[key]):
                                i = i + 1
                    k = k + 1
                if (k == checkLength):
                        del self.AASRegistryDatabase[colName][i]
                        self.saveToDatabase(self.AASRegistryDatabase)
                        return {"message": "success","index":i}
                return {"message":"failure","data":"error"}    
        except Exception as E:
            print(str(E))
            return {"message":"error","data":"error"}        
    
    def dataCount(self,colName):
        return len(self.AASRegistryDatabase[colName])

    def saveToAASXFile(self,dataC):
        with open(os.path.join(self.pyAAS.repository,self.pyAAS.aasConfigurer.baseFile), 'w', encoding='utf-8') as databaseFile1:
            json.dump(dataC, databaseFile1, ensure_ascii=False, indent=4)
    
    def savetoDataBaseFile(self,dataJ):
        with open(os.path.join(self.pyAAS.dataRepository,"database.json"), 'w', encoding='utf-8') as databaseFile2:
            json.dump(dataJ, databaseFile2, ensure_ascii=False, indent=4)

    def saveToDatabase(self,dataJ,colName):
        try:
            if colName == "AASX":
                dataC = {"Test":"123"}
                if len(dataJ["AASX"]) != 0 :
                    dataC = dataJ["AASX"][0]
                    self.aasxDataQueue.put(dataC)                
            self.dataFileDataQueue.put(dataJ)
            return {"message":"success"}
        except Exception as E: 
            self.pyAAS.serviceLogger.info("Error at saveToDatabase"+ str(E))
            return {"message":"failure"}
    