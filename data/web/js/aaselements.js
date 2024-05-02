function addSubmodeltoForm(exdomain){
	submodel_form = document.getElementById("submodel-form");
	submodel_form.innerHTML = '';
	_submodel = new Submodel();
    _submodel.createDom("submodel-form",exdomain);	
}
function addAASElementtoForm(event,exdomain,formId,aasIdentifier,submodelId,IdShortPath){
	event.stopPropagation();
    event.preventDefault();
    aas_element_form = document.getElementById(formId);
    aas_element_form.innerHTML = '';
    aas_element_form.innerHTML = `<form onsubmit="createNewAASElement(event,'aas_element_form','`+aasIdentifier+`','`+submodelId+`','`+IdShortPath+`');return false;">
				<div class="submodel-form" id = "aas_element_form">
					
				</div>
				<div class="row" style="min-height : 2.5vh;"></div>
				<div class="row">
				<div class="container">
					<div class="row">
						<div class="col-9"></div>
						<div class="col-2">
							<button class="btn btn-primary">ADD</button>
						</div>
					</div>
				</div>
			</div>
			</form>`;
    var aas_elem_type = document.getElementById("aas_elem_type").value;
    if (aas_elem_type === "SubmodelElementCollection"){
    	_aas_elem = new SubmodelElementCollection();
    	_aas_elem.createDom(formId,exdomain);	
    }
    else if (aas_elem_type === "Property"){
    	_aas_elem = new Property();
    	_aas_elem.createDom(formId,exdomain);	
    }
    else if (aas_elem_type === "Range"){
    	_aas_elem = new Range();
    	_aas_elem.createDom(formId,exdomain);	
    }
    else if (aas_elem_type === "MultiLanguageProperty"){
    	_aas_elem = new MultiLanguageProperty();
    	_aas_elem.createDom(formId,exdomain);	
    }
    else if (aas_elem_type === "ReferenceElement"){
    	_aas_elem = new ReferenceElement();
    	_aas_elem.createDom(formId,exdomain);	
    }
}
function createNewSubmodel1(event,element_form_id,aasIdentifier){
	event.stopPropagation();
    event.preventDefault();
    $("#new_submodel_modal").modal('hide');

	var httpGetRequest = new XMLHttpRequest();
	const FD = new FormData();
	let _key = new Key("Submodel","");
	let _listObject = new ListObject("temp",_key,"")
	_ref = new Reference("ExternalReference");
	_ref.keys._list.push(_listObject);
	FD.append("operation_type", "new_submodel");
	FD.append("_reference",JSON.stringify(_ref.serialize()));
	FD.append("submodel-data",JSON.stringify(_submodel.serialize()));
	httpGetRequest.open('POST',"/shells/"+aasIdentifier+'/webui');	
	httpGetRequest.onload = () => {
		window.location.replace('/shells/'+aasIdentifier+'/webui');
	}
	httpGetRequest.send(FD);
}
function createNewAASElement(event,element_form_id,aasIdentifier,submodelId,idShortPath){
	event.stopPropagation();
    event.preventDefault();
    console.log("Preparing the request");
    $("#new_aas_element").modal('hide');
    
	var httPOSTRequest = new XMLHttpRequest();
	if (submodelId === idShortPath){
		httPOSTRequest.open('POST',"/submodels/"+btoa(submodelId)+"/submodel/submodel-elements");	
		httPOSTRequest.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
		httPOSTRequest.onload = () => {
			window.location.replace('/shells/'+aasIdentifier+'/aas/submodels/'+btoa(submodelId)+'/submodel/webui');
		}
		httPOSTRequest.send(JSON.stringify(_aas_elem.serialize()));
	}
	else{
		httPOSTRequest.open('POST',"/submodels/"+btoa(submodelId)+"/submodel/submodel-elements/"+idShortPath);	
		httPOSTRequest.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
		httPOSTRequest.onload = () => {
			window.location.replace('/shells/'+aasIdentifier+'/aas/submodels/'+btoa(submodelId)+'/submodel/webui');
		}
		httPOSTRequest.send(JSON.stringify(_aas_elem.serialize()));
	}
}

function getCollectionData(_uuid){
	let collectionElem = linearData1[_uuid]
	for (var i = 0; i < collectionElem.value.length; i++ ) {
		let _elem = (linearData1[collectionElem.value[i]]).serialize();
    	if (_elem ["modelType"] == "SubmodelElementCollection"){
    		collectionElem.value[i] = getCollectionData(collectionElem.value[i]);
    	}
    	else {
    		collectionElem.value[i] =_elem
    	}
	}
	return collectionElem.serialize();
}
function saveSubmodel(event,submodelIdentifier,aasIdentifier){
	event.stopPropagation();
    event.preventDefault();
    let _submodel_New = linearData1[submodelIdentifier].serialize();
    
    for (var i = 0; i < _submodel_New["submodelElements"].length; i++ )
    {
    	let _elem = linearData1[_submodel_New["submodelElements"][i]].serialize();
    	if (_elem["modelType"] == "SubmodelElementCollection"){
    		_submodel_New["submodelElements"][i] = getCollectionData(_submodel_New["submodelElements"][i]);
    	}
    	else {
    		_submodel_New["submodelElements"][i] = _elem;
    	}
    }
    _submodel_New["id"] = submodelIdentifier;
    var httpGetRequest = new XMLHttpRequest();
	httpGetRequest.open('PUT',"/submodels/"+btoa(submodelIdentifier));
	httpGetRequest.onload = () => {
		window.location.replace("/shells/"+aasIdentifier+"/aas/submodels/"+btoa(submodelIdentifier)+"/submodel/webui");
		
	}
	httpGetRequest.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
	httpGetRequest.send(JSON.stringify(_submodel_New));
}
function delete_element(event,submodelIdentifier,aasIdentifier){
	if (submodelIdentifier === event.target.alt){
		
		var httpGetRequest1 = new XMLHttpRequest();
		httpGetRequest1.open('DELETE',"/shells/"+aasIdentifier+"/aas/submodels/"+btoa(submodelIdentifier));
		httpGetRequest1.onload = () => {
			
		}
		httpGetRequest1.send();
		
		var httpGetRequest = new XMLHttpRequest();
		httpGetRequest.open('DELETE',"/submodels/"+btoa(submodelIdentifier));
		httpGetRequest.onload = () => {
			window.location.replace("/shells/"+aasIdentifier+"/webui");
		}
		httpGetRequest.send();
		
	}
	else{
		var httpGetRequest = new XMLHttpRequest();
		
		httpGetRequest.open('DELETE',"/shells/"+aasIdentifier+"/aas/submodels/"+btoa(submodelIdentifier)+"/submodel/submodel-elements/"+ event.target.alt);
		httpGetRequest.onload = () => {
			window.location.replace("/shells/"+aasIdentifier+"/aas/submodels/"+btoa(submodelIdentifier)+"/submodel/webui");
			
		}
		httpGetRequest.send();
	}
}