from opcua import Client
import uuid
try:
    from abstract.assetendpointhandler import AsssetEndPointHandler
except ImportError:
    from main.abstract.assetendpointhandler import AsssetEndPointHandler

class AsssetEndPointHandler(AsssetEndPointHandler):

    def __init__(self, pyAAS):
        self.pyAAS = pyAAS


    def read(self,urI):
        try:
            host = urI.split("opc.tcp://")[1].split("/")[0].split(":")
            IP = host[0]
            PORT = host[1]
            nodeId = (urI.split("opc.tcp://")[1]).split("/")[-1]
            plc_opcua_Client =  Client("opc.tcp://" + IP + ":" + PORT + "/",timeout = 800000)
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

    def write(self,urI,value):
        try:
            host = urI.split("opc.tcp://")[1].split("/")[0].split(":")
            IP = host[0]
            PORT = host[1]
            nodeId = urI.split("opc.tcp://")[1].split("/")[1]
            self.td_opcua_client = Client("opc.tcp://" + IP + ":" + PORT + "/",timeout = 600000)
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
    
    def subscribe(self,urI,endPointSUbHandler):
        try:
            host = urI.split("opc.tcp://")[1].split("/")[0].split(":")
            IP = host[0]
            PORT = host[1]
            nodeName = (urI.split("opc.tcp://")[1]).split("/")[-1]
            plc_opcua_Client =  Client("opc.tcp://" + IP + ":" + PORT + "/")
            plc_opcua_Client.description = str(uuid.uuid4())
            plc_opcua_Client.connect()
            nodeId = plc_opcua_Client.get_node(nodeName)
            sub = plc_opcua_Client.create_subscription(10,endPointSUbHandler)
            handle = sub.subscribe_data_change([nodeId])
        except Exception as e1:
            print(e1)
            try:
                plc_opcua_Client.disconnect()
            except Exception as e2:
                print(e1)