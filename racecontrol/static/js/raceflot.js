$(function() {
  var upperdata = [], lowerdata = [], textdata = [];
  var updateInterval = 150, totalPoints = 300;

  var upperSource = new Eventsource('/upper')
  var lowerSource = new Eventsource('/lower')
  var textSource = new Eventsource('/text')

  upperSource.onmessage = function(e) {
    if (upperdata.length > 0)
      upperdata = upperdata.slice(1);
    var dat = e.data.split(',')

    for (var i = 0; i < 3; i++) {
      upperdata.push([299, float(dat[i])]);
    }

    // e.data

  };

  function getRandomData() {
    if (data.length > 0)
      data = data.slice(1);

    // Do a random walk
    while (data.length < totalPoints) {
      var prev = data.length > 0 ? data[data.length - 1] : 50,
        y = prev + Math.random() * 10 - 5;

      if (y < 0) {
        y = 0;
      } else if (y > 100) {
        y = 100;
      }

      data.push(y);
    }

    // Zip the generated y values with the x values
    var res = [];
    for (var i = 0; i < data.length; ++i) {
      res.push([i, data[i]])
    }
    return res;
  }

  var upperplot = $.plot('#upperplot', [upperdata], {
    series: {
      shadowSize: 0	// Drawing is faster without shadows
    },
    yaxis: {
      min: 0,
      max: 100
    },
    xaxis: {
      show: false
    }
  });

  var lowerplot = $.plot('#lowerplot', [ getRandomData() ], {
    series: {
      shadowSize: 0	// Drawing is faster without shadows
    },
    yaxis: {
      min: 0,
      max: 100
    },
    xaxis: {
      show: false
    }
  });

  function update() {
    upperplot.setData([upperdata]);
    upperplot.draw();
    lowerplot.setData([getRandomData()]);
    lowerplot.draw();
    setTimeout(update, updateInterval);
  }

  update();

  // Add the Flot version string to the footer
  $("#footer").append(" Flot " + $.plot.version + ".");
});
