"""
Copyright (c) 2023 Otto-von-Guericke-Universitaet Magdeburg, Lehrstuhl Integrierte Automation
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
"""

try:
    from utils.utils import ExecuteDBModifier, SubscriptionMessage, HistoryObject
except ImportError:
    from src.main.utils.utils import ExecuteDBModifier, SubscriptionMessage, HistoryObject

from datetime import datetime
import time


def function(td_property,asset_access_handlers) -> None:
    """

    """
    access_uri = td_property.hrefs
    update_frequency = int(td_property.update_frequency)
    aas_element = td_property.update_frequency.aasELement
    endpoint_type = ""
    if access_uri[0:8] == "opc.tcp:":
        endpoint_type = "OPCUA"
    elif access_uri[0:4] == "http":
        endpoint_type = "http"
    elif access_uri[0:4] == "https":
        endpoint_type = "https"
    else:
        pass

    while True:
        time.sleep(update_frequency)
        if endpoint_type == "OPCUA":
            new_value = asset_access_handlers["OPCUA"].read(access_uri)
            while not td_property.elem_lock:
                td_property.elem_lock = True
                _dt = datetime.now()
                _ho = HistoryObject(aas_element["value"], _dt)
                td_property.addhistoryElement(_ho)
                td_property.aasELement["value"] = new_value
                td_property.elem_lock = False
                break
                
        elif endpoint_type == "http":
            request_type = td_property.requestType
            if request_type == "get":
                _referenceId = td_property._referenceId
                new_value = str(asset_access_handlers["RESTAPI"].getData(access_uri))
                if new_value == "error":
                    pass
                else:
                    while not td_property.elem_lock:
                        td_property.elem_lock = True
                        _dt = datetime.now()
                        _ho = HistoryObject(aas_element["value"], _dt)
                        td_property.addhistoryElement(_ho)
                        td_property.aasELement["value"] = new_value
                        td_property.elem_lock = False
                        break  
                      
                '''
                if status:
                    aasHashObject = pyaas.aasHashDict.__getHashEntry__(_referenceId)
                    if len(aasHashObject.subscribers) > 0 :
                        subForward = SubscriptionMessage(_referenceId,"dd",dataElement["modelType"]["name"],
                        aasHashObject.subscribers,dataElement)
                        subForward.subscriptiondata = dataElement["value"]
                        pyaas.listnerSockets["AAS_PUBSUB"].subscription_forward_messages.put(subForward)
    
            '''
