class StringObject{
	constructor(name,required="required",text = ""){
		this.text = text;
		this._uuid = crypto.randomUUID();
		this.name = name;
		this.parentId = "";
		this.required = required;
	}
	getString(){
		return this.text;
	}
	setString(s){
		this.text = s;
	}
	getDom(){
		return `<div id = "`+this._uuid+`">
			<div class="row" style="min-height : 2.5vh;"></div>
		    <div class = "row">
				<div class = "col-1  d-flex flex-wrap align-items-center text-center">
					<span style = "size : 1em">`+this.name+`</span>
				</div>
				<div class = "col-2"></div>
				<div class = "col-8">
					<div class="form-floating">
						<input style="height : 6.5vh" type="text" class="form-control" id="`+this._uuid+"-"+this.name+`" name="`+this.name+`" value ="`+this.text+`">
						<label for="`+this.name+`">Please provide the `+this.name+`</label>
					</div>
				</div>
				<div class = "col-1"></div>
			</div>
			<div class="row" style="min-height : 2.5vh; border-bottom : 0.1vh solid #dee2e6 "></div>
		</div>`
	}
	createDom(parentId,exdomain){
		this.parentId = parentId;
		document.getElementById(this.parentId).insertAdjacentHTML(
			'afterbegin',
			this.getDom()
		);
		document.getElementById(this._uuid+"-"+this.name).addEventListener("input", (evt) => {
			this.setString(evt.target.value);
			});
	}
}
class DataObject{
	constructor(name,text = "",submodelIdentifier,idShortPath){
		this.text = text;
		this._uuid = crypto.randomUUID();
		this.name = name;
		this.parentId = "";
		this.exdomain = "";
		this.submodelIdentifier = submodelIdentifier;
		this.idShortPath = idShortPath;
	}
	getString(){
		return this.text;
	}
	setString(s){
		this.text = s;
	}
	getDom(exdomain){
		return `<div id = "`+this._uuid+`">
			<div class="row" style="min-height : 2.5vh;"></div>
		    <div class = "row">
				<div class = "col-1  d-flex flex-wrap align-items-center text-center">
					<span style = "size : 1em">`+this.name+`</span>
				</div>
				<div class = "col-2"></div>
				<div class = "col-6">
				</div>
				<div class = "col-2">
					<div class="std-submodel-add" style = "margin-left : 30%">
						<form id = "`+this._uuid+`-form" action="/submodels/`+this.submodelIdentifier+`/submodel/submodel-elements/`+this.idShortPath+`/attachment" method="get">
							<input id="operation_type" name="operation_type" type="hidden" value="download_json">
							<input type = "image" style = "height : 4vh;cursor: pointer;" id = "std-submodel-img" src="`+this.exdomain+`web/images/download.svg">
							<div class="std-submodel-add-overlay">
								<input type = "image"  style = "height : 4vh;cursor: pointer;" id = "std-submodel-img-overlay" src="`+this.exdomain+`web/images/download1.svg">
							</div>
							</form>
					</div>
				</div>
				<div class = "col-1"></div>
			</div>
			<div class="row" style="min-height : 2.5vh; border-bottom : 0.1vh solid #dee2e6 "></div>
		</div>`
	}
	createDom(parentId,exdomain){
		this.parentId = parentId;
		this.exdomain = exdomain
		document.getElementById(this.parentId).insertAdjacentHTML(
			'afterbegin',
			this.getDom()
		);
		//document.getElementById(this._uuid+"-"+this.name).addEventListener("input", (evt) => {
			//this.setString(evt.target.value);
		//	});
		//document.getElementById(this._uuid+"-"+this.form).addEventListener("click", (evt) => this.downloadFile(evt));
	}
	serialize() {
		
	}

}
class SelectObject{
	constructor(name,Enum,_item){
		this.selectedItem = _item;
		this._uuid = crypto.randomUUID();
		this.name = name;
		this.parentId = "";
		this.Enum = Enum;
		this._dom = this.getDom();
	}
	setSelectedItem(_item){
		this.selectedItem = _item;
	}	
	getSelectedItem(){
		return this.selectedItem;
	}
	getDom(){
		return 	`<div id = "`+this._uuid+`">
					<div class="row" style="min-height : 2.5vh;"></div>
					<div class="row">
							<div class="col-1  d-flex flex-wrap align-items-center text-center">
								<span style="size : 1em">`+this.name+`</span>
							</div>
							<div class="col-2"></div>
							<div class="col-8">
								<select style="height : 6.5vh" name="category" id="`+this._uuid+"-"+this.name+`" class="form-control" aria-label="Default select example">
									`+this.createOptions(this.Enum)+`
								</select>
							</div>
							<div class="col-1"></div>
						</div>
					<div class="row" style="min-height : 2.5vh; border-bottom : 0.1vh solid #dee2e6 "></div>`	
	}
	createOptions(OptionType)
	{
		let options = "";
		Object.values(OptionType).forEach(_OptionType => options = options +
		`<option value="`+_OptionType.name+`">`+_OptionType.name+`</option>`)
		return options;
	}
	createDom(parentId,exdomain){
		this.parentId = parentId;
		document.getElementById(this.parentId).insertAdjacentHTML(
				 'afterbegin',
				 this._dom
		);
		document.getElementById(this._uuid+"-"+this.name).value = this.selectedItem;
		document.getElementById(this._uuid+"-"+this.name).addEventListener("change", (evt) => {
			this.setSelectedItem(evt.target.value);
		});
	}
}
class ListObject{
	constructor(_uuid,_object,_dom){
		this._uuid = _uuid;
		this._object = _object;
		this._dom = _dom;
	}
}
class ListCollection{
	constructor(name,className){
		this._uuid = crypto.randomUUID();
		this.name = name;
		this.parentId = "";
		this.exdomain = "";
		this._list = new Array();
		this.className = className;
		this.exdomain = "";
		this._dom = "";
	}
	getDom(){
		return `<div id = "`+this._uuid+`">
					<div class="row" style="min-height : 2.5vh;"></div>
					<div class = "row">
							<div class = "col-2">
							 	<div class="std-submodel-add" >
										<input type = "image" style = "height : 3vh; width : 3svh ;cursor: pointer;" id = "`+this._uuid+`-add-button" src="`+this.exdomain+`web/images/plus_blue.svg" >
										<div class="std-submodel-add-overlay">
											<input type = "image"  style = "height : 3vh; width : 3vh ;cursor: pointer;" id = "`+this._uuid+`-add-button-overlay" src="`+this.exdomain+`web/images/plus1.svg">
										</div>
								</div>
							</div>
							<div class = "col-6">
							</div>
							<div class = "col-4  d-flex flex-wrap align-items-right text-right">
								<span>`+this.name+`</span>
							</div>
					</div>
					<div class="row" style="min-height : 2.5vh;"></div>
					<div class  = "row"  id = "`+this._uuid+`-Collection">
					</div>
					<div class="row" style="min-height : 2.5vh; border-bottom : 0.1vh solid #dee2e6 "></div>
				</div>
				`;
	}
	getObjectDom(_iuuid){
		return `<div id = "`+_iuuid+`">
		<div class = "row">
		<div class = "col-8  d-flex flex-wrap align-items-center text-center" style="min-height : 2.5vh; border-bottom : 0.1vh solid #dee2e6 ">
			<span style = "size : 1em">`+this.className+`</span>
		</div>
		<div class = "col-2">
			<div class="std-submodel-add" style = "margin-left : 50%">
				<input type = "image" style = "height : 2vh; width : 2vh ;cursor: pointer;" id = "`+_iuuid+"-remove-button"+`"  src="`+this.exdomain+`web/images/delete_button.svg" >
				<div class="std-submodel-add-overlay">
					<input type = "image"  style = "height : 2vh; width : 2vh ;cursor: pointer;" id = "`+_iuuid+"-remove-button-overlay"+`" src="`+this.exdomain+`web/images/delete_button1.svg" >
				</div>													
			</div>
			</div>
			<div class = "col-2">
			</div>
		</div>
		<div class="row" style="min-height : 2.5vh;"></div>
		<div id = `+_iuuid+"-Object"+`>
		</div>
		<div class="row" style="min-height : 2.5vh;"></div>
	</div>`
	}
	getLength(){
		return this._list.length;
	}
	getclassObject(_cuuid){
		if (this.className == "LangString"){
			return new LangString("en","",_cuuid);
		}
		if (this.className == "Reference"){
			return new Reference("GlobalReference","",null,_cuuid);
		}
		if (this.className == "Extension"){
			return new Extension("","","","xs:anyURI","","",_cuuid);
		}
		if (this.className == "HasSemantics"){
			return new HasSemantics("","",_cuuid);
		}
		if (this.className == "Key"){
			return new Key("GlobalReference","",_cuuid);
		}
		if (this.className == "Qualifier"){
			return new Qualifier("","xs:anyURI","","","ValueQualifier","","",_cuuid);
		}
	}
	addListObject(_listObject){
		document.getElementById(this._uuid+"-Collection").insertAdjacentHTML(
				 'beforeend',
				 _listObject._dom
		)
		_listObject._object.createDom(_listObject._uuid+"-Object",this.exdomain);
		document.getElementById(_listObject._uuid+"-remove-button").addEventListener( "click", (evt) => this.removeFunctionHandler(evt,_listObject._uuid));	
		document.getElementById(_listObject._uuid+"-remove-button-overlay").addEventListener( "click", (evt) => this.removeFunctionHandler(evt,_listObject._uuid));
	}
	removeFunctionHandler(evt,_iuuid) {
		evt.preventDefault();
		this.removeListObject(_iuuid);
		return false;
	}
	addListObjects(){
		for (var i = 0; i < this._list.length; i++ ) {
			let _listObject = this._list[i];
			document.getElementById(this._uuid+"-Collection").insertAdjacentHTML(
					 'beforeend',
					 this.getObjectDom(_listObject._uuid)
			)
			_listObject._object.createDom(_listObject._uuid+"-Object",this.exdomain);
			document.getElementById(_listObject._uuid+"-remove-button").addEventListener( "click", (evt) => this.removeFunctionHandler(evt,_listObject._uuid));	
			document.getElementById(_listObject._uuid+"-remove-button-overlay").addEventListener( "click", (evt) => this.removeFunctionHandler(evt,_listObject._uuid));
		}
	}
	createDom(parentId,exdomain){
		this.exdomain = exdomain
		this.parentId = parentId;
		document.getElementById(this.parentId).insertAdjacentHTML(
				 'afterbegin',
				 this.getDom()
		);
		this.addListObjects();
		document.getElementById(this._uuid+"-add-button").addEventListener( "click", (evt) => this.addFunctionHandler(evt));	
		document.getElementById(this._uuid+"-add-button-overlay").addEventListener( "click", (evt) => this.addFunctionHandler(evt));
	}
	addFunctionHandler(evt) {
		evt.preventDefault();
		let _iuuid = crypto.randomUUID();
		let _classObject = this.getclassObject(_iuuid);
		let _objectDIv = this.getObjectDom(_iuuid);
		let _listObject = new ListObject(_iuuid,_classObject,_objectDIv);
		this._list.push(_listObject);
		this.addListObject(_listObject);
		return false;
	}
	removeListObject(_nuuid){
		document.getElementById(_nuuid).remove();
		for (var i = 0; i < this._list.length; i++ ) {
			if (this._list[i]._uuid == _nuuid){
				this._list.splice(i,1);
				break;
			}
		}
	}
	serialize(){
		let jsonDataList = new Array();
		for (var i = 0; i < this._list.length; i++ ) {
			jsonDataList.push(this._list[i]._object.serialize());
		}
		return jsonDataList;
	}
	deserialize(data,parentId,exdomain){
		this.exdomain = exdomain;
		for (var i = 0; i < data.length; i++ ) {
			
			let _iuuid = crypto.randomUUID();
			let _classObject = this.getclassObject(_iuuid);
			let _objectDIv = this.getObjectDom(_iuuid);
			let _listObject = new ListObject(_iuuid,_classObject,_objectDIv);
			_classObject.deserialize(data[i],parentId,exdomain);
			this._list.push(_listObject);
		}
	}
}
class ComplexObject{
	constructor(name,className){
		this._uuid = crypto.randomUUID();
		this.name = name;
		this.parentId = "";
		this.exdomain = "";
		this.className = className;
		this.exdomain = "";
		this._object = null;
	}
	getclassObject(_cuuid){
		if (this.className == "HasSemantics"){
			return new HasSemantics("","",_cuuid);
		}
		if (this.className == "HasExtensions"){
			return new HasExtensions("","",_cuuid);
		}
		if (this.className == "AdministrativeInformation"){
			return new AdministrativeInformation("","",null,_cuuid);
		}
		if (this.className == "Reference"){
			return new Reference("","",null,_cuuid);
		}
		if (this.className == "Qualifiable"){
			return new Qualifiable("",_cuuid);
		}
	}
	getDom(){
		return 	`<div id = "`+this._uuid+`">
		<div class="row" style="min-height : 2.5vh;"></div>
		<div class = "row">
				<div class = "col-1">
				 	<div class="std-submodel-add" id = "`+this._uuid+"-add"+`">
							<input type = "image" style = "height : 3vh; width : 3vh ;cursor: pointer;" id = "`+this._uuid+`-add-button" src="`+this.exdomain+`web/images/plus_blue.svg" >
							<div class="std-submodel-add-overlay">
								<input type = "image"  style = "height : 3vh; width : 3vh ;cursor: pointer;" id = "`+this._uuid+`-add-button-overlay" src="`+this.exdomain+`web/images/plus1.svg">
							</div>
					</div>
				</div>
				<div class = "col-1">
					<div class="std-submodel-add" id = "`+this._uuid+"-remove"+`" style = "visibility: hidden;">
							<input type = "image" style = "height : 3vh; width : 3svh ;cursor: pointer;" id = "`+this._uuid+`-remove-button" src="`+this.exdomain+`web/images/delete_button.svg" >
							<div class="std-submodel-add-overlay">
								<input type = "image"  style = "height : 3vh; width : 3vh ;cursor: pointer;" id = "`+this._uuid+`-remove-button-overlay" src="`+this.exdomain+`web/images/delete_button1.svg">
							</div>
					</div>										
				</div>
				<div class = "col-6">
				</div>
				<div class = "col-4  d-flex flex-wrap align-items-right text-right">
					<span>`+this.name+`</span>
				</div>
		</div>
		<div class="row" style="min-height : 2.5vh;"></div>
		<div class  = "row"  id = "`+this._uuid+`-Object">
		</div>
		<div class="row" style="min-height : 2.5vh; border-bottom : 0.1vh solid #dee2e6 "></div>
	</div>`
	}
	createDom(parentId,exdomain){
		this.exdomain = exdomain;
		this.parentId = parentId;
		document.getElementById(this.parentId).insertAdjacentHTML(
				 'afterbegin',
				 this.getDom()
			);
		if (this._object != null){
			this._object.createDom(this._uuid+"-Object",this.exdomain);
			document.getElementById(this._uuid+"-remove").style.visibility = "visible";
			document.getElementById(this._uuid+"-add").style.visibility = "hidden";
		}
		document.getElementById(this._uuid+"-add-button").addEventListener( "click", (evt) => this.addFunctionHandler(evt));	
		document.getElementById(this._uuid+"-add-button-overlay").addEventListener( "click", (evt) => this.addFunctionHandler(evt));	
		document.getElementById(this._uuid+"-remove-button").addEventListener( "click", (evt) => this.removeFunctionHandler(evt));	
		document.getElementById(this._uuid+"-remove-button-overlay").addEventListener( "click", (evt) => this.removeFunctionHandler(evt));
	}
	addFunctionHandler(evt) {
		evt.preventDefault();
		this.addObject();
		return false;
	}
	addObject(){
		document.getElementById(this._uuid+"-remove").style.visibility = "visible";
		document.getElementById(this._uuid+"-add").style.visibility = "hidden";
		let _iuuid = crypto.randomUUID();
		this._object = this.getclassObject(_iuuid);
		this._object.createDom(this._uuid+"-Object",this.exdomain);
	}
	removeObject(){
		document.getElementById(this._uuid+"-add").style.visibility = "visible";
		document.getElementById(this._uuid+"-remove").style.visibility = "hidden";
		document.getElementById(this._uuid+"-Object").innerHTML = "";
		this._object = null;
	}
	removeFunctionHandler(evt) {
		evt.preventDefault();
		this.removeObject();
		return false;
	}
	serialize(){
		if (this._object != null){
			return this._object.serialize();
		}
		else {
			return {};
		}
	}
	deserialize(data,parentId,exdomain){
		let _iuuid = crypto.randomUUID();
		this._object = this.getclassObject(_iuuid);
		this._object.deserialize(data,parentId,exdomain);
	}
}
class ModelingKind{
	static Instance = new ModelingKind("Instance")
	static Template = new ModelingKind("Template")
}
class KeyType {
	static GlobalReference = new KeyType("GlobalReference")
	static AnnotatedRelationshipElement = new KeyType("AnnotatedRelationshipElement")
	static AssetAdministrationShell = new KeyType("AssetAdministrationShell")
	static BasicEventElement = new KeyType("BasicEventElement")
	static Blob = new KeyType("Blob")
	static Capability = new KeyType("Capability")
	static ConceptDescription = new KeyType("ConceptDescription")
	static Identifiable = new KeyType("Identifiable")
	static DataElement = new KeyType("DataElement")
	static Entity = new KeyType("Entity")
	static EventElement = new KeyType("EventElement")
	static File = new KeyType("File")
	static MultiLanguageProperty = new KeyType("MultiLanguageProperty")
	static Operation = new KeyType("Operation")
	static Property = new KeyType("Property")
	static Range = new KeyType("Range")
	static ReferenceElement = new KeyType("ReferenceElement")
	static Referable = new KeyType("Referable")
	static RelationshipElement = new KeyType("RelationshipElement")
	static Submodel = new KeyType("Submodel")
	static SubmodelElement = new KeyType("SubmodelElement")
	static SubmodelElementList = new KeyType("SubmodelElementList")
	static SubmodelElementCollection = new KeyType("SubmodelElementCollection");

  constructor(name) {
	  this.name = name;
  }
}
class LangCode {
	static en = new LangCode("en");
	static de = new LangCode("de");
	static fr = new LangCode("fr");
	static jp = new LangCode("jp");
	static cn = new LangCode("cn");
	
  constructor(name) {
	  this.name = name;
  }
}
class DataTypeXSD{
	static xs_anyURI = new DataTypeXSD("xs:anyURI");
	static xs_base64Binary = new DataTypeXSD("xs:base64Binary");
	static xs_boolean = new DataTypeXSD("xs:boolean");
	static xs_date = new DataTypeXSD("xs:date");
	static xs_dateTime = new DataTypeXSD("xs:dateTime");
	static xs_dateTimeStamp = new DataTypeXSD("xs:dateTimeStamp");
	static xs_decimal = new DataTypeXSD("xs:decimal");
	static xs_double = new DataTypeXSD("xs:double");
	static xs_duration = new DataTypeXSD("xs:duration");
	static xs_float = new DataTypeXSD("xs:float");
	static xs_gDay = new DataTypeXSD("xs:gDay");
	static xs_gMonth = new DataTypeXSD("xs:gMonth");
	static xs_gMonthDay = new DataTypeXSD("xs:gMonthDay");
	static xs_gYear = new DataTypeXSD("xs:gYear");
	static xs_gYearMonth = new DataTypeXSD("xs:gYearMonth");
	static xs_hexBinary = new DataTypeXSD("xs:hexBinary");
	static xs_string = new DataTypeXSD("xs:string");
	static xs_time = new DataTypeXSD("xs:time");
	static xs_dayTimeDuration = new DataTypeXSD("xs:dayTimeDuration");
	static xs_yearMonthDuration = new DataTypeXSD("xs:yearMonthDuration");
	static xs_integer = new DataTypeXSD("xs:integer");
	static xs_long = new DataTypeXSD("xs:long");
	static xs_int = new DataTypeXSD("xs:int");
	static xs_short = new DataTypeXSD("xs:short");
	static xs_byte = new DataTypeXSD("xs:byte");
	static xs_nonNegativeInteger = new DataTypeXSD("xs:nonNegativeInteger");
	static xs_positiveInteger = new DataTypeXSD("xs:positiveInteger");
	static xs_unsignedLong = new DataTypeXSD("xs:unsignedLong");
	static xs_unsignedInt = new DataTypeXSD(	"xs:unsignedInt");
	static xs_unsignedShort = new DataTypeXSD("xs:unsignedShort");
	static xs_unsignedByte = new DataTypeXSD("xs:unsignedByte");
	static xs_nonPositiveInteger = new DataTypeXSD("xs:nonPositiveInteger");
	static xs_negativeInteger = new DataTypeXSD("xs:negativeInteger");
	
	
  constructor(name) {
	  this.name = name;
  }
}
class RefType{
	static GlobalReference = new RefType("GlobalReference");
	static GlobalReference = new RefType("GlobalReference");
	
	
  constructor(name) {
	  this.name = name;
  }
}
class CategoryType{
	static CONSTANT = new CategoryType("CONSTANT");
	static PARAMETER = new CategoryType("PARAMETER");
	static VARIABLE= new CategoryType("VARIABLE");
	
  constructor(name) {
	  this.name = name;
  }
}
class QualifierKind{
	static valueQualifier = new QualifierKind("ValueQualifier");
	static ConceptQualifier = new QualifierKind("ConceptQualifier");
	static TemplateQualifier = new QualifierKind("TemplateQualifier");

  constructor(name) {
	  this.name = name;
  }
}
class Key{
	constructor(type="GlobalReference",value,_uuid = ""){
		this.type = new SelectObject("type",KeyType,"GlobalReference");
		this.value = new StringObject("text");
		this._uuid = _uuid
		if (_uuid == ""){this._uuid = crypto.randomUUID();}
	}
	serialize(){
        return {"type":this.type.getSelectedItem(),"value":this.value.getString()};
     }
    createDom(parentId,exdomain){
		document.getElementById(parentId).insertAdjacentHTML(
				 'afterbegin',
					`<div id = "`+this._uuid+`">
					<div class = "row">
						<div class = "col-1"></div>
						<div class = "col-5">
						<div id = "`+this._uuid+"-type"+`"> </div>
						</div>
						<div class = "col-5">
							<div class="form-floating">
								<div id = "`+this._uuid+"-value"+`"> </div>
							</div>
						</div>
						<div class = "col-1">
												
						</div>
					</div>
					<div class="row" style="min-height : 2.5vh;"></div>
				</div>`
		);
		this.type.createDom(this._uuid+"-type",exdomain);
		this.value.createDom(this._uuid+"-value",exdomain);
    }
    deserialize(data,parentId,exdomain){
    	this.type.setSelectedItem(data["type"]);
    	this.value.setString(data["value"]);
    }
}
class LangString{
    constructor(language="en",text = "",_uuid = ""){
        this.language = new SelectObject("language",LangCode,language);
        this.text = new StringObject("text","",text);
        this._uuid = _uuid;
    }
    serialize(){
        return {"language":this.language.getSelectedItem(),
        		"text":this.text.getString()};
    }
    createDom(parentId,exdomain){
    	if (this._uuid == ""){this._uuid = crypto.randomUUID()};
    	document.getElementById(parentId).insertAdjacentHTML(
				 'afterbegin',
					`<div class = "row" id = "`+this._uuid+"LangString"+`">
						<div class = "col-6">
						<div id = "`+this._uuid+"LangString-language"+`"> </div>
						</div>
						<div class = "col-6">
							<div class="form-floating">
								<div id = "`+this._uuid+"LangString-text"+`"> </div>
							</div>
						</div>
					</div>
					<div class="row" style="min-height : 2.5vh;"></div>`
		);
		this.text.createDom(this._uuid+"LangString-language");
		this.language.createDom(this._uuid+"LangString-text");
    }
    deserialize(data,parentId,exdomain){
    	this.text.setString(data["text"]);
    	this.language.setSelectedItem(data["language"]);
    }
}
class Reference{
	constructor(type="GlobalReference",keys,referredSemanticId,_uuid){
		this.type =  new SelectObject("type",RefType,type);
		this.keys = new ListCollection("keys","Key");
		this.referredSemanticId = referredSemanticId;
		this._uuid = _uuid ;
		if (_uuid == ""){this._uuid = crypto.randomUUID();}
	}
	serialize(){
		let jsonData = {};
		jsonData["type"] = this.type.getSelectedItem();
		jsonData["keys"] = this.keys.serialize();
		//if (this.referredSemanticId != null)  jsonData["referredSemanticId"] = this.referredSemanticId.serialize();
		return jsonData;
	}
	createDom(parentId,exdomain){
		document.getElementById(parentId).insertAdjacentHTML(
				 'afterbegin',
					`<div id = "`+this._uuid+`">
						<div id = "`+this._uuid+"-type"+`"> </div>
						<div class="row" style="min-height : 2.5vh;"></div>
						<div id = "`+this._uuid+"-keys"+`"> </div>
					</div>`);
		this.type.createDom(this._uuid+"-type",exdomain);
		this.keys.createDom(this._uuid+"-keys",exdomain);
	}
	deserialize(data,parentId,exdomain){
		if (data.hasOwnProperty('type')){
			this.type.setSelectedItem(data["type"]);
		}
		if (data.hasOwnProperty('keys')){
			this.keys.deserialize(data["keys"],parentId,exdomain);
		}	
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
		return jsonData;
		if (this.embeddedDataSpecifications.length > 0) jsonData["embeddedDataSpecifications"] = this.embeddedDataSpecifications.map(x => {return x.serialize();});
		return jsonData;
	}
}
class AdministrativeInformation extends HasDataSpecification{
    constructor(version, revision,dataSpecifications,uuid){
    	super(dataSpecifications);
        this.version  = new StringObject("version");
        this.revision = new StringObject("revision");
        if (uuid == ""){this.uuid = crypto.randomUUID();}
    }
    serialize(){
        let jsonData = super.serialize();
        jsonData["version"] = this.version.getString();
        jsonData["revision"] = this.revision.getString();
        return jsonData;
    }
    deserialize(data,parentId,exdomain){
		if (data.hasOwnProperty('version')){
			this.version.setString(data["version"]);
		}
		if (data.hasOwnProperty('revision')){
			this.revision.setString(data["revision"]);
		}
    }
    createDom(parentId,exdomain){
    	this.version.createDom(parentId,exdomain);
    	this.revision.createDom(parentId,exdomain);
    }
}
class HasSemantics{
	constructor(semanticId,supplementalSemanticIds,_uuid=""){
		this.semanticId = new ComplexObject("semanticId","Reference");
		this.supplementalSemanticIds = new ListCollection("supplementalSemanticIds","Reference");
		this._uuid = _uuid;
	}
	serialize(){
		let jsonData = {}
		if (this.semanticId._object != null){
			jsonData["semanticId"] = this.semanticId.serialize(); 
		}
		if (this.supplementalSemanticIds.getLength() > 0 ){
			jsonData["supplementalSemanticIds"] = this.supplementalSemanticIds.serialize();
		}
		return jsonData
	}
	createDom(parentId,exdomain){
		this.semanticId.createDom(parentId,exdomain);
		this.supplementalSemanticIds.createDom(parentId,exdomain);
	}
	deserialize(data,parentId,exdomain) {
		if (data.hasOwnProperty('semanticId')){
	    	this.semanticId.deserialize(data["semanticId"],parentId,exdomain);
		}
		if (data.hasOwnProperty('supplementalSemanticIds')){
			this.supplementalSemanticIds.deserialize(data["supplementalSemanticIds"],parentId,exdomain);
		}
	}
}
class Qualifier extends HasSemantics{
	constructor(type,valueType="xs:anyURI",semanticId,supplementalSemanticIds,kind="valueQualifier",
				value,valueId,_uuid=""){
		super(semanticId,supplementalSemanticIds);
		this.kind = new SelectObject("kind",QualifierKind,kind);
		this.valueType = new SelectObject("valueType",DataTypeXSD,valueType);
		this.value = new StringObject("value");
		this.type = new StringObject("type");
		this.valueId = new ComplexObject("valueId","Reference");
		this._HasSemantics = new ComplexObject("HasSemantics","HasSemantics");
		this._uuid = _uuid;
		if (_uuid == ""){this._uuid = crypto.randomUUID();}
	}
	serialize(){
		let jsonData = {}
		jsonData = super.serialize();
		jsonData["type"] = this.type.getString();
		jsonData["valueType"] = this.valueType.getSelectedItem();
		jsonData["value"] = this.value.getString();
		jsonData["kind"] = this.kind.getSelectedItem();
		if (this.valueId._object != null) {
			jsonData["valueId"] = this.valueId.serialize();
		}
		return jsonData;
	}
	deserialize(data,parentId,exdomain) {
		if (data.hasOwnProperty('type')){
			this.type.setString(data["type"]);
		}
		if (data.hasOwnProperty('value')){
			this.value.setString(data["value"]);
		}
		if (data.hasOwnProperty('valueType')){
			this.valueType.setSelectedItem(data["valueType"]);
		}
		if (data.hasOwnProperty('kind')){
			this.kind.setSelectedItem(data["kind"]);
		}
		if (data.hasOwnProperty('valueId')){
			this.valueId.deserialize(data["valueId"],parentId,exdomain);
		}
	}
	createDom(parentId,exdomain){
		//super.createDom(parentId,exdomain);
		this.valueId.createDom(parentId,exdomain);
		this.valueType.createDom(parentId,exdomain);
		this.kind.createDom(parentId,exdomain);
		this.value.createDom(parentId,exdomain);
		this.type.createDom(parentId,exdomain);
	}
}
class Extension extends HasSemantics{
	constructor(name,semanticId,supplementalSemanticIds,
			valueType="xs:anyURI",value,refersTo,_uuid){
		super(semanticId,supplementalSemanticIds);
		this.valueType = new SelectObject("valueType",DataTypeXSD,valueType);
		this.value = new StringObject("value");
		this.name = new StringObject("name");
		this.refersTo = new ComplexObject("refersTo","Reference");
		this._uuid = _uuid;
		if (_uuid == ""){this._uuid = crypto.randomUUID();} 
	}
	serialize(){
		let jsonData = super.serialize();
		jsonData["name"] = this.name.getString();
		jsonData["value"] = this.value.getString();
		jsonData["valueType"] = this.valueType.getSelectedItem();
		if (this.refersTo._object != null){
			jsonData["refersTo"] = this.refersTo.serialize(); 
		}
		return jsonData;
	}
	createDom(parentId,exdomain){
		super.createDom(parentId,exdomain);
		this.refersTo.createDom(parentId,exdomain);
		this.valueType.createDom(parentId,exdomain);
		this.value.createDom(parentId,exdomain);
		this.name.createDom(parentId,exdomain);
    }
	deserialize(data,parentId,exdomain){
		if (data.hasOwnProperty("name")){
			this.name.setString(data["name"]);
		}
		if (data.hasOwnProperty("value")){
			this.value.setString(data["value"]);
		}
		if (data.hasOwnProperty("valueType")){
			this.valueType.setSelectedItem(data["valueType"]);
		}
		if (data.hasOwnProperty("refersTo")){
			this.refersTo.deserialize(data["refersTo"],parentId,exdomain);
		}
		super.deserialize(data,parentId,exdomain);
	}
}
class HasExtensions {
	constructor(extensions){
		this.extensions = new ListCollection("Extension","Extension");
	}
	serialize(){
		let jsonData = {};
		if (this.extensions.getLength() > 0 ){
			jsonData["extensions"] = this.extensions.serialize();
		}
		return jsonData;
	}
	deserialize(data,parentId,exdomain){
		if (data.hasOwnProperty("extensions")){
			this.extensions.deserialize(data["extensions"],parentId,exdomain);
		}
	}
	createDom(parentId,exdomain){
    	this.extensions.createDom(parentId,exdomain);
    }
}
class Referable extends HasExtensions{
	constructor(extensions,category="CONSTANT",idShort,displayName,description,checksum){
		super(extensions);
		this.category = new SelectObject("category",CategoryType,category);
	    this.idShort = new StringObject("idShort");
	    this.displayName = new ListCollection("displayName","LangString");
	    this.description = new ListCollection("description","LangString");
	    this.checksum = new StringObject("checksum");
	}
	serialize(){
		let jsonData = super.serialize();
		if (this.idShort.getString() != ""){
			jsonData["idShort"] = this.idShort.getString();	
		}
		if (this.category.getSelectedItem() != ""){
			jsonData["category"] = this.category.getSelectedItem();
		}
		if (this.displayName.getLength() > 0) {
			jsonData["displayName"] = this.displayName.serialize();
		}
		if (this.description.getLength() > 0) {
			jsonData["description"] = this.description.serialize();
		}
		if (this.checksum.getString() != ""){
			jsonData["checksum"] = this.checksum.getString();
		} 
		return jsonData;
	}
	createDom(parentId,exdomain){
		super.createDom(parentId,exdomain);
		this.description.createDom(parentId,exdomain);
		this.displayName.createDom(parentId,exdomain);
		this.category.createDom(parentId);
		this.checksum.createDom(parentId);
		this.idShort.createDom(parentId);
	}
	deserialize(data,parentId,exdomain){
		if (data.hasOwnProperty('category')){
		}
		if (data.hasOwnProperty('idShort')){
			this.idShort.setString(data['idShort']);
		}
		if (data.hasOwnProperty('displayName')){
			this.displayName.deserialize(data["displayName"],parentId,exdomain);
		}
		if (data.hasOwnProperty('description')){
			this.description.deserialize(data["description"],parentId,exdomain);
		}
		if (data.hasOwnProperty('checksum')){
			this.checksum.setString(data['checksum']);
		}
		super.deserialize(data,parentId,exdomain);
	}
}
class Identifiable extends Referable{
	constructor(id,extensions,category,idShort,displayName,description,checksum,administration){
		super(extensions,category,idShort,displayName,description,checksum);
	    this.id = new StringObject("id",true,id);
	    this.administration = new ComplexObject("administration","AdministrativeInformation");
	}
	createDom(parentId,exdomain){
		this.administration.createDom(parentId,exdomain);
		super.createDom(parentId,exdomain);
	}
	serialize(){
		let jsonData = super.serialize();
		if (this.administration._object != null){
			jsonData["administration"] = this.administration.serialize();
		}
		jsonData["id"] = ""//this.id.getString();
		return jsonData;
	}
	deserialize(data,parentId,exdomain){
		if (data.hasOwnProperty('id')){
			this.id.setString(data["id"]);
		}
		if (data.hasOwnProperty('administration')){
			this.administration.deserialize(data["administration"],parentId,exdomain);
		}
		super.deserialize(data,parentId,exdomain);
	}
}
class HasKind{
	constructor(kind){
		this.kind = kind
	}
}
class Qualifiable{
	constructor(qualifiers,_uuid){
		this.qualifiers = new ListCollection("Qualifier","Qualifier");
		this._uuid = _uuid; 
		if (_uuid == ""){this._uuid = crypto.randomUUID();}
	}
	serialize(){
		let jsonData = {}
		if (this.qualifiers.length > 0)   jsonData["qualifiers"] = this.qualifiers.map(x => {return x.serialize();});
		return jsonData;
	}
	createDom(parentId,exdomain){
    	this.qualifiers.createDom(parentId,exdomain);
    }
	deserialize(data,parentId,exdomain){
		this.qualifiers.deserialize(data,parentId,exdomain);
	}
}

class SubmodelElement extends Referable {
	constructor(extensions,category,idShort,displayName,description,
			checksum,kind,semanticId,supplementalSemanticIds,
			qualifiers,embeddedDataSpecifications){
		   super(extensions,category,idShort,displayName,description,
			checksum);
		   this.kind = new SelectObject("kind",ModelingKind,kind);
		   this._Qualifiable = new ComplexObject("Qualifiable","Qualifiable");
		   this._HasSemantics = new ComplexObject("HasSemantics","HasSemantics");
		   this.embeddedDataSpecifications = embeddedDataSpecifications;
		}	
	serialize(){
		let jsonData =  super.serialize();
		jsonData["kind"] = this.kind.getSelectedItem();
		if (this._HasSemantics._object != null){
			if (this._HasSemantics._object.semanticId._object != null){	
				jsonData["semanticId"] = this._HasSemantics._object.semanticId.serialize(); 
			}
			if (this._HasSemantics._object.supplementalSemanticIds != null){
				if (this._HasSemantics._object.supplementalSemanticIds.getLength() > 0){
					jsonData["semanticId"] = this._HasSemantics._object.supplementalSemanticIds.serialize();
				} 
			}
		}
		if (this._Qualifiable._object != null){
			if (this._Qualifiable._object.qualifiers.getLength() > 0 ){
				jsonData["qualifiers"] = this._Qualifiable._object.qualifiers.serialize();
			}
		}
		
		//if (this.embeddedDataSpecifications.length > 0)	jsonData["embeddedDataSpecifications"] = this.embeddedDataSpecifications.map(x => {return x.serialize();});
		
		return jsonData;
	}
	createDom(parentId,exdomain){
		this._Qualifiable.createDom(parentId,exdomain);
		this._HasSemantics.createDom(parentId,exdomain);
		super.createDom(parentId,exdomain);
	}
	deserialize(data,parentId,exdomain){
		if (data.hasOwnProperty('qualifiers')){
			this._Qualifiable.deserialize(data['qualifiers'],parentId,exdomain);
		}
		this._HasSemantics.deserialize(data,parentId,exdomain);
		super.deserialize(data,parentId,exdomain);
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
	createDom(parentId,exdomain){
		super.createDom(parentId,exdomain);
	}
	deserialize(data,parentId,exdomain){
		super.deserialize(data,parentId,exdomain);
		
	}
}
class Property extends DataElement{
	constructor(extensions,category,idShort,displayName,description,
			checksum,kind,semanticId,supplementalSemanticIds,
			qualifiers,embeddedDataSpecifications,
			valueType="xs:string",
			value,
			valueId){
			super(extensions,category,idShort,displayName,description,
					checksum,kind,semanticId,supplementalSemanticIds,
					qualifiers,embeddedDataSpecifications);
			this.value = new StringObject("value");
			this.valueType = new SelectObject("valueType",DataTypeXSD,valueType);
			this.valueId = new ComplexObject("valueId","Reference");
			this.modelType = "Property";
	}
	serialize(){
		let jsonData =  super.serialize();
		jsonData["value"] = this.value.getString();
		jsonData["valueType"] = this.valueType.getSelectedItem();
		if (this.valueId._object != null){
			jsonData["valueId"] = this.valueId.serialize();
		}
		jsonData["modelType"] = "Property";
		return jsonData;
	}
	deserialize(data,parentId,exdomain){
		super.deserialize(data,parentId,exdomain);
		if (data.hasOwnProperty('value')){
			this.value.setString(data['value']);
		}
		
	}
	createDom(parentId,exdomain){
		this.uuid = crypto.randomUUID();
		this.exdomain = exdomain;
		document.getElementById(parentId).insertAdjacentHTML(
				 'afterbegin',
				 `<div class="temp" id = "`+this.uuid+`">
				 </div>`);
		this.value.createDom(this.uuid,exdomain);
		this.valueType.createDom(this.uuid,exdomain);
		this.valueId.createDom(this.uuid,exdomain);
		super.createDom(this.uuid,exdomain);
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
			this.value = new ListCollection("value","LangString");
			this.valueId =new ComplexObject("valueId","Reference");
			this.modelType = "MultiLanguageProperty";
	}
	serialize(){
		let jsonData =  super.serialize();
		jsonData["value"] = this.value.serialize();
		if (this.valueId._object != null){
			jsonData["valueId"] = this.valueId.serialize();
		}
		jsonData["modelType"] = "MultiLanguageProperty";
		return jsonData;
	}
	deserialize(data,parentId,exdomain){
		super.deserialize(data,parentId,exdomain);
		if (data.hasOwnProperty("value")){
			this.value.deserialize(data["value"],parentId,exdomain);
		}
	}
	createDom(parentId,exdomain){
		this.uuid = crypto.randomUUID();
		this.exdomain = exdomain;
		document.getElementById(parentId).insertAdjacentHTML(
				 'afterbegin',
				 `<div class="temp" id = "`+this.uuid+`">
				 </div>`);
		this.value.createDom(parentId,exdomain);
		this.valueId.createDom(this.uuid,exdomain);
		super.createDom(parentId,exdomain);
	}
}
class Range extends DataElement{
	constructor(extensions,category,idShort,displayName,description,
			checksum,kind,semanticId,supplementalSemanticIds,
			qualifiers,embeddedDataSpecifications,
			valueType="xs:string",
			min,
			max){
			super(extensions,category,idShort,displayName,description,
					checksum,kind,semanticId,supplementalSemanticIds,
					qualifiers,embeddedDataSpecifications);
			this.valueType = new SelectObject("valueType",DataTypeXSD,valueType);
			this.min = new StringObject("min");
			this.max =  new StringObject("max");
			this.valueId = new ComplexObject("valueId","Reference");
			this.modelType = "Range";
	}
	serialize(){
		let jsonData =  super.serialize();
		if (this.valueId._object != null){
			jsonData["valueId"] = this.valueId.serialize();
		}
		jsonData["valueType"] = this.valueType.getSelectedItem();
		jsonData["min"] = this.min.getString();
		jsonData["max"] = this.max.getString();
		jsonData["modelType"] = "Range";
		return jsonData;
	}
	deserialize(data,parentId,exdomain){
		super.deserialize(data,parentId,exdomain);
		if (data.hasOwnProperty('min')){
			this.min.setString(data["min"]);
		}
		if (data.hasOwnProperty('max')){
			this.max.setString(data["max"]);
		}
	}
	createDom(parentId,exdomain){
		this.uuid = crypto.randomUUID();
		this.exdomain = exdomain;
		document.getElementById(parentId).insertAdjacentHTML(
				 'afterbegin',
				 `<div class="temp" id = "`+this.uuid+`">
				 </div>`);
		this.max.createDom(this.uuid,exdomain);
		this.min.createDom(this.uuid,exdomain);
		this.valueType.createDom(this.uuid,exdomain);
		this.valueId.createDom(this.uuid,exdomain);
		super.createDom(this.uuid,exdomain);

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
			this.value = new ComplexObject("value","Reference");
			this.modelType = "ReferenceElement";
	}		
	serialize(){
		let jsonData =  super.serialize();
		jsonData["value"] = this.value.serialize();
		if (this.valueId._object != null){
			jsonData["valueId"] = this.valueId.serialize();
		}
		jsonData["modelType"] = "ReferenceElement";
		return jsonData;
	}
	deserialize(data,parentId,exdomain){
		super.deserialize(data,parentId,exdomain);
		if (data.hasOwnProperty("value")){
			this.value.deserialize(data["value"],parentId,exdomain);
		}
	}
	createDom(parentId,exdomain){
		this.uuid = crypto.randomUUID();
		this.exdomain = exdomain;
		document.getElementById(parentId).insertAdjacentHTML(
				 'afterbegin',
				 `<div class="temp" id = "`+this.uuid+`">
				 </div>`);
		this.value.createDom(parentId,exdomain);
		super.createDom(parentId,exdomain);
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
		jsonData["value"] = this.value.serialize();
		jsonData["contentType"] = this.contentType.getSelectedItem();
		jsonData["modelType"] = "Blob";
		return jsonData;
	}	
}
class IFile extends DataElement{
	constructor(extensions,category,idShort,displayName,description,
			checksum,kind,semanticId,supplementalSemanticIds,
			qualifiers,embeddedDataSpecifications,
			value,
			contentType){
			super(extensions,category,idShort,displayName,description,
					checksum,kind,semanticId,supplementalSemanticIds,
					qualifiers,embeddedDataSpecifications);
			this.contentType = contentType;
			this.modelType = "File";
			this.idShortPath = "";
			this.submodelIdentifier = ""
			this.value = new DataObject("value","",this.submodelIdentifier,this.idShortPath);
	}
	serialize(){
		let jsonData =  super.serialize();
		jsonData["value"] = this.value.text;
		//jsonData["contentType"] = this.contentType.getSelectedItem();
		jsonData["modelType"] = "File";
		return jsonData;
	}
	deserialize(data,parentId,exdomain){
		super.deserialize(data,parentId,exdomain);
		if (data.hasOwnProperty("value")){
			this.value.text = data["value"];
		}
	}
	createDom(parentId,exdomain){
		this.value.createDom(parentId,exdomain);
		super.createDom(parentId,exdomain);
	}
}
class SubmodelElementCollection extends SubmodelElement{
	constructor(extensions,category,idShort,displayName,description,
			checksum,kind,semanticId,supplementalSemanticIds,
			qualifiers,embeddedDataSpecifications,value){
				super(extensions,category,idShort,displayName,description,
						checksum,kind,semanticId,supplementalSemanticIds,
						qualifiers,embeddedDataSpecifications);
				this.value = new Array();
				this.modelType = "SubmodelElementCollection";
			}
	serialize(){
		let jsonData =  super.serialize();
		if (this.value != null){
			if (this.value.length > 0 ){
				jsonData["value"] = new Array();
				for (var elemId of this.value){
					jsonData["value"].push(elemId);
				}
				
			}	
		}
		jsonData["modelType"] = this.modelType;
		return jsonData;
	}
	deserialize(data,parentId,exdomain){
		super.deserialize(data,parentId,exdomain);
	}
	createDom(parentId,exdomain){
		super.createDom(parentId,exdomain);
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
		// let jsonData = {};
		// if jsonData["value"] !=null jsonData["value"] =
		// this.value.serialize();
		// return jsonData;
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
	constructor(id,
				extensions,category,idShort,displayName,description,
				checksum,
				administration,kind,semanticId,supplementalSemanticIds,
				qualifiers,embeddedDataSpecifications,submodelElements,uuid=""){
		super(id,extensions,category,idShort,displayName,description,
				checksum,administration);
       this.kind = kind;
       this._Qualifiable = new ComplexObject("Qualifiable","Qualifiable");
       this._HasSemantics = new ComplexObject("HasSemantics","HasSemantics");
       this.embeddedDataSpecifications = embeddedDataSpecifications;
       this.submodelElements = submodelElements;
       this.uuid =uuid;
       this.exdomain = "";
    }
	createDom(parent,exdomain){
		this.uuid = crypto.randomUUID();
		this.exdomain = exdomain;
		document.getElementById(parent).insertAdjacentHTML(
				 'afterbegin',
				 `<div class="temp" id = "`+this.uuid+`">
				 </div>`);
		this._Qualifiable.createDom(this.uuid,exdomain);
		this._HasSemantics.createDom(this.uuid,exdomain);
		super.createDom(this.uuid,exdomain);
	}
	serialize(){
		let jsonData =  super.serialize();
		//jsonData["kind"] = this.kind.getString();
		jsonData["modelType"] = "Submodel";
		if (this._HasSemantics._object != null){
			if (this._HasSemantics._object.semanticId._object != null){	
				jsonData["semanticId"] = this._HasSemantics._object.semanticId.serialize(); 
			}
			if (this._HasSemantics._object.supplementalSemanticIds != null){
				if (this._HasSemantics._object.supplementalSemanticIds.getLength() > 0){
					jsonData["semanticId"] = this._HasSemantics._object.supplementalSemanticIds.serialize();
				} 
			}
		}
		if (this._Qualifiable._object != null){
			if (this._Qualifiable._object.qualifiers.getLength() > 0 ){
				jsonData["qualifiers"] = this._Qualifiable._object.qualifiers.serialize();
			}
		}
			
		if (this.embeddedDataSpecifications != null){
			if (this.embeddedDataSpecifications.getLength() > 0 ){
				jsonData["embeddedDataSpecifications"] = this.embeddedDataSpecifications.serialize();
			}	
		}
		if (this.submodelElements != null){
			if (this.submodelElements.length > 0 ){
				jsonData["submodelElements"] = new Array()
				for (var elemId of this.submodelElements){
					jsonData["submodelElements"].push(elemId);
				}
				
			}	
		}
		jsonData["modelType"] = "Submodel";
		return jsonData;
	}
	deserialize(data,parentId,exdomain){
		super.deserialize(data,parentId,exdomain);
		if (data.hasOwnProperty('qualifiers')){
			
			this._Qualifiable.deserialize(data['qualifiers'],parentId,exdomain);
		}
	  if (data.hasOwnProperty('submodelElements')){
			this.submodelElements = data["submodelElements"];
	    }
		this._HasSemantics.deserialize(data,parentId,exdomain);
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
