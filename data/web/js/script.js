function createProductionStepTags(skill_name,submodel_id,idShort,stepSequence){
	var canvasId = skill_name+'.'+submodel_id+'.'+idShort+'.'+stepSequence;
	var canvas = document.getElementById(canvasId);
	console.log(canvas.width);
	var context = canvas.getContext('2d');
	var centerX = canvas.width /8;
	var centerY = canvas.height / 2;
	var radius = canvas.height / 4;
  

	context.beginPath();
	context.arc(centerX-radius*2, centerY, radius, 0, 2 * Math.PI, false);
	context.fillStyle = '#0034d7E6';
	context.fill();
	context.lineWidth = 0;
	context.strokeStyle = '#003300';
	context.stroke();


	context.beginPath();
	context.fillStyle = "white";
	context.font = "1em Georgia bold";	  
	context.fillText(stepSequence, centerX-radius*2.2, centerY+radius*0.25);
	context.fill();	
	context.stroke();
	
}
function getLog_MainService(){
	var output = document.getElementById('logParagraph_MainService');
	var httpGetRequest = new XMLHttpRequest();
	httpGetRequest.open('POST','/log');
	httpGetRequest.onload = () => {
		const logData = (httpGetRequest.responseText)
		document.getElementById("logParagraph_MainService").innerHTML = logData.replace(/\\n/g, "<br>");
	}
	httpGetRequest.send();
}

function getLog(skillName,aasId){
	var httpGetRequest = new XMLHttpRequest();
	httpGetRequest.open('POST',"/shells/"+aasId+'/log/'+skillName+'/webui');
	httpGetRequest.onload = () => {
	const logData = JSON.parse((httpGetRequest.responseText).replace('\\u$1',/([0-9a-z]{4})/g));
	const logData1 = (logData.split("******"));
	let paragraphText = ""; 
	
	for (i = 0; i < logData1.length; i++) {
		let logText = (logData1[i]).toString();
		paragraphText =  paragraphText+ "<br/>" +logText  ; 
	}
	document.getElementById("logParagraph").innerHTML = paragraphText;
    }
	httpGetRequest.send()
}
function get_MessageData(messageID,conversationId,exDomain,aasIdentifier){
	var uri = encodeURI(messageID+"**"+conversationId);
	var output = document.getElementById('data_Content_modal');
	var httpGetRequest = new XMLHttpRequest();
	httpGetRequest.open('GET',"/"+aasIdentifier+"/search?searchQuery="+uri,true);
	document.getElementById("FrameTreeDiv").innerHTML = "";
	document.getElementById("data_Content_header").innerHTML = "";
	httpGetRequest.onload = () => {
		var data = (httpGetRequest.responseText);
		var data1 = data.replace(/\\n/g, "<br>");
		data = JSON.parse(data1);
		console.log(data);
		document.getElementById("data_Content_header").innerHTML = messageID;
		
		var downloadImg = document.createElement('img');
		downloadImg.setAttribute("alt","exportJSON");
		downloadImg.setAttribute("style","height: 2.5vh; width : 2.5vh;");
		downloadImg.setAttribute("src",exDomain+"web/images/download.svg");

		var downloadA = document.createElement('a');
		downloadA.setAttribute("id","exportJSON");
		downloadA.setAttribute("class","btn");
		downloadA.setAttribute("onclick","downloadI40JSON(data)");		
		downloadA.appendChild(downloadImg);
		var I40Data = "text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(data));
		// what to return in order to show download window?

		downloadA.setAttribute("href", "data:"+I40Data);
		downloadA.setAttribute("download", messageID+".json"); 
				
		var downloadCsvCol1 = document.createElement('div');
		downloadCsvCol1.setAttribute("class","col-8"); 

		downloadCsvCol1.appendChild( createResultFrameTree(data));

		var downloadCsvCol2 = document.createElement('div');
		downloadCsvCol2.setAttribute("class","col-4");		
		downloadCsvCol2.appendChild(downloadA);

		var treeROW = document.createElement('div');
		treeROW.setAttribute("class","row");
		treeROW.appendChild(downloadCsvCol1);
		treeROW.appendChild(downloadCsvCol2);
				

		document.getElementById("FrameTreeDiv").appendChild(treeROW);

		setResultFrameTreeListner()
	}
httpGetRequest.send();
}
function setResultFrameTreeListner()
{
 	$('.FrameTreeDivClass .listElement').click(function(){
 	    $('.highlight').removeClass('highlight');
 		$(this).addClass('highlight');

 	});

 	var toggler = document.getElementsByClassName("rbox");
 	var i;
	//
 	for (i = 0; i < toggler.length; i++) {
 	  toggler[i].addEventListener("click", function() {
 		  
 	    (this.parentElement.querySelector(".rNested").classList.toggle("active"));
 	    this.classList.toggle("rcheck-box");
 	  });
 	}
}

//Submodel Tree creation

function createSubmodelTree(submodel,data,exDomain,aasIndex)
{
 	var submodelUlNested = document.createElement('ul'); 
 	submodelUlNested.setAttribute("class","nested");
	var testURL = processEachSubmodelElement(data[submodel]['data'],submodel,submodelUlNested,exDomain,aasIndex);
	
	var submodelLI = document.createElement('li');
	submodelLI.appendChild(createSpanElement(submodel,"Submodel"));
	submodelLI.appendChild(testURL);
 	
	var submodelUL = document.createElement('ul'); 
	submodelUL.setAttribute("id","submodelTree");
	submodelUL.appendChild(submodelLI);
 	
 	var t = document.getElementById(submodel+"TreeDiv");
	t.appendChild(submodelUL);
}
function processEachSubmodelElement(connectstatusDict,submodel,submodelUL,exDomain,aasIndex)
{
	if ( typeof connectstatusDict === "object")
		{
			for (const [key, value] of Object.entries(connectstatusDict)) {
				
				if (value["type"] == "collection")
				{
						objectUl1 = document.createElement('ul');
						objectUl1.setAttribute("class","nested");
						returnli = processEachSubmodelElement(value["data"],submodel,objectUl1,exDomain,aasIndex);
						objectli = document.createElement('li');
						objectli.setAttribute("id",key);
						objectli.setAttribute("onclick","showCollectionData('"+aasIndex+"','"+submodel+"',"+JSON.stringify(value["qualifierList"]) +","+JSON.stringify(value["semanticIdList"])+",'"+key+"','"+exDomain+"','"+value["idShortPath"]+"','"+value["identificationId"]+"');event.stopPropagation()");
						objectli.append(createSpanElement(key,"collection"));
						objectli.append(returnli);
						submodelUL.append(objectli);
				}
				else if (value["type"] == "Property") {
					text = document.createElement('li');
					text.setAttribute("class","listElement");
					text.setAttribute("onclick","showPropertyData('"+aasIndex+"','"+submodel+"',"+JSON.stringify(value["qualifierList"]) +","+JSON.stringify(value["semanticIdList"]) +","+ JSON.stringify(value["data"])+",'"+key+"','"+exDomain+"','"+value["idShortPath"]+"','"+value["identificationId"]+"');event.stopPropagation()");
					text.appendChild(createAPropertySPAN(key,value,"Property"));
					submodelUL.append(text);
				}
				else if (value["type"] == "Range") {
					text = document.createElement('li');
					text.setAttribute("class","listElement");
					text.setAttribute("onclick","showRangeData('"+aasIndex+"','"+submodel+"',"+JSON.stringify(value["qualifierList"]) +","+JSON.stringify(value["semanticIdList"]) +","+ JSON.stringify(value["data"])+",'"+key+"','"+exDomain+"','"+value["idShortPath"]+"','"+value["identificationId"]+"');event.stopPropagation()");
					text.appendChild(createAPropertySPAN(key,value,"Range"));
					submodelUL.append(text);
				}
				else if (value["type"] == "MultiLanguageProperty") {
					text = document.createElement('li');
					text.setAttribute("class","listElement");
					text.setAttribute("onclick","showMLPData('"+aasIndex+"','"+submodel+"',"+JSON.stringify(value["qualifierList"]) +","+JSON.stringify(value["semanticIdList"]) +","+ JSON.stringify(value["data"])+",'"+key+"','"+exDomain+"','"+value["idShortPath"]+"','"+value["identificationId"]+"');event.stopPropagation()");
					text.appendChild(createAPropertySPAN(key,value,"MultiLanguageProperty"));
					submodelUL.append(text);
				}
				else if (value["type"] == "File") {
					text = document.createElement('li');
					text.setAttribute("class","listElement");
					text.setAttribute("onclick","showFileData('"+aasIndex+"','"+submodel+"',"+JSON.stringify(value["qualifierList"]) +","+JSON.stringify(value["semanticIdList"]) +","+ JSON.stringify(value["data"])+",'"+key+"','"+exDomain+"','"+value["idShortPath"]+"','"+value["identificationId"]+"');event.stopPropagation()");
					text.appendChild(createAPropertySPAN(key,value,"File"));
					submodelUL.append(text);
				}
				else if (value["type"] == "Blob") {
					text = document.createElement('li');
					text.setAttribute("class","listElement");
					text.setAttribute("onclick","showBlobData('"+aasIndex+"','"+submodel+"',"+JSON.stringify(value["qualifierList"]) +","+JSON.stringify(value["semanticIdList"]) +","+ JSON.stringify(value["data"])+",'"+key+"','"+exDomain+"','"+value["idShortPath"]+"','"+value["identificationId"]+"');event.stopPropagation()");
					text.appendChild(createAPropertySPAN(key,value,"Blob"));
					submodelUL.append(text);
				}
				else if (value["type"] == "ReferenceElement") {
					text = document.createElement('li');
					text.setAttribute("class","listElement");
					text.setAttribute("onclick","showRefElemData('"+aasIndex+"','"+submodel+"',"+JSON.stringify(value["qualifierList"]) +","+JSON.stringify(value["semanticIdList"]) +","+ JSON.stringify(value["data"])+",'"+key+"','"+exDomain+"','"+value["idShortPath"]+"','"+value["identificationId"]+"');event.stopPropagation()");
					text.appendChild(createAPropertySPAN(key,value,"ReferenceElement"));
					submodelUL.append(text);
				}
				else if (value["type"] == "AnnotatedRelationshipElement") {
					text = document.createElement('li');
					text.setAttribute("class","listElement");
					text.setAttribute("onclick","showAnRefElemData('"+aasIndex+"','"+submodel+"',"+JSON.stringify(value["qualifierList"]) +","+JSON.stringify(value["semanticIdList"]) +","+ JSON.stringify(value["data"])+",'"+key+"','"+exDomain+"','"+value["idShortPath"]+"','"+value["identificationId"]+"');event.stopPropagation()");
					text.appendChild(createAPropertySPAN(key,value,"AnnotatedRelationshipElement"));
					submodelUL.append(text);
				}
				else if (value["type"] == "RelationshipElement") {
					text = document.createElement('li');
					text.setAttribute("class","listElement");
					text.setAttribute("onclick","showRelationShipElemData('"+aasIndex+"','"+submodel+"',"+JSON.stringify(value["qualifierList"]) +","+JSON.stringify(value["semanticIdList"]) +","+ JSON.stringify(value["data"])+",'"+key+"','"+exDomain+"','"+value["idShortPath"]+"','"+value["identificationId"]+"');event.stopPropagation()");
					text.appendChild(createAPropertySPAN(key,value,"AnnotatedRelationshipElement"));
					submodelUL.append(text);
				}
				else if (value["type"] == "Capability") {
					text = document.createElement('li');
					text.setAttribute("class","listElement");
					text.setAttribute("onclick","showCapabilityData('"+aasIndex+"','"+submodel+"',"+JSON.stringify(value["qualifierList"]) +","+JSON.stringify(value["semanticIdList"]) +","+ JSON.stringify(value["data"])+",'"+key+"','"+exDomain+"','"+value["idShortPath"]+"','"+value["identificationId"]+"');event.stopPropagation()");
					text.appendChild(createAPropertySPAN(key,value,"Capability"));
					submodelUL.append(text);
				}
				else if (value["type"] == "Operation") {
					text = document.createElement('li');
					text.setAttribute("class","listElement");
					text.setAttribute("onclick","showOperationData('"+aasIndex+"','"+submodel+"',"+JSON.stringify(value["qualifierList"]) +","+JSON.stringify(value["semanticIdList"]) +","+ JSON.stringify(value["data"])+",'"+key+"','"+exDomain+"','"+value["idShortPath"]+"','"+value["identificationId"]+"');event.stopPropagation()");
					text.appendChild(createAPropertySPAN(key,value,"Operation"));
					submodelUL.append(text);
				}
				else if (value["type"] == "BasicEvent") {
					text = document.createElement('li');
					text.setAttribute("class","listElement");
					text.setAttribute("onclick","showbEventData('"+aasIndex+"','"+submodel+"',"+JSON.stringify(value["qualifierList"]) +","+JSON.stringify(value["semanticIdList"]) +","+ JSON.stringify(value["data"])+",'"+key+"','"+exDomain+"','"+value["idShortPath"]+"','"+value["identificationId"]+"');event.stopPropagation()");
					text.appendChild(createAPropertySPAN(key,value,"BasicEvent"));
					submodelUL.append(text);
				}
				else if (value["type"] == "Entity") {
					text = document.createElement('li');
					text.setAttribute("class","listElement");
					text.setAttribute("onclick","showEntityData('"+aasIndex+"','"+submodel+"',"+JSON.stringify(value["qualifierList"]) +","+JSON.stringify(value["semanticIdList"]) +","+ JSON.stringify(value["data"])+",'"+key+"','"+exDomain+"','"+value["idShortPath"]+"','"+value["identificationId"]+"');event.stopPropagation()");
					text.appendChild(createAPropertySPAN(key,value,"Entity"));
					submodelUL.append(text);
				}				
			}
		}

	else {
		
	}
	return submodelUL;
}
function createSpanElement(spanText,spanPrefix)
{
	span1 = document.createElement('span');
	span1.setAttribute("style","color:white;background-color:#6c8ebf;");
	span1.innerHTML = spanPrefix;
	
	span2 = document.createElement('span');
	span2.setAttribute("style","color:black");
	span2.innerHTML = "&nbsp;&nbsp;"+spanText;
	
	var textSpan3 = document.createElement('span');
	textSpan3.setAttribute("class","listElement");
	textSpan3.appendChild(span1);
	textSpan3.appendChild(span2);
	
 	var textSpan = document.createElement('span');
 	textSpan.setAttribute("class","box");
 	textSpan.appendChild(textSpan3);
 	
 	return textSpan;
}

function createAPropertySPAN(key,value,elemType)
{
	span1 = document.createElement('span');
	span1.setAttribute("style","color:white;background-color:#6c8ebf;");
	span1.innerHTML = elemType ;
	
	span2 = document.createElement('span');
	span2.setAttribute("style","color:black;");
	span2.innerHTML = '&nbsp &nbsp' +key;
	
	span3 = document.createElement('span');
	span3.appendChild(span1);
	span3.appendChild(span2);
	return span3;
}
function submodelElem(aasIndex,propertyName,submodelName,elemType,idShortPath,additionalInfo,submodelidentificationId)
{
	var formData = new FormData();
    formData.append("submodelName", submodelName);
	formData.append("submodelElemType", elemType);
	formData.append("submodelElemidShortPath", idShortPath);
	formData.append("submodelElemAdditionalInfo", additionalInfo);
	formData.append("submodelidentificationId", submodelidentificationId);
	formData.append("aasIndex", aasIndex);
	formData.append("newValue", document.getElementById("newValue_Text").value);
	
	 $('#propertyUpdate').modal('hide');
		var httpGetRequest = new XMLHttpRequest();
		httpGetRequest.open('PUT','/'+aasIndex+'/submodels/elem');
		httpGetRequest.onload = () => {
			const logData = (httpGetRequest.responseText)
		}
		httpGetRequest.send(formData);
		if (submodelName.toUpperCase() == "NAMEPLATE")
		{
		dataElemDiv = document.getElementById(additionalInfo+"."+propertyName);
		dataElemDiv.innerHTML = document.getElementById("newValue_Text").value;
		}
		else if (submodelName.toUpperCase() == "TECHNICALDATA")
		{
		dataElemDiv = document.getElementById(propertyName);
		dataElemDiv.innerHTML = document.getElementById("newValue_Text").value;
		}
		else if (submodelName.toUpperCase() == "IDENTIFICATION")
		{
		dataElemDiv = document.getElementById(propertyName);
		dataElemDiv.innerHTML = document.getElementById("newValue_Text").value;
		}
		else {
		if (elemType == "Range"){
			dataElemDiv = document.getElementById(idShortPath+"."+additionalInfo);
			dataElemDiv.innerHTML = document.getElementById("newValue_Text").value;
		}
		else{
			dataElemDiv = document.getElementById(idShortPath);
			dataElemDiv.innerHTML = document.getElementById("newValue_Text").value;
		}
	}
	
}
function modalSubmodelDataModifier(aasIndex,propertyName,submodelName,elemType,idShortPath,additionalInfo,identificationId)
{
	document.getElementById("submodelPropertyHeader").innerHTML = "Update " + propertyName;
	document.getElementById("submodelNameInnerText").value = submodelName;
	document.getElementById("submodelElemNameInnerText").value = propertyName;
	document.getElementById("submodelElemTypeInnerText").value = elemType;
	document.getElementById("submodelElemidShortPathText").value = idShortPath;
	document.getElementById("submodelElemAdditionalInfo").value = additionalInfo;
	document.getElementById("submodelidentificationId").value = identificationId;
	
	button = document.getElementById("submodelElemButton");
	button.setAttribute("onclick","submodelElem('"+aasIndex+"','"+propertyName+"','"+submodelName+"'"+",'"+elemType+"','"+idShortPath+"','"+additionalInfo+"','"+identificationId+"')");
}
function createImageInput(aasIndex,propertyName,submodelName,imageSrc,exDomain,elemType,idShortPath,additionalInfo,identificationId)
{
	imageInput = document.createElement("input");
	imageInput.setAttribute("type","image");
	imageInput.setAttribute("style","height: 3vh;width: 3vh");
	imageInput.setAttribute("onclick","modalSubmodelDataModifier('"+aasIndex+"','"+propertyName+"','"+submodelName+"'"+",'"+elemType+"','"+idShortPath+"','"+additionalInfo+"','"+identificationId+"')");
	imageInput.setAttribute("data-bs-toggle","modal");
	imageInput.setAttribute("data-bs-target","#propertyUpdate");
	imageInput.setAttribute("data-whatever","@mdo");
	imageInput.setAttribute("src",exDomain+"static/images/"+imageSrc+".svg");
	imageInput.setAttribute("name","submit");
	
	return imageInput;
}
function createEditButton(aasIndex,propertyName,submodelName,exDomain,elemType,idShortPath,additionalInfo,identificationId)
{
	inputImage = createImageInput(aasIndex,propertyName,submodelName,"edit",exDomain,elemType,idShortPath,additionalInfo,identificationId);
	inputAImage = createImageInput(aasIndex,propertyName,submodelName,"edit1",exDomain,elemType,idShortPath,additionalInfo,identificationId);
	
	var overlayDiv = document.createElement("div");
	overlayDiv.setAttribute("class","overlay");
	overlayDiv.appendChild(inputAImage);
	
	var imageCon = document.createElement("div");
	imageCon.setAttribute("class","imagecontainer");
	imageCon.appendChild(inputImage);
	imageCon.appendChild(overlayDiv);
	
	return imageCon;
}
function showData(value,key,submodel,elem) {
	var v = document.getElementById(submodel+"LeafValuep");
	v.innerHTML = value;
	var editButton = createEditButton(submodel,key);
	var submodelleafValueDiv = document.getElementById(submodel+"leafValueDiv");
	submodelleafValueDiv.innerHTML = '';
	submodelleafValueDiv.appendChild(editButton);	
}
//Search Result Tree creation
function getLisItem(key,value)
{
	var ListItem = document.createElement("li");
	ListItem.setAttribute("class","list-group-item");
	ListItem.setAttribute("id",key);
	ListItem.innerHTML = key + "&nbsp:&nbsp" + value;
	return ListItem;
}
function createQualifierpanel(submodel,qualDict){
	var quaList = document.createElement("ul");
	quaList.setAttribute("class","list-group list-group-flush");
	quaList.setAttribute("id",submodel+"QualList");
	for ([key, value] of Object.entries(qualDict)) {
		quaList.appendChild(getLisItem(key,value));
		}
	var qualListDiv = document.getElementById(submodel+"QualListDiv").appendChild(quaList);
}
function createSemanticIdpanel(submodel,semanticIdDict){
	var semanticList = document.createElement("ul");
	semanticList.setAttribute("class","list-group list-group-flush");
	semanticList.setAttribute("id",submodel+"semanticList");
	for ([key, value] of Object.entries(semanticIdDict)) {
		semanticList.appendChild(getLisItem(key,value));
		}
	document.getElementById(submodel+"SemanticListDiv").appendChild(semanticList);	
}
function setDataEmpty(submodel)
{
	document.getElementById(submodel+"SemanticListDiv").innerHTML = "";
	document.getElementById(submodel+"DatalListDiv").innerHTML = "";
	document.getElementById(submodel+"QualListDiv").innerHTML = "";
}

function showCapabilityData(aasIndex,submodel,qualDict,semanticIdDict,valueData,id,exDomain,idShortPat,identificationIdh) {
	setDataEmpty(submodel);
	createQualifierpanel(submodel,qualDict);
	createSemanticIdpanel(submodel,semanticIdDict);
}

function showFileData(aasIndex,submodel,qualDict,semanticIdDict,valueData,id,exDomain,idShortPath,identificationId) {
	setDataEmpty(submodel);
	filePath = valueData.split("/")
	createQualifierpanel(submodel,qualDict);
	createSemanticIdpanel(submodel,semanticIdDict);
	var documentDownload = document.createElement("a"); 
	var imagedocument = document.createElement("img");
	imagedocument.setAttribute("class","imagedocument");
	imagedocument.setAttribute("src",exDomain+"static/images/download.svg");
	documentDownload.setAttribute("href",valueData);
	documentDownload.appendChild(imagedocument);
	var fileList = document.createElement("ul");
	fileList.setAttribute("class","list-group list-group-flush");
	fileList.setAttribute("id",submodel+"valueList");
	fileList.appendChild(documentDownload);
	var DatalListDiv = document.getElementById(submodel+"DatalListDiv").appendChild(fileList);
}
function getBlobData(data,mimeType){
    const blob = new Blob([data], {type: mimeType});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    if (mimeType === "application/json")
    	{
    	a.download ="blobData.json";
    	}
    else{
    	a.download ="blobData.txt";
    }	
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
}

function showOperationData(aasIndex,submodel,qualDict,semanticIdDict,valueData,id,exDomain,idShortPath,identificationId) {
	setDataEmpty(submodel);
	createQualifierpanel(submodel,qualDict);
	createSemanticIdpanel(submodel,semanticIdDict);
	
	for (var i = 0; i < (valueData["inputVariable"]).length; i ++)
	{
		var inputVariableElem = document.createElement("ul");
		inputVariableElem.setAttribute("class","list-group list-group-flush");
		inputVariableElem.setAttribute("id",submodel+"valueList");
		inputVariableElem.appendChild(getLisItem("inputVariable : "+valueData["inputVariable"][i]["value"]["submodelElement"]["idShort"],valueData["inputVariable"][i]["value"]["submodelElement"]["value"]));
		document.getElementById(submodel+"DatalListDiv").appendChild(inputVariableElem);
	}

	for (var i = 0; i < (valueData["outputVariable"]).length; i ++)
	{
		var outputVariableElem = document.createElement("ul");
		outputVariableElem.setAttribute("class","list-group list-group-flush");
		outputVariableElem.setAttribute("id",submodel+"valueList");
		outputVariableElem.appendChild(getLisItem("outputVariable : "+valueData["outputVariable"][i]["value"]["submodelElement"]["idShort"],valueData["outputVariable"][i]["value"]["submodelElement"]["value"]));
		document.getElementById(submodel+"DatalListDiv").appendChild(outputVariableElem);
	}
	for (var i = 0; i < (valueData["inoutputVariable"]).length; i ++)
	{
		var inoutputVariableElem = document.createElement("ul");
		inoutputVariableElem.setAttribute("class","list-group list-group-flush");
		inoutputVariableElem.setAttribute("id",submodel+"valueList");
		inoutputVariableElem.appendChild(getLisItem("inoutputVariable : "+valueData["inoutputVariable"][i]["value"]["submodelElement"]["idShort"],valueData["inoutputVariable"][i]["value"]["submodelElement"]["value"]));
		document.getElementById(submodel+"DatalListDiv").appendChild(inoutputVariableElem);
	}
}

function showAnRefElemData(aasIndex,submodel,qualDict,semanticIdDict,valueData,id,exDomain,idShortPath,identificationId) {
	setDataEmpty(submodel);
	createQualifierpanel(submodel,qualDict);
	createSemanticIdpanel(submodel,semanticIdDict);
	
	for (var i = 0; i < (valueData["first"]["keys"]).length; i ++)
	{
		var anRefElement = document.createElement("ul");
		anRefElement.setAttribute("class","list-group list-group-flush");
		anRefElement.setAttribute("id",submodel+"valueList");
		anRefElement.appendChild(getLisItem("first : "+valueData["first"]["keys"][i]["type"],valueData["first"]["keys"][i]["value"]));
		document.getElementById(submodel+"DatalListDiv").appendChild(anRefElement);
	}

	for (var i = 0; i < (valueData["second"]["keys"]).length; i ++)
	{
		var anRefElement = document.createElement("ul");
		anRefElement.setAttribute("class","list-group list-group-flush");
		anRefElement.setAttribute("id",submodel+"valueList");
		anRefElement.appendChild(getLisItem("second : "+valueData["second"]["keys"][i]["type"],valueData["second"]["keys"][i]["value"]));
		document.getElementById(submodel+"DatalListDiv").appendChild(anRefElement);
	}
}
function getAnchoredLisItem(key,value)
{
	var ListItem = document.createElement("li");
	ListItem.setAttribute("class","list-group-item");
	ListItem.setAttribute("id",key);
	ListItem.innerHTML = key + "&nbsp:&nbsp" + '<a href="'+value+'" target="_blank" >LINK</a>';
	return ListItem;
}
function showRelationShipElemData(aasIndex,submodel,qualDict,semanticIdDict,valueData,id,exDomain,idShortPath,identificationId) {
	setDataEmpty(submodel);
	createQualifierpanel(submodel,qualDict);
	createSemanticIdpanel(submodel,semanticIdDict);
	
	for (var i = 0; i < (valueData["first"]["keys"]).length; i ++)
	{
		var anRefElement = document.createElement("ul");
		anRefElement.setAttribute("class","list-group list-group-flush");
		anRefElement.setAttribute("id",submodel+"valueList");
		anRefElement.appendChild(getLisItem("first : "+valueData["first"]["keys"][i]["type"],valueData["first"]["keys"][i]["value"]));
		document.getElementById(submodel+"DatalListDiv").appendChild(anRefElement);
	}

	for (var i = 0; i < (valueData["second"]["keys"]).length; i ++)
	{
		var anRefElement = document.createElement("ul");
		anRefElement.setAttribute("class","list-group list-group-flush");
		anRefElement.setAttribute("id",submodel+"valueList");
		if (valueData["second"]["keys"][i]["type"] === "GlobalReference"){

			anRefElement.appendChild(getAnchoredLisItem("second : "+valueData["second"]["keys"][i]["type"],valueData["second"]["keys"][i]["value"]));
		}
		document.getElementById(submodel+"DatalListDiv").appendChild(anRefElement);
	}
}
function showEntityData(aasIndex,submodel,qualDict,semanticIdDict,valueData,id,exDomain,idShortPath,identificationId) {
	setDataEmpty(submodel);
	createQualifierpanel(submodel,qualDict);
	createSemanticIdpanel(submodel,semanticIdDict);
	
	for (var i = 0; i < (valueData["keys"]).length; i ++)
	{
		var anRefElement = document.createElement("ul");
		anRefElement.setAttribute("class","list-group list-group-flush");
		anRefElement.setAttribute("id",submodel+"valueList");
		anRefElement.appendChild(getLisItem(valueData["keys"][i]["type"],valueData["keys"][i]["value"]));
		document.getElementById(submodel+"DatalListDiv").appendChild(anRefElement);
	}

}

function showRefElemData(aasIndex,submodel,qualDict,semanticIdDict,valueData,id,exDomain,idShortPath,identificationId) {
	setDataEmpty(submodel);
	createQualifierpanel(submodel,qualDict);
	createSemanticIdpanel(submodel,semanticIdDict);
	
	for (var i = 0; i < (valueData["value"]["keys"]).length; i ++)
	{
		var anRefElement = document.createElement("ul");
		anRefElement.setAttribute("class","list-group list-group-flush");
		anRefElement.setAttribute("id",submodel+"valueList");
		anRefElement.appendChild(getLisItem("first : "+valueData["value"]["keys"][i]["type"],valueData["value"]["keys"][i]["value"]));
		document.getElementById(submodel+"DatalListDiv").appendChild(anRefElement);
	}

}

function showBlobData(aasIndex,submodel,qualDict,semanticIdDict,valueData,mimeType,id,exDomain,idShortPath,identificationId) {
	setDataEmpty(submodel);
	
	createQualifierpanel(submodel,qualDict);
	createSemanticIdpanel(submodel,semanticIdDict);
	var documentDownload = document.createElement("a"); 
	documentDownload.setAttribute("href","javascript:void(0);");
	var imagedocument = document.createElement("img");
	imagedocument.setAttribute("class","imagedocument");
	imagedocument.setAttribute("src",exDomain+"static/images/download.svg");
	if (mimeType === "application/json")
    	{
			imagedocument.setAttribute("onClick","getBlobData("+JSON.stringify(valueData)+",'"+mimeType+"')");
    	}
    else{
    	imagedocument.setAttribute("onClick","getBlobData("+valueData+",'"+mimeType+"')");
    }
	documentDownload.appendChild(imagedocument);
	var blobList = document.createElement("ul");
	blobList.setAttribute("class","list-group list-group-flush");
	blobList.setAttribute("id",submodel+"valueList");
	blobList.appendChild(documentDownload);
	var DatalListDiv = document.getElementById(submodel+"DatalListDiv").appendChild(blobList);
	
}
function showPropertyData(aasIndex,submodel,qualDict,semanticIdDict,valueData,id,exDomain,idShortPath,identificationId) {
	setDataEmpty(submodel);
	createQualifierpanel(submodel,qualDict);
	createSemanticIdpanel(submodel,semanticIdDict);
	var valueInformationList = document.createElement("ul");
	valueInformationList.setAttribute("class","list-group list-group-flush");
	valueInformationList.setAttribute("id",submodel+"valueList");
	valueInformationList.appendChild(getPropertyItem(aasIndex,id,valueData,submodel,exDomain,idShortPath,identificationId));
	var DatalListDiv = document.getElementById(submodel+"DatalListDiv").appendChild(valueInformationList);
}
function showCollectionData(aasIndex,submodel,qualDict,semanticIdDict,valueData,id,exDomain,idShortPath) {																					  
	setDataEmpty(submodel);
	createQualifierpanel(submodel,qualDict);
	createSemanticIdpanel(submodel,semanticIdDict);
	var valueInformationList = document.createElement("ul");
	valueInformationList.setAttribute("class","list-group list-group-flush");
	valueInformationList.setAttribute("id",submodel+"valueList");
																														 
	var DatalListDiv = document.getElementById(submodel+"DatalListDiv").appendChild(valueInformationList);
}

function getPropertyItem(aasIndex,key,value,submodel,exDomain,idShortPath,identificationId){
	
	var rowDiv = document.createElement("div");
	rowDiv.setAttribute("class","row");
	
	var propertyColDiv = document.createElement("div");
	propertyColDiv.setAttribute("class","col-8");
	var propertyP = document.createElement("p");
	propertyP.innerHTML = value;
	propertyP.setAttribute("id",idShortPath);
	propertyColDiv.appendChild(propertyP);
	
	var imageColDiv = document.createElement("div");
	imageColDiv.setAttribute("class","col-4");
	imageColDiv.appendChild(createEditButton(aasIndex,key,submodel,exDomain,"Property",idShortPath," ",identificationId));
	
	rowDiv.appendChild(propertyColDiv);
	rowDiv.appendChild(imageColDiv);
	
	
	var ListItem = document.createElement("li");
	ListItem.setAttribute("class","list-group-item");
	ListItem.setAttribute("id",key);
	ListItem.appendChild(rowDiv);
	return ListItem;
}
function showRangeData(aasIndex,submodel,qualDict,semanticIdDict,valueData,id,exDomain,idShortPath) {
	setDataEmpty(submodel);
	createQualifierpanel(submodel,qualDict);
	createSemanticIdpanel(submodel,semanticIdDict);
	var minList = document.createElement("ul");
	minList.setAttribute("class","list-group list-group-flush");
	minList.setAttribute("id",submodel+"valueList");
	minList.appendChild(getRangeItem(aasIndex,id,valueData["min"],submodel,exDomain,idShortPath,"min",identificationId));
	document.getElementById(submodel+"DatalListDiv").appendChild(minList);
	
	
	var maxList = document.createElement("ul");
	maxList.setAttribute("class","list-group list-group-flush");
	maxList.setAttribute("id",submodel+"valueList");
	maxList.appendChild(getRangeItem(aasIndex,id,valueData["max"],submodel,exDomain,idShortPath,"max",identificationId));
	document.getElementById(submodel+"DatalListDiv").appendChild(maxList);
}
function getRangeItem(aasIndex,key,value,submodel,exDomain,idShortPath,rangeType,identificationId){
	
	var rowDiv = document.createElement("div");
	rowDiv.setAttribute("class","row");
	
	var rangeColDiv = document.createElement("div");
	rangeColDiv.setAttribute("class","col-8");
	var rangeP = document.createElement("p");
	rangeP.innerHTML = value;
	rangeP.setAttribute("id",idShortPath+"."+rangeType);
	rangeColDiv.appendChild(rangeP);
	
	
	var imageColDiv = document.createElement("div");
	imageColDiv.setAttribute("class","col-4");
	imageColDiv.appendChild(createEditButton(aasIndex,key,submodel,exDomain,"Range",idShortPath,rangeType,identificationId));
	
	rowDiv.appendChild(rangeColDiv);
	rowDiv.appendChild(imageColDiv);
	
	
	var ListItem = document.createElement("li");
	ListItem.setAttribute("class","list-group-item");
	ListItem.setAttribute("id",key);
	ListItem.appendChild(rowDiv);
	return ListItem;
}
function showMLPData(aasIndex,submodel,qualDict,semanticIdDict,valueData,id,exDomain,idShortPath,identificationId) {
	setDataEmpty(submodel);
	createQualifierpanel(submodel,qualDict);
	createSemanticIdpanel(submodel,semanticIdDict);
	for (var i = 0; i < (valueData["langString"]).length; i ++)
		{
			var langString = document.createElement("ul");
			langString.setAttribute("class","list-group list-group-flush");
			langString.setAttribute("id",submodel+"valueList");
			langString.appendChild(getLisItem(valueData["langString"][i]["language"],valueData["langString"][i]["text"]));
			document.getElementById(submodel+"DatalListDiv").appendChild(langString);
		}
	
}
function showAttributeData(aasIndex,submodel,qualDict,semanticIdDict,id){
	setDataEmpty(submodel);
	createQualifierpanel(submodel,qualDict);
	createSemanticIdpanel(submodel,semanticIdDict);
}

function processDirectionMessage(messages,conVId,exDomain,aasIndex)
{
	messagesList = []
	for ( var i = 0; i < messages.length; i ++)
	{
		var messageId = (messages[i]).split(":")[0];
		var entryTime = (messages[i]).split(":")[1] +":"+ (messages[i]).split(":")[2] +":"+ (messages[i]).split(":")[3];
		
		var spanALink1 = document.createElement("span");
		spanALink1.setAttribute("style","searchLink");
		spanALink1.innerHTML = messageId;
		
		var spanALink2 = document.createElement("span");
		spanALink2.setAttribute("style","color:lightgrey");
		spanALink2.innerHTML = "&nbsp;"+"( " + entryTime + " )";
		
		var aLink = document.createElement("a");	
		aLink.setAttribute("class","searchLink");
		aLink.setAttribute("href","#");
		aLink.setAttribute("style","text-decoration:none;color:black; cursor: pointer;");
		aLink.setAttribute("onclick","get_MessageData('"+ messageId+"','"+conVId+"','"+exDomain+"','"+aasIndex+"')");
		aLink.setAttribute("data-bs-toggle","modal");
		aLink.setAttribute("data-bs-target","#framedataBox");
		aLink.setAttribute("data-whatever","@mdo");
		aLink.appendChild(spanALink1);
		aLink.appendChild(spanALink2);
		
		var col = document.createElement("td");	
		col.appendChild(aLink);
		var row = document.createElement("tr");	
		row.appendChild(col);
		//
		messagesList.push(row)
	}
	return messagesList;
}
function createTable(messages,conVId,exDomain,aasIdentifier)
{
	var messagesList = processDirectionMessage(messages,conVId,exDomain,aasIdentifier);
	var tbody= document.createElement("tbody");
	for ( var i = 0; i < messagesList.length; i ++)
	{
		tbody.appendChild(messagesList[i]);
	}
	var htmlTable = document.createElement("table");
	htmlTable.setAttribute("class","table");
	htmlTable.setAttribute("style","text-align: center;");
	htmlTable.appendChild(tbody);
	return htmlTable;
}
function createSearResultTree(data,exDomain,aasIndex)
{	
	var resultList = data[Object.keys(data)[0]];
	var searchResultInbound = document.getElementById("searchResultInbound");
	searchResultInbound.appendChild(createTable(resultList["inbound"],String(Object.keys(data)[0]),exDomain,aasIndex));
	
	var searchResultInternal = document.getElementById("searchResultInternal");
	searchResultInternal.appendChild(createTable(resultList["internal"],String(Object.keys(data)[0]),exDomain,aasIndex));
	
	var searchResultOutbound = document.getElementById("searchResultOutbound");
	searchResultOutbound.appendChild(createTable(resultList["outbound"],String(Object.keys(data)[0]),exDomain,aasIndex));
}
// Result Frame Tree
function createResultFrameTree(data)
{
	var messageId = data["frame"]["messageId"];
	var conversationId = data["frame"]["conversationId"]
	var _type = data["frame"]["type"]
	var frameUlNested = document.createElement('ul'); 
 	frameUlNested.setAttribute("class","rNested");
	var testURL = processEachResultFrameElement(data,messageId,frameUlNested,_type);

	var frameLI = document.createElement('li');
	frameLI.appendChild(createResultFrameSpanElement(conversationId));
	frameLI.appendChild(testURL);
 	
	var frameUL = document.createElement('ul'); 
	frameUL.setAttribute("id","resultTree");
	frameUL.appendChild(frameLI);

 	return frameUL;
}
function processEachResultFrameElement(data,coversationId,frameUL,frameType)
{
	if ( typeof data === "object")
	{
		for (const [key, value] of Object.entries(data)) {
			if ( typeof value == "object")
				{
				if (key === "interactionElements") {
					
					if (frameType == "register")
						{
							text = document.createElement('li');			
							text.appendChild(createResultFramePropertySPAN(key,"Descriptor"))
							frameUL.append(text);
						}
					else{
						objectUl1 = document.createElement('ul');
						objectUl1.setAttribute("class","rNested");
						returnli = processEachResultFrameElement(value,coversationId,objectUl1);
						objectli = document.createElement('li');
						objectli.append(createResultFrameSpanElement(key));
						objectli.append(returnli);
						frameUL.append(objectli);
					}
				}
				else{
					objectUl1 = document.createElement('ul');
					objectUl1.setAttribute("class","rNested");
					returnli = processEachResultFrameElement(value,coversationId,objectUl1);
					objectli = document.createElement('li');
					objectli.append(createResultFrameSpanElement(key));
					objectli.append(returnli);
					frameUL.append(objectli);
				}
			}
					
			else {
				text = document.createElement('li');			
				text.appendChild(createResultFramePropertySPAN(key,value))
				frameUL.append(text);
			}
		}
	}
	else {
		
	}
	return frameUL;
}
function createResultFrameSpanElement(spanText)
{
	span1 = document.createElement('span');
	span1.setAttribute("style","color:white;background-color:#6c8ebf;");
	span1.innerHTML = "Coll";
	
	span2 = document.createElement('span');
	span2.setAttribute("style","color:black;background-color:white;");
	span2.innerHTML = "&nbsp;&nbsp;"+spanText;
	
	
 	var textSpan = document.createElement('span');
 	textSpan.setAttribute("class","rbox");
	textSpan.setAttribute("id","listElement");
 	textSpan.appendChild(span1);
	textSpan.appendChild(span2);
 	
 	return textSpan;
}

function createResultFramePropertySPAN(key,value)
{
	span1 = document.createElement('span');
	span1.setAttribute("style","color:white;background-color:#6c8ebf;");
	span1.innerHTML = "Prop"
	span2 = document.createElement('span');
	span2.setAttribute("style","color:black;");
	if (isNaN(key))
	{
		span2.innerHTML = "&nbsp;&nbsp;"+key+"&nbsp;&nbsp; :"+"&nbsp;&nbsp;"+value;
	}
	else {
		span2.innerHTML = "&nbsp;&nbsp;"+value;
	}
	
	span3 = document.createElement('span');
	span3.setAttribute("class","listElement");
	span3.appendChild(span1);
	span3.appendChild(span2);
	return span3;
}

function downloadI40JSON(i40Data) {

    
    var data = "text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(i40Data));
    el.setAttribute("href", "data:"+data);
    el.setAttribute("download", "data.json");    
}

function updateFileName(filePath){
	var documentDiv = document.getElementById("documentDownload");
	//var filename = (filePath).split("/");
	documentDiv.setAttribute("href","document"+filePath);
			
	var documentDiv1 = document.getElementById("DigitalFile");
	documentDiv1.innerHTML = filename[3];
}

function ShowDocumentSubdomain(subData,subList,languageDomain)
		{
			for (let i = 0; i < subList.length; i++) {
			var documentDiv = document.getElementById(subList[i]);
			var keyValue = subData[subList[i]];
			if (typeof keyValue === "undefined" || keyValue === null) {
				keyValue = "";
			}
			if (typeof keyValue === "object") {
				keyValue = keyValue[languageDomain];
			}
			
			documentDiv.innerHTML = keyValue;	
		}
		} 

function createDocumentDomainDiv(domainData,documentDomain,key,languageDomain,documentPartId){
	var DocumentPartDiv = document.createElement("div");
	DocumentPartDiv.setAttribute("class","row");
	DocumentPartDiv.setAttribute("id",documentPartId);
	
	var DocumentPartHeader = document.createElement("div");
	DocumentPartHeader.setAttribute("class","row");
	DocumentPartHeader.setAttribute("id",documentPartId+"Header");
	DocumentPartHeader.setAttribute("style","border-bottom-width:1px;border-bottom-color: black;border-bottom-style: solid;");
	DocumentPartHeader.innerHTML = key;
	DocumentPartDiv.appendChild(DocumentPartHeader);
	for (var domainELement of documentDomain)
	{
		var keyValue = domainData[domainELement];
		
		if (typeof keyValue === "undefined" || keyValue === null) {
			keyValue = "";
		}
		var documentRow = document.createElement("div");
		documentRow.setAttribute("class","row");
		documentRow.setAttribute("style","margin-top : 2.5vh;");
		
		var documentCol1 = document.createElement("div");
		documentCol1.setAttribute("class","col-6");	
		documentCol1.innerHTML = domainELement + ":";

		var documentCol2 = document.createElement("div");
		documentCol2.setAttribute("class","col-6");	
		documentCol2.innerHTML = "<p>"+keyValue+"</p>";
		
		documentRow.appendChild(documentCol1);
		documentRow.appendChild(documentCol2);
		DocumentPartDiv.appendChild(documentRow);
	}
	document.getElementById(documentPartId).appendChild(DocumentPartDiv);
}

function ShowDocumentPart(domainData,documentDomain,languageDomain,documentPartId){
    document.getElementById(documentPartId).innerHTML = "";	
	for (var key in domainData) {
		var DocumentSeperatorDiv = document.createElement("div");
		DocumentSeperatorDiv.setAttribute("class","row");
		DocumentSeperatorDiv.setAttribute("style","height : 2.5vh;");
		document.getElementById(documentPartId).appendChild(DocumentSeperatorDiv);
		createDocumentDomainDiv(domainData[key],documentDomain,key,languageDomain,documentPartId);
	}
}

function ShowDocumentData(childIndex,parentIndex,languageDomain)
{
	var _documentList = documentList[languageDomain]["data"]
	var childI = childIndex - 1;
	var parentI = parentIndex - 1;
	var documentData = _documentList[parentI][childI];	
	var DocumentDomain = ["DocumentDomainId","DocumentId","IsPrimary"];
	var DocumentClassification = ["ClassificationSystem","ClassId","ClassName"];
	var DocumentVersion = ["Language","DocumentVersionId","SetDate","StatusValue","OrganizationName","OrganizationOfficialName","Title","SubTitle","Summary"];
	ShowDocumentPart(documentData["DocumentIdDomain"],DocumentDomain,"languageDomain","DocumentIdDomains");
	var DocumentSeperatorDiv = document.createElement("div");
			DocumentSeperatorDiv.setAttribute("class","row");
			DocumentSeperatorDiv.setAttribute("style","height : 2.5vh;");
			document.getElementById("DocumentPart").appendChild(DocumentSeperatorDiv);
			
			ShowDocumentPart(documentData["DocumentClassification"],DocumentClassification,languageDomain,"DocumentClassification");

			
			ShowDocumentSubdomain(documentData["DocumentVersion"],DocumentVersion,languageDomain);
			updateFileName(documentData["DocumentVersion"]["DigitalFile01"]);
}
function getCoordinates( el ) {
    var rect = el.getBoundingClientRect();
    return {
        left: rect.left + window.pageXOffset,
        top: rect.top + window.pageYOffset,
        width: rect.width || el.offsetWidth,
        height: rect.height || el.offsetHeight
    };
}
function vh(v) {
	  var h = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);
	  return (v * h) / 100;
	}

function vw(v) {
	  var w = Math.max(document.documentElement.clientWidth, window.innerWidth || 0);
	  return (v * w) / 100;
	}

function xyCoordinatesInternal(div1C){
	div2 = document.getElementById('div-internal');
    var off2 = getCoordinates(div2);

    x2 = div1C.left + (div1C.width)/ 2;
    y2 = div1C.top +  div1C.height;

    x1 = off2.left + (off2.width) / 2;
    y1 = off2.top - vh(2);
    drawLine(x1,x2,y1,y2,"","lineInternal");
}	

function xyCoordinatesInBound(div1C){
	div2 = document.getElementById('div-inbound');
    var off2 = getCoordinates(div2);

    x2 = div1C.left;
    y2 = div1C.top +  div1C.height;

    x1 = off2.left + off2.width;
    y1 = off2.top - vh(2);
    drawLine(x1,x2,y1,y2," &#x3C;","lineInbound");
}	
function xyCoordinatesOutbound(div1C){
	div2 = document.getElementById('div-outbound');
    var off2 = getCoordinates(div2);

    x1 = div1C.left + (div1C.width);
    y1 = div1C.top +  div1C.height;

    x2 = off2.left;
    y2 = off2.top - vh(2);
    drawLine(x1,x2,y1,y2," &#x3C;","lineOutbound");
}	
function drawLine(x1,x2,y1,y2,lineData,divId) { 
	var color = "#0034D7";
	var thickness = 1;

    var length = Math.sqrt(((x2-x1) * (x2-x1)) + ((y2-y1) * (y2-y1)));

    var cx = ((x1 + x2) / 2) - (length / 2);
    var cy = ((y1 + y2) / 2) - (thickness / 2);

    var angle = Math.atan2((y1-y2),(x1-x2))*(180/Math.PI);

    var arrowLine = "<div id ='" +divId+"' style='padding:0px; margin:0px; font-size : 200%; height:" + thickness + "px; background-color:" + color + "; line-height:1px; position:absolute; left:" + cx + "px; top:" + cy + "px; width:" + length + "px; -moz-transform:rotate(" + angle + "deg); -webkit-transform:rotate(" + angle + "deg); -o-transform:rotate(" + angle + "deg); -ms-transform:rotate(" + angle + "deg); transform:rotate(" + angle + "deg);' >" +lineData+"</div>";

    document.body.innerHTML += arrowLine;
}

function loaded() {

	div1 = document.getElementById('svg-Div');
	 // Inbound
	divC = getCoordinates(div1)
	xyCoordinatesInBound(divC);
	// OutBound
	xyCoordinatesOutbound(divC);
	//Internal
	xyCoordinatesInternal(divC);
}

function searchQueryAAS() {
    var input, filter, ul, li, a, i, txtValue;
    input = document.getElementById("search-input");
    filter = input.value.toUpperCase();
    ul = document.getElementById("aas-list-ul");
    li = ul.getElementsByTagName("li");
    for (i = 0; i < li.length; i++) {
        a = li[i].getElementsByTagName("a")[0];
        txtValue = a.textContent || a.innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
            li[i].style.display = "";
        } else {
            li[i].style.display = "none";
        }
    }
}
function getCFP(conversationId){
	var httpGetRequest = new XMLHttpRequest();
	httpGetRequest.open('GET',"/"+conversationId+'/cfp');
	httpGetRequest.onload = () => {
		var resultList = JSON.parse(httpGetRequest.responseText);
		console.log(resultList,httpGetRequest.responseText);
		var cfp_conversationIdElem = document.getElementById("cfp_conversationId");
		cfp_conversationIdElem.innerHTML = "";
		var cfpList = resultList["cfpList"];
		for (let i = 0; i < cfpList.length; i++) {
			var _row = `<tr>
				<td style = "border: 1px solid #ddd;">`+cfpList[i][0]+`</td>
				<td style = "border: 1px solid #ddd;">`+cfpList[i][1]+`</td>
				<td style = "border: 1px solid #ddd;">`+cfpList[i][2]+`</td>
				<td style = "border: 1px solid #ddd;">`+cfpList[i][3]+`</td>
				<td style = "border: 1px solid #ddd;">`+cfpList[i][4]+`</td>
			</tr>`;
			cfp_conversationIdElem.insertAdjacentHTML(
					'afterbegin',
					_row
				);
		}
	}
	httpGetRequest.send();
}		


