function addSubmodeltoForm(exdomain){
	submodel_form = document.getElementById("submodel-form");
	submodel_form.innerHTML = '';
	_submodel = new Submodel();
    _submodel.createDom("submodel-form",exdomain);	
}
function createNewSubmodel1(event,element_form_id,aasIdentifier){
	event.stopPropagation();
    event.preventDefault();
    $("#new_submodel_modal").modal('hide');

	var httpGetRequest = new XMLHttpRequest();
	const FD = new FormData();
	let _key = new Key("Submodel","");
	let _listObject = new ListObject("temp",_key,"")
	_ref = new Reference("GlobalReference");
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
