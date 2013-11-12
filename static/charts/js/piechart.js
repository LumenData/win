// 
//   var testdata = [
//     {
//       key: "One",
//       y: 5
//     },
//     {
//       key: "Two",
//       y: 2
//     },
//     {
//       key: "Three",
//       y: 9
//     },
//     {
//       key: "Four",
//       y: 7
//     },
//     {
//       key: "Five",
//       y: 4
//     },
//     {
//       key: "Six",
//       y: 3
//     },
//     {
//       key: "Seven",
//       y: .5
//     }
//   ];
// 
// var testdata = [{"y": "4", "key": "1965-05-02"}, {"y": "3", "key": "1980-11-20"}, {"y": "3", "key": "1990-01-01"}];
var testdata = chartData;

nv.addGraph(function() {
    var width = 500,
        height = 500;

    var chart = nv.models.pieChart()
        .x(function(d) { return d.key })
        .y(function(d) { return d.y })
        .color(d3.scale.category10().range())
        .width(width)
        .height(height);

      d3.select("#mainChart")
          .datum(testdata)
        .transition().duration(1200)
          .attr('width', width)
          .attr('height', height)
          .call(chart);

    chart.dispatch.on('stateChange', function(e) { nv.log('New State:', JSON.stringify(e)); });

    return chart;
});
