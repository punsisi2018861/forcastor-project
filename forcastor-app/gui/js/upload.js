let {PythonShell} = require('python-shell')
var path = require("path")

function testfunc(){
    swal("hello");
}

document.getElementById('formFile').addEventListener('change', function() {
    console.log('path to file>>> '+this.files[0].path);
    if ( /\.(xlsx|png|gif)$/i.test(this.files[0].name) === false ) {
      Swal.fire({
        icon: 'error',
        title: 'file format error',
        text: 'Upload Microsoft xlsx format!',
        })
      }  
      else{var filePath = this.files[0].path;
  
        localStorage.setItem("filePath", this.files[0].path);
        window.location = 'rfm.html';
      }

});