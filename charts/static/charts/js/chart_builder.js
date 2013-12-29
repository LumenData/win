
// Document Ready
$(document).ready(function(){
	console.log("Document Loaded");
	
	//////////////// Set up Sortables ////////////////
	
	// Initialize: Sortable areas
	$(".connectedSortable").sortable({
		connectWith: ".connectedSortable",
		scroll : false,
		// 	helper: 'clone',
		// 	start: function (e, ui) { 
		// 		ui.item.show();
		// 	},

	}).disableSelection();
	
	// Event: Any time a pill is dragged to a new location
	$(".connectedSortable").on( "sortreceive", function( event, ui ) {
		
		// If it came from filters or predictions dropzones, delete it
		if(($(ui.sender).attr('id') == "report-filters") || ($(ui.sender).attr('id') == "report-predictions")){
			if($(ui.item).hasClass("clone")){
				$(ui.item).remove();
			}
		}

		// If it is dropped into anything except filters or predictions, update the chart
		sortable_area_id = $(this).attr('id');
		if(sortable_area_id != "report-filters")
			if(sortable_area_id == "report-predictions"){
				if($("#report-predictions").children(".clone").size() > 0)
					update_chart();
			}
			else
				update_chart();
	});
	
	//////////////// Predictions ////////////////
	
	// Event: When pill is dropped into Predictions dropzone
	$("#report-predictions").on("sortreceive", function(event, ui){
		if($("#report-predictions").children(".clone").size() == 0){
			// Clone the pill and send the clone back to where the original came from
			$(ui.sender).prepend( $(ui.item).clone() );
		
			// Change the style to show emphasis
			$(ui.item).removeClass("btn-default");
			$(ui.item).addClass("btn-danger");
			$(ui.item).addClass("clone");

			// Change the icon to a target
			$(ui.item).children("i").removeClass().html("");
			$(ui.item).children("i").addClass("glyphicon glyphicon-screenshot");

			// Call the function that will load and show the popover
			show_prediction_popover(event, ui);

			// Create a 'training_percent' data attribute
			$(ui.item).attr("data-training_nrow", null);
		}
	});

	// Function: Start prediction popover
	function show_prediction_popover( event, ui ) {
		$.ajax({
		  	type: "GET",
		  	url: "/charts/prediction_popover",
		  	dataType: "html",
		  	async: false,
			data: {
				"dataframe_id": dataframe_id, 
				"column_name": $(ui.item).attr('id')
			},
			success : function(data) {
				var popover_content = "<div class='popover_wrapper' data-parent_id='" + $(ui.item).attr("id") + "'>" + data + "</div>";

				$(ui.item).popover({
					placement: 'left',
					html : true,
					container: '#right_panel',
					content: popover_content
				});
			}
		});
		
		$(ui.item).popover('show');
		
		var item_top_px = $("#report-predictions").offset().top;
		$(".popover").css("top", item_top_px - 90);
		$(".arrow").css("top", item_top_px + 15);

	}

	//////////////// Filter - Popover ////////////////
	
	// Event: When pill dropped into filter dropzone
	$( "#report-filters" ).on( "sortreceive", function(event, ui){
		// Clone the pill and send the clone back to where the original came from
		$(ui.sender).prepend( $(ui.item).clone() );

		// Create a 'filter-clause' data attribute
		$(ui.item).attr("data-filter_clause", null);
		$(ui.item).addClass("clone");

		// Replace icon with filter icon
		$(ui.item).children("i").removeClass().html("");
		$(ui.item).children("i").addClass("glyphicon glyphicon-filter");

		// Call the function that will load and show the popover
		show_filter_popover(event, ui);

		// Create an event to open the popover on click
		$(ui.item).on('click', function(){ 
			$(ui.item).removeAttr("data-filter_clause");			
			show_filter_popover(event, ui);
		});
	});

	// Function: Show Filter Popover
	function show_filter_popover( event, ui ) {
		$.ajax({
		  	type: "GET",
		  	url: "/charts/autofilter",
		  	dataType: "html",
		  	async: false,
			data: {"dataframe_id": dataframe_id, "column_name": $(ui.item).attr('id')},
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
	}

	// Event: When clone draged out of Predictions dropzone
	$("#report-filters, #report-predictions").on("sortstart", {distance: 10}, function( event, ui ) {
		// Hide and remove it, update the chart
		if($(ui.item).hasClass("clone")){
			$(ui.item).popover("hide");
			$(ui.item).toggle( "highlight", complete = function(){
				$(ui.item).remove();
				update_chart();
			});

			if($(this).attr("id") == "report-predictions"){
				$(".prediction_output").addClass("hidden");
				$("#report-predictions").append($(".prediction_output"));
				update_chart();
			}
		}
	});

	// Show modal if no DataFrame is selected
	if(typeof(dataframe_id) == "undefined"){
		$('#myModal').modal()
	}
	
	// Dev only //
	//var item = $("#area_category");
	//var sender = $("#column-list-dims");
	//$("#report-predictions").append(item);
	//$("#report-predictions").trigger("sortreceive", {'item':  item, 'sender': sender});


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

	// Collect input to chart builder input into dictionary
	// Should replace this hard coded url later with something from django
	chart_builder_input = {
		"dataframe_id": dataframe_id, 
		"row_names": row_names, 
		"column_names": col_names,
		"group_names": group_names,
		"size_names": size_names,
		"filter_clauses": filter_clauses
	};

	var request = $.ajax({
		url: "/charts/autochart",
		type: "GET",
		data: {"chart_builder_input": JSON.stringify(chart_builder_input)},
		dataType: "html"
	}).done(function(response) {
		// $("#chart_loading").hide();
		$("#report-area").html(response);
		// $("#report-area").show();

	});
}

/////////////// Update Predictions ///////////////

function update_predictions(){
	
	// Get rownames from row sortable area 		
	var target_name = $("#report-predictions").children(".clone").attr('id');
	var training_nrow = $("#report-predictions").children(".clone").data('training_nrow');
	var column_exclusions = $("#report-predictions").children(".clone").data('column_exclusions');

	// Collect input to chart builder input into dictionary
	// Should replace this hard coded url later with something from django
	prediction_builder_input = {
		"dataframe_id": dataframe_id, 
		"target_name": target_name, 
		"training_nrow": training_nrow,
		"column_exclusions": column_exclusions
	};

	var request = $.ajax({
		url: "/predictions",
		type: "GET",
		data: prediction_builder_input,
		dataType: "html"
	}).done(function(response) {
		console.debug(response);
		
		// Unhide other elements and move the target pill to the top of the list
		$(".prediction_output").removeClass("hidden");
		$("#report-predictions").children(".clone").prependTo("#report-predictions");
		
		if($("#report-predictions").children(".clone").data("type") == 'varchar'){
			$("#report-predictions").children("#prediction, #prediction_accurate").data("type", "varchar");			
			$("#report-predictions").children("#prediction, #prediction_accurate").children("i")
				.removeClass()
				.addClass("glyphicon glyphicon-font")
				.html("");	
		}
		else{
			$("#report-predictions").children("#prediction, #prediction_accurate").data("type", "int");
			$("#report-predictions").children("#prediction, #prediction_accurate").children("i")
				.removeClass()
				.addClass("hashicon")
				.html("#");
		}
	});
}

