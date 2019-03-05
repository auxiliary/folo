// This file is required by the index.html file and will
// be executed in the renderer process for that window.
// All of the Node.js APIs are available in this process.

document.querySelector(".btn-run").addEventListener("click", function(){
    exec = require('child_process').exec;
    exec("python -m trace variable " + this.config_filename + " " + filename);
});
