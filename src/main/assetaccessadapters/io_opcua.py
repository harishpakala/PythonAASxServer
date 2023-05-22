from opcua import Client
from datetime import datetime
from asyncua import Client, ua, Node
import time
import uuid

try:
    from utils.utils import HistoryObject
except ImportError:
    from main.utils.utils import HistoryObject
try:
    from abstract.assetendpointhandler import AsssetEndPointHandler
except ImportError:
    from main.abstract.assetendpointhandler import AsssetEndPointHandler


class AsssetEndPointHandler(AsssetEndPointHandler):

    def __init__(self, pyAAS):
        self.pyAAS = pyAAS

    def get_opcua_handler(self, uRI):
        # apart from the nodeid it should include username and password if any.
        try:
            plc_opcua_Client = Client(uRI, timeout=800000)
            plc_opcua_Client.description = str(uuid.uuid4())
            plc_opcua_Client.session_timeout = 600000
            plc_opcua_Client.secure_channel_timeout = 600000
            plc_opcua_Client.connect()
            return plc_opcua_Client, True
        except Exception as E:
            print(str(E))
            return None, False

    def close_opcua_handler(self, handler):
        try:
            handler.disconnect()
            return True
        except Exception as E:
            print(str(E))
            return False

    def read(self, urI):
        try:
            host = urI.split("opc.tcp://")[1].split("/")[0].split(":")
            IP = host[0]
            PORT = host[1]
            nodeId = (urI.split("opc.tcp://")[1]).split("/")[-1]
            plc_opcua_Client = Client("opc.tcp://" + IP + ":" + PORT + "/", timeout=800000)
            plc_opcua_Client.description = str(uuid.uuid4())
            plc_opcua_Client.session_timeout = 600000
            plc_opcua_Client.secure_channel_timeout = 600000
            plc_opcua_Client.connect()
            rValue = (plc_opcua_Client.get_node(nodeId)).get_value()
            plc_opcua_Client.disconnect()
            return rValue
        except Exception as e1:
            try:
                plc_opcua_Client.disconnect()
                return "error"
            except Exception as e2:
                return "error"

    def write(self, urI, value):
        try:
            host = urI.split("opc.tcp://")[1].split("/")[0].split(":")
            IP = host[0]
            PORT = host[1]
            nodeId = urI.split("opc.tcp://")[1].split("/")[1]
            self.td_opcua_client = Client("opc.tcp://" + IP + ":" + PORT + "/", timeout=600000)
            self.td_opcua_client.description = str(uuid.uuid1())
            self.td_opcua_client.connect()
            tdProperty = self.td_opcua_client.get_node(nodeId)
            tdProperty.set_value(value)
        except Exception as E:
            self.td_opcua_client.disconnect()
            return str(E)
        finally:
            self.td_opcua_client.disconnect()
            return "Success"

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
                client = Client(url="opc.tcp://localhost:4851")
                async with client:
                    subscription = await client.create_subscription(0.1, self.handler)
                    tnode = (client.get_node("ns=1;i=1023"))
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


