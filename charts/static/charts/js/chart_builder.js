
// Document Ready
$(document).ready(function(){
	console.log("Document Loaded");

	$(".connectedSortable").on( "sortreceive", function( event, ui ) {
		// Get rownames from row sortable area 		
		var row_names = new Array();
		$("#report-rows").children().each(function(){
			row_names.push($(this).attr('id')); 
		});

		// Get column names from row sortable area 		
		var col_names = new Array();
		$("#report-columns").children().each(function(){
			col_names.push($(this).attr('id')); 
		});
		
		// Get group name from sortable area
		var group_names = new Array();
		$("#report-group").children().each(function(){
			group_names.push($(this).attr('id')); 
		});
		
		// Get group name from sortable area
		var size_names = new Array();
		$("#report-size").children().each(function(){
			size_names.push($(this).attr('id')); 
		});

		// Collect input to chart builder input into dictionary
		// Should replace this hard coded url later with something from django
		chart_builder_input = {
			"chart_builder_url": "/charts/autochart",
			"dataframe_id": dataframe_id, 
			"row_names": row_names, 
			"column_names": col_names,
			"group_names": group_names,
			"size_names": size_names
		};

		console.debug(chart_builder_input);

		$("#chart_loading_bar").show();
		updateChart(chart_builder_input);
		$("#chart_loading_bar").hide();
	});

	if(typeof(dataframe_id) == "undefined"){
		$('#myModal').modal()
	}
});

function updateChart(chart_builder_input){

	var request = $.ajax({
		url: chart_builder_input["chart_builder_url"],
		type: "GET",
		data: {"chart_builder_input": JSON.stringify(chart_builder_input)},
		dataType: "html"
	}).done(function(response) {
		$( "#report-area" ).html(response);
	});
}

$(function() {
	$(".connectedSortable").sortable({
		connectWith: ".connectedSortable",
		scroll : false,
	}).disableSelection();
});


