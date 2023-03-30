class NObject{
	constructor(){
		this.object = null;
	}
	getObject(){
		
	}
}
class ListObject{
	constructor(count){
		this.list = new Array();
	}
	append(_obj){
		this.list.push(_obj);
	}
	remove(_id){
		for (var i = 0; i < this.list.length; i++ ) {
			if (this.list[i]._uuid == _id){
				this.list.splice(i,1);
				break;
			}
		}
	}
}
function getInputElement(elementName,required,_uuid){
	let inputText = document.createElement("input");
	inputText.setAttribute("style","height : 6.5vh");
	inputText.setAttribute("type","text");
	inputText.setAttribute("class","form-control");
	inputText.setAttribute("id",_uuid);
	inputText.setAttribute("name",elementName);
	inputText.attributes.required  = required;
	return inputText;
}

function getSelectElement(selectType,_uuid){
	let options = null ;
	if (selectType == "lang-code"){
		options = langOption();
	}
	if (selectType == "category"){
		options = categoryOption();
	}
	if (selectType == "valueType"){
		options = DataTypeXSD();
	}
	if (selectType == "reference"){
		options = ReferenceTypes();
	}
	if (selectType == "key"){
		options = KeyTypes();
	}
	if (selectType == "QualifierKind"){
		options = qualifierKind();
	}
	let selectElement = document.createElement("select");
	selectElement.setAttribute("style","height : 6.5vh");
	selectElement.setAttribute("name",selectType);
	selectElement.setAttribute("id",_uuid);
	selectElement.setAttribute("class","form-control");
	selectElement.setAttribute("aria-label","Default select example");
	selectElement.innerHTML = options;
	return selectElement;
}
function addlangString(parentId,exdomain,langStringObjects){
	let _uuid = crypto.randomUUID();
	let newId = parentId+"-"+"langString"+"-"+_uuid;
	let inputTextElement = getInputElement("lang-text","","lang-text"+_uuid);
	let selectElement = getSelectElement("lang-code","lang-code"+_uuid);
	
	document.querySelector('#'+parentId).insertAdjacentHTML(
			 'beforeend',
			`<div id = "`+newId+`">
				<div class = "row">
					<div class = "col-2"></div>
					<div class = "col-3">
					`+selectElement.outerHTML+`
					</div>
					<div class = "col-4">
						<div class="form-floating">
							`+inputTextElement.outerHTML+`
						</div>
					</div>
					<div class = "col-2  d-flex flex-wrap align-items-center justify-content-center">
						<div class="std-submodel-add" style = "margin-left : 50%">
							<input type = "image" style = "height : 3vh;cursor: pointer;" id = "`+newId+`-remove-button"  src="`+exdomain+`web/images/delete_button.svg" >
							<div class="std-submodel-add-overlay">
								<input type = "image"  style = "height : 3vh;cursor: pointer;" id = "`+newId+`-remove-button-overlay" src="`+exdomain+`web/images/delete_button1.svg" >
							</div>													
						</div>					
					</div>
				</div>
				<div class="row" style="min-height : 2.5vh;"></div>
			</div>`
			
	)
		
	
	let langText = new StringObject("");
	document.getElementById("lang-text"+_uuid).addEventListener("input", function (evt) {
		evt.preventDefault();
		langText.setString(evt.target.value);
		return false;
			});	
	

	let langCode = new StringObject("en");
	document.getElementById("lang-code"+_uuid).addEventListener("change", function (evt) {
		evt.preventDefault();
		langCode.setString(evt.target.value);
		return false;
	});
	
	let _langString = new LangString(langCode,langText,newId);
	langStringObjects.append(_langString);
	document.getElementById(newId+"-remove-button").addEventListener( "click", function (evt) {
	    evt.preventDefault();
	    removeLangString(newId,exdomain,langStringObjects);
		return false;
	})
	document.getElementById(newId+"-remove-button-overlay").addEventListener( "click", function (evt) {
		evt.preventDefault();
		removeLangString(newId,exdomain,langStringObjects);
		return false;
	});	
	return false;
}
function removeLangString(langStringId,exdomain,langStringObjects){
	document.getElementById(langStringId).remove();
	langStringObjects.remove(langStringId);
}
function addAdministration(parentId,exDomain,_administration){
	document.querySelector('#'+parentId+"-administration_Childs").insertAdjacentHTML(
			'beforeend',
			`<div class = "row" style = "height : 5vh">
						<div class = "col-2  d-flex flex-wrap align-items-center text-center">
							<span style = "size : 1em">Version</span>
						</div>
						<div class = "col-2"></div>
						<div class = "col-8  d-flex flex-wrap align-items-center text-center">
							<div class="form-floating">
								<input style = "height : 6.5vh" type="text" class="form-control" id="`+parentId+`administration-version" name="administration-version" required="required">
							</div>
						</div>
			</div>
			<div class="row" style="min-height : 2.5vh;"></div>
			<div class="row" style="min-height : 2.5vh;"></div>
			<div class = "row" style = "height : 5vh">
				<div class = "col-2  d-flex flex-wrap align-items-center text-center">
					<span style = "size : 1em">Revision</span>
				</div>
				<div class = "col-2"></div>
				<div class = "col-8  d-flex flex-wrap align-items-center text-center">
					<div class="form-floating">
						<input style = "height : 6.5vh" type="text" class="form-control" id="`+parentId+`administration-revision" name="`+parentId+`administration-revision" required="required">
					</div>
				</div>
			</div>`);
			document.getElementById(parentId+"-add_button").remove();
			let version = new StringObject("");
			document.getElementById(parentId+"administration-version").addEventListener("input", function (evt) {
				evt.preventDefault();
				version.setString(evt.target.value);
				return false;
					});	
			

			let revision = new StringObject("");
			document.getElementById(parentId+"administration-revision").addEventListener("input", function (evt) {
				evt.preventDefault();
				revision.setString(evt.target.value);
				return false;
			});	
			_administration.version = version;
			_administration.revision = revision;
}
function addKey(parentId,exDomain,_referenceObject1){
	let _uuid = crypto.randomUUID();
	let newId = parentId+"-key-"+_uuid;
	let _referenceObject = _referenceObject1;
	console.log("done _referenceObject");
	let _keyType = new StringObject("");
	let _keyType_uuid = crypto.randomUUID();
	let _keyTypeselectElement = getSelectElement("key",_keyType_uuid);

	
	let keyText = new StringObject("");
	let _keyText_uuid = crypto.randomUUID();
	let keyTextElement = getInputElement("key-text","",_keyText_uuid);

	
	document.querySelector('#'+parentId).insertAdjacentHTML(
	'beforeend',
	`<div id = "`+newId+`">
		<div class = "row">
			<div class = "col-2"></div>
			<div class = "col-3">
				`+_keyTypeselectElement.outerHTML+`
			</div>
			<div class = "col-4">
				<div class="form-floating">
				`+keyTextElement.outerHTML+`
				</div>
			</div>
			<div class = "col-2  d-flex flex-wrap align-items-center justify-content-center">
				<div class="std-submodel-add" style = "margin-left : 50%">
				<input type = "image" style = "height : 3vh;cursor: pointer;" id = "`+newId+`-remove-button"  src="`+exDomain+`web/images/delete_button.svg" >
					<div class="std-submodel-add-overlay">
						<input type = "image"  style = "height : 3vh;cursor: pointer;" id = "`+newId+`-remove-button-overlay" src="`+exDomain+`web/images/delete_button1.svg" >
					</div>													
				</div>					
			</div>
		</div>
	</div>
	<div class="row" style="min-height : 2.5vh;"></div>`);
	document.getElementById(keyTextElement.id).addEventListener("input", (evt) => {
		keyText.setString(evt.target.value);
		});	
	document.getElementById(_keyTypeselectElement.id).addEventListener("change", (evt) => {
		_keyType.setString(evt.target.value);
		});
	let _key = new Key(_keyType,keyText,_uuid);
	_referenceObject.keys.append(_key);
	document.getElementById(newId+"-remove-button").addEventListener( "click", function (evt) {
	    evt.preventDefault();
	    removeKey(newId,_referenceObject);
		return false;
	});
	document.getElementById(newId+"-remove-button-overlay").addEventListener( "click", function (evt) {
		evt.preventDefault();
		removeKey(newId,_referenceObject);
		return false;
	});	
}
function removeKey(parentId,_referenceObject)
{
	document.getElementById(parentId).remove();
	for (var i = 0; i < _referenceObject.keys.length; i++ ) {
		_referenceObject.keys.splice(i,1);
	}
}

function referenceAddButton(parentType,exDomain){
	document.querySelector('#'+parentType+"_add_button").insertAdjacentHTML(
			 'beforeend',
			 `<div class="std-submodel-add">
				 <input type = "image" style = "height : 3vh; width : 3svh ;cursor: pointer;" id = "std-submodel-img" src="`+exDomain+`web/images/plus_blue.svg" onclick="addReference('`+parentType+`','`+parentType+`References','`+exDomain+`',false);return false;">
				 <div class="std-submodel-add-overlay">
				 <input type = "image"  style = "height : 3vh; width : 3vh ;cursor: pointer;" id = "std-submodel-img-overlay" src="`+exDomain+`web/images/plus1.svg" onclick="addReference('`+parentType+`','`+parentType+`References','`+exDomain+`',false);return false;">
				 </div>
			 </div>`
	)
}

function addValueType(parentId,domain){
	let _valueType = new StringObject("xs:anyType");
	let _uuid = crypto.randomUUID();
	let selectElement = getSelectElement("valueType",parentId+_uuid);
	document.querySelector('#'+parentId).insertAdjacentHTML(
			 'afterbegin',
				`<div class = "row">
					<div class = "col-4  d-flex flex-wrap align-items-center text-center">
						<span style = "size : 1em">ValueType </span>
					</div>
					<div class = "col-2"></div>
					<div class = "col-4  d-flex flex-wrap align-items-center text-center">
						`+selectElement.outerHTML+`
					</div>
					<div class = "col-2"></div>
				</div>	
				<div class="row" style="min-height : 2.5vh; border-bottom : 0.1vh solid #dee2e6 "></div>		
			</div>`
	);
	document.getElementById(selectElement.id).addEventListener("change", (event) => {
		_valueType.setString(event.target.value);
	});
	return _valueType;
}
function addQualifierKind(parentId,domain){
	let _kind = new StringObject("valueQualifier");
	let _uuid = crypto.randomUUID();
	let selectElement = getSelectElement("QualifierKind",parentId+_uuid);
	document.querySelector('#'+parentId).insertAdjacentHTML(
			 'afterbegin',
				`
				<div class = "row">
					<div class = "col-4  d-flex flex-wrap align-items-center text-center">
						<span style = "size : 1em">Kind </span>
					</div>
					<div class = "col-2"></div>
					<div class = "col-4  d-flex flex-wrap align-items-center text-center">
						`+selectElement.outerHTML+`
					</div>
					<div class = "col-2"></div>
				</div>	
				<div class="row" style="min-height : 2.5vh; border-bottom : 0.1vh solid #dee2e6 "></div>		
			</div>`
	);
	document.getElementById(selectElement.id).addEventListener("change", (event) => {
	_kind.setString(event.target.value);
	});
	return _kind;
}
function addSimpleElement(elementName, parentElement,exdomain,required,borderRequired){
	let _borderRow = "";
	if (borderRequired) _borderRow = returnBorderRow();
	newId = parentElement + "-"+elementName 
	let _uuid = crypto.randomUUID();
	let inputElement = getInputElement(elementName,required,_uuid);
	document.querySelector('#'+parentElement).insertAdjacentHTML(
			 'afterbegin',
			 `<div id = "`+newId+`">
				<div class="row" style="min-height : 2.5vh;"></div>
			    <div class = "row">
					<div class = "col-2  d-flex flex-wrap align-items-center text-center">
						<span style = "size : 1em">`+elementName+`</span>
					</div>
					<div class = "col-2"></div>
					<div class = "col-6  d-flex flex-wrap align-items-center text-center">
						<div class="form-floating">
							`+inputElement.outerHTML+`
							<label for="`+elementName+`">Please provide the `+elementName+`</label>
						</div>
					</div>
					<div class = "col-2"></div>
				</div>
				<div class="row" style="min-height : 2.5vh;"></div>
				`+ _borderRow+`
			</div>`)
	
	let _simpleElement = new StringObject("");
	document.getElementById(inputElement.id).addEventListener("input", (evt) => {
		_simpleElement.setString(evt.target.value);
		});	
	return _simpleElement;
}
function addLangStringUtliizer(elementName,parentElement,exdomain){
	let newId = parentElement + "-"+elementName;
	let langStringObjects = new ListObject("empty");
	  
	document.querySelector('#'+parentElement).insertAdjacentHTML(
			 'afterbegin',
	`			<div id = "`+newId+`">
				<div class="row" style="min-height : 2.5vh;"></div>
				<div class = "row">
						<div class = "col-2">
						 	<div class="std-submodel-add" >
									<input type = "image" style = "height : 3vh; width : 3svh ;cursor: pointer;" id = "`+newId+`-add-button" src="`+exdomain+`web/images/plus_blue.svg" >
									<div class="std-submodel-add-overlay">
										<input type = "image"  style = "height : 3vh; width : 3vh ;cursor: pointer;" id = "`+newId+`-add-button-overlay" src="`+exdomain+`web/images/plus1.svg">
									</div>
							</div>
						</div>
						<div class = "col-6">
						</div>
						<div class = "col-4  d-flex flex-wrap align-items-right text-right">
							<span>`+elementName+`</span>
						</div>
				</div>
				<div class="row" style="min-height : 2.5vh;"></div>
				<div class  = "row"  id = "`+newId+`-LangStringSet">
				</div>
				<div class="row" style="min-height : 2.5vh; border-bottom : 0.1vh solid #dee2e6 "></div>
			</div>
	`);
	
	document.getElementById(newId+"-add-button").addEventListener( "click", function (evt) {
	    evt.preventDefault();
		addlangString(newId+"-LangStringSet",exdomain,langStringObjects);
		return false;
	});
	document.getElementById(newId+"-add-button-overlay").addEventListener( "click", function (evt) {
		evt.preventDefault();
		addlangString(newId+"-LangStringSet",exdomain,langStringObjects)
		return false;
	});	
	return langStringObjects;
};
function removeReference(referenceId,parentId,removeaddbutton,_referenceObject){
	document.getElementById(referenceId).remove();
	if (removeaddbutton){
		document.getElementById(parentId+"-add-button").style.visibility = "visible";
	}
	_referenceObject.type = new NObject();
	_referenceObject.keys = new ListObject("empty");
	
}
function getReference(parentId,exDomain,removeaddbutton,_referenceObject1){
	let _uuid = crypto.randomUUID();
	let newId = parentId+`-Reference-`+_uuid;
	let _referenceObject = _referenceObject1;
	let referenceType = new StringObject("");
	let referenceTypeselectElement = getSelectElement("reference");
	referenceTypeselectElement.addEventListener("change", (event) => {
		referenceType.setString(event.target.value);
	});
	
	_referenceObject.type = referenceType;
	document.querySelector('#'+parentId).insertAdjacentHTML(
			 'beforeend',
			 	
	 `<div id = "`+newId+`">
				<div class = "row" id = "referenceType">
					<div class = "col-2"><span>type</span></div>
					<div class = "col-2"></div>
					<div class = "col-6  d-flex flex-wrap align-items-center text-center">
						`+
						referenceTypeselectElement.outerHTML
						+`
					</div>
					<div class = "col-2">
						<div class="std-submodel-add" style = "margin-left : 50%">
							<input type = "image" style = "height : 3vh;cursor: pointer;" id = "`+newId+`-ref-remove-button"  src="`+exDomain+`web/images/delete_button.svg"  >
							<div class="std-submodel-add-overlay">
								<input type = "image"  style = "height : 3vh;cursor: pointer;" id = "`+newId+`-ref-remove-button-overlay" src="`+exDomain+`web/images/delete_button1.svg" >
							</div>													
						</div>	
					 </div>
			      </div>
				 <div class="row" style="min-height : 2.5vh;"></div>
				 <div id = "`+newId+`-Keys">
				 	<div class = "row">
						<div class = "col-2">
						 	<div class="std-submodel-add" >
									<input type = "image" style = "height : 2vh; width : 2vh ;cursor: pointer;" id = "`+newId+`-Keys-add-button" src="`+exDomain+`web/images/plus_blue.svg" >
									<div class="std-submodel-add-overlay">
										<input type = "image"  style = "height : 2vh; width : 2vh ;cursor: pointer;" id = "`+newId+`-Keys-add-button-overlay" src="`+exDomain+`web/images/plus1.svg">
									</div>
							</div>
						</div>
						<div class = "col-6">
						</div>
						<div class = "col-4  d-flex flex-wrap align-items-right text-right">
							<span>Keys</span>
						</div>
				     </div>
				<div class="row" style="min-height : 2.5vh;"></div>
			</div>
			<div class="row">
				<div class = "col-8"  style=" border-bottom : 0.1vh solid black "></div>
				<div class = "col-4"></div>
			</div>
			<div class="row" style="min-height : 2.5vh;"></div>
			</div>`
	);
	console.log("startig add key listner");
	document.getElementById(newId+"-Keys-add-button").addEventListener( "click", function (evt) {
	    evt.preventDefault();
	    console.log("fired add key");
	    addKey(newId+"-Keys",exDomain,_referenceObject);
	    return false;
	});
	document.getElementById(newId+"-Keys-add-button-overlay").addEventListener( "click", function (evt) {
		evt.preventDefault();
		console.log("fired add key");
		addKey(newId+"-Keys",exDomain,_referenceObject);
		return false;
	});	
	
	document.getElementById(newId+"-ref-remove-button").addEventListener( "click", function (evt) {
	    evt.preventDefault();
	    removeReference(newId,parentId,removeaddbutton,_referenceObject);
	    return false;
	});
	document.getElementById(newId+"-ref-remove-button-overlay").addEventListener( "click", function (evt) {
		evt.preventDefault();
		removeReference(newId,parentId,removeaddbutton,_referenceObject);
		return false;
	});	
	
}

function addReferences(parentId,exDomain,semanticIdList1,removeaddbutton){
	let _ruuid1 = crypto.randomUUID();
	let semanticIdList = semanticIdList1;
	let _referenceSemanticId = new Reference(new StringObject("GlobalReference"),new ListObject("empty"),new NObject(),_ruuid1);
	semanticIdList.append(_referenceSemanticId);
	getReference(parentId,exDomain,removeaddbutton,_referenceSemanticId)
}

function addReference(parentId,exDomain,_referenceReferTo,removeaddbutton){
	getReference(parentId,exDomain,removeaddbutton,_referenceReferTo);
	if (removeaddbutton){
		document.getElementById(parentId+"-add-button").style.visibility = "hidden";
	}
}
function removeHasSemantic(parentId,exdomain,_HasSemantics)
{	
	let parent = document.getElementById(parentId);
	while (parent.firstChild) {
	        parent.removeChild(parent.firstChild);
	}
	document.getElementById(parentId+"-add-button").style.visibility = 'visible';
	document.getElementById(parentId+"-remove-button").style.visibility = 'hidden';
	_HasSemantics.semanticId = null;
	_HasSemantics.supplementalSemanticIds = new ListObject("empty");
}
function addHasSemantic(parentId,exdomain,_hasSemantics){
	document.getElementById(parentId+"-add-button").style.visibility = 'hidden';
	document.getElementById(parentId+"-remove-button").style.visibility = 'visible';
	let _ruuid = crypto.randomUUID();
	let _ruuid1 = crypto.randomUUID();
	let _HasSemantics = _hasSemantics;
	_HasSemantics.semanticId = new Reference(new StringObject("GlobalReference"),new ListObject("empty"),new NObject(),_ruuid);
	document.querySelector('#'+parentId).insertAdjacentHTML(
			 'afterbegin',
				`<div>
					<div class="row" style="min-height : 2.5vh;"></div>	
					<div  id = "`+parentId+`-SemanticId">
					<div class="row">
						<div class = "col-6" style="min-height : 2.5vh; border-bottom : 0.1vh solid #dee2e6 ">
							<span style = "size : 1em">semnticId</span>
						</div>
						<div class = "col-2">
							<div class="std-submodel-add" id = "`+parentId+"-SemanticId-Reference-add-button"+`">
								<input type = "image" style = "height : 3vh; width : 3svh ;cursor: pointer;" id = "`+_ruuid+"-add-button"+`" src="`+exdomain+`web/images/plus_blue.svg" >
								<div class="std-submodel-add-overlay">
								 	<input type = "image"  style = "height : 3vh; width : 3vh ;cursor: pointer;" id = "`+_ruuid+"-add-button-overlay"+`" src="`+exdomain+`web/images/plus1.svg" >
								</div>
							</div>								
						</div>
						<div class = "col-4"></div>
					</div>
					<div class="row" style="min-height : 2.5vh;"></div>
					<div id = "`+parentId+`-SemanticId-Reference">
						<div class="row" style="min-height : 2.5vh;"></div>
				 </div>
				
				   <div class="row" style="min-height : 2.5vh;"></div>
					<div id = "`+parentId+`-SupplemeticSemanticIds">
				<div  class = "row">
					<div class = "col-6  d-flex flex-wrap align-items-center text-center" style="min-height : 2.5vh; border-bottom : 0.1vh solid #dee2e6 ">
						<span style = "size : 1em">Supplemental SemanticIds</span>
					</div>
					<div class = "col-2">
						<div class="std-submodel-add">
							<input type = "image" style = "height : 3vh; width : 3svh ;cursor: pointer;" id = "`+_ruuid1+"-add-button"+`" src="`+exdomain+`web/images/plus_blue.svg" >
							<div class="std-submodel-add-overlay">
								<input type = "image"  style = "height : 3vh; width : 3vh ;cursor: pointer;" id = "`+_ruuid1+"-add-button-overlay"+`" src="`+exdomain+`web/images/plus1.svg">
							</div>
					     </div>				
					  </div>
					  <div class = "col-4">
				      </div>
				  </div>	
			    <div class="row" style="min-height : 2.5vh;"></div>	
		        <div id = "`+parentId+`-SupplementalSemanticId-References">
		        </div>
		   </div>
				 </div>
				`);
	document.getElementById(_ruuid+"-add-button").addEventListener( "click", function (evt) {
	    evt.preventDefault();
	    addReference(parentId+"-SemanticId-Reference",exdomain,_HasSemantics.semanticId,true);
		return false;
	});
	document.getElementById(_ruuid+"-add-button-overlay").addEventListener( "click", function (evt) {
		evt.preventDefault();
		addReference(parentId+"-SemanticId-Reference",exdomain,_HasSemantics.semanticId,true);
		return false;
	});	
	
	document.getElementById(_ruuid1+"-add-button").addEventListener( "click", function (evt) {
	    evt.preventDefault();
	    addReferences(parentId+"`-SupplementalSemanticId-References",exdomain,_HasSemantics.supplementalSemanticIds,false);
		return false;
	});
	document.getElementById(_ruuid1+"-add-button-overlay").addEventListener( "click", function (evt) {
		evt.preventDefault();
		addReferences(parentId+"-SupplementalSemanticId-References",exdomain,_HasSemantics.supplementalSemanticIds,false);
		return false;
	});	
}

function addHasSemantics(parentElement,exdomain,_HasSemantics1){
	let newId = parentElement+"-HasSemantics";
	let _HasSemantics = _HasSemantics1;
	document.querySelector('#'+parentElement).insertAdjacentHTML(
			 'afterbegin',
			`<div id = "`+newId+`">
				<div class="row" style="min-height : 2.5vh;"></div>
				<div class = "row">
						<div class = "col-2" id = "`+newId+`-Data-add-button">
								<div class="std-submodel-add">
										<input type = "image" style = "height : 3vh; width : 3vh ;cursor: pointer;" id = "`+newId+`-add-button" src="`+exdomain+`web/images/plus_blue.svg" >
										<div class="std-submodel-add-overlay">
											<input type = "image"  style = "height : 3vh; width : 3vh ;cursor: pointer;" id = "`+newId+`-add-button-overlay" src="`+exdomain+`web/images/plus1.svg" >
										</div>
								</div>							
						</div>
						<div class = "col-2" id = "`+newId+`-Data-remove-button" style = "visibility : hidden">
							<div class="std-submodel-add">
										<input type = "image" style = "height : 3vh; width : 3vh ;cursor: pointer;" id = "`+newId+`-remove-button" src="`+exdomain+`web/images/delete_button.svg" >
										<div class="std-submodel-add-overlay">
											<input type = "image"  style = "height : 3vh; width : 3vh ;cursor: pointer;" id = "`+newId+`-remove-button-overlay" src="`+exdomain+`web/images/delete_button1.svg" >
										</div>
							</div>							
						</div>
						<div class = "col-4">
						</div>
						<div class = "col-4  d-flex flex-wrap align-items-right text-right">
							<span>HasSemantics</span>
						</div>
				</div>
				<div class="row" style="min-height : 2.5vh;"></div>
				<div id = "`+newId+"-Data"+`">
					
				</div>
				<div class="row" style="min-height : 2.5vh; border-bottom : 0.1vh solid #dee2e6 "></div>
			</div>`);
	
		document.getElementById(newId+"-add-button").addEventListener( "click", function (evt) {
		    evt.preventDefault();
		    addHasSemantic(newId+"-Data",exdomain,_HasSemantics);
			return false;
		});
		document.getElementById(newId+"-add-button-overlay").addEventListener( "click", function (evt) {
			evt.preventDefault();
			addHasSemantic(newId+"-Data",exdomain,_HasSemantics);
			return false;
		});	
	
		document.getElementById(newId+"-remove-button").addEventListener( "click", function (evt) {
		    evt.preventDefault();
		    removeHasSemantic(newId+"-Data",exdomain,_HasSemantics);
			return false;
		});
		document.getElementById(newId+"-remove-button-overlay").addEventListener( "click", function (evt) {
			evt.preventDefault();
			removeHasSemantic(newId+"-Data",exdomain,_HasSemantics);
			return false;
		});	
}
function addCategory(parentElement){
	let newId = parentElement+"-"+"Category";
	let _category = new StringObject("CONSTANT");
	let selectElement = getSelectElement("category");
		
	document.querySelector('#'+parentElement).insertAdjacentHTML(
			 'afterbegin',
	`<div id = "`+newId+`">
					<div class="row" style="min-height : 2.5vh;"></div>
					<div class = "row">
						<div class = "col-4  d-flex flex-wrap align-items-center text-center">
							<span style = "size : 1em">Category </span>
						</div>
						<div class = "col-2"></div>
						<div class = "col-4  d-flex flex-wrap align-items-center text-center">
							`+selectElement.outerHTML+`
						</div>
						<div class = "col-2"></div>
					</div>	
					<div class="row" style="min-height : 2.5vh; border-bottom : 0.1vh solid #dee2e6 "></div>		
				</div>`);
	document.getElementById(selectElement.id).addEventListener("change", (event) => {
		_category.setString(event.target.value);
	});
	return _category;
}
function addAdministrationParent(parentElement,exdomain){
	let newId = parentElement +"-"+"administration";
	let _administration = new AdministrativeInformation(new StringObject(""),new StringObject(""),new StringObject(""));
	document.querySelector('#'+parentElement).insertAdjacentHTML(
			 'afterbegin',
`
			 <div id = "`+newId+`">
				<div class="row" style="min-height : 2.5vh;"></div>
				<div class = "row">
						<div class = "col-2">
						 	<div class="std-submodel-add" id = "`+newId+`-add_button">
									<input type = "image" style = "height : 3vh; width : 3svh ;cursor: pointer;" id = "`+newId+`-add-button" src="`+exdomain+`web/images/plus_blue.svg" >
									<div class="std-submodel-add-overlay"id = "`+newId+`-add_button-overlay">
										<input type = "image"  style = "height : 3vh; width : 3vh ;cursor: pointer;" id = "`+newId+`-add-button-overlay" src="`+exdomain+`web/images/plus1.svg">
									</div>
							</div>
						</div>
						<div class = "col-6">
						</div>
						<div class = "col-4  d-flex flex-wrap align-items-right text-right">
							<span>administration</span>
						</div>
				</div>
				<div class="row" style="min-height : 2.5vh;"></div>
				<div id = "`+newId+`-administration_Childs">

				</div>
				<div class="row" style="min-height : 2.5vh;"></div>
				<div class="row" style="min-height : 2.5vh; border-bottom : 0.1vh solid #dee2e6 "></div>
			</div>
`);
	document.getElementById(newId+"-add-button").addEventListener( "click", function (evt) {
	    evt.preventDefault();
	    addAdministration(newId,exdomain,_administration);
		return false;
	})
	document.getElementById(newId+"-add-button-overlay").addEventListener( "click", function (evt) {
		evt.preventDefault();
		addAdministration(newId,exdomain,_administration);
		return false;
	});
	
	return _administration;
}
function removeExtension(_extensionId,extensionList){
	document.getElementById(_extensionId).remove();
	extensionList.remove(_extensionId);
}
function returnBorderRow()
{
	return `<div class="row" style="min-height : 2.5vh; border-bottom : 0.1vh solid #dee2e6 "></div>`;
}

function addExtension(parentId,exdomain,extensionsList){
	let _uuid = crypto.randomUUID();
	let newId = parentId + "-" + "Extension" + "-" + _uuid;
	
	let _name = new StringObject("");
	let _name_uuid = crypto.randomUUID();
	let nameTextElement = getInputElement("name","",_name_uuid);
	nameTextElement.addEventListener("input", (event) => {
		_name.setString(event.target.value);
			});	
	
	let _value = new StringObject("");
	let _value_uuid = crypto.randomUUID();
	let valueTextElement = getInputElement("value","",_value_uuid);
	valueTextElement.addEventListener("input", (event) => {
		_value.setString(event.target.value);
			});
	
	let valueType = new StringObject("xs:anyURI");
	let _valueType_uuid = crypto.randomUUID();
	let valueTypeselectElement = getSelectElement("valueType",_valueType_uuid);
	valueTypeselectElement.addEventListener("change", (event) => {
		valueType.setString(event.target.value);
	});
	let _ruuid = crypto.randomUUID();
	let _referenceReferTo = new Reference(new StringObject("GlobalReference"),new ListObject("empty"),null,_ruuid)
	
	document.querySelector('#'+parentId).insertAdjacentHTML(
			 'afterbegin',
				`	<div id = "`+newId+`">
						<div id = "`+newId+`-name">
							<div class = "row">
								<div class = "col-8  d-flex flex-wrap align-items-center text-center" style="min-height : 2.5vh; border-bottom : 0.1vh solid #dee2e6 ">
									<span style = "size : 1em">Extension</span>
								</div>
								<div class = "col-2">
									<div class="std-submodel-add" style = "margin-left : 50%">
										<input type = "image" style = "height : 2vh; width : 2vh ;cursor: pointer;" id = "`+newId+"remove-button"+`"  src="`+exdomain+`web/images/delete_button.svg" >
										<div class="std-submodel-add-overlay">
											<input type = "image"  style = "height : 2vh; width : 2vh ;cursor: pointer;" id = "`+newId+"remove-button-overlay"+`" src="`+exdomain+`web/images/delete_button1.svg" >
										</div>													
									</div>
								</div>
								<div class = "col-2">
								</div>
							</div>
							<div class="row" style="min-height : 2.5vh;"></div>	
													
							<div class = "row">
								<div class = "col-2  d-flex flex-wrap align-items-center text-center">
									<span style = "size : 1em">name</span>
								</div>
								<div class = "col-2"></div>
								<div class = "col-6  d-flex flex-wrap align-items-center text-center">
									<div class="form-floating">
										`+nameTextElement.outerHTML+`
										<label for="name">Please provide the name</label>
									</div>
								</div>
								<div class = "col-2"></div>
							</div>
							<div class="row" style="min-height : 2.5vh;"></div>
						</div>
						<div id = "`+newId+`-value">
							<div class = "row">
								<div class = "col-2  d-flex flex-wrap align-items-center text-center">
									<span style = "size : 1em">value</span>
								</div>
								<div class = "col-2"></div>
								<div class = "col-6  d-flex flex-wrap align-items-center text-center">
									<div class="form-floating">
										`+valueTextElement.outerHTML+`
										<label for="value">Please provide the value</label>
									</div>
								</div>
								<div class = "col-2"></div>
							</div>
							<div class="row" style="min-height : 2.5vh;"></div>						
						</div>
						<div id = "`+newId+`-valueType">
						
						<div class="row" style="min-height : 2.5vh;"></div>	
						</div>
						<div id = "`+newId+`-refersTo">
							<div class="row">
								<div class = "col-6" style="min-height : 2.5vh; border-bottom : 0.1vh solid #dee2e6 ">
									<span style = "size : 1em">refersTo</span>
								</div>
								<div class = "col-2">
									<div class="std-submodel-add" id = "`+newId+"-refersTo-Reference-add-button"+`">
										 <input type = "image" style = "height : 3vh; width : 3svh ;cursor: pointer;" id = "std-submodel-img" src="`+exdomain+`web/images/plus_blue.svg" onclick="addReference('`+newId+"-refersTo-Reference"+`','`+exdomain+"',"+_referenceReferTo+`,true);return false;">
										 <div class="std-submodel-add-overlay">
										 	<input type = "image"  style = "height : 3vh; width : 3vh ;cursor: pointer;" id = "std-submodel-img-overlay" src="`+exdomain+`web/images/plus1.svg" onclick="addReference('`+newId+"-refersTo-Reference"+`','`+exdomain+"',"+_referenceReferTo+`,true);return false;">
										 </div>
									 </div>								
								</div>
								<div class = "col-4"></div>
							</div>
							<div class="row" style="min-height : 2.5vh;"></div>
							<div id = "`+newId+`-refersTo-Reference">
								<div class="row" style="min-height : 2.5vh;"></div>
							</div>
						</div>
						<div id = "`+newId+`-HS">
						</div>
						<div class="row">
							<div class = "col-8"  style=" border-bottom : 0.25vh solid black ">
							</div>
							<div class = "col-4">
							</div>
						</div>
						<div class="row" style="min-height : 2.5vh;"></div>
					</div>
				`);
	
		document.getElementById(newId+"remove-button").addEventListener( "click", function (evt) {
		    evt.preventDefault();
		    removeExtension(newId,extensionsList);
			return false;
		})
		document.getElementById(newId+"remove-button-overlay").addEventListener( "click", function (evt) {
			evt.preventDefault();
			removeExtension(newId,extensionsList);
			return false;
		});	
		
		
	_hasSemantics = addHasSemantics(newId+"-HS",exdomain);
	let _valueType = addValueType(newId+"-valueType",exdomain);
	_extension = new Extension(_name,valueType,_value,
			_hasSemantics.semanticId,_hasSemantics.supplementalSemanticIds,
			_referenceReferTo,newId);
	extensionsList.append(_extension); 
}

function addHasExtensions(element_form_id,exdomain,extensions){
	let newId = element_form_id + "-" +  "HasExtensions";
	document.querySelector('#'+element_form_id).insertAdjacentHTML(
			 'afterbegin',
				`<div id = "`+newId+`">
				<div class="row" style="min-height : 2.5vh;"></div>
				<div class = "row">
						<div class = "col-2" id = "`+newId+`-add-button1">
								<div class="std-submodel-add">
										<input type = "image" style = "height : 3vh; width : 3vh ;cursor: pointer;" id = "`+newId+"-add-button"+`" src="`+exdomain+`web/images/plus_blue.svg" >
										<div class="std-submodel-add-overlay">
											<input type = "image"  style = "height : 3vh; width : 3vh ;cursor: pointer;" id = "`+newId+"-add-button-overlay"+`" src="`+exdomain+`web/images/plus1.svg">
										</div>
								</div>							
						</div>
						<div class = "col-6">
						</div>
						<div class = "col-4  d-flex flex-wrap align-items-right text-right">
							<span style = "font-style : bold">HasExtensions</span>
						</div>
				</div>
				<div class="row" style="min-height : 2.5vh;"></div>
				<div id = "`+newId+`-Extensions">
					
				</div>
				<div class="row" style="min-height : 2.5vh;"></div>
				<div class="row" style="min-height : 2.5vh; border-bottom : 0.1vh solid #dee2e6 "></div>
			</div>`)
			document.getElementById(newId+"-add-button").addEventListener( "click", function (evt) {
			    evt.preventDefault();
			    console.log("add");
			    addExtension(newId+"-Extensions",exdomain,extensions);
				return false;
			})
			document.getElementById(newId+"-add-button-overlay").addEventListener( "click", function (evt) {
				evt.preventDefault();
				console.log("add-overlay");
				addExtension(newId+"-Extensions",exdomain,extensions);
				return false;
			});
}
function addQualifiable(element_form_id,exdomain,_qualifiable1){
	let newId = element_form_id+ "-Qualifiable";
	let _qualifiable2 = _qualifiable1;
	document.querySelector('#'+element_form_id).insertAdjacentHTML(
			 'afterbegin',
				`<div id = "`+newId+`">
				<div class="row" style="min-height : 2.5vh;"></div>
				<div class = "row">
						<div class = "col-2" id = "`+newId+`-add">
								<div class="std-submodel-add">
										<input type = "image" style = "height : 3vh; width : 3vh ;cursor: pointer;" id = "`+newId+`-add-button" src="`+exdomain+`web/images/plus_blue.svg" >
										<div class="std-submodel-add-overlay">
											<input type = "image"  style = "height : 3vh; width : 3vh ;cursor: pointer;" id = "`+newId+`-add-button-overlay" src="`+exdomain+`web/images/plus1.svg" >
										</div>
								</div>							
						</div>
						<div class = "col-6">
						</div>
						<div class = "col-4  d-flex flex-wrap align-items-right text-right">
							<span style = "font-style : bold">Qualifiable</span>
						</div>
				</div>
				<div class="row" style="min-height : 2.5vh;"></div>
				<div id = "`+newId+`-Qualifiers">
					
				</div>
				<div class="row" style="min-height : 2.5vh;"></div>
				<div class="row" style="min-height : 2.5vh; border-bottom : 0.1vh solid #dee2e6 "></div>
			</div>`);
	
	document.getElementById(newId+"-add-button").addEventListener( "click", function (evt) {
	    evt.preventDefault();
	    addQualifier(newId+"-Qualifiers",exdomain,_qualifiable2);
		return false;
	})
	document.getElementById(newId+"-add-button-overlay").addEventListener( "click", function (evt) {
		evt.preventDefault();
		addQualifier(newId+"-Qualifiers",exdomain,_qualifiable2);
		return false;
	});
}
function removeQualifier(parentId,_qualifiable){
	document.getElementById(parentId).remove();
	langStringObjects.remove(langStringId);
}
function addQualifier(parentId,exdomain,_qualifiable1){
	let _uuid = crypto.randomUUID();
	let _qualifiable = _qualifiable1;
	document.querySelector('#'+parentId).insertAdjacentHTML(
			 'afterbegin',
				`	<div id = "`+parentId+`-Qualifier-`+_uuid+`">
						<div id = "`+parentId+`-Qualifier-name">
							<div class = "row">
								<div class = "col-8  d-flex flex-wrap align-items-center text-center" style="min-height : 2.5vh; border-bottom : 0.1vh solid #dee2e6 ">
									<span style = "size : 1em">Qualifier</span>
								</div>
								<div class = "col-2">
									<div class="std-submodel-add" style = "margin-left : 50%">
										<input type = "image" style = "height : 2vh; width : 2vh ;cursor: pointer;" id = "`+parentId+"-Qualifier-"+_uuid+"-remove-button"+`"  src="`+exdomain+`web/images/delete_button.svg" >
										<div class="std-submodel-add-overlay">
											<input type = "image"  style = "height : 2vh; width : 2vh ;cursor: pointer;" id = "`+parentId+"-Qualifier-"+_uuid+"-remove-button-overlay"+`" src="`+exdomain+`web/images/delete_button1.svg" >
										</div>													
									</div>
								</div>
								<div class = "col-2">
								</div>
							</div>
							<div class="row" style="min-height : 2.5vh;"></div>
						</div>
						<div id = "`+parentId+`-Qualifier-value">
						</div>
						<div class="row" style="min-height : 2.5vh;"></div>	
						<div id = "`+parentId+`-Qualifier-type">
						</div>
						<div class="row" style="min-height : 2.5vh;"></div>		
						<div id = "`+parentId+`-Qualifier-kind">
						</div>
						<div class="row" style="min-height : 2.5vh;"></div>	
						<div id = "`+parentId+`-Qualifier-valueType">
						</div>
						<div class="row" style="min-height : 2.5vh;"></div>
						<div id = "`+parentId+`-Qualifier-valueId">
							<div class="row">
								<div class = "col-6" style="min-height : 2.5vh; border-bottom : 0.1vh solid #dee2e6 ">
									<span style = "size : 1em">valueId</span>
								</div>
								<div class = "col-2" id ="`+parentId+"-Qualifier-valueId-Reference"+"-add-button"+`" >
									<div class="std-submodel-add" id = "`+parentId+"-Qualifier-valueId-Reference-add-button"+`">
										 <input type = "image" style = "height : 3vh; width : 3svh ;cursor: pointer;" id = "`+parentId+"-Qualifier-valueId-Refer-add-button"+`" src="`+exdomain+`web/images/plus_blue.svg">
										 <div class="std-submodel-add-overlay">
										 <input type = "image"  style = "height : 3vh; width : 3vh ;cursor: pointer;" id = "`+parentId+"-Qualifier-valueId-Refer-add-button-overlay"+`" src="`+exdomain+`web/images/plus1.svg" >
										 </div>
									 </div>								
								</div>
								<div class = "col-4"></div>
							</div>
							<div id = "`+parentId+"-Qualifier-valueId-Reference"+`">
								<div class="row" style="min-height : 2.5vh;"></div>
								
							</div>
						</div>
						<div id = "`+parentId+`-HS">
						</div>
						<div class="row">
							<div class = "col-8"  style=" border-bottom : 0.25vh solid black ">
							</div>
							<div class = "col-4">
							</div>
						</div>
						<div class="row" style="min-height : 2.5vh;"></div>
					</div>
				`);
	let _valueId = new NObject();
	
	document.getElementById(parentId+"-Qualifier-valueId-Refer-add-button").addEventListener( "click", function (evt) {
	    evt.preventDefault();
	    addReference(parentId+"-Qualifier-valueId-Reference",exdomain,valueId,true);
		return false;
	});
	document.getElementById(parentId+"-Qualifier-valueId-Refer-add-button-overlay").addEventListener( "click", function (evt) {
		evt.preventDefault();
		addReference(parentId+"-Qualifier-valueId-Reference",exdomain,valueId,true);
		return false;
	});	
	
	document.getElementById(parentId+"-Qualifier-"+_uuid+"-remove-button").addEventListener( "click", function (evt) {
	    evt.preventDefault();
	    removeQualifier(parentId+"-Qualifier-"+_uuid,langStringObjects);
		return false;
	})
	document.getElementById(parentId+"-Qualifier-"+_uuid+"-remove-button-overlay").addEventListener( "click", function (evt) {
		evt.preventDefault();
		removeQualifier(parentId+"-Qualifier-"+_uuid,_qualifiable);
		return false;
	});	
	
	let _valueType = addValueType_Qual(parentId+"-Qualifier-valueType",exdomain);
	let _kind = addQualifierKind(parentId+"-Qualifier-kind",exdomain);
	let _value = addSimpleElement('value',parentId+"-Qualifier-value",exdomain,"",true);
	let _type = addSimpleElement('type',parentId+"-Qualifier-type",exdomain,"",true);
	let semanticId = new NObject();
	let supplementalSemanticIds = new ListObject();
	let _qualifierHasSemantics = new HasSemantics(semanticId,supplementalSemanticIds);
	addHasSemantics(parentId+"-HS",exdomain,_qualifierHasSemantics);
	_qualifier = new Qualifier(_type,_valueType,semanticId,
			supplementalSemanticIds,_kind,_value,_valueId,parentId+"-Qualifier-"+_uuid);
	_qualifiable.append(_qualifier);
}

function addReferable(element_form_id,exdomain){
	let _extension = addHasExtensions(element_form_id,exdomain);
	let _checksum = addSimpleElement('checksum',element_form_id,exdomain,"",true);
	let descriptionList = addLangStringUtliizer('description',element_form_id,exdomain);
	let displayNameList = addLangStringUtliizer('displayName',element_form_id,exdomain);
	let _category = addCategory(element_form_id);
	let _idShort = addSimpleElement('idShort',element_form_id,exdomain,"required",true);
	return new Referable(new ListObject("empty"),_category,_idShort,displayNameList,descriptionList,_checksum)
}
function addIdentifiable(element_form_id,exdomain){
	let _administration = addAdministrationParent(element_form_id,exdomain);
	let _referable = addReferable(element_form_id,exdomain);
	return new Identifiable(new StringObject(""),_referable.extensions,
							   _referable.category,
							   _referable.idShort,
							   _referable.displayName,
							   _referable.description,
							   _referable.checksum,_administration);	
}
function addSubmodeltoForm(exdomain){
	submodel_form = document.getElementById("submodel-form");
	submodel_form.innerHTML = '';
	_submodel = new Submodel();
    _submodel.createDom("submodel-form",exdomain);
    
//	submodel_form = document.getElementById("submodel-form");
//	submodel_form.innerHTML = '';
//	_qualifiable = new ListObject();
//	addQualifiable("submodel-form",exdomain,_qualifiable);
//	_HasSemantics = new HasSemantics(new NObject(),new ListObject("empty"));
//	addHasSemantics("submodel-form",exdomain,_HasSemantics);
//	_identifiable = addIdentifiable("submodel-form",exdomain);
	
}
// _hasSemantics.semanticId,_hasSemantics.supplementalSemanticIds
function addSubmodelElement(element_form_id,exdomain){
	addReferable(element_form_id,exdomain);
}
function addDataElement(element_form_id,exdomain){
	addSubmodelElement(element_form_id,exdomain);
}
function addPropertytoForm(element_form_id,exdomain){
	element_form = document.getElementById(element_form_id);
	addDataElement(element_form_id,exdomain);
	addSimpleElement('Value',element_form_id,exdomain,"required");
	addValueType(element_form_id,exdomain);
	addValueId(element_form_id,exdomain);
}
function addMultiLanguagePropertytoForm(element_form_id,exdomain){
	element_form = document.getElementById(element_form_id);
	addDataElement(element_form_id,exdomain);
	addLangStringUtliizer('Value',element_form_id,exdomain,"required");
	addValueId(element_form_id,exdomain);
}
function addRangetoForm(element_form_id,exdomain){
	element_form = document.getElementById(element_form_id);
	addDataElement(element_form_id,exdomain);
	addSimpleElement('min',element_form_id,exdomain,"required");
	addSimpleElement('max',element_form_id,exdomain,"required");
	addValueType(element_form_id,exdomain);
}
function addReferenceElementtoForm(element_form_id,exdomain){
	element_form = document.getElementById(element_form_id);
	addDataElement(element_form_id,exdomain);
	
	// TODO
}
function addBlobtoForm(element_form_id,exdomain){
	element_form = document.getElementById(element_form_id);
	addDataElement(element_form_id,exdomain);
	addSimpleElement('value',element_form_id,exdomain,"required");
	addVcontentType(element_form_id,exdomain);
}
function addFiletoForm(element_form_id,exdomain){
	element_form = document.getElementById(element_form_id);
	addDataElement(element_form_id,exdomain);
	addSimpleElement('value',element_form_id,exdomain,"required");
	addVcontentType(element_form_id,exdomain);
}
function addSubmodelElementCollection(element_form_id,exdomain){
	addSubmodelElement(element_form_id,exdomain);
	// to do how to add values 
}
function getCategoryData(element){
	let category = element.querySelector("select");
	return category.options[category.selectedIndex].value;
}
function getLangStringSetData(element,elementName){
	var langStringList = new ListObject("empty");
	for (const child of element.children) {
		if (child.id == element.id+"-LangStringSet"){
			let LangStringSet = child;
			for(var i = 0; i < LangStringSet.children.length; i++) 
				{
					let langCodeSelect = langStrings.children[i].querySelector("select");
					let langtextInput = langStrings.children[i].querySelector("input");
					let langCode = langCodeSelect.options[langCodeSelect.selectedIndex].value;
					let langText = langtextInput.value;
					langStringList.append(new LangString(langCode,langText));
				}
		}
	}
	return langStringList;
}
function getSemanticIdData(has_seamntics){
	let semanticId = has_seamntics.querySelector("#")
}
function getSupplementalSemanticIdsData(){
	
}
function getHasSemanticsData(has_seamntics){
	return [getSemanticIdData(has_seamntics),getSupplementalSemanticIdsData(has_seamntics)]
}

function getAdministrationData(element_form_id){
	let administrationElement = document.getElementById(element_form_id+"-"+"administration");
	let administrationchildrens = administrationElement.querySelector("#adiminstration_Childs");
	if((administrationchildrens.children).length == 0){
		return null;
	}
	else {
		let versionElement = administrationchildrens.querySelector("#administration-version");
		let revisionElement = administrationchildrens.querySelector("#administration-revision");
		return new AdministrativeInformation(versionElement.value,revisionElement.value,new ListObject("empty"));
	}
}
function getReferableData(element_form_id){
	var idShort,checksum,displayName,description,category;
	idShort=checksum=displayName=description=category= null;
	let elementForm = document.getElementById(element_form_id);
	for (const child of elementForm.children) {
		if (child.id == element_form_id+"-idShort"){
			idShort = child.querySelector("input").value;
		}
		if (child.id == element_form_id+"-checksum"){
			checksum = child.querySelector("input").value;;
		}
		if (child.id == element_form_id+"-displayName"){
			displayName = getLangStringSetData(child,"displayName");
		}
		if (child.id == element_form_id+"-description"){
			description = getLangStringSetData(child,"description");
		}
		if (child.id == element_form_id+"-category"){
			category = getCategoryData(child);
		}
		if (child.id == element_form_id+"-HasExtensions"){
			category = getHasExtensionsData(child);
		}
		if (child.id == element_form_id+"-Qualifiable"){
			category = GetQualifiableData(child);
		}
		if (child.id == element_form_id+"-HasSemantics"){
			category = getHasSemanticsData(child);
		}
	}
	return [new ListObject("empty"),category,idShort,displayName,description,checksum];
}
function getIdentifiableData(element_form_id){
	return ["temp",getReferableData(element_form_id),getAdministrationData(element_form_id)];
}
function getKind(element_form_id){
	return "Instance";
}
function getReferences(referenceElement,element_form_id)
{
	let elementForm = document.getElementById(element_form_id);
	let _references = elementForm.querySelector("#"+element_form_id+"-"+referenceElement+"References");
	if(_references.children.length == 0){
		return new ListObject("empty");
	}
	else {
		let referencesList =  new ListObject("empty")
		for(var i = 0; i < _references.children.length; i++) {
			let _reference = _references.children[i];
			if (_reference.id == element_form_id+"-"+referenceElement+"References_Reference"){
				let ReferenceType = _reference.querySelector("#referenceType");
				let refTyp_Select = ReferenceType.querySelector("select")
				let refType = refTyp_Select.options[refTyp_Select.selectedIndex].value;
				let _keysP = _reference.querySelector("#"+"Key_"+element_form_id+"-"+referenceElement+"References_Keys");
				let keysList = []
				if (_keysP != null){
					for(var i = 0; i < _keysP.children.length; i++) {
						let _key = _keysP.children[i];
						let _keySelect = _key.querySelector("select");
						let keyType = _keySelect.options[_keySelect.selectedIndex].value;
						let keyValue = _key.querySelector("#key-text").value;
						keysList.append(new Key(keyType,keyValue));
					}
				}
				referencesList.append(new Reference(refType,keysList,null));
			}
		}
		return referencesList;
	}
}
function createNewSubmodel1(event,element_form_id,aasIdentifier){
	event.stopPropagation();
    event.preventDefault();
    $("#new_submodel_modal").modal('hide');
    
}
function createNewSubmodel(event,element_form_id,aasIdentifier){
	event.stopPropagation();
    event.preventDefault();
    $("#new_submodel_modal").modal('hide');
    console.log(_HasSemantics,_identifiable);
/*    let _identifiable = getIdentifiableData(element_form_id); 
    let _hasSemantics = getHasSemanticsData(element_form_id);
    let _qualifiable = getQualifiableData(element_form_id);
	let _newSubmodel = new Submodel(_identifiable[0],
    						   _identifiable[1][0],
    						   _identifiable[1][1],
    						   _identifiable[1][2],
    						   _identifiable[1][3],
    						   _identifiable[1][4],
    						   _identifiable[1][5],
    						   _identifiable[2],
    						   "Instance",
    						   _hasSemantics[0],_hasSemantics[1],[],[],[]);
	let jSubmodelObject = _newSubmodel.serialize();

	var httpGetRequest = new XMLHttpRequest();
	const FD = new FormData();
	let _ref = new Reference("GlobalReference",[new Key("Submodel","")]);
	FD.append("operation_type", "new_submodel");
	FD.append("_reference",JSON.stringify(_ref.serialize()));
	FD.append("submodel-data",JSON.stringify(jSubmodelObject));
	httpGetRequest.open('POST',"/shells/"+aasIdentifier+'/webui');
	httpGetRequest.onload = () => {
		window.location.replace('/shells/'+aasIdentifier+'/webui');
	}
	httpGetRequest.send(FD);
	*/
}
