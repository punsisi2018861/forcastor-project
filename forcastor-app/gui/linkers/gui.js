let {PythonShell} = require('python-shell')
var path = require("path")

function testfunc(){
    swal("hello");
}

document.getElementById('formFile').addEventListener('change', function() {
    console.log('path to file>>> '+this.files[0].path);

    var filePath = this.files[0].path;
  
    var options = {
      scriptPath : path.join(__dirname, '/../engine/'),
      args : [filePath]
    }
  
    let pyshell = new PythonShell('prediction.py', options);
  
  
    pyshell.on('message', function(message) {
      Swal.fire({
        title: 'Error!',
        text: message,
        icon: 'error',
        confirmButtonText: 'Cool'
      })
    })
    // document.getElementById('file-input').value = "";

});