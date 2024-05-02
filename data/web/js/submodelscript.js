
function createCollectionAccordins(collectionData)
{
	for (elem in collectionData["value"]){
		if (submodelELem['modelType'] != "SubmodelElementCollection"){
			createCollectionAccordins(submodelELem)
		}
		else{
			
		}		
	}
}
function createSubmodelAccordins(submodelData,submodelIdShort)
{
	submodelAccordin = document.getElementById("Accordin"+submodelIdShort);
	if (submodelData.hasOwnProperty("submodelElements")){
		for (submodelELem in submodelData['submodelElements']){
			if (submodelELem['modelType'] != "SubmodelElementCollection"){
				createCollectionAccordins(submodelELem)
			}
			else{
				
			}
		}
	}
}