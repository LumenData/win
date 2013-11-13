// Format expected is something like:
// [{'y': '3', 'key': 'Elizabeth'}, {'y': '4', 'key': 'Govind'}, {'y': '5', 'key': 'Heather'}]

nv.addGraph(function() {
//     var width = 500,
//         height = 500;

    var chart = nv.models.pieChart()
        .x(function(d) { return d.key })
        .y(function(d) { return d.y })
        .color(d3.scale.category10().range())
//         .width(width)
//         .height(height)
        ;

      d3.select("#mainChart")
          .datum(chartData)
        .transition().duration(1200)
//           .attr('width', width)
//           .attr('height', height)
          .call(chart);

    chart.dispatch.on('stateChange', function(e) { nv.log('New State:', JSON.stringify(e)); });

    return chart;
});
