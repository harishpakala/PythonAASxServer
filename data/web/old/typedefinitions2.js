class Key{
	constructor(type, value,uuid){
		this.type = type;
		this.value = value;
		this.uuid = uuid;
	}
    serialize(){
        return {"type":this.type,"value":this.value};
        }
}
class Reference{
	constructor(type,keys,referredSemanticId,uuid){
		this.type = type;
		this.keys = keys;
		this.referredSemanticId = referredSemanticId;
		this.uuid = uuid;
	}
	serialize(){
		let jsonData = {};
		jsonData["type"] = this.type;
		if (this.keys.length > 0)   jsonData["keys"] = this.keys.map(x => {return x.serialize();});
		if (this.referredSemanticId != null)  jsonData["referredSemanticId"] = this.referredSemanticId.serialize();
		return jsonData;
	}
}
class LangString{
    constructor(language, text,_uuid = ""){
        this.language = language;
        this.text = text;
        this._uuid = _uuid;
    }
    serialize(){
        return {"language":this.language,
        		"text":this.text};
        }
}
class EmbeddedDataSpecification{
	constructor(dataSpecification,dataSpecificationContent){
		this.dataSpecification = dataSpecification;
		this.dataSpecificationContent = dataSpecificationContent;
	}
    serialize(){
    	if (this.dataSpecification != null)  jsonData["dataSpecification"] = this.dataSpecification.serialize();
    	if (this.dataSpecificationContent != null)  jsonData["dataSpecificationContent"] = this.dataSpecificationContent.serialize();
    }
}
class HasDataSpecification{
	constructor(embeddedDataSpecifications){
		this.embeddedDataSpecifications = embeddedDataSpecifications;
	}
	serialize(){
		let jsonData = {}
		if (this.embeddedDataSpecifications.length > 0) jsonData["embeddedDataSpecifications"] = this.embeddedDataSpecifications.map(x => {return x.serialize();});
		return jsonData;
	}
}
class AdministrativeInformation extends HasDataSpecification{
    constructor(version, revision,dataSpecifications){
    	super(dataSpecifications);
        this.version = version;
        this.revision = revision;
    }
    serialize(){
        let jsonData = super.serialize();
        jsonData["version"] = this.version;
        jsonData["revision"] = this.revision;
        return jsonData;
    }
}
class HasSemantics{
	constructor(semanticId,supplementalSemanticIds){
		this.semanticId = semanticId
		this.supplementalSemanticIds = supplementalSemanticIds
	}
	serialize(){
		let jsonData = {}
		if (this.semanticId != null)  jsonData["semanticId"] = this.semanticId.serialize(); 
		if (this.supplementalSemanticIds.length > 0)   jsonData["supplementalSemanticIds"] = this.supplementalSemanticIds.map(x => {return x.serialize();});
		return jsonData
	}
}
class Qualifier extends HasSemantics{
	constructor(type,valueType,semanticId,supplementalSemanticIds,kind,
				value,valueId){
		super(semanticId,supplementalSemanticIds);
		this.type = type;
		this.valueType = valueType;
		this.kind = kind;
		this.value = value;
		this.valueId = valueId;
	}
	serialize(){
		jsonData = super.serialize();
		if (this.type != null)  jsonData["type"] = this.type;
		if (this.valueType != null)  jsonData["valueType"] = this.valueType;
		if (this.value != null)  jsonData["value"] = this.valueType;
		if (this.value != null)  jsonData["value"] = this.valueId.map(x => {return x.serialize();});
		return jsonData;
	}
}

class Extension extends HasSemantics{
	constructor(name,semanticId,supplementalSemanticIds,
			valueType,value,refersTo,uuid){
		super(semanticId,supplementalSemanticIds);
		this.valueType = valueType;
		this.value = value;
		this.refersTo = refersTo;
		this.uuid = uuid;
	}
	serialize(){
		let jsonData = super.serialize();
		if (this.value != null)  jsonData["value"] = this.value;
		if (this.valueType != null)  jsonData["valueType"] = this.idShort;
		if (this.refersTo != null)  jsonData["idShort"] = this.refersTo.serialize();
		return jsonData;
	}
}
class HasExtensions {
	constructor(extensions){
		this.extensions = extensions;
	}
	serialize(){
		let jsonData = {};
		if (this.extensions.length > 0)   jsonData["extensions"] = this.extensions.map(x => {return x.serialize();});
		return jsonData;
	}
}
class Referable extends HasExtensions{
	constructor(extensions,category,idShort,displayName,description,checksum){
		super(extensions);
		this.category = category;
	    this.idShort = idShort;
	    this.displayName = displayName;
	    this.description = description;
	    this.checksum = checksum;
	}
	serialize(){
		let jsonData = super.serialize();
		if (this.idShort != null)  jsonData["idShort"] = this.idShort;
		if (this.category != null)  jsonData["category"] = this.category;
		if (this.displayName.length > 0)   jsonData["displayName"] = this.displayName.map(x => {return x.serialize();});
		if (this.description.length > 0)   jsonData["description"] = this.description.map(x => {return x.serialize();});
		if (this.checksum != null)  jsonData["checksum"] = this.checksum;
		return jsonData;
	}
}
class Identifiable extends Referable{
	constructor(id,extensions,category,idShort,displayName,description,checksum,administration){
		super(extensions,category,idShort,displayName,description,checksum);
	    this.id = id;
	    this.administration = administration;
	}
	serialize(){
		let jsonData = super.serialize();
		jsonData["id"] = this.id;
		if (this.administration) jsonData["administration"] = this.administration.serialize();
		return jsonData;
	}
}
class HasKind{
	constructor(kind){
		this.kind = kind
	}
}
class Qualifiable{
	constructor(qualifiers){
		this.qualifiers = qualifiers
	}
	serialize(){
		let jsonData = {}
		if (this.qualifiers.length > 0)   jsonData["qualifiers"] = this.qualifiers.map(x => {return x.serialize();});
		return jsonData;
	}
}
class SubmodelElement extends Referable {
	constructor(extensions,category,idShort,displayName,description,
			checksum,kind,semanticId,supplementalSemanticIds,
			qualifiers,embeddedDataSpecifications){
		   super(extensions,category,idShort,displayName,description,
			checksum);
		   this.kind = kind;
		   this.semanticId = semanticId;
		   this.supplementalSemanticIds = supplementalSemanticIds; 
		   this.qualifiers = qualifiers;
		   this.embeddedDataSpecifications = embeddedDataSpecifications;
		}	
	serialize(){
		let jsonData =  super.serialize();
		if (this.kind != null) jsonData["kind"] = this.kind;
		if (this.semanticId != null) jsonData["semanticId"] = this.semanticId.serialize();
		if (this.supplementalSemanticIds.length > 0) jsonData["supplementalSemanticIds"] = this.supplementalSemanticIds.map(x => {return x.serialize();});
		if (this.qualifiers.length > 0) sjsonData["qualifiers"] = this.qualifiers.map(x => {return x.serialize();});
		if (this.embeddedDataSpecifications.length > 0)	jsonData["embeddedDataSpecifications"] = this.embeddedDataSpecifications.map(x => {return x.serialize();});
		
		return jsonData;
	}
}
class DataElement extends SubmodelElement{
	constructor(extensions,category,idShort,displayName,description,
			checksum,kind,semanticId,supplementalSemanticIds,
			qualifiers,embeddedDataSpecifications){
			super(extensions,category,idShort,displayName,description,
					checksum,kind,semanticId,supplementalSemanticIds,
					qualifiers,embeddedDataSpecifications);
		}
	serialize(){
		let jsonData =  super.serialize();
		return jsonData;
	}
}
class Property extends DataElement{
	constructor(extensions,category,idShort,displayName,description,
			checksum,kind,semanticId,supplementalSemanticIds,
			qualifiers,embeddedDataSpecifications,
			valueType,
			value,
			valueId){
			super(extensions,category,idShort,displayName,description,
					checksum,kind,semanticId,supplementalSemanticIds,
					qualifiers,embeddedDataSpecifications);
			this.valueType = valueType
			this.value = value;
			this.valueId =valueId;
	}
	serialize(){
		let jsonData =  super.serialize();
		if (this.value != null) jsonData["value"] = this.value;
		if (this.valueType != null) jsonData["valueType"] = this.valueType;
		if (this.valueId != null) jsonData["valueId"] = this.valueId.serialize();
		jsonData["modelType"] = "Property";
		return jsonData;
	}
}
class MultiLanguageProperty extends DataElement{
	constructor(extensions,category,idShort,displayName,description,
			checksum,kind,semanticId,supplementalSemanticIds,
			qualifiers,embeddedDataSpecifications,
			value,
			valueId){
			super(extensions,category,idShort,displayName,description,
					checksum,kind,semanticId,supplementalSemanticIds,
					qualifiers,embeddedDataSpecifications);
			this.value = value;
			this.valueId =valueId;	
	}
	serialize(){
		let jsonData =  super.serialize();
		if (this.value.length > 0) jsonData["value"] = this.value.map(x => {return x.serialize();});
		if (this.valueId != null) jsonData["valueId"] = this.valueId.serialize();
		jsonData["modelType"] = "MultiLanguageProperty";
		return jsonData;
	}
}
class Range extends DataElement{
	constructor(extensions,category,idShort,displayName,description,
			checksum,kind,semanticId,supplementalSemanticIds,
			qualifiers,embeddedDataSpecifications,
			valueType,
			min,
			max){
			super(extensions,category,idShort,displayName,description,
					checksum,kind,semanticId,supplementalSemanticIds,
					qualifiers,embeddedDataSpecifications);
			this.valueType = valueType;
			this.min =min;
			this.max = max;
	}
	serialize(){
		let jsonData =  super.serialize();
		if (this.valueType != null) jsonData["valueId"] = this.valueType;
		if (this.min != null) jsonData["min"] = this.min;
		if (this.max != null) jsonData["max"] = this.max;
		jsonData["modelType"] = "Range";
		return jsonData;
	}
}
class ReferenceElement extends DataElement{
	constructor(extensions,category,idShort,displayName,description,
			checksum,kind,semanticId,supplementalSemanticIds,
			qualifiers,embeddedDataSpecifications,
			value){
			super(extensions,category,idShort,displayName,description,
					checksum,kind,semanticId,supplementalSemanticIds,
					qualifiers,embeddedDataSpecifications);
			this.value = value;
	}		
	serialize(){
		let jsonData =  super.serialize();
		if (this.value.length > 0) jsonData["value"] = this.value.map(x => {return x.serialize();});
		jsonData["modelType"] = "ReferenceElement";
		return jsonData;
	}	
}
class Blob extends DataElement{
	constructor(extensions,category,idShort,displayName,description,
			checksum,kind,semanticId,supplementalSemanticIds,
			qualifiers,embeddedDataSpecifications,
			value,
			contentType){
			super(extensions,category,idShort,displayName,description,
					checksum,kind,semanticId,supplementalSemanticIds,
					qualifiers,embeddedDataSpecifications);
			this.value = value;
			this.contentType = contentType;
	}
	serialize(){
		let jsonData =  super.serialize();
		if (this.value != null) jsonData["value"] = this.value;
		if (this.contentType != null) jsonData["contentType"] = this.contentType;
		jsonData["modelType"] = "Blob";
		return jsonData;
	}	
}
class File extends DataElement{
	constructor(extensions,category,idShort,displayName,description,
			checksum,kind,semanticId,supplementalSemanticIds,
			qualifiers,embeddedDataSpecifications,
			value,
			contentType){
			super(extensions,category,idShort,displayName,description,
					checksum,kind,semanticId,supplementalSemanticIds,
					qualifiers,embeddedDataSpecifications);
			this.value = value;
			this.contentType = contentType;		
	}
	serialize(){
		let jsonData =  super.serialize();
		if (this.value != null) jsonData["value"] = this.value;
		if (this.contentType != null) jsonData["contentType"] = this.contentType;
		jsonData["modelType"] = "Blob";
		return jsonData;
	}
}
class SubmodelElementCollection extends SubmodelElement{
	constructor(extensions,category,idShort,displayName,description,
			checksum,kind,semanticId,supplementalSemanticIds,
			qualifiers,embeddedDataSpecifications,value){
				super(extensions,category,idShort,displayName,description,
						checksum,kind,semanticId,supplementalSemanticIds,
						qualifiers,embeddedDataSpecifications);
				this.value = value;
			}
	serialize(){
		let jsonData =  super.serialize();
		if (this.value.length > 0) jsonData["value"] = this.value.map(x => {return x.serialize();});
		jsonData["modelType"] = "SubmodelElementCollection";
		return jsonData;
	}
}
class Capability extends SubmodelElement{
	constructor(extensions,category,idShort,displayName,description,
			checksum,kind,semanticId,supplementalSemanticIds,
			qualifiers,embeddedDataSpecifications
			){
			super(extensions,category,idShort,displayName,description,
					checksum,kind,semanticId,supplementalSemanticIds,
					qualifiers,embeddedDataSpecifications);
	}
	serialize(){
		let jsonData =  super.serialize();
		jsonData["modelType"] = "Capability";
		return jsonData;
	}			
}
class EventElement extends SubmodelElement{
	constructor(extensions,category,idShort,displayName,description,
			checksum,kind,semanticId,supplementalSemanticIds,
			qualifiers,embeddedDataSpecifications
			){
			super(extensions,category,idShort,displayName,description,
					checksum,kind,semanticId,supplementalSemanticIds,
					qualifiers,embeddedDataSpecifications);
	}
	serialize(){
		let jsonData =  super.serialize();
		return jsonData;
	}	
}
class BasicEventElement extends EventElement {
	constructor(extensions,category,idShort,displayName,description,
			checksum,kind,semanticId,supplementalSemanticIds,
			qualifiers,embeddedDataSpecifications,
			observed,direction,state,messageTopic,messageBroker,
			lastUpdate,minInterval,maxInterval
			){
			super(extensions,category,idShort,displayName,description,
					checksum,kind,semanticId,supplementalSemanticIds,
					qualifiers,embeddedDataSpecifications);
			this.observed = observed;
			this.direction = direction;
			this.state = state;
			this.messageTopic = messageTopic;
			this.messageBroker = messageBroker;
			this.lastUpdate = lastUpdate;
			this.minInterval = minInterval;
			this.maxInterval = maxInterval;
	}
	serialize(){
		let jsonData =  super.serialize();
		if (this.observed != null) jsonData["observed"] = this.observed.serialize();
		if (this.direction.length > 0)   jsonData["direction"] = this.direction.map(x => {return x.serialize();});
		if (this.state != null) jsonData["state"] = this.state;
		if (this.messageTopic != null) jsonData["messageTopic"] = this.messageTopic;
		if (this.messageBroker != null) jsonData["messageBroker"] = this.messageBroker.serialize();
		if (this.lastUpdate != null) jsonData["lastUpdate"] = this.lastUpdate;
		if (this.minInterval != null) jsonData["minInterval"] = this.minInterval;
		if (this.maxInterval != null) jsonData["maxInterval"] = this.maxInterval;
		jsonData["modelType"] = "BasicEventElement";
		return jsonData;
	}		
}
class OperationVariable {
	constructor(value){
		this.value = value
	}
	serialize(){
		//let jsonData = {};
		//if jsonData["value"] !=null  jsonData["value"] = this.value.serialize();
		//return jsonData;
	}
}
class Operation extends SubmodelElement{
	constructor(extensions,category,idShort,displayName,description,
			checksum,kind,semanticId,supplementalSemanticIds,
			qualifiers,embeddedDataSpecifications
			){
			super(extensions,category,idShort,displayName,description,
					checksum,kind,semanticId,supplementalSemanticIds,
					qualifiers,embeddedDataSpecifications,
					outputVariables,inoutputVariables,inputVariables);
	}
	serialize(){
		let jsonData =  super.serialize();
		if (this.inputVariables.length > 0)   jsonData["inputVariables"] = this.inputVariables.map(x => {return x.serialize();});
		if (this.outputVariables.length > 0)   jsonData["outputVariables"] = this.outputVariables.map(x => {return x.serialize();});
		if (this.inoutputVariables.length > 0)   jsonData["inoutputVariables"] = this.inoutputVariables.map(x => {return x.serialize();});
		jsonData["modelType"] = "Operation";
		return jsonData;
	}	
}
class SpecificAssetId extends HasSemantics{
	constructor(name,value,externalSubjectId,
			semanticId,supplementalSemanticIds){
		super(semanticId,supplementalSemanticIds);
		this.name = name;
		this.value = value;
		this.externalSubjectId = externalSubjectId;
	}
	serialize(){
		let jsonData =  super.serialize();
		if (this.name != null) jsonData["name"] = this.name;
		if (this.value != null) jsonData["value"] = this.value;
		if (this.externalSubjectId != null) jsonData["externalSubjectId"] = this.externalSubjectId.serialize();
		return jsonData;
	}	
}
class Resource{
	constructor(path,contentType){
		this.path = path;
		this.contentType = contentType;
	}
	serialize(){
		let jsonData = {};
		jsonData["path"] = this.path;
		jsonData["contentType"] = this.contentType;
	}
}
class AssetInformation{
	constructor(assetKind,globalAssetId,specificAssetId,
			defaultThumbnail){
		this.assetKind = assetKind;
		this.globalAssetId = globalAssetId;
		this.specificAssetId = specificAssetId
		this.defaultThumbnail = defaultThumbnail;
	};
	serialize(){
		let jsonData = {};
		jsonData["assetKind"] = this.assetKind;
		if (this.globalAssetId != null) jsonData["globalAssetId"] = this.globalAssetId.serialize();
		if (this.specificAssetId != null) jsonData["specificAssetId"] = this.specificAssetId.serialize();
		if (this.defaultThumbnail != null) jsonData["defaultThumbnail"] = this.defaultThumbnail.serialize();
		return jsonData;
	}
}
class AssetAdministrationShell extends Identifiable{
	constructor(id,assetInformation,extensions,category,idShort,displayName,description,
			checksum,administration,embeddedDataSpecifications,derivedFrom,submodels){   
		super(id,extensions,category,idShort,displayName,description,
				checksum,administration);
		this.embeddedDataSpecifications = embeddedDataSpecifications
		this.derivedFrom = derivedFrom;
		this.submodels = submodels;
		this.assetInformation = assetInformation;
	}
	serialize(){
		let jsonData =  super.serialize();
		if (this.derivedFrom != null){
			jsonData["derivedFrom"] = derivedFrom
		}
		if (this.embeddedDataSpecifications.length > 0){
			jsonData["embeddedDataSpecifications"] = this.embeddedDataSpecifications.map(x => {return x.serialize();});
		}
		if (this.submodels.length > 0){
			jsonData["submodels"] = this.submodelss.map(x => {return x.serialize();});
		}
		jsonData["modelType"] = "AssetAdministrationShell";
		return jsonData;
	}
}
class Submodel extends Identifiable{
	constructor(id,extensions,category,idShort,displayName,description,
				checksum,administration,kind,semanticId,supplementalSemanticIds,
				qualifiers,embeddedDataSpecifications,submodelElements){
       
		super(id,extensions,category,idShort,displayName,description,
				checksum,administration);
       this.kind = kind;
	   this.semanticId = semanticId;
       this.supplementalSemanticIds = supplementalSemanticIds; 
       this.qualifiers = qualifiers;
       this.embeddedDataSpecifications = embeddedDataSpecifications;
       this.submodelElements = embeddedDataSpecifications;
    }
	serialize(){
		let jsonData =  super.serialize();
		jsonData["kind"] = this.kind;
		jsonData["modelType"] = "Submodel";
		if (this.semanticId != null){
			jsonData["semanticId"] = this.semanticId.serialize();
		}
		if (this.supplementalSemanticIds.length > 0){
			jsonData["supplementalSemanticIds"] = this.supplementalSemanticIds.map(x => {return x.serialize();});
		}
		if (this.qualifiers.length > 0){
			jsonData["qualifiers"] = this.qualifiers.map(x => {return x.serialize();});
		}
		if (this.embeddedDataSpecifications.length > 0){
				jsonData["embeddedDataSpecifications"] = this.embeddedDataSpecifications.map(x => {return x.serialize();});
		}
		if (this.submodelElements.length > 0){
			jsonData["submodelElements"] = this.submodelElements.map(x => {return x.serialize();});
		}
		jsonData["modelType"] = "Submodel";
		return jsonData;
	}
}
class ConceptDescription extends Identifiable{
	constructor(id,assetInformation,extensions,category,idShort,displayName,description,
			checksum,administration,embeddedDataSpecifications,derivedFrom,submodels){   
		super(id,extensions,category,idShort,displayName,description,
				checksum,administration);
		this.embeddedDataSpecifications = embeddedDataSpecifications
		this.isCaseOf = isCaseOf;
	}
	serialize(){
		let jsonData =  super.serialize();
		if (this.embeddedDataSpecifications.length > 0){
			jsonData["embeddedDataSpecifications"] = this.embeddedDataSpecifications.map(x => {return x.serialize();});
		}
		if (this.isCaseOf.length > 0){
			jsonData["isCaseOf"] = this.isCaseOf.map(x => {return x.serialize();});
		}
		jsonData["modelType"] = "ConceptDescription";
		return jsonData;	
	}
}
class Environment {
	constructor(assetAdministrationShells,submodels,conceptDescriptions){
		this.assetAdministrationShells = assetAdministrationShells;
		this.submodels = submodels
		this.conceptDescriptions = conceptDescriptions
	}
	serialize(){
		let jsonData = {};
		if (this.assetAdministrationShells.length > 0){
			let assetAdministrationShellsList = []
			for (const _assetAdministrationShell of this.assetAdministrationShells){
				assetAdministrationShellsList.push(_assetAdministrationShell.serialize())
			}
			jsonData["assetAdministrationShells"] = assetAdministrationShellsList
		}
		if (this.submodels.length > 0){
			let submodelsList = []
			for (const _submodel of this.submodels){
				submodelsList.push(_submodel.serialize())
			}
			jsonData["submodels"] = submodelsList
		} 
		if (this.conceptDescriptions.length > 0){
			let conceptDescriptionsList = []
			for (const _conceptDescription of this.conceptDescriptions){
				conceptDescriptionsList.push(_conceptDescription.serialize())
			}
			jsonData["conceptDescriptions"] = conceptDescriptionsList
		}
	}
}

class Deserialize{
	constructor(aas_meta_model_element){
		this.aas_meta_model_element = aas_meta_model_element
	}
	
	deserialize_Keys(){
		
	}
	deserialize_Reference(){
		
	}
	deserialize_Referable(){
		
	}
	deserialize_Idenitifiable(_Identifiable){
		
	}
	deserialize_semanticId(){
		
	}
	deserialize_supplementalSemanticIds(){
		
	}
	deserialize_HasSemantics(){
		
	}
	deserialize_assetAdministrationShell(_assetAdministrationShell){
		
		
		return AssetAdministrationShell(id);
	}
	deserialize_submodel(_submodel){
		
		return Submodel();
	}
	deserialize_conceptDescription(cD){
		
		return ConceptDescription();
	}
	deserialize_environment(envD){
		let assetAdministrationShellsList = [];
		let submodelsList = [];
		let conceptDescriptionsList = [];
		
		if (this.aas_meta_model_element.hasOwnProperty("assetAdministrationShells")){
			
			for (const _assetAdministrationShell of envD["assetAdministrationShells"]){
				assetAdministrationShellsList.push(deserialize_assetAdministrationShell(_assetAdministrationShell));
			}
		}
		if (this.aas_meta_model_element.hasOwnProperty("submodels")){
			for (const _submodel of envD["submodels"]){
				submodelsList.push(deserialize_submodel(_submodel));
			}
		}
		if (this.aas_meta_model_element.hasOwnProperty("conceptDescriptions")){
			for (const _conceptDescription of envD["conceptDescriptions"]){
				conceptDescriptionsList.push(deserialize_conceptDescription(_conceptDescription));
			}
		}
		env =  Environment(assetAdministrationShellsList,submodelsList,conceptDescriptionsList);
		return env;
	}
	
	get_object(){
		// Check if it is the environment 
		if (this.aas_meta_model_element.hasOwnProperty("assetAdministrationShells") ||
				this.aas_meta_model_element.hasOwnProperty("submodels") ||
				this.aas_meta_model_element.hasOwnProperty("conceptDescriptions")){
			return deserilize_envioronment;
		}
		else {
			if (this.aas_meta_model_element["modelType"] == "Submodel"){
				
			}
		}
	}
}