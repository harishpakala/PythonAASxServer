"""
Copyright (c 2023 Otto-von-Guericke-Universitaet Magdeburg, Lehrstuhl Integrierte Automation
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt.
This source code may use other Open Source software components (see LICENSE.txt.
"""
from typing import Optional, List,Dict
from main.models.aastypes import Reference

class SecurityDefinition:
    def __init__(self, scheme : str, proxy : Optional[str] = None):
        self.proxy = proxy
        self.scheme = scheme

class BasicSecurityScheme(SecurityDefinition):
    def __init__(self, scheme : str, proxy : Optional[str] = None,
                 name : Optional[str] = None, _in : Optional[str] = None):
        self.name = name
        self._in = _in
        SecurityDefinition.__init__(self, scheme, proxy)

class PskSecurityScheme(SecurityDefinition):
    def __init__(self, scheme : str, proxy : Optional[str] = None,
                 Identity : Optional[str] = None):
        self.Identity = Identity
        SecurityDefinition.__init__(self, scheme, proxy)
        
class DigestSecurityScheme(SecurityDefinition):
    def __init__(self, scheme : str, proxy : Optional[str] = None,
                 name : Optional[str] = None, _in : Optional[str] = None, qop : Optional[str] = None):
        self.name = name
        self._in = _in
        self.qop = qop
        SecurityDefinition.__init__(self, scheme, proxy)

class BearerSecurityScheme(SecurityDefinition):
    def __init__(self, scheme : str, proxy : Optional[str] = None,
                 name : Optional[str] = None, _in : Optional[str] = None, authorization : Optional[str] = None,
                 alg  : Optional[str] = None, format  : Optional[str] = None):
        self.name = name
        self._in = _in
        self.authorization = authorization
        self.alg = alg
        self.format = format
        SecurityDefinition.__init__(self, scheme, proxy)

class OAuth2SecurityScheme(SecurityDefinition):
    def __init__(self, scheme : str, flow : str, proxy : Optional[str] = None,
                token : Optional[str] = None,refresh : Optional[str] = None,
                authorization : Optional[str] = None, scopes : Optional[List[str]] = None):
        self.flow = flow
        self.proxy = proxy
        self.token = token
        self.refresh = refresh
        self.authorization = authorization
        self.scopes = scopes
        SecurityDefinition.__init__(self, scheme, proxy)

class ComboSecurityScheme(SecurityDefinition):
    def __init__(self, scheme : str, proxy : Optional[str] = None,
                 oneOf : Optional[List[Reference]] = None, allOf : Optional[List[Reference]] = None):
        self.oneOf = oneOf
        self.allOf = allOf
        SecurityDefinition.__init__(self, scheme, proxy)

class NoSecurityScheme(SecurityDefinition):
    def __init__(self, scheme : str, proxy : Optional[str] = None):
        SecurityDefinition.__init__(self, scheme, proxy)

class AutoSecurityScheme(SecurityDefinition):
    def __init__(self, scheme : str, proxy : Optional[str] = None):
        SecurityDefinition.__init__(self, scheme, proxy)

class EndPointMetaData:
    def __init__(self,base :str, contentType : Optional[str] = None, 
                 securityDefinitions : List[SecurityDefinition] = None, security : List[Reference] = None,
                 modv_mostSignificantByte  : Optional[str] = None, 
                 modv_mostSignificantWord : Optional[str] = None):
        self.base = base
        self.contentType = contentType
        self.securityDefinitions = securityDefinitions
        self.security = security
        self.modv_mostSignificantByte = modv_mostSignificantByte
        self.modv_mostSignificantWord = modv_mostSignificantWord

class HTVHeader:
    def __init__(self,htv_fieldName :  Optional[str] = None, htv_fieldValue :  Optional[str] = None):
        self.htv_fieldName = htv_fieldName
        self.htv_fieldValue = htv_fieldValue

class Form:
    def __init__(self, contentType :  Optional[str] = None, subprotocol :  Optional[str] = None,
                 href : Optional[str] = None, security : Optional[List[Reference]] = None,
                 htv_methodName :  Optional[str] = None, htv_headers : Optional[List[HTVHeader]] = None,
                 mqv_retain :  Optional[str] = None,mqv_controlPacket :  Optional[str] = None,
                 mqv_qos :  Optional[str] = None,modv_function :  Optional[str] = None,modv_entity :  Optional[str] = None,
                 modv_zeroBasedAddressing :  Optional[str] = None,modv_timeout :  Optional[str] = None,
                 modv_pollingTime :  Optional[str] = None,modv_type :  Optional[str] = None,
                 modv_mostSignificantByte :  Optional[str] = None,modv_mostSignificantWord :  Optional[str] = None):
        
        self.contentType = contentType
        self.subprotocol = subprotocol
        self.href = href
        self.security = security
        self.htv_methodName = htv_methodName
        self.htv_headers = htv_headers
        self.mqv_retain = mqv_retain
        self.mqv_controlPacket = mqv_controlPacket
        self.mqv_qos = mqv_qos
        self.modv_function = modv_function
        self.modv_entity = modv_entity
        self.modv_zeroBasedAddressing = modv_zeroBasedAddressing
        self.modv_timeout = modv_timeout
        self.modv_pollingTime = modv_pollingTime
        self.modv_type = modv_type
        self.modv_mostSignificantByte = modv_mostSignificantByte
        self.modv_mostSignificantWord = modv_mostSignificantWord

class Item:
    def __init__(self):
        pass

class _range:
    def __init__(self):
        pass

class Propertie:
    def __init__(self):
        pass
    
class Action:
    def __init__(self):
        pass
    
class Event:
    def __init__(self):
        pass    

class Property:
    _property = "https://admin-shell.io/idta/AssetInterfaceDescription/1/0/PropertyDefinition"
    _forms = "https://www.w3.org/2019/wot/td#hasForm"
    _key = "https://admin-shell.io/idta/AssetInterfacesDescription/1/0/key"
    _title = "https://www.w3.org/2019/wot/td#title"
    _observable = "https://www.w3.org/2019/wot/td#isObservable"
    _type = "https://www.w3.org/1999/02/22-rdf-syntax-ns#type"
    _const = "https://www.w3.org/2019/wot/json-schema#const"
    _enum = "https://www.w3.org/2019/wot/json-schema#enum"
    _default = "https://www.w3.org/2019/wot/json-schema#default"
    _unit = "https://schema.org/unitCode"
    _min_max = "https://admin-shell.io/idta/AssetInterfacesDescription/1/0/minMaxRange"
    _lengthRange = "https://admin-shell.io/idta/AssetInterfacesDescription/1/0/lengthRange"
    _items = "https://www.w3.org/2019/wot/json-schema#items"
    _itemsRange = "https://admin-shell.io/idta/AssetInterfacesDescription/1/0/itemsRange"
    _valueSemantics = "https://admin-shell.io/idta/AssetInterfacesDescription/1/0/valueSemantics"
    _properties = "https://www.w3.org/2019/wot/json-schema#properties"
    
    def __init__(self,forms : Optional[List[Form]] = None, key : Optional[str] = None,title : Optional[str] = None,
                 observable : Optional[str] = None, _type : Optional[str] = None,
                 const : Optional[str] = None, enum : Optional[List[str]] = None,
                 default : Optional[str] = None, unit : Optional[str] = None,
                 min_max : Optional[_range] = None, lengthRange : Optional[_range] = None,
                 items : Optional[List[Item]] = None, itemsRange : Optional[_range] = None,
                 valueSemantics : Optional[Reference] = None, properties : Optional[Propertie] = None,
                  ):
        self.forms = forms
        self.key = key
        self.title = title
        self.observable = observable
        self.tdtype = _type
        self.const = const
        self.enum = enum
        self.default = default
        self.unit = unit
        self.min_max = min_max
        self.lengthRange = lengthRange
        self.items = items
        self.itemsRange = itemsRange
        self.valueSemantics = valueSemantics
        self.properties = properties

class InteractionMetaData:
    _properties = "https://www.w3.org/2019/wot/td#hasPropertyAffordance"
    def __init__(self,properties : Optional[Dict[str, Property]] = None,
                 actions : Optional[Dict[str,Action]] = None,
                 events : Optional[Dict[str,Event]] = None):
        self.properties = properties
        self.actions = actions
        self.events = events

class InterfaceDescription:
    _title = "interactionMetaData"
    _title = "https://www.w3.org/2019/wot/td#title"
    _created = "http://purl.org/dc/terms/created"
    _modified = "http://purl.org/dc/terms/modified"
    _support  = "https://www.w3.org/2019/wot/td#supportContact"
    _endPointMetaData = "https://admin-shell.io/idta/AssetInterfacesDescription/1/0/EndpointMetadata" 
    _interactionMetaData = "https://admin-shell.io/idta/AssetInterfacesDescription/1/0/InteractionMetadata"
    _externalDescriptor = "https://admin-shell.io/idta/AssetInterfacesDescription/1/0/ExternalDescriptor"
    
    def __init__(self, title :str, created : Optional[str] = None, modified :  Optional[str] = None,
                 support : Optional[str] = None, endPointMetaData : Optional[EndPointMetaData] = None,
                 interactionMetaData  : Optional[InteractionMetaData] = None):
        
        self.title = title
        self.created = created
        self.modified = modified
        self.support = support
        self.endPointMetaData = endPointMetaData
        self.interactionMetaData = interactionMetaData

class Configuration:
    _configuration = "https://admin-shell.io/idta/AssetInterfacesMappingConfiguration/1/0/MappingeConfiguration"
    _InterfaceReference = "https://admin-shell.io/idta/AssetInterfacesMappingConfiguration/1/0/InterfaceReference"
    _MappingSourceSinkRelations = "https://admin-shell.io/idta/AssetInterfacesMappingConfiguration/1/0/MappingSourceSinkRelations"
    
    def __init__(self,InterfaceReference : str,MappingSourceSinkRelations : List[str]):
        self.InterfaceReference = InterfaceReference
        self.MappingSourceSinkRelations = MappingSourceSinkRelations
    
class AIDMappingConfiguration:
    _configurations = "https://admin-shell.io/idta/AssetInterfacesMappingConfiguration/1/0/MappingeConfigurations"
    def __init__(self,configurations : Optional[List[Configuration]]):
        self.configurations = configurations
    
class Deserialization_AID:
    def __init__(self):
        pass
    
    def geSemanticID(self,element):
        return element["semanticId"]["keys"][0]["value"]
    
    def getEndpointMetaData(self,emd):
        for element in emd["value"]:
            pass
        
        return None
        
    def getForms(self,forms):
        return []
    
    def getproperty(self,propertysmc):
        _property = Property()
        for elem in propertysmc["value"]:
            semanticId = self.geSemanticID(elem)
            if semanticId == Property._key:   
                _property.Key = elem["value"]
            elif semanticId == Property._title: 
                _property.title= elem["value"]
            elif semanticId == Property._observable: 
                _property.observable = elem["value"]    
            elif semanticId == Property._forms: 
                _property.forms = self.getForms(elem)
            elif semanticId == Property._valueSemantics: 
                _property.valueSemantics = elem["value"]
            elif semanticId == Property._type: 
                _property.tdtype = elem["value"]
            elif semanticId == Property._default: 
                _property.default = elem["value"]    
            elif semanticId == Property._unit: 
                _property.unit = elem["value"]    
            elif semanticId == Property._lengthRange: 
                _property.lengthRange = elem["value"]    
            elif semanticId == Property._itemsRange: 
                _property.itemsRange = elem["value"]    
            elif semanticId == Property._items: 
                _property.items = self.getItems(elem)    
        
        return _property    
    
    def getInterfactionMetaData(self,imd):
        _interactionMetaData = InteractionMetaData()
        for element in imd["value"]:
            semanticId = self.geSemanticID(element)
            if semanticId == InteractionMetaData._properties:
                for propertysmc in element["value"]:
                    if self.geSemanticID(propertysmc) == Property._property:
                        _interactionMetaData.properties[propertysmc["idShort"]] = self.getproperty(propertysmc)
                
    def getInterface(self,interface_submodel):
        _interfaceDescription = InterfaceDescription("")
        for element in interface_submodel["value"]: 
            semanticId = self.geSemanticID(element) 
            if semanticId == InterfaceDescription._title:
                _interfaceDescription.title = element["value"]
            elif semanticId == InterfaceDescription._created:
                _interfaceDescription.created = element["value"]
            elif semanticId == InterfaceDescription._modified:
                _interfaceDescription.modified = element["value"]
            elif semanticId == InterfaceDescription._support:
                _interfaceDescription.support = element["value"]
            elif semanticId == InterfaceDescription._endPointMetaData:
                _interfaceDescription.endPointMetaData = self.getEndpointMetaData(element)
            elif semanticId == InterfaceDescription._interactionMetaData:
                _interfaceDescription.interactionMetaData = self.getInterfactionMetaData(element)
    
    def get_asset_interfaces(self,aidSubmodel):
        aid = dict()
        for element in aidSubmodel["submodelElements"]: 
            if self.geSemanticID(element) == "https://admin-shell.io/idta/AssetInterfacesDescription/1/0/Interface":
                aid[element["idShort"]] = self.getInterface(element)

class Identifier:
    def __init__(self,submodelId, idShortpath):
        self.submodelId = submodelId
        self.idShortpath = idShortpath
        

class Deserialization_AID_MC:
    def __init__(self):
        pass
    
    def getSemanticID(self,element):
        return element["semanticId"]["keys"][0]["value"]
    
    def getConfiguration(self,config):
        configuration = Configuration()
        for element in config["value"]:
            if self.getSemanticID(element) == Configuration._InterfaceReference:
                configuration.InterfaceReference = element["value"]
            
            if self.getSemanticID(element) == Configuration._MappingSourceSinkRelations:
                mappings = []
                for mapping in element["value"]:
                    mappings.append(mapping["value"])
                configuration.MappingSourceSinkRelations = mappings
    
    def getMappingConfigurations(self,mappingConfiguration):
        aidMappingConfiguration = AIDMappingConfiguration()
        configurations = []
        for element in mappingConfiguration["submodelElements"]:
            if self.getSemanticID(element) == AIDMappingConfiguration._configurations:
                for config in element["value"]:
                    if self.getSemanticID(config) == Configuration._configuration:
                        configurations.append(self.getConfiguration(config))
        aidMappingConfiguration.configurations = configurations
                    