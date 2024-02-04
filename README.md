# PythonLIASampleServer

## Dependencies

This repository hosts the source code for RIC architecture, 

:one: The  code is written in Python 3.9 <br />
:two: All the Python dependencies are specified in the [requirements.txt](https://github.com/harishpakala/PythonAASxServer/blob/master/requirements.txt) <br />
:three: The LIA OVGU development uses eclipse editor, accordingly eclipse related project files are provided in the repository.

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
<strong>python3.9 vws_ric.py</strong> <br/>

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
|<http://localhost:60012/shells>/{path:aasIdentifier}/aas/skills/{path:skillName}/skillName                                        | ❌|❌|❌|✔️|


## Logs
The python project maintains a logger, all the important aspects regarding its functionality  are captured with logger. The entire log information is stored into .LOG files under the src &gt; main &gt; logs folder.

## Issues
If you want to request new features or report bug [submit a new issue](https://github.com/admin-shell-io/python-aas-registry/issues/new)

## License

Python AAS Registry is Licensed under Apache 2.0, the complete license text including the copy rights is included under [License.txt](https://github.com/harishpakala/PythonAASxServer/blob/main/LICENSE.txt)

* APScheduler,python-snap7,jsonschema,aiocoap,hbmqtt MIT License <br />
* Flask,werkzeug, Flask-RESTful, python-dotenv BSD-3-Clause <br />
* requests Apache License, Version 2.0 <br />
* paho-mqtt Eclipse Public License 2.0 and the Eclipse Distribution License 1.0 <br />

