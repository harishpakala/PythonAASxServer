from datetime import datetime
from asyncua import Client, ua, Node
import time
import asyncio

try:
    from utils.utils import HistoryObject
except ImportError:
    from main.utils.utils import HistoryObject

class OPCUAEndPointHandler:

    def __init__(self):
        pass
        
    def get_uri_nodeid(self,uri):
        host = uri.split("opc.tcp://")[1].split("/")[0].split(":")
        ip_address = host[0]
        port = host[1]
        node_id = (uri.split("opc.tcp://")[1]).split("/")[-1]
        _uri = "opc.tcp://" + ip_address + ":" + port + "/"
        return [_uri,node_id]

    async def get_opcua_handler(self, uRI):
        # apart from the nodeid it should include username and password if any.
        try:
            uri_nodeid = self.get_uri_nodeid(uRI)
            client_hadler = Client(url=uri_nodeid[0])
            async with client_hadler:
                return client_hadler
        except Exception as E:
            return None
        
    async def close_opcua_handler(self, client_hadler):
        try:
            client_hadler.disconnect()
            return True
        except Exception as E:
            return False

    async def _write(self,uRI,write_value):
        try:
            uri_nodeid = self.get_uri_nodeid(uRI)
            client_hadler = Client(url=uri_nodeid[0])
            async with client_hadler:
                _node = client_hadler.get_node(uri_nodeid[1])
                await _node.write_value(write_value)
            return True
        except Exception as E:
            return False

    async def _write_DataValue(self,uRI,write_value):
        try:
            uri_nodeid = self.get_uri_nodeid(uRI)
            client_hadler = Client(url=uri_nodeid[0])
            async with client_hadler:
                _node = client_hadler.get_node(uri_nodeid[1])
                await _node.set_value(ua.DataValue(write_value))
            return True
        except Exception as E:
            print(str(E))
            return False

    async def _read(self,uRI):
        try:
            uri_nodeid = self.get_uri_nodeid(uRI)
            client_hadler = Client(url=uri_nodeid[0])
            async with client_hadler:
                _node = client_hadler.get_node(uri_nodeid[1])
                _node_value = await _node.get_value()
            return _node_value
        except Exception as E:
            return False

    async def _read_data_value(self,uRI):
        try:
            uri_nodeid = self.get_uri_nodeid(uRI)
            client_hadler = Client(url=uri_nodeid[0])
            async with client_hadler:
                _node = client_hadler.get_node(uri_nodeid[1])
                _node_value = await _node.read_data_value()
            return _node_value
        except Exception as E:
            return False

class OPCUASubscriptionHandler:
    """
    Subscription Handler. To receive events from server for a subscription
    This class is just a sample class. Whatever class having these methods can be used
    """
    
    def set_property(self,td_property):
        self.td_property = td_property        
    
    def datachange_notification(self, node: Node, val, data):
        """
        called for every datachange notification from server
        """
        while not self.td_property.elem_lock:
            self.td_property.elem_lock = True
            _dt = datetime.now()
            _ho = HistoryObject(self.td_property.aasELement["value"], _dt)
            self.td_property.addhistoryElement(_ho)
            self.td_property.aasELement["value"] = val
            self.td_property.elem_lock = False
            break        
        
    def event_notification(self, event: ua.EventNotificationList):
        """
        called for every event notification from server
        """
        pass

    def status_change_notification(self, status: ua.StatusChangeNotification):
        """
        called for every status change notification from server
        """
        pass

class OPCUASubscription:
    def __init__(self,_uri,_handler):
        self.poll = True
        self.uri_nodeid = self.get_uri_nodeid(_uri)
        self.handler = _handler

    def get_uri_nodeid(self,uri):
        host = uri.split("opc.tcp://")[1].split("/")[0].split(":")
        ip_address = host[0]
        port = host[1]
        node_id = (uri.split("opc.tcp://")[1]).split("/")[-1]
        _uri = "opc.tcp://" + ip_address + ":" + port + "/"
        return [_uri,node_id]

    async def subscribe(self):
        while True:
            time.sleep(0.1)
            print("New COnnection")
            try:
                client = Client(url=self.uri_nodeid[0])
                async with client:
                    subscription = await client.create_subscription(0.1, self.handler)
                    tnode = (client.get_node(self.uri_nodeid[1]))
                    await subscription.subscribe_data_change(tnode)
                    while True:
                        time.sleep(0.1)
                        et = await client.get_endpoints()
                        if len(et) == 0:
                            print("connection broke")
                            break
            except Exception as E:
                print(str(E))
                pass#await asyncio.sleep(0.1)


opcuaeHandler = OPCUAEndPointHandler()

ht = asyncio.run(opcuaeHandler._write("opc.tcp://localhost:4851/ns=1;i=1004","3K650000548506"))
print(ht)