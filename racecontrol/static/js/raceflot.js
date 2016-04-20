$(function() {
  var upperdata = [], lowerdata = [], textdata = [];
  var updateInterval = 300, totalPoints = 300;

  var umin = [], umax = [], uavg = [];
  var lmin = [], lmax = [], lavg = [];

  for (var i = 0; i < totalPoints; i++) {
    umin.push([i, 50]);
    umax.push([i, 50]);
    uavg.push([i, 50]);
    lmin.push([i, 50]);
    lmax.push([i, 50]);
    lavg.push([i, 50]);
  }

  var subscribe = new EventSource('/subscribe');

  subscribe.onmessage = function(e) {

    var vals = e.data.split(',');

    var upper = vals.slice(0, 3);
    var lower = vals.slice(3, 6);
    var text  = vals.slice(6, 9);

    umin = umin.slice(1);
    umax = umax.slice(1);
    uavg = uavg.slice(1);

    lmin = lmin.slice(1);
    lmax = lmax.slice(1);
    lavg = lavg.slice(1);

    umin.push([0, parseFloat(upper[0])]);
    umax.push([0, parseFloat(upper[1])]);
    uavg.push([0, parseFloat(upper[2])]);

    lmin.push([0, parseFloat(lower[0])]);
    lmax.push([0, parseFloat(lower[1])]);
    lavg.push([0, parseFloat(lower[2])]);

    for (var i = 0; i < totalPoints; i++) {
      umin[i][0] = i;
      umax[i][0] = i;
      uavg[i][0] = i;
      lmin[i][0] = i;
      lmax[i][0] = i;
      lavg[i][0] = i;
    }

    upperdata.length = 0;
    upperdata = [
          {label: "HV MIN", data: umin},
          {label: "HV MAX", data: umax},
          {label: "HV AVG", data: uavg}
    ];

    lowerdata.length = 0;
    lowerdata = [
          {label: "PT MIN", data: lmin},
          {label: "PT MAX", data: lmax},
          {label: "PT AVG", data: lavg}
    ];

    document.getElementById('text1').innerHTML =
      "<h3>Ride Height Front: " + text[0].slice(0, 6) + "</h3>";
    document.getElementById('text2').innerHTML =
      "<h3>Ride Height Rear: " + text[1].slice(0, 6) + "</h3>";
    document.getElementById('text3').innerHTML =
      "<h3>Mean Tire Pressure: " + text[2].slice(0, 6) + "</h3>";
  };

  var upperoptions = {
    series: {
      shadowSize: 0	// Drawing is faster without shadows
    },
    yaxis: {
      min: 0,
      max: 100,
      show: true
    },
    xaxis: {
      min: 0,
      max: totalPoints,
      show: false
    }
  };

  var loweroptions = {
    series: {
      shadowSize: 0	// Drawing is faster without shadows
    },
    yaxis: {
      min: 0,
      max: 100,
      show: true
    },
    xaxis: {
      min: 0,
      max: totalPoints,
      show: false
    }
  };

  var upperplot = $.plot($('#upperplot'), upperdata, upperoptions);
  var lowerplot = $.plot($('#lowerplot'), lowerdata, loweroptions);

  function update() {
    upperplot.setData(upperdata);
    upperplot.draw();
    lowerplot.setData(lowerdata);
    lowerplot.draw();
    setTimeout(update, updateInterval);
  }

  update();

  // Add the Flot version string to the footer
  $("#footer").append(" Flot " + $.plot.version + ".");
});
