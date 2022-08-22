'''
Created on 24 Oct 2021

@author: pakala
'''
try:
    from utils.utils import ExecuteDBModifier,SubscriptionMessage
except ImportError:
    from main.utils.utils import ExecuteDBModifier,SubscriptionMessage
import uuid
from datetime import datetime


import random
def createNewQualifier(newValue):
    return {
              "type": "value",
              "valueType": "",
              "value": newValue,
              "modelType": {
                "name": "Qualifier"
              }
            }

def createRandomData(propertyName):
    peak_chance = random.randint(0, 100)
    
    if peak_chance < 10:  # 10% chance for under-value
        if (propertyName == "Processvalue"):
            return float(random.randint(2309, 2409) / 100)
        if (propertyName == "Temperature"):
            return float(random.randint(6889, 6989) / 100)
        if (propertyName == "Setpoint"):
            return float(random.randint(7889, 7989) / 100)
    elif peak_chance > 90:  # 10% chance for peak-value
        if (propertyName == "Processvalue"):
            return float(random.randint(2415, 2515) / 100)
        if (propertyName == "Temperature"):
            return float(random.randint(7045, 7145) / 100)
        if (propertyName == "Setpoint"):
            return float(random.randint(7889, 7989) / 100)
    else:
        if (propertyName == "Processvalue"):
            return float(random.randint(2409, 2415) / 100)
        if (propertyName == "Temperature"):
            return float(random.randint(6989, 7045) / 100)
        if (propertyName == "Setpoint"):
            return float(random.randint(7889, 7989) / 100)

def function(pyAAS, *args):
    params = args[0]
    valueList = params['value']
    labelList = params['label']
    accessURI = params["href"]
    dataElement = params["dataElement"].aasELement
    if (accessURI[0:8] == "opc.tcp:"):
        newValue = pyAAS.assetaccessEndpointHandlers["OPCUA"].read(accessURI)
        if newValue == "error":
            pass
        else:
            del valueList[0]
            del labelList[0]
            labelList.append(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            valueList.append(newValue)
            pyAAS.tdPropertiesList[params["key"]]["value"] = valueList
            pyAAS.tdPropertiesList[params["key"]]["label"] = labelList

    elif (accessURI[0:4] == "http"):
        requestType = params["requestType"] 
        if requestType == "get":
            _referenceId = params["_referenceId"]
            newValue = str(pyAAS.AASendPointHandlerObjects["RESTAPI"].getData(accessURI))
            dataElement["value"] = newValue
            edm = ExecuteDBModifier(pyAAS)
            instanceId = str(datetime.now()) +"."+params["propertyName"]
            msg,status = edm.executeModifer({"data":{"elemData":dataElement,
                                            "_idShortpath" : _referenceId,
                                            },"method":"putSubmodelElem","instanceId" :instanceId })
            if status:
                aasHashObject = pyAAS.aasHashDict.__getHashEntry__(_referenceId)
                if len(aasHashObject.subscribers) > 0 :
                    subForword = SubscriptionMessage(_referenceId,"dd",dataElement["modelType"]["name"],aasHashObject.subscribers,dataElement)
                    subForword.subscriptiondata = dataElement["value"]
                    pyAAS.listnerSockets["AAS_PUBSUB"].subscription_forward_messages.put(subForword)

        
                    