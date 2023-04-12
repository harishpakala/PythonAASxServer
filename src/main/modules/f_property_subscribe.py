"""
Copyright (c) 2023 Otto-von-Guericke-Universitaet Magdeburg, Lehrstuhl Integrierte Automation
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
"""

try:
    from assetaccessadapters.io_aas import AASPubSubHandler
except ImportError:
    from main.assetaccessadapters.io_aas import AASPubSubHandler
try:
    from assetaccessadapters.io_opcua import AssetOPCUAEndPointSubscription
except ImportError:
    from main.assetaccessadapters.io_opcua import AssetOPCUAEndPointSubscription


def function(td_property,asset_access_handlers):
    access_uri = td_property.href
    if access_uri[0:8] == "opc.tcp:":
        handler = AssetOPCUAEndPointSubscription(td_property)
        asset_access_handlers["OPCUA"].subscribe(access_uri, handler)