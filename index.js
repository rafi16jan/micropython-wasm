var mp = require('./lib/micropython.js');
var browser = true;
if (typeof window === 'undefined' && typeof importScripts === 'undefined') {
  mp.onRuntimeInitialized();
  browser = false;
}
module.exports.init = global.mp_js_init;
module.exports.do_str = global.mp_js_do_str;
module.exports.init_repl = global.mp_js_init_repl;
module.exports.process_char = global.mp_js_process_char;
if (browser) {
  var stdout = document.createElement('div');
  stdout.id = 'mp_js_stdout';
  stdout.style.display = 'none';
  stdout.addEventListener('print', function (event) {
    console.log(event.data);
  }, false);
  document.body.append(stdout);
  var interval = setInterval(() => {
    if (global.mp_js_init) {
      module.exports.init = global.mp_js_init;
      module.exports.do_str = global.mp_js_do_str;
      module.exports.init_repl = global.mp_js_init_repl;
      module.exports.process_char = global.mp_js_process_char;
      clearInterval(interval);
    }
  }, 0);
}
