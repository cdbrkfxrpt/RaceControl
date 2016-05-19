// RaceControl, a bidirectional CAN bus telemetry platform.
// Copyright (C) 2016 Florian Eich
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//    http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

$(function() {
  // Create the arrays for the plot data
  var upperdata = [], lowerdata = [];
  // Define the update timeout (milliseconds) and the number of data points
  var updateInterval = 300, totalPoints = 300;

  // These arrays will hold the raw data sent through the EventSource
  var umin = [], umax = [], uavg = [];
  var lmin = [], lmax = [], lavg = [];

  // Loop through the raw data arrays to instantiate them fully and create a
  // base graph for the user (which I think looks nicer than a blank plot).
  for (var i = 0; i < totalPoints; i++) {
    umin.push([i, 50]);
    umax.push([i, 50]);
    uavg.push([i, 50]);
    lmin.push([i, 50]);
    lmax.push([i, 50]);
    lavg.push([i, 50]);
  }

  // Create the EventSource that will handle the server connection
  var subscribe = new EventSource('/subscribe');

  // Function to execute when receiving a server message
  subscribe.onmessage = function(e) {

    // Split CSV joined values
    var vals = e.data.split(',');

    // Distribute them into variables corresponding to the plot they belong to
    var upper = vals.slice(0, 3);
    var lower = vals.slice(3, 6);
    var text  = vals.slice(6, 9);

    // Remove the first element from the raw data arrays by slicing them
    umin = umin.slice(1);
    umax = umax.slice(1);
    uavg = uavg.slice(1);

    lmin = lmin.slice(1);
    lmax = lmax.slice(1);
    lavg = lavg.slice(1);

    // Push the received value to the raw data
    umin.push([0, parseFloat(upper[0])]);
    umax.push([0, parseFloat(upper[1])]);
    uavg.push([0, parseFloat(upper[2])]);

    lmin.push([0, parseFloat(lower[0])]);
    lmax.push([0, parseFloat(lower[1])]);
    lavg.push([0, parseFloat(lower[2])]);

    // Re-index the elements of the raw data to the correct x values
    for (var i = 0; i < totalPoints; i++) {
      umin[i][0] = i;
      umax[i][0] = i;
      uavg[i][0] = i;

      lmin[i][0] = i;
      lmax[i][0] = i;
      lavg[i][0] = i;
    }

    // Empty the plot data arrays, then fill them with the raw data
    upperdata.length = 0;
    upperdata = [
          {label: "HV MAX", data: umax},
          {label: "HV AVG", data: uavg},
          {label: "HV MIN", data: umin}
    ];

    lowerdata.length = 0;
    lowerdata= [
          {label: "PT MAX", data: lmax},
          {label: "PT AVG", data: lavg},
          {label: "PT MIN", data: lmin}
    ];

    // Push the text field values to the HTML document. Limit the string length
    // to 6 so the numbers don't grow out of the field by slicing the strings
    document.getElementById('text1').innerHTML =
      "<h3>Ride Height Front: " + text[0].slice(0, 6) + "</h3>";
    document.getElementById('text2').innerHTML =
      "<h3>Ride Height Rear: " + text[1].slice(0, 6) + "</h3>";
    document.getElementById('text3').innerHTML =
      "<h3>Mean Tire Pressure: " + text[2].slice(0, 6) + "</h3>";
  };

  // Set the options for the plots
  var upperoptions = {
    series: {
      shadowSize: 0	// Drawing is faster without shadows
    },
    // minmax values are required or the plot won't scale in the
    // current Twitter Bootstrap simple theme
    yaxis: {
      min: 10,
      max: 65,
      show: true
    },
    // minmax values are required or the plot won't scale in the
    // current Twitter Bootstrap simple theme
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
    // minmax values are required or the plot won't scale in the
    // current Twitter Bootstrap simple theme
    yaxis: {
      min: 340,
      max: 580,
      show: true
    },
    // minmax values are required or the plot won't scale in the
    // current Twitter Bootstrap simple theme
    xaxis: {
      min: 0,
      max: totalPoints,
      show: false
    }
  };

  // Draw the plots
  var upperplot = $.plot($('#upperplot'), upperdata, upperoptions);
  var lowerplot = $.plot($('#lowerplot'), lowerdata, loweroptions);

  // Set the self-updating function with setTimeout
  function update() {
    upperplot.setData(upperdata);
    upperplot.draw();
    lowerplot.setData(lowerdata);
    lowerplot.draw();
    setTimeout(update, updateInterval);
  }

  // Execute the updating function
  update();

  // Add the Flot version string to the footer
  $("#footer").append(" Flot " + $.plot.version + ".");
});
