// document.getElementById("uploadBtn").onchange = function () {
// 	document.getElementById("uploadFile").value = this.value;
// };

function toTitleCase(str) {
	return str.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
}

$(document).ready(function(){
	console.log("Document Loaded");

	$("#report-rows").on( "sortreceive", function( event, ui ) {
		window.rows_name = event.toElement.id;
		console.debug(window.rows_name);
		
		updateChart();
	});

	$("#report-columns").on( "sortreceive", function( event, ui ) {
		window.column_name = event.toElement.id;
		console.debug(window.column_name);
		
		updateChart();
	});
});

function updateChart(){
	var request = $.ajax({
		url: "/charts",
		type: "GET",
		data: {dataframe_id: window.dataframe_id, column_name: window.rows_name},
		dataType: "html"
	}).done(function(html) {
		$( "#report-area" ).html(html);
	});
}

$(function() {
	$(".connectedSortable").sortable({
		connectWith: ".connectedSortable"
	}).disableSelection();
});


