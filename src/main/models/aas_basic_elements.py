'''
Created on 21 Jun 2022

@author: pakala
'''
from enum import Enum
from typing import List

try:
    from utils.utils import Immutable
except ImportError as E:
    from main.utils.utils import Immutable

class Identification(object):
    def __init__(self,_id: str, idType: str):
        self.id = _id
        self.idType = idType

class KeyElements(Enum):
        Undefined                       = "Undefined"

        GlobalReference                 = "GlobalReference"
        FragmentReference               = "FragmentReference"
        AccessPermissionRule            = "AccessPermissionRule"
        
        #submodel Elements
        AnnotatedRelationshipElement    = "AnnotatedRelationshipElement"
        BasicEvent                      = "BasicEvent"
        Blob                            = "Blob"
        Capability                      = "Capability"
        ConceptDictionary               = "ConceptDictionary"
        DataElement                     = "DataElement"
        File                            = "File" 
        Entity                          = "Entity"
        Event                           = "Event"                     
        MultiLanguageProperty           = "MultiLanguageProperty"
        Operation                       = "Operation"
        Property                        = "Property"
        Range                           = "Range"
        ReferenceElement                = "ReferenceElement"
        RelationshipElement             = "RelationshipElement"
        SubmodelElement                 = "SubmodelElement"
        SubmodelElementCollection       = "SubmodelElementCollection"
        
        View                            = "View"
        
        # AAS Main Elements
        Asset                           = "Asset"
        AssetAdministrationShell        = "AssetAdministrationShell"
        ConceptDescription              = "ConceptDescription"
        Submodel                        = "Submodel"
    
class Key(Immutable):
    def __init__(self, _type:str,local: bool, value: str, index: int, idType: str):
        self.type = _type
        self.local = local
        self.value = value
        self.index = index
        self.idType = idType
        
class Reference(Immutable):
    def __init__(self,keys: List[Key] ):
        self.keys = keys

    def add_newkey(self,key: Key):
        self.keys.append(key)
    
    def deleteKeyatIndex(self):
        del self.keys[0]

    def deleteKeyByValue(self,value):
        for key,index in enumerate(self.keys):
            if key.value == value:
                del self.keys[index]


class Identifier():
    pass

class AdministrativeInformation():
    pass

class Referable():
    pass

class Identifiable(Referable):
    def __init__(self):
        super().__init__()
        self.administration: Optinal[AdministrativeInformation] = None
        self.identification: Identifier = Identifier("","IRDI")

class HasDataSpecification():
    def __init__(self):
        pass
class AssetAdministrationShell(Identifiable,HasDataSpecification):
    def __init__(self):
        pass
    