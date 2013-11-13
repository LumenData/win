// document.getElementById("uploadBtn").onchange = function () {
// 	document.getElementById("uploadFile").value = this.value;
// };

function toTitleCase(str) {
	return str.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
}

$(document).ready(function(){
	console.log("Document Loaded");

	$(".connectedSortable").on( "sortreceive", function( event, ui ) {
		var row_names = new Array();
		$("#report-rows").children().each(function(){
			row_names.push($(this).attr('id')); 
		});

		var col_names = new Array();
		$("#report-columns").children().each(function(){
			col_names.push($(this).attr('id')); 
		});
		
		console.debug(row_names);
		console.debug(col_names);
		
		updateChart(row_names, col_names);
	});
});

function updateChart(row_names, column_names){
// 	var cols = JSON.stringify(col_names);

	var request = $.ajax({
		url: "/charts/autochart",
		type: "GET",
		data: {dataframe_id: window.dataframe_id, row_names: row_names, column_names: column_names},
		dataType: "html"
	}).done(function(response) {
		$( "#report-area" ).html(response);
	});
}

$(function() {
	$(".connectedSortable").sortable({
		connectWith: ".connectedSortable"
	}).disableSelection();
});


