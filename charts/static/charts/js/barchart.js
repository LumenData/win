// Format expected is something like:
// chart_data = [{key: "Test Data", values: [{label: 1, value: 2}, {label: 4, y: value}]}];

var xaxis_label = chart_options["xaxis_label"];
var yaxis_label = chart_options["yaxis_label"];
var xaxis_type = chart_options["xaxis_type"];
var group_label = chart_options["group_label"];

console.debug("Chart_Data as it enters barchar.js", JSON.parse(JSON.stringify(chart_data)));

if(group_label.length == 0){
	// change 'x' and 'y' labels to 'label' and 'value' in JSON
	var chart_data = JSON.parse(JSON.stringify(chart_data), function(k, v) {
		if (k == "x") 
			this.label = v;
		else if (k == "y")
			this.value = v;
		else
			return v;
	});

	nv.addGraph(function() {
		var chart = nv.models.discreteBarChart()
			.x(function(d) { return d.label })
			.y(function(d) { return d.value })
			.staggerLabels(true)
			.tooltips(true)
			.showValues(false)

		// Add margin to make room for axis label
		chart.margin({left:75, bottom: 75}); 
		chart.xAxis.axisLabel(xaxis_label);
 		chart.yAxis.axisLabel(yaxis_label);
//		chart.showLegend(true);
		
		d3.select('#mainChart').datum(chart_data).transition().duration(500).call(chart);
		nv.utils.windowResize(chart.update);
		return chart;
	});
}
else{
	// Have to make up for the fact that NVD3 needs 0 y values instead of missing dicts
	// Create a list of unique x-axis values by looping through each value	
	var all_x_values = [];
	for(i in chart_data){
		for(j in chart_data[i].values){
			x_value = chart_data[i].values[j].x.valueOf();
			if(all_x_values.indexOf(x_value) == -1)
				all_x_values.push(x_value);
		}
	}

	// Build a list of missing values for each array, then fill them in 	
	for(i in chart_data){
		// Weird that we iterate on this, but otherwise we should clone it since simple assignment wont work
		var cross_off_list = [];
		all_x_values.forEach(function(v){
			cross_off_list.push(v);
		});

		for(j in chart_data[i].values){
			var x_value = chart_data[i].values[j].x.valueOf()
			x_value_index_in_cross_off_list = cross_off_list.indexOf( x_value )

			if(x_value_index_in_cross_off_list != -1)
				cross_off_list.splice( x_value_index_in_cross_off_list, 1 );
		}
		
		for(k in cross_off_list){
			if(xaxis_type == "date")
				x_value = new Date(cross_off_list[k])
			else
				x_value = cross_off_list[k]
			
			filler_dict = {'x': x_value, 'y': 0};

			chart_data[i].values.push( filler_dict );
		}
	}

	// We have to sort it now too for nvd3
	function compare_array_of_dicts(a,b) {
		if (a.x < b.x)
			return -1;
		else if (a.x > b.x)
			return 1;
		else
			return 0;
	}

	for(i in chart_data){
		chart_data[i].values.sort(compare_array_of_dicts);
	}
	// End the part where we fill in missing values and sort

	nv.addGraph(function() {
		var chart = nv.models.multiBarChart();
		chart.staggerLabels(true);
		//chart.stacked(true);
 		chart.showLegend(show_legend);

		d3.select('#mainChart').datum(chart_data).transition().duration(500).call(chart);
		nv.utils.windowResize(chart.update);
 
		return chart;
	});
}

