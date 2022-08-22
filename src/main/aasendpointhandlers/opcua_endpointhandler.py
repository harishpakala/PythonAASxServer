'''
Copyright (c) 2021-2022 OVGU LIA
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
'''

try:
    from abstract.endpointhandler import AASEndPointHandler
except ImportError:
    from main.abstract.endpointhandler import AASEndPointHandler


class AASEndPointHandler(AASEndPointHandler):

    def __init__(self, pyAAS, ipaddressComdrv, portComdrv, msgHandler):
        super(AASEndPointHandler, self).__init__(pyAAS, ipaddressComdrv, portComdrv, msgHandler)
        self.msgHandler = msgHandler

        
    def configure(self):
        self.ipaddressComdrv = self.pyAAS.lia_env_variable["LIA_AAS_OPCUA_HOST"]
        self.portComdrv = int(self.pyAAS.lia_env_variable["LIA_AAS_OPCUA_PORT"])

    def update(self, channel):
        pass
            
    def start(self):     
        pass


    def stop(self):
        pass
    
    def dispatchMessage(self, send_Message): 
        pass
            
    def retrieveMessage(self, x):
        pass
        
            
