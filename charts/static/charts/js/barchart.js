// Format expected is something like:
// chart_data = [{key: "Test Data", values: [{label: 1, value: 2}, {label: 4, y: value}]}];

var xaxis_label = chart_options["xaxis_label"];
var yaxis_label = chart_options["yaxis_label"];
var xaxis_type = chart_options["xaxis_type"];

nv.addGraph(function() {
	var chart = nv.models.discreteBarChart()
		.x(function(d) { return d.label })
		.y(function(d) { return d.value })
		.staggerLabels(true)
		.tooltips(false)
		.showValues(true)
 
	d3.select('#mainChart')
		.datum(chart_data)
		.transition().duration(500)
		.call(chart);
 
	nv.utils.windowResize(chart.update);
 
	return chart;
});
 

