from opcua import Client
import uuid
from datetime import datetime

try:
    from utils.utils import HistoryObject
except ImportError:
    from src.main.utils.utils import HistoryObject
try:
    from abstract.assetendpointhandler import AsssetEndPointHandler
except ImportError:
    from src.main.abstract.assetendpointhandler import AsssetEndPointHandler


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

    def subscribe(self, uri, endPointSUbHandler):
        plc_opcua_client = None
        try:
            host = uri.split("opc.tcp://")[1].split("/")[0].split(":")
            ip_address = host[0]
            port = host[1]
            node_id = (uri.split("opc.tcp://")[1]).split("/")[-1]
            plc_opcua_client = Client("opc.tcp://" + ip_address + ":" + port + "/")
            plc_opcua_client.description = str(uuid.uuid4())
            plc_opcua_client.connect()
            node = plc_opcua_client.get_node(node_id)
            sub = plc_opcua_client.create_subscription(10, endPointSUbHandler)
            handle = sub.subscribe_data_change([node])
        except Exception as e1:
            print(e1)
            try:
                plc_opcua_client.disconnect()
            except Exception as e2:
                print(e1)


class AssetOPCUAEndPointSubscription:

    def __init__(self, td_property):
        self.td_property = td_property

    def datachange_notification(self, node, val, data):
        aas_element = self.td_property.aasELement
        while not self.td_property.elem_lock:
            self.td_property.elem_lock = True
            _dt = datetime.now()
            _ho = HistoryObject(self.td_property.aas_element["value"], _dt)
            self.td_property.addhistoryElement(_ho)
            self.td_property.aasELement["value"] = val
            self.td_property.elem_lock = False
            break