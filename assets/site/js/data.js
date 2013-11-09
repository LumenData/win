// document.getElementById("uploadBtn").onchange = function () {
// 	document.getElementById("uploadFile").value = this.value;
// };


$(function() {
	$("#sortable1, #sortable2").sortable({
		connectWith: ".connectedSortable"
	}).disableSelection();
});

function toTitleCase(str) {
	return str.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
}

$(function() {
	$( "#draggable" ).draggable();
});

