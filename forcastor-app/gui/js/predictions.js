let {PythonShell} = require('python-shell')
var path = require("path")
var newpath = require("path")

let $ = jQuery = require('jquery');

console.log('path >> '+localStorage.getItem("filePath"));

var filePath = localStorage.getItem("filePath");
  
var options = {
  scriptPath : path.join(__dirname, '/../engine/'),
  args : [filePath]
}

var modal = document.getElementById("loader");
var loaderMessege = document.getElementById("loadingMsg");
var downloadBtn = document.getElementById("downloadbtn");
modal.style.display = "block";

// let pyshell = new PythonShell('prediction.py', options);
let pyshell = new PythonShell('dayPrediction.py', options);



pyshell.on('message', function(message) {
  modal.style.display = "none";
  loaderMessege.style.display = "none";
  downloadBtn.style.display = "block";
  Swal.fire({
    title: 'Complete!',
    text: message,
    icon: 'success',
    confirmButtonText: 'View'
  })

  document.getElementById("content").innerHTML='<object type="text/html" data="datatable1.html" style="width: 600px; height: 300px"></object>';

})


function browseResult(e){
  var fileselector = document.getElementById("fileselector").files[0].path;
  console.log(fileselector);
  loaderMessege.style.display = "block";

  var options = {
    scriptPath : newpath.join(__dirname, '/../engine/'),
    args : [fileselector]
  }

  let newpyshell = new PythonShell('download.py', options);

  newpyshell.on('message', function(message) {
    loaderMessege.style.display = "none";
    Swal.fire({
      // title: 'Downloaded!',
      text: message,
      icon: 'success',
      confirmButtonText: 'Done'
    })
  
  })


}
