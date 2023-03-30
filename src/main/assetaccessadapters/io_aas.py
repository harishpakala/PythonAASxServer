import uuid
try:
    from abstract.assetendpointhandler import AsssetEndPointHandler
except ImportError:
    from main.abstract.assetendpointhandler import AsssetEndPointHandler
try:
    from utils.utils import ExecuteDBModifier, SubscriptionMessage
except ImportError:
    from main.utils.utils import ExecuteDBModifier, SubscriptionMessage
try:
    from pubsub.client.socketclient import SocketClient
except ImportError:
    from main.pubsub.client.socketclient import SocketClient

try:
    from pubsub.utils import SocketConfig
except ImportError:
    from main.pubsub.utils import SocketConfig

class AASPubSubHandler(AsssetEndPointHandler):

    def __init__(self,params,func):
        self.uri = params["href"]
        self.func = func
        self.aasId = params["aasId"]
        self.propertyIdSHort  = params["_referenceId"]
        self.dataElement = params["dataElement"]
        
    def subscribe(self):
        try:
            temp = (self.uri[6:]).split("/")
            domain = ((temp)[0]).split(":")
            nodeId = '/'.join(temp[1:])
            
            serverConfig = SocketConfig(domain[0],domain[1],"clientSocket")
            aasSocketClient = SocketClient(self.aasId,serverConfig)
            aasSocketClient.on_message = self.func
            aasSocketClient.description = str(uuid.uuid4())
            if (aasSocketClient.connect("Test")):
                aasSocketClient.subscribe("Test", [nodeId])
            else:
                return False
                
        except Exception as E:
            print(str(E))

class PyAASSubscriptionHandler(object):
    def __init__(self, pyAAS, params):
        self.pyAAS = pyAAS
        self.params = params

    def on_message(self, i40Message):
        new_value = i40Message["interactionElements"][0]
        dataElement = self.params["dataElement"]
        dataElement["value"] = new_value
        edm = ExecuteDBModifier(self.pyAAS)
        msg, status = edm.execute({"data": {"elemData": dataElement,
                                            "_idShortpath": self.params["_referenceId"],
                                            }, "method": "putSubmodelElem", "instanceId": str(uuid.uuid1())})

    def handle(self):
        accessURI = self.params["href"]
        if (accessURI[0:3] == "AAS"):
            handler = AASPubSubHandler(self.params, self.on_message)
            handler.subscribe()