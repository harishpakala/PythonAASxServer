"""
Copyright (c 2023 Otto-von-Guericke-Universitaet Magdeburg, Lehrstuhl Integrierte Automation
Author: Harish Kumar Pakala
This source code is licensed under the Apache License 2.0 (see LICENSE.txt.
This source code may use other Open Source software components (see LICENSE.txt.
"""
from enum import Enum, unique
from typing import Optional, List,Dict,Any

import uuid

@unique
class ModelingKind(Enum):
    Instance = "Instance"
    Template = "Template"

@unique
class DataTypeXSD(Enum):
    xs_anyURI = "xs:anyURI"
    xs_base64Binary = "xs:base64Binary"
    xs_boolean = "xs:boolean"
    xs_date = "xs:date"
    xs_dateTime = "xs:dateTime"
    xs_dateTimeStamp = "xs:dateTimeStamp"
    xs_decimal = "xs:decimal"
    xs_double = "xs:double"
    xs_duration = "xs:duration"
    xs_float = "xs:float"
    xs_gDay = "xs:gDay"
    xs_gMonth = "xs:gMonth"
    xs_gMonthDay = "xs:gMonthDay"
    xs_gYear = "xs:gYear"
    xs_gYearMonth = "xs:gYearMonth"
    xs_hexBinary = "xs:hexBinary"
    xs_string = "xs:string"
    xs_time = "xs:time"
    xs_dayTimeDuration = "xs:dayTimeDuration"
    xs_yearMonthDuration = "xs:yearMonthDuration"
    xs_integer = "xs:integer"
    xs_long = "xs:long"
    xs_int = "xs:int"
    xs_short = "xs:short"
    xs_byte = "xs:byte"
    xs_nonNegativeInteger = "xs:nonNegativeInteger"
    xs_positiveInteger = "xs:positiveInteger"
    xs_unsignedLong = "xs:unsignedLong"
    xs_unsignedInt =     "xs:unsignedInt"
    xs_unsignedShort = "xs:unsignedShort"
    xs_unsignedByte = "xs:unsignedByte"
    xs_nonPositiveInteger = "xs:nonPositiveInteger"
    xs_negativeInteger = "xs:negativeInteger"

@unique
class CategoryType(Enum):
    CONSTANT = "CONSTANT"
    PARAMETER = "PARAMETER"
    VARIABLE= "VARIABLE"

@unique
class QualifierKind(Enum):
    valueQualifier = "ValueQualifier"
    ConceptQualifier = "ConceptQualifier"
    TemplateQualifier = "TemplateQualifier"

@unique
class KeyType(Enum):
    GlobalReference ="GlobalReference"
    AnnotatedRelationshipElement ="AnnotatedRelationshipElement"
    AssetAdministrationShell ="AssetAdministrationShell"
    BasicEventElement ="BasicEventElement"
    Blob ="Blob"
    Capability ="Capability"
    ConceptDescription ="ConceptDescription"
    Identifiable ="Identifiable"
    DataElement ="DataElement"
    Entity ="Entity"
    EventElement ="EventElement"
    File ="File"
    MultiLanguageProperty ="MultiLanguageProperty"
    Operation ="Operation"
    Property ="Property"
    Range ="Range"
    ReferenceElement ="ReferenceElement"
    Referable ="Referable"
    RelationshipElement ="RelationshipElement"
    Submodel ="Submodel"
    SubmodelElement ="SubmodelElement"
    SubmodelElementList ="SubmodelElementList"
    SubmodelElementCollection ="SubmodelElementCollection"


@unique
class RefType(Enum):
    ExternalReference = "ExternalReference"
    ModelReference  = "ModelReference"

class Key:
    def __init__(self,_type:KeyType,value :str) -> None:
        self.type = _type
        self.value = value

    def serialize_json(self) -> Dict:
        data = dict()
        data["type"] = self.type
        data["value"] = self.value

        return data

    @staticmethod
    def deserialize_json(json_data) -> "Key":
        _key = Key(json_data["type"],json_data["value"])

        return _key

class LangString:
    def __init__(self, language: str, text:str) -> None:
        self.language = language
        self.text = text

    def serialize_json(self) -> Dict:
        data = dict()
        data["language"] = self.language
        data["text"] = self.text

        return data

    @staticmethod
    def deserialize_json(json_data) -> "LangString":
        _langString = LangString(json_data["language"],json_data["text"])

        return _langString

class Reference:
    def __init__(self, keys : List["Key"], _type : str,
                 referredSemanticId: Optional["Reference"] = None) -> None:
        self.type = _type
        self.keys = keys
        self.referredSemanticId = referredSemanticId

    def serialize_json(self) -> Dict:
        data = dict()
        data["type"] = self.type
        data["keys"] = [key.serialize_json() for key in self.keys]
        if self.referredSemanticId is not None: data["referredSemanticId"] = self.referredSemanticId.serialize_json()

        return data

    @staticmethod
    def deserialize_json(json_data) -> "Reference":
        _keys  = [Key.deserialize_json(_key) for _key in json_data["keys"]]
        _referredSemanticId = Reference.deserialize_json(json_data["referredSemanticId"]) if "referredSemanticId" in json_data else None
        _reference = Reference(_keys,json_data["type"],_referredSemanticId)

        return _reference

class DataSpecificationContent:
    def __init__(self):
        pass

class EmbeddedDataSpecification:
    def __init__(self,dataSpecification : Reference,
                 dataSpecificationContent : DataSpecificationContent) -> None:
        self.dataSpecification = dataSpecification
        self.dataSpecificationContent = dataSpecificationContent

    def serialize_json(self) -> Dict:
        data = dict()
        data["dataSpecification"] = self.dataSpecification
        data["dataSpecificationContent"] = self.dataSpecificationContent

        return data

    @staticmethod
    def deserialize_json(json_data) -> "EmbeddedDataSpecification":
        _dataSpecification = Reference.deserialize_json(json_data["dataSpecification"]) if "dataSpecification" in json_data else None
        _dataSpecificationContent = None

        _embeddedDataSpecification= EmbeddedDataSpecification(_dataSpecification)

        return _embeddedDataSpecification

class HasDataSpecification:
    def __init__(self, embeddedDataSpecifications : List[EmbeddedDataSpecification]):
        self.embeddedDataSpecifications = embeddedDataSpecifications

    def serialize_json(self) -> Dict:
        data = dict()
        if "embeddedDataSpecifications" in json_data : data["embeddedDataSpecifications"] = [embeddedDataSpecification.serialize_json() for embeddedDataSpecification in self.embeddedDataSpecifications]
        return data

    @staticmethod
    def deserialize_json(json_data) -> "HasDataSpecification":
        _embeddedDataSpecifications = [EmbeddedDataSpecification.deserialize_json(_embeddedDataSpecification)
                                       for _embeddedDataSpecification in json_data["embeddedDataSpecifications"]] if "embeddedDataSpecifications" in json_data else None
        _hasDataSpecification = HasDataSpecification(_embeddedDataSpecifications)

        return _hasDataSpecification

class AdministrativeInformation(HasDataSpecification):
    def __init__(self,version : Optional[str] = None,
                 revision : Optional[str] = None,
                 dataSpecifications : Optional[List["EmbeddedDataSpecification"]] = None):
        HasDataSpecification.__init__(self,dataSpecifications)
        self.version = version
        self.revision = revision
        self.dataSpecifications = dataSpecifications

    def serialize_json(self) -> Dict:
        data = dict()
        if self.version is not None : data["version"] = self.version
        if self.revision is not None : data["revision"] = self.revision
        if self.dataSpecifications is not None : data["dataSpecifications"] = HasDataSpecification.serialize_json(self)

        return data

    @staticmethod
    def deserialize_json(json_data) -> "AdministrativeInformation":
        _version = json_data["version"] if "version" in json_data else None
        _revision = json_data["_revision"] if "revision" in json_data else None
        _dataSpecifications = [EmbeddedDataSpecification.deserialize_json(_dataSpecification) for _dataSpecification in json_data["dataSpecifications"]] if "dataSpecification" in json_data else None

        _AdministrativeInformation = AdministrativeInformation(_version,_revision,_dataSpecifications)

        return _AdministrativeInformation

class HasSemantics:
    def __init__(self, semanticId: Optional[Reference] = None,
                 supplementalSemanticIds : Optional[List[Reference]] = None):

        self.semanticId = semanticId
        self.supplementalSemanticIds = supplementalSemanticIds

    def serialize_json(self) -> Dict:
        data = dict()
        if self.semanticId is not None : data["semanticId"] = self.semanticId.serialize_json()
        if self.supplementalSemanticIds is not None : data["supplementalSemanticIds"] = [supplementalSemanticId.serialize_json() for supplementalSemanticId in self.supplementalSemanticIds]

        return data

    @staticmethod
    def deserialize_json(json_data) -> "HasSemantics":
        _semanticId = Reference.deserialize_json(json_data["semanticId"]) if "semanticId" in json_data else None
        _supplementalSemanticIds  = [Reference.deserialize_json(_reference) for _reference in json_data["supplementalSemanticIds"]]  if "supplementalSemanticIds" in json_data else None

        _hasSemantics = HasSemantics(_semanticId,_supplementalSemanticIds)
        return _hasSemantics

class Qualifier(HasSemantics):
    def __init__(self,_type : str,valueType : DataTypeXSD,
                 semanticId: Optional[Reference] = None,
                 supplementalSemanticIds : Optional[List[Reference]] = None,
                 value : Optional[str] = None,valueId : Optional[Reference] = None):
        HasSemantics.__init__(self, semanticId, supplementalSemanticIds)
        self.type = _type
        self.valueType = valueType
        self.value = value
        self.valueId = valueId

    def serialize_json(self)->Dict:
        data = dict()
        if self.type is not None : data["type"] = self.type
        if self.valueType is not None : data["valueType"] = self.valueType
        if self.semanticId is not None : data["semanticId"] = self.semanticId.serialize_json()
        if self.supplementalSemanticIds is not None : data["supplementalSemanticIds"] = [supplementalSemanticId.serialize_json() for supplementalSemanticId in self.supplementalSemanticIds]
        if self.value is not None : data["value"] = self.value
        if self.valueId is not None : data["valueId"] = self.valueId.serialize_json()

        return data

    @staticmethod
    def deserialize_json(json_data) -> "Qualifier":
        _hasSemantics = HasSemantics.deserialize_json(json_data)
        _value = json_data["value"] if "value" in json_data else None
        _valueId = Reference.deserialize_json(json_data["valueId"]) if "valueId" in json_data else None

        _qualifier = Qualifier(json_data["type"],json_data["valueType"],_hasSemantics.semanticId,_hasSemantics.supplementalSemanticIds,
                               _value,_valueId)

        return _qualifier

class Extension(HasSemantics):
    def __init__(self,name : str,valueType : DataTypeXSD, semanticId: Optional[Reference] = None,
                 supplementalSemanticIds : Optional[List[Reference]] = None,
                 value : Optional[str] = None,
                 refersTo :  Optional[List[Reference]] = None):
        HasSemantics.__init__(self, semanticId, supplementalSemanticIds)
        self.name = name
        self.valueType = valueType
        self.value = value
        self.refersTo = refersTo

    def serialize_json(self)->Dict:
        data = dict()
        data["name"] = self.name
        data["valueType"] = self.valueType
        if self.semanticId is not None : data["semanticId"] = self.semanticId.serialize_json()
        if self.supplementalSemanticIds is not None : data["supplementalSemanticIds"] = [supplementalSemanticId.serialize_json() for supplementalSemanticId in self.supplementalSemanticIds]
        if self.value is not None : data["value"] = self.value
        if self.refersTo is not None: data["refersTo"] = [_reference.serialize_json() for _reference in self.refersTo]

        return data

    @staticmethod
    def deserialize_json(json_data) -> "Extension":
        _hasSemantics = HasSemantics.deserialize_json(json_data)
        _value = json_data["value"] if "value" in json_data["value"] else None
        _refersTo = Reference.deserialize_json(json_data["refersTo"]) if "refersTo" in json_data["refersTo"] else None

        _extension = Extension(json_data["name"],json_data["valueType"],_hasSemantics.semanticId,_hasSemantics.supplementalSemanticIds,
                               _value,_refersTo)

        return _extension

class HasExtensions:
    def __init__(self, extensions : Optional[List[Extension]] = None):
        self.extensions = extensions

    def serialize_json(self) -> Dict:
        data = dict()
        if self.extensions is not None : data["extensions"] = [extension.serialize_json() for extension in self.extensions]
        return data

    @staticmethod
    def deserialize_json(_extensions_list) -> "HasExtensions":
        _list = []
        for _extension in _extensions_list:
            _list.append(Extension.deserialize_json(_extension))
        _hasExtension = HasExtensions(_list)

        return _hasExtension

class Referable(HasExtensions):
    """
        An element that is referable by its idShort. This ID is not globally unique. This ID is unique
        within the name space of the element.
    """

    def __init__(self, idShort : Optional[str] = None,category : Optional[str] = None,
                 displayName : Optional[List[LangString]] = None,
                 description : Optional[List[LangString]] = None, checksum : Optional[str] = None,
                 extensions : Optional[List[Extension]] = None,) -> None:
        HasExtensions.__init__(self, extensions)
        self.idShort = idShort
        self.category = category
        self.displayName = displayName
        self.description = description
        self.checksum = checksum

    def serialize_json(self) -> Dict:
        data = dict()
        if self.idShort is not None: data["idShort"] = self.idShort
        if self.category is not None : data["category"] = self.category
        if self.displayName is not None : data["displayName"] = [langString.serialize_json() for langString in self.displayName ]
        if self.description is not None : data["description"] = [langString.serialize_json() for langString in self.description ]
        if self.checksum is not None : data["checksum"] = self.checksum
        if self.extensions is not None: data["extensions"] = HasExtensions.serialize_json(self)["extensions"]
        return data

    @staticmethod
    def deserialize_json(json_data) -> "Referable":
        _idShort = json_data["idShort"] if "idShort" in json_data else None
        _category = json_data["category"] if "category" in json_data else None
        _displayName = [LangString.deserialize_json(_langString) for _langString in json_data["displayName"]] if "displayName" in json_data else None
        _description = [LangString.deserialize_json(_langString) for _langString in json_data["description"]] if "description" in json_data else None
        _checksum = json_data["checksum"] if "checksum" in json_data else None
        _extensions = HasExtensions.deserialize_json(json_data["extensions"]).extensions if "extensions" in json_data else None
        _referable = Referable(_idShort,_category,_displayName,_description,_checksum,_extensions)

        return _referable

class Identifiable(Referable):
    """
    An element that has a globally unique identifier.
    """
    def __init__(self,_id, idShort : Optional[str] = None,
                 category : Optional[str] = None,
                 displayName : Optional[List[LangString]] = None,
                 description : Optional[List[LangString]] = None,checksum : Optional[str] = None,
                 extensions : Optional[List[Extension]] = None,
                 administration : Optional[AdministrativeInformation] = None) -> None:
        Referable.__init__(self,idShort,category,displayName,description,checksum,extensions)
        self.id = _id
        self.administration = administration

    def serialize_json(self) -> Dict:
        data = Referable.serialize_json(self)
        data["id"] = self.id
        if self.administration is not None : data["administration"] = self.administration.serialize_json()

        return data

    @staticmethod
    def deserialize_json(json_data) -> "Identifiable":
        _referable = Referable.deserialize_json(json_data)
        _administration = AdministrativeInformation.deserialize_json(json_data)  if "administration" in json_data else None

        _identifiable = Identifiable(json_data["id"],_referable.idShort,_referable.category,
                                      _referable.displayName,_referable.description,
                                     _referable.checksum,_referable.extensions,_administration)
        return _identifiable

class Qualifiable:
    def __init__(self,qualifiers : Optional[List[Qualifier]] = None) -> None:
        self.qualifiers = qualifiers

    def serialize_json(self) -> Dict:
        data = dict()
        if self.qualifiers is not None : data["qualifiers"] = [qualifier.serialize_json() for qualifier in self.qualifiers]

        return data

    @staticmethod
    def deserialize_json(json_data) -> "Qualifiable":
        _qualifiers = [ Qualifier.deserialize_json(_qualifier) for _qualifier in json_data["qualifiers"]]  if "qualifiers" in json_data else None
        _qualifiable = Qualifiable(_qualifiers)

        return _qualifiable

class HasKind:
    def __init__(self,kind : str) -> None:
        self.kind = kind

    def serialize_json(self):
        return self.kind

class SubmodelElement(Referable, HasKind,HasSemantics, Qualifiable, HasDataSpecification):
    def __init__(self, idShort : Optional[str] = None,
                 category : Optional[str] = None,
                 displayName : Optional[List[LangString]] = None,
                 description : Optional[List[LangString]] = None,checksum : Optional[str] = None,
                 extensions: Optional[List[Extension]] = None,
                 kind : Optional[str] = None,
                 semanticId: Optional[Reference] = None,
                 supplementalSemanticIds : Optional[List[Reference]] = None,
                 qualifiers : Optional[List[Qualifier]] = None,
                 embeddedDataSpecifications : List[EmbeddedDataSpecification] = None):
        Referable.__init__(self,idShort,category, displayName, description, checksum, extensions)
        HasSemantics.__init__(self, semanticId, supplementalSemanticIds)
        Qualifiable.__init__(self, qualifiers)
        HasDataSpecification.__init__(self, embeddedDataSpecifications)
        self.kind = kind
        self.modelType = ""

    def serialize_json(self) -> Dict:
        data = Referable.serialize_json(self) | HasSemantics.serialize_json(self) |  Qualifiable.serialize_json(self) | HasDataSpecification.serialize_json(self)
        if self.kind is not None : data["kind"] = self.kind
        return data

    def add(self , idShortpath :str, element : "SubmodelElement"):
        pass

    def delete(self, idShortpath :str):
        pass

    @staticmethod
    def deserialize_json(json_data : Dict) -> "SubmodelElement":
        _referable = Referable.deserialize_json(json_data)
        _hasSemantics = HasSemantics.deserialize_json(json_data)
        _qualifiable = Qualifiable.deserialize_json(json_data)
        _embeddedDataSpecifications = [EmbeddedDataSpecification.deserialize_json(_embeddedDataSpecification)
                                        for _embeddedDataSpecification in json_data["embeddedDataSpecifications"]]  if "_embeddedDataSpecification" in json_data else None
        
        _kind = json_data["kind"] if "kind" in json_data else None   
        _submodelElement = SubmodelElement(_referable.idShort,_referable.category,_referable.displayName,_referable.description,_referable.checksum,
                                           _referable.extensions,_kind,
                                           _hasSemantics.semanticId,_hasSemantics.supplementalSemanticIds,_qualifiable.qualifiers,_embeddedDataSpecifications)

        return _submodelElement

class DataElement(SubmodelElement):
    def __init__(self, idShort : Optional[str] = None,category : Optional[str] = None,
                 displayName : Optional[List[LangString]] = None,
                 description : Optional[List[LangString]] = None,checksum : Optional[str] = None,
                 extensions: Optional[List[Extension]] = None,
                 kind: Optional[str] = None,
                 semanticId: Optional[Reference] = None,
                 supplementalSemanticIds : Optional[List[Reference]] = None,
                 qualifiers : Optional[List[Qualifier]] = None,
                 embeddedDataSpecifications : List[EmbeddedDataSpecification] = None):
        SubmodelElement.__init__(self, idShort, category, displayName, description, checksum,extensions,kind,
                                 semanticId, supplementalSemanticIds,qualifiers,embeddedDataSpecifications)
        self.modelType = ""

    def serialize_json(self) -> Dict:
        data = SubmodelElement.serialize_json(self)

        return data

    @staticmethod
    def deserialize_json(json_data : Dict) -> "DataElement":
        _submodelElement = SubmodelElement.deserialize_json(json_data)
        _dataElement = DataElement(_submodelElement.idShort,_submodelElement.category,_submodelElement.displayName,
                                   _submodelElement.description,_submodelElement.checksum,_submodelElement.extensions,
                                   _submodelElement.kind,_submodelElement.semanticId,
                                   _submodelElement.supplementalSemanticIds,_submodelElement.qualifiers,
                                   _submodelElement.embeddedDataSpecifications)

        return _dataElement

class Property(DataElement):
    def __init__(self,valueType : DataTypeXSD, value : str,idShort : Optional[str] = "", 
                 category : Optional[str] = None,
                 displayName : Optional[List[LangString]] = None,
                 description : Optional[List[LangString]] = None,
                 checksum : Optional[str] = None,
                 extensions: Optional[List[Extension]] = None,
                 kind: Optional[str] = None,
                 semanticId: Optional[Reference] = None,
                 supplementalSemanticIds : Optional[List[Reference]] = None,
                 qualifiers : Optional[List[Qualifier]] = None,
                 embeddedDataSpecifications : List[EmbeddedDataSpecification] = None,
                 valueId : Optional[Reference] = None):
        DataElement.__init__(self,idShort, category, displayName, description, checksum,extensions,kind,
                                 semanticId, supplementalSemanticIds,qualifiers,embeddedDataSpecifications)
        self.valueType = valueType
        self.value = value
        self.valueId = valueId
        self.modelType = "Property"
        
    def serialize_json(self) -> Dict:
        data = DataElement.serialize_json(self)
        data["valueType"] = self.valueType
        data["value"] = self.value
        if self.valueId is not None : data["valueId"] = self.valueId.serialize_json()
        data["modelType"] = self.modelType
        return data

    @staticmethod
    def deserialize_json(json_data : Dict) -> "Property":
        _dataElement = DataElement.deserialize_json(json_data)
        _property = Property(json_data["valueType"],json_data["value"],_dataElement.idShort,
                                   _dataElement.category,_dataElement.displayName,
                                   _dataElement.description,_dataElement.checksum, _dataElement.extensions,
                                   _dataElement.kind,_dataElement.semanticId,
                                   _dataElement.supplementalSemanticIds,_dataElement.qualifiers,
                                   _dataElement.embeddedDataSpecifications)

        return _property

class MultiLanguageProperty(DataElement):
    def __init__(self,value: Optional[List[LangString]] = None, valueId: Optional[Reference] = None,
                 idShort: Optional[str] = None,
                 category : Optional[str] = None,
                 displayName : Optional[List[LangString]] = None,
                 description : Optional[List[LangString]] = None,checksum : Optional[str] = None,
                 extensions: Optional[List[Extension]] = None,
                 kind: Optional[str] = None,
                 semanticId: Optional[Reference] = None,
                 supplementalSemanticIds : Optional[List[Reference]] = None,
                 qualifiers : Optional[List[Qualifier]] = None,
                 embeddedDataSpecifications : List[EmbeddedDataSpecification] = None):
        DataElement.__init__(self, idShort, category, displayName, description, checksum, extensions, kind,
        semanticId, supplementalSemanticIds, qualifiers, embeddedDataSpecifications)

        self.value = value
        self.valueId = valueId
        self.modelType = "MultiLanguageProperty"
        
    def serialize_json(self) -> Dict:
        data = DataElement.serialize_json(self)
        if self.value is not None : data["value"] = [langString.serialize_json() for langString in self.value]
        if self.valueId is not None : data["valueId"] = self.valueId.serialize_json()
        data["modelType"] = self.modelType
        return data

    @staticmethod
    def deserialize_json(json_data : Dict) -> "MultiLanguageProperty":
        _dataElement = DataElement.deserialize_json(json_data)
        _value = [LangString.deserialize_json(_langString) for _langString in json_data["langString"]] if "langString" in json_data else None
        _valueId = Reference.deserialize_json(json_data["valueId"]) if "valueId" in json_data else None

        _MultiLanguageProperty = MultiLanguageProperty(_value,_valueId,_dataElement.idShort,
                                   _dataElement.category,_dataElement.displayName,
                                   _dataElement.description,_dataElement.checksum, _dataElement.extensions,
                                   _dataElement.kind,_dataElement.semanticId,
                                   _dataElement.supplementalSemanticIds,_dataElement.qualifiers,
                                   _dataElement.embeddedDataSpecifications)

        return _MultiLanguageProperty

class Range(DataElement):
    def __init__(self,valueType : DataTypeXSD,
                 _min : Optional[str] = None, _max : Optional[str] = None,
                 idShort : Optional[str] = None,category : Optional[str] = None,
                 displayName : Optional[List[LangString]] = None,
                 description : Optional[List[LangString]] = None,
                 checksum : Optional[str] = None,
                 extensions: Optional[List[Extension]] = None,
                 kind: Optional[str] = None,
                 semanticId: Optional[Reference] = None,
                 supplementalSemanticIds : Optional[List[Reference]] = None,
                 qualifiers : Optional[List[Qualifier]] = None,
                 embeddedDataSpecifications : List[EmbeddedDataSpecification] = None):
        DataElement.__init__(self, idShort, category, displayName, description, checksum, extensions, kind,
        semanticId, supplementalSemanticIds, qualifiers, embeddedDataSpecifications)


        self.valueType = valueType
        self.min = _min
        self.max = _max
        self.modelType = "Range"
        
    def serialize_json(self) -> Dict:
        data = DataElement.serialize_json(self)
        data["valueType"] = self.valueType
        if self.min is not None : data["min"] = self.min
        if self.max is not None : data["max"] = self.max
        data["modelType"] = self.modelType

        return data

    @staticmethod
    def deserialize_json(json_data : Dict) -> "Range":
        _dataElement = DataElement.deserialize_json(json_data)
        _min = json_data["min"] if "min" in json_data else None
        _max = json_data["max"] if "max" in json_data else None

        _range = Range(json_data["valueType"],_min,_max,_dataElement.idShort,
                                   _dataElement.category,_dataElement.displayName,
                                   _dataElement.description,_dataElement.checksum, _dataElement.extensions,
                                   _dataElement.kind,_dataElement.semanticId,
                                   _dataElement.supplementalSemanticIds,_dataElement.qualifiers,
                                   _dataElement.embeddedDataSpecifications)

        return _range

class ReferenceElement(DataElement):
    def __init__(self, value : Optional[Reference] = None, idShort : Optional[str] = None,
                 category : Optional[str] = None,
                 displayName : Optional[List[LangString]] = None,
                 description : Optional[List[LangString]] = None,checksum : Optional[str] = None,
                 extensions: Optional[List[Extension]] = None,
                 kind: Optional[str] = None,
                 semanticId: Optional[Reference] = None,
                 supplementalSemanticIds : Optional[List[Reference]] = None,
                 qualifiers : Optional[List[Qualifier]] = None,
                 embeddedDataSpecifications : List[EmbeddedDataSpecification] = None):
        DataElement.__init__(self, idShort, category, displayName, description, checksum, extensions, kind,
        semanticId, supplementalSemanticIds, qualifiers, embeddedDataSpecifications)


        self.value = value
        self.modelType = "ReferenceElement"
        
    def serialize_json(self) -> Dict:
        data = DataElement.serialize_json(self)
        if self.value is not None : data["value"] = self.value.serialize_json()
        data["modelType"] = self.modelType
        return data

    @staticmethod
    def deserialize_json(json_data : Dict):
        _dataElement = DataElement.deserialize_json(json_data)
        _value = Reference.deserialize_json(json_data["value"]) if "value" in json_data else None
        _referenceElement = ReferenceElement(_value,_dataElement.idShort,
                                   _dataElement.category,_dataElement.displayName,
                                   _dataElement.description,_dataElement.checksum, _dataElement.extensions,
                                   _dataElement.kind,_dataElement.semanticId,
                                   _dataElement.supplementalSemanticIds,_dataElement.qualifiers,
                                   _dataElement.embeddedDataSpecifications)

        return _referenceElement

class Blob(DataElement):
    def __init__(self,contentType : str , value : Optional[bytes] = None, idShort : Optional[str] = None,
                 category : Optional[str] = None,
                 displayName : Optional[List[LangString]] = None,
                 description : Optional[List[LangString]] = None,checksum : Optional[str] = None,
                 extensions: Optional[List[Extension]] = None,
                 kind: Optional[str] = None,
                 semanticId: Optional[Reference] = None,
                 supplementalSemanticIds : Optional[List[Reference]] = None,
                 qualifiers : Optional[List[Qualifier]] = None,
                 embeddedDataSpecifications : List[EmbeddedDataSpecification] = None):
        DataElement.__init__(self, idShort, category, displayName, description, checksum, extensions, kind,
        semanticId, supplementalSemanticIds, qualifiers, embeddedDataSpecifications)

        self.value = value
        self.contentType = contentType
        self.modelType = "Blob"

    def serialize_json(self) -> Dict:
        data = DataElement.serialize_json(self)
        if self.value is not None : data["value"] = self.value
        data["contentType"] = self.contentType
        data["modelType"] = self.modelType
        return data


    @staticmethod
    def deserialize_json(json_data : Dict):
        _dataElement = DataElement.deserialize_json(json_data)
        _value = json_data["value"] if "value" in json_data else None

        _blob = Blob(json_data["contentType"],_value,_dataElement.idShort,
                                   _dataElement.category,_dataElement.displayName,
                                   _dataElement.description,_dataElement.checksum, _dataElement.extensions,
                                   _dataElement.kind,_dataElement.semanticId,
                                   _dataElement.supplementalSemanticIds,_dataElement.qualifiers,
                                   _dataElement.embeddedDataSpecifications)

        return _blob

class File(DataElement):
    def __init__(self,contentType : str , value : Optional[str] = None,
                 category : Optional[str] = None, idShort : Optional[str] = None,
                 displayName : Optional[List[LangString]] = None,
                 description : Optional[List[LangString]] = None,checksum : Optional[str] = None,
                 extensions: Optional[List[Extension]] = None,
                 kind: Optional[str] = None,
                 semanticId: Optional[Reference] = None,
                 supplementalSemanticIds : Optional[List[Reference]] = None,
                 qualifiers : Optional[List[Qualifier]] = None,
                 embeddedDataSpecifications : List[EmbeddedDataSpecification] = None):
        DataElement.__init__(self, idShort, category, displayName, description, checksum, extensions, kind,
        semanticId, supplementalSemanticIds, qualifiers, embeddedDataSpecifications)
        self.value = value
        self.contentType = contentType
        self.modelType = "File"

    def serialize_json(self) -> Dict:
        data = DataElement.serialize_json(self)
        if self.value is not None : data["value"] = self.value
        data["contentType"] = self.contentType
        data["modelType"] = self.modelType
        return data


    @staticmethod
    def deserialize_json(json_data : Dict):
        _dataElement = DataElement.deserialize_json(json_data)
        _value = json_data["value"] if "value" in json_data else None

        _file = File(json_data["contentType"],_value,_dataElement.idShort,
                                   _dataElement.category,_dataElement.displayName,
                                   _dataElement.description,_dataElement.checksum, _dataElement.extensions,_dataElement.semanticId,
                                   _dataElement.supplementalSemanticIds,_dataElement.qualifiers,
                                   _dataElement.embeddedDataSpecifications)

        return _file

class SubmodelElementCollection(SubmodelElement):
    def __init__(self, idShort : Optional[str] = None,
                 category : Optional[str] = None,
                 displayName : Optional[List[LangString]] = None,
                 description : Optional[List[LangString]] = None,checksum : Optional[str] = None,
                 extensions : Optional[List[Extension]] = None,kind: Optional[str] = None,
                 semanticId: Optional[Reference] = None,
                 supplementalSemanticIds : Optional[List[Reference]] = None,
                 qualifiers : Optional[List[Qualifier]] = None,
                 embeddedDataSpecifications : List[EmbeddedDataSpecification] = None,
                 value : Optional[List[SubmodelElement]] = None):
        SubmodelElement.__init__(self, idShort, category, displayName, description, checksum,extensions,kind,
                                 semanticId, supplementalSemanticIds,qualifiers,embeddedDataSpecifications)
        self.value = value
        self.hasDict = HashMap()
        self.modelType = "SubmodelElementCollection"

    @staticmethod
    def deserialize_json(json_data):
        _submodel_element = SubmodelElement.deserialize_json(json_data)
        _element_dict = dict()
        for _collection_element in json_data["value"]:
            _element_type = _collection_element["modelType"]
            _element = eval(_element_type).deserialize_json(_collection_element)
            _element_dict[_submodel_element.idShort + "." + _element.idShort] = _element
            if _element.modelType == "SubmodelElementCollection":
                #_element.hasDict.modify_namespaces(_submodel_element.idShort)
                _elem_Hash_dict = _element.hasDict.dict()
                for key in list(_elem_Hash_dict.keys()):
                    _element_dict[_submodel_element.idShort + "." + key] = _elem_Hash_dict[key]

        _submodelCollection = SubmodelElementCollection(_submodel_element.idShort, _submodel_element.category,
                                _submodel_element.displayName, _submodel_element.description,
                                _submodel_element.checksum,_submodel_element.extensions,_submodel_element.kind,_submodel_element.semanticId, _submodel_element.supplementalSemanticIds,
                                _submodel_element.qualifiers, _submodel_element.embeddedDataSpecifications)

        _submodelCollection.hasDict.extend(_element_dict)

        return _submodelCollection

    def get(self, idShortPath: str) -> Any:
        return self.hasDict.get(idShortPath).serialize_json()

    def delete(self, idShortPath: str) -> bool:
        if self.hasDict.isNamespacePresent(idShortPath):
            self.hasDict.delete(idShortPath)
            _id_short_path_split = idShortPath.split(".")
            if len(_id_short_path_split) > 2:
                self.hasDict.get(idShortPath[:-2]).delete(idShortPath[:-1])
            return True
        else:
            return False

    def append(self,_element : SubmodelElement, idShortPath: Optional[str] = None) -> bool:
        if idShortPath is not None:
            if self.hasDict.isNamespacePresent(idShortPath):
                id_Split =  idShortPath.split(".")
                for i in range(len(id_Split)-1,-1,-1):
                    _temp_idSHortPath = ".".join(id_Split[i:])   
                    _child_Path = ".".join(id_Split[0:i+1]) 
                    self.hasDict.get(_child_Path).hasDict.insert(_temp_idSHortPath + "." + _element.idShort if _temp_idSHortPath != "" else _element.idShort ,_element)
                self.hasDict.insert(".".join(id_Split)+"."+_element.idShort,_element)
                return True
            else:
                return False
        else:
            self.hasDict.insert(self.idShort+"."+_element.idShort,_element)
            return True


    def serialize_json(self) -> Dict:
        data = SubmodelElement.serialize_json(self)
        if self.hasDict.count() > 0 :
            values = [] 
            #print(list(self.hasDict.dict().keys()),self.idShort)
            for key,element in self.hasDict.dict().items():
                if len(key.split(".")) == 2:
                    values.append(element.serialize_json())
                else:
                    pass
            data["value"] = values
        data["modelType"] = self.modelType
        return data

class Capability(SubmodelElement):
    def __init__(self,extensions : Optional[List[Extension]] = None,
                 category : Optional[str] = None, idShort : Optional[str] = None,
                 displayName : Optional[List[LangString]] = None,
                 description : Optional[List[LangString]] = None,checksum : Optional[str] = None,
                 kind: Optional[str] = None,
                 semanticId: Optional[Reference] = None,
                 supplementalSemanticIds : Optional[List[Reference]] = None,
                 qualifiers : Optional[List[Qualifier]] = None,
                 embeddedDataSpecifications : List[EmbeddedDataSpecification] = None):
        SubmodelElement.__init__(self, extensions, category, idShort, displayName, description, checksum,kind,
                                 semanticId, supplementalSemanticIds,qualifiers,embeddedDataSpecifications)
        self.modelType = "Capability"

    def serialize_json(self) -> Dict:
        data = SubmodelElement.serialize_json(self)
        data["modelType"] = self.modelType
        return data

class EventElement(SubmodelElement):
    def __init__(self,extensions : Optional[List[Extension]] = None,
                 category : Optional[str] = None, idShort : Optional[str] = None,
                 displayName : Optional[List[LangString]] = None,
                 description : Optional[List[LangString]] = None,checksum : Optional[str] = None,
                 kind: Optional[str] = None,
                 semanticId: Optional[Reference] = None,
                 supplementalSemanticIds : Optional[List[Reference]] = None,
                 qualifiers : Optional[List[Qualifier]] = None,
                 embeddedDataSpecifications : List[EmbeddedDataSpecification] = None):
        SubmodelElement.__init__(self, extensions, category, idShort, displayName, description, checksum,kind,
                                 semanticId, supplementalSemanticIds,qualifiers,embeddedDataSpecifications)
        
    def serialize_json(self) -> Dict:
        data = SubmodelElement.serialize_json(self)
        return data

class Direction:
    pass

class StateOfEvent:
    pass

class BasicEventElement(EventElement):
    def __init__(self,
                 observed: Reference, direction: Direction, state: StateOfEvent,
                 messageTopic: Optional[str] = None, messageBroker: Optional[Reference] = None,
                 lastUpdate: Optional[str] = None, minInterval: Optional[str] = None,
                 maxInterval: Optional[str] = None,idShort : Optional[str] = None,
                 category : Optional[str] = None,
                 displayName : Optional[List[LangString]] = None,
                 description : Optional[List[LangString]] = None,checksum : Optional[str] = None,
                 extensions: Optional[List[Extension]] = None,
                 kind: Optional[str] = None,
                 semanticId: Optional[Reference] = None,
                 supplementalSemanticIds : Optional[List[Reference]] = None,
                 qualifiers : Optional[List[Qualifier]] = None,
                 embeddedDataSpecifications : List[EmbeddedDataSpecification] = None,
                 ):
        EventElement.__init__(self, extensions, category, idShort, displayName, description, checksum,kind,
                                 semanticId, supplementalSemanticIds,qualifiers,embeddedDataSpecifications)
        self.observed = observed
        self.direction = direction
        self.state = state
        self.messageTopic = messageTopic
        self.messageBroker = messageBroker
        self.lastUpdate = lastUpdate
        self.minInterval = minInterval
        self.maxInterval = maxInterval
        self.modelType = "BasicEventElement"

    def serialize_json(self)->Dict:
        data = EventElement.serialize_json(self)
        data["observed"] = self.observed
        data["direction"] = self.direction
        data["state"] = self.state
        if self.messageTopic is not None : data["messageTopic"] = self.messageTopic
        if self.messageBroker is not None : data["messageBroker"] = self.messageBroker.serialize_json()
        if self.lastUpdate is not None : data["lastUpdate"] = self.lastUpdate
        if self.minInterval is not None : data["minInterval"] = self.minInterval
        if self.maxInterval is not None : data["maxInterval"] = self.maxInterval
        data["modelType"] = self.modelType

        return data

class SpecificAssetID(HasSemantics):
    def __init__(self,name : str,value : str,semanticId: Optional[Reference] = None,
                 supplementalSemanticIds : Optional[List[Reference]] = None):
        HasSemantics.__init__(self, semanticId, supplementalSemanticIds)
        self.name = name
        self.value = value

    def serialize_json(self) -> Dict:
        data = HasSemantics.serialize_json(self)
        data["name"] = self.name
        data["value"] = self.value

        return data

class Resource:
    def __init__(self,path,contentType):
        self.path = path
        self.contentType = contentType

    def serialize_json(self) -> Dict:
        data = dict()
        data["path"] = self.path
        data["contentType"] = self.contentType

        return  data

class AssetKind:
    pass

class AssetInformation:
    def __init__(self,assetKind : AssetKind,globalAssetId : Optional[str],
                 specificAssetId : Optional[List[SpecificAssetID]] = None,
                 defaultThumbnail : Optional[Resource] = None):
        self.assetKind = assetKind
        self.globalAssetId = globalAssetId
        self.specificAssetId = specificAssetId
        self.defaultThumbnail = defaultThumbnail

    def serialize_json(self) -> Dict:
        data = dict()
        data["assetKind"] = self.assetKind
        if self.globalAssetId is not None : data["globalAssetId"] = self.globalAssetId
        if self.specificAssetId is not None : data["specificAssetId"] = self.specificAssetId
        if self.defaultThumbnail is not None : data["defaultThumbnail"] = self.defaultThumbnail

        return data

class AssetAdministrationShell(Identifiable,HasDataSpecification):
    def __init__(self,_id : str,assetInformation : AssetInformation,
                 extensions : Optional[List[Extension]] = None,
                 category : Optional[str] = None, idShort : Optional[str] = None,
                 displayName : Optional[List[LangString]] = None,
                 description : Optional[List[LangString]] = None,checksum : Optional[str] = None,
                 administration : Optional[AdministrativeInformation] = None,
                 embeddedDataSpecifications: Optional[List[EmbeddedDataSpecification]] = None,
                 derivedFrom: Optional["Reference"] = None,
                 submodels: Optional[List["Reference"]] = None):
        Identifiable.__init__(self, _id, extensions, category, idShort, displayName, description, checksum, administration)
        HasDataSpecification.__init__(self, embeddedDataSpecifications)
        self.assetInformation = assetInformation
        self.derivedFrom = derivedFrom
        self.submodels = submodels

    def serialize_json(self)->Dict:
        data =  Identifiable.serialize_json(self) | HasDataSpecification.serialize_json(self)
        data["assetInformation"] = self.assetInformation
        if self.derivedFrom is not None : data["derivedFrom"] = self.derivedFrom
        if self.submodels is not None : data["submodels"] = [reference.serialize_json() for reference in self.submodels]

        return data

class UUIDGenerator:

    @staticmethod
    def getnewUUID() -> str:
        """
            returns an uuid of type str
        """
        return str(uuid.uuid4())

class HashMap:
    def __init__(self):
        super().__init__()
        self.hashDict = dict()
        self.elementCount = 0
        
    def count(self) -> int:
        """
        """
        return len(list(self.hashDict.keys()))

    def insert(self, key, hashObject) -> None:
        """
        """
        self.elementCount = self.elementCount + 1
        self.hashDict[key] = hashObject

    def delete(self, key) -> None:
        """
        """
        self.elementCount = self.elementCount - 1
        del self.hashDict[key]

    def get(self, key) -> SubmodelElement:
        """
        """
        return self.hashDict[key]

    def get_namespaces(self) -> list:
        """
        """
        return list(self.hashDict.keys())

    def isNamespacePresent(self, key) -> bool:
        """
        """
        if key in list(self.hashDict.keys()):
            return True
        else:
            return False

    def extend(self, hashDict : Dict ) -> None:
        for key in hashDict.keys():
            self.insert(key,hashDict[key])

    def dict(self) -> Dict:
        return self.hashDict

    def modify_namespaces(self,_namespace) -> bool:
        _keys = list(self.hashDict.keys())
        for key in _keys:
            self.hashDict[_namespace + "." + key] = self.hashDict[key]
            del self.hashDict[key]
        return True

    def get_entries(self) -> List:
        return  list(self.hashDict.values())

class Submodel(Identifiable, HasKind, HasSemantics, Qualifiable, HasDataSpecification):
    """
    A submodel defines a specific aspect of the asset represented by the AAS.
    A submodel is used to structure the digital representation and technical
    functionality of an Administration Shell into distinguishable parts. Each submodel
    refers to a well-defined domain or subject matter. Submodels can become
    standardized and, thus, become submodels templates.
    """
    __uuid_gen = UUIDGenerator()

    def __init__(self,_id : str, idShort : Optional[str] = None,
                 category : Optional[str] = None,
                 displayName : Optional[List[LangString]] = None,
                 description : Optional[List[LangString]] = None,checksum : Optional[str] = None,
                 extensions: Optional[List[Extension]] = None,
                 administration : Optional[AdministrativeInformation] = None,
                 kind : Optional[HasKind] = None, semanticId : Optional[Reference] = None,
                 supplementalSemanticIds : Optional[List[Reference]] = None,
                 qualifiers : Optional[List[Qualifier]] = None,
                 embeddedDataSpecifications: Optional[List[EmbeddedDataSpecification]] = None,
                 submodelElements : Optional[HashMap] = None
                 ) -> None:
        Identifiable.__init__(self, _id, idShort,category, displayName, description, checksum,extensions, administration)
        Qualifiable.__init__(self, qualifiers)
        HasSemantics.__init__(self, semanticId, supplementalSemanticIds)
        HasDataSpecification.__init__(self, embeddedDataSpecifications)
        self.submodelElements = submodelElements
        self.modelType = "Submodel"
        self.hasDict = HashMap()
        self.kind = kind

    @staticmethod
    def deserialize_json(json_data):
        _identifiable = Identifiable.deserialize_json(json_data)
        _hasSemantics = HasSemantics.deserialize_json(json_data)
        _qualifiable = Qualifiable.deserialize_json(json_data)
        _hasDataSpecification = HasDataSpecification.deserialize_json(json_data)
        _kind = json_data["kind"] if "kind" in json_data else None

        submodel = Submodel(_identifiable.id, _identifiable.idShort, _identifiable.category,
                            _identifiable.displayName, _identifiable.description,
                            _identifiable.checksum, _identifiable.extensions, _identifiable.administration, _kind,
                            _hasSemantics.semanticId, _hasSemantics.supplementalSemanticIds, _identifiable.extensions,
                            _qualifiable.qualifiers, _hasDataSpecification.embeddedDataSpecifications)

        if "submodelElements" in json_data:
            _element_dict = dict()
            for _submodelElement in json_data["submodelElements"]:
                _element_type = _submodelElement["modelType"]
                _element = eval(_element_type).deserialize_json(_submodelElement)
                _element_dict[_element.idShort] = _element
                if _element.modelType == "SubmodelElementCollection":
                    _element_dict = _element_dict | _element.hasDict.dict()

            submodel.hasDict.extend(_element_dict)
        return submodel

    def get(self,idShortPath : str) -> Any:
        if self.hasDict.isNamespacePresent(idShortPath):
            return self.hasDict.get(idShortPath)
        else:
            return None

    def delete(self, idShortPath : str) -> bool:
        if self.hasDict.isNamespacePresent(idShortPath):
            self.hasDict.delete(idShortPath)
            _id_short_path_split = idShortPath.split(".")
            if len(_id_short_path_split) > 1:
                self.hasDict.get(idShortPath[:-2]).delete(idShortPath[:-1])
            return  True
        else:
            return False

    def append(self,_element : SubmodelElement, idShortPath: Optional[str] = None) -> bool:
        if idShortPath is not None:
            if self.hasDict.isNamespacePresent(idShortPath):
                id_Split =  idShortPath.split(".")
                for i in range(len(id_Split)-1,-1,-1):
                    _temp_idSHortPath = ".".join(id_Split[i:])   
                    _child_Path = ".".join(id_Split[0:i+1]) 
                    self.hasDict.get(_child_Path).hasDict.insert(_temp_idSHortPath + "." + _element.idShort if _temp_idSHortPath != "" else _element.idShort ,_element)
                self.hasDict.insert(".".join(id_Split)+"."+_element.idShort,_element)
                return True
            else:
                return False
        else:
            self.hasDict.insert(_element.idShort,_element)
            return True
            
    def serialize_json(self) -> Dict:
        data =  Identifiable.serialize_json(self)  | Qualifiable.serialize_json(self) | HasSemantics.serialize_json(self) | HasDataSpecification.serialize_json(self)
        if self.kind is not None : data["kind"] = self.kind
        data["modelType"] = self.modelType

        if self.hasDict.count() > 0:
            submodelElements = []
            for key,element in self.hasDict.dict().items():
                if len(key.split(".")) == 1 :
                    submodelElements.append(element.serialize_json())
            data["submodelElements"] = submodelElements
        return data

class ConceptDescription(Identifiable,HasDataSpecification):
    def __init__(self,_id : str,
                 extensions : Optional[List[Extension]] = None,
                 category : Optional[str] = None, idShort : Optional[str] = None,
                 displayName : Optional[List[LangString]] = None,
                 description : Optional[List[LangString]] = None,checksum : Optional[str] = None,
                 administration : Optional[AdministrativeInformation] = None,
                 embeddedDataSpecifications: Optional[List[EmbeddedDataSpecification]] = None,
                 isCaseOf : Optional[List[Reference]] = None
                 ):
        Identifiable.__init__(self, _id, extensions, category, idShort, displayName, description, checksum, administration)
        HasDataSpecification.__init__(self, embeddedDataSpecifications)
        self.isCaseOf = isCaseOf

    def serialize_json(self) -> Dict:
        data =  Identifiable.serialize_json(self) | HasDataSpecification.serialize_json(self)
        if self.isCaseOf is not None : data["isCaseOf"] = [reference.serialize_json() for reference in self.isCaseOf]

        return data

class Environment:
    def __init__(self, assetAdministrationShells : Optional[List[AssetAdministrationShell]] = None,
                submodels : Optional[List[Submodel]] = None,
                conceptDescriptions : Optional[List[ConceptDescription]] = None
                ):
        self.assetAdministrationShells = assetAdministrationShells
        self.submodels = submodels
        self.conceptDescriptions = conceptDescriptions

    def serialize_json(self) -> Dict:
        data = dict()
        if self.assetAdministrationShells is not None : data["assetAdministrationShells"] = [assetAdministrationShell.serialize_json() for assetAdministrationShell in self.assetAdministrationShells]
        if self.submodels is not None : data["submodels"] = [submodel.serialize_json() for submodel in self.submodels]
        if self.conceptDescriptions is not None : data["conceptDescriptions"] = [conceptDescription.serialize_json() for conceptDescription in self.conceptDescriptions]

        return data

import json

with open("status2.json", encoding='utf-8') as json_file:
    json_data = json.load(json_file)
    _submodel = Submodel.deserialize_json(json_data)
    _property = Property("xs:string","HelloWorld","Test1")
    _submodel.add(_property,"TechnicalProperties.WorkpieceProperties.Dimensions")
    print(json.dumps(_submodel.serialize_json()))
    print("============")
    #print(_submodel.hasDict.hashDict.keys())
