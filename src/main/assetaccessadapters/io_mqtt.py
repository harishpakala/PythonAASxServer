'''
Copyright (c) 2021-2022 OVGU LIA
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
'''
try:
    from utils.utils import HistoryObject
except ImportError:
    from main.utils.utils import HistoryObject

class MQTTSubscriptionHandler:
    
    def __init__(self,propertyConfig):
        self.propertyConfig = propertyConfig
    
    def subscribe(self):
        while True:
            pass
