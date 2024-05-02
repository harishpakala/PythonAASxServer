"""
Copyright (c) 2023 Otto-von-Guericke-Universitaet Magdeburg, Lehrstuhl Integrierte Automation
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
"""

try:
    from assetaccessadapters.io_http import HTTPEndPointSubscriptionHandler
except ImportError:
    from main.assetaccessadapters.io_http import HTTPEndPointSubscriptionHandler

try:
    from assetaccessadapters.io_mqtt import MQTTSubscriptionHandler
except ImportError:
    from main.assetaccessadapters.io_mqtt import MQTTSubscriptionHandler

try:
    from assetaccessadapters.io_opcua import ModBusSubscriptionHandler
except ImportError:
    from main.assetaccessadapters.io_opcua import ModBusSubscriptionHandler

try:
    from assetaccessadapters.io_opcua import OPCUASubscriptionHandler,OPCUASubscription
except ImportError:
    from main.assetaccessadapters.io_opcua import OPCUASubscriptionHandler,OPCUASubscription


class PropertyHandler:
    def __init__(self,propertyConfig):
        self.propertyConfig = propertyConfig
        self.adaptorType = ""
        
    def unpack_properties(self):
        pass
    
    def start(self):
        self.unpack_properties()
        if self.adaptorType == "HTTP" :
            pass
        elif self.adaptorType == "OPCUA" :
            pass
        elif self.adaptorType == "MQTT" :
            pass
        elif self.adaptorType == "MODBUS":
            pass
    
    def stop(self):
        pass
    
    def restart(self):
        self.stop()
        self.restart()