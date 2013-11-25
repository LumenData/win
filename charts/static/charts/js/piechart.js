// Format expected is something like:
// [{'y': '3', 'key': 'Elizabeth'}, {'y': '4', 'key': 'Govind'}, {'y': '5', 'key': 'Heather'}]

var xaxis_label = chart_options["xaxis_label"];
var yaxis_label = chart_options["yaxis_label"];
var xaxis_type = chart_options["xaxis_type"];

nv.addGraph(function() {

	var chart = nv.models.pieChart()
        .x(function(d) { return d.key })
        .y(function(d) { return d.y })
        .color(d3.scale.category10().range());

		d3.select("#mainChart")
		.datum(chart_data)
		.transition().duration(1200)
		.call(chart);

	chart.dispatch.on('stateChange', function(e) { nv.log('New State:', JSON.stringify(e)); });

    return chart;
});
