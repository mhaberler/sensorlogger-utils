$(document).ready(function () {
  const ctx = document.getElementById("myChart").getContext("2d");

  const myChart = new Chart(ctx, {
    type: "line",
    data: {
      datasets: [{ label: "Temperature", }],
    },
    options: {
      borderWidth: 3,
      borderColor: ['rgba(255, 99, 132, 1)',],
    },
  });

  function addData(label, data) {
    myChart.data.labels.push(label);
    myChart.data.datasets.forEach((dataset) => {
      dataset.data.push(data);
    });
    myChart.update();
  }

  function removeFirstData() {
    myChart.data.labels.splice(0, 1);
    myChart.data.datasets.forEach((dataset) => {
      dataset.data.shift();
    });
  }



  const MAX_DATA_COUNT = 100;
  //connect to the socket server.
  const url = "http://" + "127.0.0.1" + ":" + location.port;
  console.log(url);
  // var socket = io.connect(url);
  // var socket = io.connect("http://" + document.domain + ":" + location.port);
  var socket = io.connect();
  // var socket = io.connect( { forceNew: true });

  // client-side
  socket.on("connect", () => {
    console.log(socket.id); // x8WIv7-mJelg7on_ALbx
  });

  socket.on("connect_error", (err) => {
    console.log(`connect_error due to ${err.message}`);
  });
  socket.on('disconnect', function (reason) {
    console.log('User 1 disconnected because ' + reason);
  });
  //receive details from server
  socket.on("updateSensorData", function (msg) {
    console.log("Received sensorData :: " + msg.date + " :: " + msg.value);

    // Show only MAX_DATA_COUNT data
    if (myChart.data.labels.length > MAX_DATA_COUNT) {
      removeFirstData();
    }
    addData(msg.date, msg.value);
  });
  socket.on("updateLocation", function (msg) {
    console.log("Received location :: " + msg.date + " :: " + msg.value);

    // // Show only MAX_DATA_COUNT data
    // if (myChart.data.labels.length > MAX_DATA_COUNT) {
    //   removeFirstData();
    // }
    // addData(msg.date, msg.value);
  });
});
