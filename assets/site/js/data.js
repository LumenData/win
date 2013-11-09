// document.getElementById("uploadBtn").onchange = function () {
// 	document.getElementById("uploadFile").value = this.value;
// };

function toTitleCase(str) {
	return str.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
}

$(document).ready(function(){
	console.log("Document Loaded");

	$("#report-rows").on( "sortreceive", function( event, ui ) {
		elementName = event.toElement.id;
		console.debug(elementName);
	});
});


$(function() {
	$(".connectedSortable").sortable({
		connectWith: ".connectedSortable"
	}).disableSelection();
});


