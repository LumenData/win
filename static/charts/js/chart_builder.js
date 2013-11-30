
// Document Ready
$(document).ready(function(){
	console.log("Document Loaded");
	
	$(".connectedSortable").sortable({
		connectWith: ".connectedSortable",
		scroll : false,
// 		helper: 'clone',
// 		start: function (e, ui) { 
// 			ui.item.show();
// 		},

	}).disableSelection();

	//////////////// Set up Sortables ////////////////

	$(".connectedSortable").on( "sortreceive", function( event, ui ) {
		// Any time a pill is dragged to a new location, update chart
		// Unless the pill was dragged from filters in which case delete the element
		
		console.debug(ui);
		if($(ui.sender).attr('id') == "report-filters")
			$(ui.item).remove()
		if($(this).attr('id') != "report-filters")
			update_chart();
	});
	
	//////////////// Filter - Popover ////////////////
	
	$( "#report-filters" ).on( "sortreceive", function( event, ui ) {
		filter_item = $(ui.item).clone();
		$(ui.sender).prepend(filter_item);

		$.ajax({
		  	type: "GET",
		  	url: "/charts/autofilter",
		  	dataType: "html",
		  	async: false,
			data: {"dataframe_id": dataframe_id, "column_name": filter_item.attr('id')},
			success : function(data) {
				var popover_content = "<div class='popover_wrapper' data-parent_id='" + $(ui.item).attr("id") + "'>" + data + "</div>";

				$(ui.item).popover({
					placement: 'left',
					html : true,
					container: 'body',
					content: popover_content
				});
			}
		});	
		
		$(ui.item).popover('show');
	});
	
	$("#report-filters").on("sortstart", {distance: 10}, function( event, ui ) {
		// When something is dragged from filters, delete it
		$(ui.item).popover("hide");
		$(ui.item).toggle( "highlight", 300, complete = function(){
			$(ui.item).remove();
			update_chart();
		});
	});

	if(typeof(dataframe_id) == "undefined"){
		$('#myModal').modal()
	}
	
});

/////////////// Update Chart ///////////////

function update_chart(){

// 	$("#report-area").hide();
// 	$("#chart_loading").toggle('fade');
	
	
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
	
	var filter_clauses = new Array();
	$("#report-filters").children().each(function(){
		filter_clauses.push($(this).data('filter_clause')); 
	});
	
	console.debug(filter_clauses);
	

	// Collect input to chart builder input into dictionary
	// Should replace this hard coded url later with something from django
	chart_builder_input = {
		"chart_builder_url": "/charts/autochart",
		"dataframe_id": dataframe_id, 
		"row_names": row_names, 
		"column_names": col_names,
		"group_names": group_names,
		"size_names": size_names,
		"filter_clauses": filter_clauses
	};

	var request = $.ajax({
		url: chart_builder_input["chart_builder_url"],
		type: "GET",
		data: {"chart_builder_input": JSON.stringify(chart_builder_input)},
		dataType: "html"
	}).done(function(response) {
		// $("#chart_loading").hide();
		$("#report-area").html(response);
		// $("#report-area").show();

	});
}
