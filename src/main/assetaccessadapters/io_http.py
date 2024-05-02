'''
Copyright (c) 2021-2022 OVGU LIA
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
'''
from datetime import datetime
import time
import requests

try:
    from utils.utils import HistoryObject
except ImportError:
    from main.utils.utils import HistoryObject

class HTTPEndPointSubscriptionHandler:
    
    def __init__(self,propertyConfig):
        self.propertyConfig = propertyConfig
    
    def unpack_property_config(self):
        self.updateFrequency = 2   
        
        
    def subscribe(self):
        while True:
            requests.get()
            time.sleep(self.updateFrequency)
