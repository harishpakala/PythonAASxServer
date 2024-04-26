# PythonAASxServer

## Dependencies

This repository hosts the source code for Python AASx Server, 

:one: The  code is written in Python 3.9 <br />
:two: All the Python dependencies are specified in the [requirements.txt](https://github.com/harishpakala/PythonAASxServer/blob/master/requirements.txt) <br />
:three: The LIA OVGU development uses eclipse editor, accordingly eclipse related project files are provided in the repository.

### Installing Dependencies
<strong>pip3 install -r requirements.txt</strong> <br/>

## Configuration
The source code is associated with a .env file, all the configuration variables are specified in it.
<pre><code>
LIA_AAS_RESTAPI_DOMAIN_INTERN=localhost
LIA_AAS_RESTAPI_DOMAIN_EXTERN=localhost
LIA_AAS_RESTAPI_PORT_EXTERN=60012
LIA_AAS_RESTAPI_PORT_INTERN=60012
LIA_AAS_MQTT_HOST=localhost
LIA_AAS_MQTT_PORT=1883
LIA_preferedI40EndPoint=MQTT
LIA_REGISTRYENDPOINT=http://liabroker.ddns.net:9021/i40commu
LIA_AAS_PACKAGE=AAS_LIA_Demonstrator.json
LIA_PUBSUB_LISTNER_HOST=localhost
LIA_PUBSUB_LISTNER_PORT=4051
LIA_SECURITY_ENABLED=Y
LIA_AUTHENTICATION_SERVER=22
LIA_PATH2SIGNINGKEY=identityserver.test.rsa.pem
LIA_PATH2AUTHCERT=identityserver.test.rsa.cer
LIA_NAMESPACE=ovgu.de
</code></pre>
## Running 
1) The base python program is organized inside the src/main subdirectory.  <br/>
<strong>python3.9 pyaasxServer.py</strong> <br/>

## AAS Registry Rest API Services
The table 2 provides list of rest services the Python AASx Serve rprovides, it also lists down the allowed operations for each of the service. The services are as per the guidelines of [AAS Detail Part 2](https://www.plattform-i40.de/PI40/Redaktion/DE/Downloads/Publikation/Details_of_the_Asset_Administration_Shell_Part_2_V1.html). 

{aasIdentifier} = idShort or global unique identifier of AAS or global unique identifier of the aaset that the AAS is representing <br />
{submodelIdentifier} = idShort or global unique identifier of Submodel <br />

|                         HTTP URI                                                 |        GET         |        PUT         |       DELETE       |     POST         |
|----------------------------------------------------------------------------------| ------------------ | ------------------ | ------------------ | -----------------|
|<http://localhost:60012/shells>                                                   | ✔️|❌|❌|✔️|
|<http://localhost:60012/shells/{path:aasIdentifier}>                              | ✔️|✔️|✔️|❌|
|<http://localhost:60012/shells/{path:aasIdentifier}/aas>                          | ✔️|✔️|❌|❌|
|<http://localhost:60012/shells/{path:aasIdentifier}/aas/submodels>                | ✔️|❌|❌|✔️|
|<http://localhost:60012/shells/{path:aasIdentifier}/aas/submodels/{path:submodelIdentifier}>| ❌|❌|✔️|❌|
|<http://localhost:60012/shells/{path:aasIdentifier}/aas/asset-information>        | ✔️|✔️|❌|❌|
|<http://localhost:60012/shells/{path:aasIdentifier}/aas/submodels>        | ✔️|❌|❌|❌|
|<http://localhost:60012/shells/{path:aasIdentifier}/aas/submodels/{path:submodelIdentifier}/submodel>         | ✔️|✔️|❌|❌|
|<http://localhost:60012/shells/{path:aasIdentifier}/aas/submodels/{path:submodelIdentifier}/submodel/submodel-elements>    | ✔️|❌|❌|✔️|
|<http://localhost:60012/shells/{path:aasIdentifier}/aas/submodels/{path:submodelIdentifier}/submodel/submodel-elements/{path:idShortPath}>| ✔️|✔️|✔️|✔️|
|<http://localhost:60012/shells/{path:aasIdentifier}/aas/submodels/{path:submodelIdentifier}/submodel/submodel-elements/{path:idShortPath}/attachment> | ✔️|✔️|❌|❌|
|<http://localhost:60012/submodels> | ✔️|❌|❌|✔️|
|<http://localhost:60012/submodels/{path:submodelIdentifier}> | ✔️|✔️|❌|❌|
|<http://localhost:60012/submodels/{path:submodelIdentifier}/submodel> | ✔️|✔️|❌|❌|
|<http://localhost:60012/submodels/{path:submodelIdentifier}/submodel/submodel-elements> | ✔️|❌|❌|✔️|
|<http://localhost:60012/submodels/{path:submodelIdentifier}/submodel/submodel-elements/{path:idShortPath}> | ✔️|✔️|✔️|✔️|
|<http://localhost:60012/submodels/{path:submodelIdentifier}/submodel/submodel-elements/{path:idShortPath}/attachment>| ✔️|✔️|❌|❌|
|<http://localhost:60012/concept-descriptions>| ✔️|❌|❌|✔️|
|<http://localhost:60012/concept-descriptions/{path:cdIdentifier}>| ✔️|✔️|✔️|❌|
|<http://localhost:60012/shells/{path:aasIdentifier}/aas/skills/{path:skillName}/skill>| ❌|❌|❌|✔️|

## Back Ground 
### Finite State Machines and the SKills.
<p align="justify">
In PythonAASxServer the concept skills represent the behavior of the type 3 AAS. These skills are modelled as Finite State Machines (FSM). The interactions between the skills happens with exchange the [I4.0 Messages](https://github.com/harishpakala/I40_Language_Semantics) <br/>
   
<strong>Interaction Protocols </strong> represent structured sequence of messages exchanged between multiple partners / actors to achieve a specified goal (Example : Three-Way Handhake Protocol). An instance / execution of an interaction protocol is associated with a specific conversationID, all the messages wihtin the concersation have the same conversationID within I4.0 frame part. Each skilll in a Interaction Protocol is specific Role Name. There could be multiple skills with same Role Name.<br/>

The Python source-code created by the state machine creator contains a set of classes. Each state represents a specific state and the entire state machine is represensted by anotehr class, that coordinates it's execution. <br/>

Each skill / FSM is associated with a specific queue within in the [PythonAASxServer](https://github.com/harishpakala/PythonAASxServer) framework.<br/>

Transitions between the states are expected due to one of the three event-types a) Inbound Message, b) Internal Trigger c) External Trigger.<br/>
</p>

## Sample State

```
class Hello(AState):
    message_in =  ["Ping",]       
    
    def initialize(self):
        # Gaurd variables for enabling the transitions
        self.SendAck_Enabled = True 
            
    def actions(self) -> None:
        if (self.wait_untill_timeout(10)):
            message = self.receive(WaitforHi.message_in[0])
            self.save_in_message(message)
        
    def transitions(self) -> object:
        if (self.SendAck_Enabled):
            return "SendAck"
```

<p align="center">
A Hello state formatted as per Pyhton AASxServer and the StateMachine creator.
</p>

* The Hello state inherits the class Abstract class <strong>AState</strong> [source-code](https://github.com/harishpakala/PythonAASxServer/blob/c308300e3e78dbac5cacbbf6c09fc526a4d52eff/src/main/utils/sip.py#L43). <br/>
* The static variable message_in represents the list of messages that the FSM is expected to receive in the specific state. <br/>
* This class provides a set of guard conditions reequired for transitions to the next state. All the logic to the be executed within the Hello state needs to be written in the <strong>actions()</strong> method. <br/>
* The <strong>transitions()</strong> method should not be edited. <br/>
* For every next state a boolean guard variable will be provided in the constructor of the class, extracted from the JSON file. All the guard variables are defaulted to True. <br/>
* The developer needs to disable gaurd variable (False) in the <strong>actions()</strong> method, for the state that is not the next one. <br/>
* The [PythonAASxServer](https://github.com/harishpakala/PythonAASxServer) framework takes care and hide the complete mechanism behind the exchange of I4.0 messages between the skills. <br/>

### Send and Receive Methods 

```
receive(msg_in)
```
<p align="center">
Returns the first message from the inbound queue of type msg_in, if there is no message the method returns None.
</p>
<br/>

```
receive_all(msg_in)
```

<p align="center">
Returns all the messages from the inbound queue of type msg_in, if there is no message the method returns an empty list.
</p>
<br/>

### I4.0 Message creation Method  

```
create_i40_message(msg_out,conversationId,receiverId,receiverRole)
```
<p>
Creates an I4.0 message of type 'msg_out' with a specific 'conversationId'. The senderRole will the SKill that has called this method. The receiverRole is destination skill.
The combination of receiverId and receiverRole is expected to be unique within the specific interaction. The senderId or the receiverId represents unique Id of the type3 AAS to which the SKill is attached.
</p>
<br/>

### Saving the I4.0 messages to the backend Methods

```
save_in_message(msg)
```
<p align="center">
Copies the contents of an inbound I4.0 messsage to backend.
</p>
<br/>

```
save_out_message(msg_in)
```

<p align="center">
Copies the contents of an outbound I4.0 messsage to backend.
</p>
<br/>

### AASx Data Access Methods

```
GetSubmodelById(submodelId)
```

<p align="center">
Returns the submodel of the specified submodelId. In case the submodel is not present or any internal error it returns error.
</p>
<br/>

```
GetSubmodelELementByIdshoortPath(submodelId)
```

<p>
Returns the submodel-element of the specified submodelId and IdShortPath combination. In case the submodel-element is not present or any internal error it returns error.
</p>
<br/>

```
save_submodel(submodel)
```

<p align="center">
The replaces the existing submodel with the new submodel specified. Successful updation will return True, else returns False.
</p>
<br/>



### Predefined guard Methods

```
wait_untill_timeout(timer)
```
<p align="center">
The Control waits untill a specific number of seconds as assigned to argument to the method.
</p>
<br/>

```
wait_untill_message(message_count,msg_types)
```
<p>
The Control waits untill a specific number of messaages are arrived in the buffer of the message type specified as an argument msg_types (List of strings).
</p>
<br/>

```
wait_untill_message_timeout(message_count,timer,msg_types)
```
<p>
The Control waits untill a specific number of messaages are arrived in the buffer of the message type specified as an argument msg_types (List of strings). However if the timer expires, the control returns.
</p>
<br/>

### Data access between states of a FSM

Every FSM skill is provided by tape by the [PythonAASxServer](https://github.com/harishpakala/PythonAASxServer) framework. Each entry in the tape is key value pair.

```
push(key,value)
```
<p>
Push a data element 'value' to the tape with an associated 'key'.
</p>
<br/>

```
retrieve(key)
```
<p>
Returns the value associated with the specific key.
</p>
<br/>

```
flush()
```
<p>
Clears the tapes, removes all the key,value pairs. Usually it is done afer an iteration of the FSM.
</p>
<br/>


## Controller class of a FSM AccessProvider

class AccessProvider(Actor):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''      
        Actor.__init__(self,"AccessProvider",
                       "www.admin-shell.io/interaction/3WayHandshake",
                       "Access Provision","Start")
                        

    def start(self):
        self.run("Start")


## Logs
The python project maintains a logger, all the important aspects regarding its functionality  are captured with logger. The entire log information is stored into .LOG files under the src &gt; main &gt; logs folder.

## Issues
If you want to request new features or report bug [submit a new issue](https://github.com/harishpakala/PythonAASxServer/issues/new)

## License

Python AAS Registry is Licensed under Apache 2.0, the complete license text including the copy rights is included under [License.txt](https://github.com/harishpakala/PythonAASxServer/blob/main/LICENSE.txt)

* APScheduler,python-snap7,jsonschema,aiocoap,hbmqtt MIT License <br />
* Flask,werkzeug, Flask-RESTful, python-dotenv BSD-3-Clause <br />
* requests Apache License, Version 2.0 <br />
* paho-mqtt Eclipse Public License 2.0 and the Eclipse Distribution License 1.0 <br />

