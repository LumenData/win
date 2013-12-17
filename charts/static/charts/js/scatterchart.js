// Format expected is something like:
// chart_data = [{key: "Test Data", values: [{x: 1, y: 2}, {x: 4, y: 4}, {x: 5, y: 8}]}];
// chart_data size can be added at the level of 'x' and 'y'.  New colors are set by separate dictionaries with key and value elements of their own in the master list


var chart;
nv.addGraph(function() {
	chart = nv.models.scatterChart()
		.showDistX(true)
		.showDistY(true)
		.useVoronoi(true)
		.color(d3.scale.category10().range())
		.transitionDuration(300)
		;

	chart.xAxis.axisLabel(xaxis_label);
	chart.yAxis.axisLabel(yaxis_label);
	chart.showLegend(show_legend);

	chart.tooltipContent(function(key, x, y, e, graph) {
		console.debug(e);
		var tip = '<h3>' + key + '</h3>';
		if(size_label){
			tip += '<br><h3>' + size_label + ": " + e['point']['size'] + '</h3>';
		}
		return tip;
	});

	d3.select('#mainChart')
		.datum(chart_data)
		.call(chart);

	nv.utils.windowResize(chart.update);
	chart.dispatch.on('stateChange', function(e) { ('New State:', JSON.stringify(e)); });
	return chart;
});