
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

		updateChart(chart_builder_input);
		
	});
	
	//////////////// Handle Filters ////////////////
	
	$( "#report-filters" ).on( "sortreceive", function( event, ui ) {
		filter_item = $(ui.item[0]).clone();
		$(ui.sender).append(filter_item);
		
		// var title = $(ui.item).attr('title') + " - Filter";
		// $(ui.item).attr('title',title);

		var popover_content;

		$.ajax({
		  type: "GET",
		  url: "/charts/autofilter",
		  dataType: "html",
		  async: false,
		  success : function(data) {
						popover_content = data;
					}
		});	

		$(ui.item[0]).popover({
			placement: 'left',
			html : true,
			container: 'body',
			content: popover_content
		});
		
		$(ui.item[0]).popover('show');

	});
	
	$( "#report-filters" ).on( "sortstart",{distance: 30}, function( event, ui ) {
		console.debug($(ui.item[0]));
		$(ui.item[0]).popover("hide");
		$(ui.item[0]).toggle( "highlight" );
	});

	if(typeof(dataframe_id) == "undefined"){
		$('#myModal').modal()
	}
	
});
	
function updateChart(chart_builder_input){

// 	$("#report-area").hide();
// 	$("#chart_loading").toggle('fade');
	
	console.debug("chart_builder_input");
	console.debug(chart_builder_input);

			
	var request = $.ajax({
		url: chart_builder_input["chart_builder_url"],
		type: "GET",
		data: {"chart_builder_input": JSON.stringify(chart_builder_input)},
		dataType: "html"
	}).done(function(response) {
// 		$("#chart_loading").hide();
		$("#report-area").html(response);
// 		$("#report-area").show();

	});
}


