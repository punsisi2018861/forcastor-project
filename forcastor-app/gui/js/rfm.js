let {PythonShell} = require('python-shell')
var path = require("path")

console.log('path >> '+localStorage.getItem("filePath"));

var filePath = localStorage.getItem("filePath");
  
var options = {
  scriptPath : path.join(__dirname, '/../engine/'),
  args : [filePath]
}

let pyshell = new PythonShell('prediction.py', options);


pyshell.on('message', function(message) {
  Swal.fire({
    title: 'HEY!',
    text: message,
    icon: 'info',
    confirmButtonText: 'Cool'
  })
})
