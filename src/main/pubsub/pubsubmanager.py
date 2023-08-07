"""
Copyright (c) 2021-2022 OVGU LIA
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
"""
import socket
import threading
try:
    from pubsub.server.sokcetserver import SocketListner
except ImportError:
    from  src.main.pubsub.server.sokcetserver import SocketListner
try:
    from pubsub.utils import SocketConfig
except ImportError:
    from  src.main.utis import SocketConfig
    

class PubSubManager:
    def __init__(self,pyaas):
        self.pyaas = pyaas
        self.listnersConfig = self.pyaas.listeners_config
        self.listnersSocketConfig = dict()
        
    def configure_listner(self):
        try:
            for listnername in self.listnersConfig.keys():
                listnerConfig = self.listnersConfig[listnername] 
                self.listnersSocketConfig[listnername] = SocketConfig(listnerConfig["host"],listnerConfig["port"],listnername)
            return True    
        except Exception as E:
            self.serviceLogger.info('Error while creating the configuration for PubSub Listners. '+str(E))
            return False
    
    def configure_listner_sockets(self):
        try:    
            for listnername in self.listnersSocketConfig:
                _listnersocketConfig = self.listnersSocketConfig[listnername]
                listnerInstance = socket.socket(_listnersocketConfig.AF_INET, _listnersocketConfig.SOCK_STREAM)
                socketListner = SocketListner(_listnersocketConfig,listnerInstance,self.pyAAS)
                self.pyAAS.listenerSockets[listnername] = socketListner
            return True
        except Exception as E:
            self.serviceLogger.info('Error while creating the configuration for PubSub Listners. '+str(E))
            return False
        
    def start_listners(self):
        try:
            for listnername in self.pyAAS.listenerSockets:
                listnerthread = threading.Thread(target=self.pyAAS.listenerSockets[listnername].socket_start, )
                listnerthread.start()
            return True
        except Exception as E:
            print(str(E))
            return False
        
    def stop_listners(self):
        try:
            for listnername in self.listnerSockets.keys():
                self.listnerSockets[listnername].socket_shutdown()
            return True
        except Exception as E:
            print(str(E))
            return False        