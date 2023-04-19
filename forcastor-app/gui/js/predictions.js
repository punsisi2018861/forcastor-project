let {PythonShell} = require('python-shell')
var path = require("path")

let $ = jQuery = require('jquery');

console.log('path >> '+localStorage.getItem("filePath"));

var filePath = localStorage.getItem("filePath");
  
var options = {
  scriptPath : path.join(__dirname, '/../engine/'),
  args : [filePath]
}

var modal = document.getElementById("loader");
var loaderMessege = document.getElementById("loadingMsg");
modal.style.display = "block";

// let pyshell = new PythonShell('prediction.py', options);
let pyshell = new PythonShell('dayPrediction.py', options);



pyshell.on('message', function(message) {
  modal.style.display = "none";
  loaderMessege.style.display = "none";
  Swal.fire({
    title: 'Complete!',
    text: message,
    icon: 'info',
    confirmButtonText: 'View'
  })

  document.getElementById("content").innerHTML='<object type="text/html" data="datatable1.html" style="width: 600px; height: 300px"></object>';

})
