'''
Copyright (c) 2021-2022 OVGU LIA
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt).
This source code may use other Open Source software components (see LICENSE.txt).
'''
try:
    import queue as Queue
except ImportError:
    import Queue as Queue
from datetime import datetime,timedelta

class DataManager(object):
    '''
    classdocs
    '''

    def __init__(self, pyAAS):
        '''
        Constructor
        '''
        self.pyAAS = pyAAS
       
        self.InBoundProcessingQueue = Queue.Queue()
        self.outBoundProcessingDict = {}
    
    def pushInboundMessage(self,msg):
        self.InBoundProcessingQueue.put(msg)
     
    def configure(self):
        self.pyAAS.serviceLogger.info('The Database manager is being configured')
    
    def requestHandler(self):
        self.POLL = True
        self.pyAAS.serviceLogger.info('The Database manager is being started')
        while self.POLL:
            if (self.InBoundProcessingQueue).qsize() != 0:
                inMessage = self.InBoundProcessingQueue.get()
                if inMessage["functionType"] == 1:
                    dba = self.pyAAS.dba
                    _dba_method = getattr(dba,inMessage['method'])
                    if inMessage['data'] is not None:
                        self.outBoundProcessingDict[inMessage["instanceid"]] = _dba_method(inMessage['data'])
                    else:
                        self.outBoundProcessingDict[inMessage["instanceid"]] = _dba_method()
                elif inMessage['functionType'] == 3:
                    dba = self.pyAAS.dba
                    entryTime = ((datetime.now()+ timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S.%f"))[:-3]
                    dba.saveNewConversationMessage(inMessage['conversationId'],
                                                         inMessage['messageType'],
                                                         inMessage["messageId"],
                                                         inMessage["direction"],
                                                         inMessage["message"],entryTime,inMessage["SenderAASID"])
    def start(self):
        self.requestHandler()
        self.pyAAS.serviceLogger.info('The Database manager is started')
        
    def stop(self):
        self.pyAAS.serviceLogger.info('The Database manager is being stopped')
        self.POLL = False
        self.pyAAS.serviceLogger.info('The Database manager is stopped')
        
    def update(self):
        pass
