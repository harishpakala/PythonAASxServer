"""
Copyright (c) 2023 Otto-von-Guericke-Universitaet Magdeburg, Lehrstuhl Integrierte Automation
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
"""
import asyncio
try:
    from assetaccessadapters.io_opcua import OPCUASubscriptionHandler,OPCUASubscription
except ImportError:
    from main.assetaccessadapters.io_opcua import OPCUASubscriptionHandler,OPCUASubscription


def function(td_property):
    access_uri = td_property.href
    
    if access_uri[0:8] == "opc.tcp:":
        _handler = OPCUASubscriptionHandler()
        _handler.set_property(td_property.elemObject)
        opcua_sub = OPCUASubscription(access_uri,_handler)
        asyncio.run(opcua_sub.subscribe())
    
    if access_uri[0:4] == "http":
        pass