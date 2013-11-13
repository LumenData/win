// Format expected is something like:
// [{key: "Test Data",values: [{x: 1, y: 2}, {x: 4, y: 4}, {x: 5, y: 8}]}];
// chartData = testdata2;

nv.addGraph(function() {
	var chart = nv.models.lineChart();

	chart.xAxis
		.axisLabel('Time (ms)')
		.tickFormat(d3.format(',r'));

	chart.yAxis
		.axisLabel('Voltage (v)')
		.tickFormat(d3.format('.02f'));

	d3.select('#mainChart')
		.datum(chartData)
		.transition().duration(500)
		.call(chart);

  nv.utils.windowResize(chart.update);

  return chart;
});