// Format expected is something like:
// chart_data = [{key: "Test Data", values: [{x: 1, y: 2}, {x: 4, y: 4}, {x: 5, y: 8}]}];

var xaxis_label = chart_options["xaxis_label"];
var yaxis_label = chart_options["yaxis_label"];
var xaxis_type = chart_options["xaxis_type"];

console.debug(chart_data)

nv.addGraph(function() {
	var chart = nv.models.lineChart();

	if(xaxis_type == "date"){
		chart.xAxis.axisLabel(xaxis_label).tickFormat(function (d) {
			return d3.time.format("%x")(new Date(d))
		});
	}
	else{
		chart.xAxis
			.axisLabel(xaxis_label)
			.tickFormat(d3.format(',r'));
	}

	// Add margin to make room for y axis label
	chart.margin({left:75});  
	
	chart.yAxis
		.axisLabel(yaxis_label)
		.showMaxMin(false)
		.tickFormat(d3.format(',02d'));
	
	d3.select('#mainChart')
		.datum(chart_data)
		.transition().duration(500)
		.call(chart);

  nv.utils.windowResize(chart.update);

  return chart;
});



