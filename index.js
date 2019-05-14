var mp = require('./lib/micropython.js');
mp.onRuntimeInitialized();
module.exports.init = global.mp_js_init;
module.exports.do_str = global.mp_js_do_str;
module.exports.init_repl = global.mp_js_init_repl;
module.exports.process_char = global.mp_js_process_char;
