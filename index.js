global.mpjscache = {};
let pyjs;
const browser = (typeof window || typeof importScripts) !== 'undefined';
let stdout_text = '';
let stdout_ready = false;
let stdout_print = (stdout) => {
  if (browser) stdout = stdout.data;
  if (!browser) stdout = stdout.toString();
  stdout_text += stdout;
  if (stdout_text.indexOf('mpjsendline') > -1) {
    stdout_text = stdout_text.replace('mpjsendline', '');
    stdout_ready = true;
    //console.log(stdout_text);
  }
}
global.mpjsPrintStdout = stdout_print;
global.formatString = (object) => object !== undefined ? JSON.stringify(object) : null

const mp = require('./lib/micropython.js');
if (typeof webpackJsonp !== 'object') {
  pyjs = require('fs').readFileSync(__dirname + '/js.py').toString();
}
else {
  pyjs = require('!raw-loader!' + './js.py').default;
}

function wait_exist(fn) {
  return new Promise((resolve, reject) => {
    const clear = (id) => {
      clearInterval(id);
      resolve();
    }
    const interval = setInterval(() => {if (fn()) clear(interval)}, 0);
  });
}

if (browser) {
  window.global = window;
  const stdout = document.createElement('div');
  stdout.id = 'mp_js_stdout';
  stdout.style.display = 'none';
  stdout.addEventListener('print', stdout_print, false);
  document.body.append(stdout);
}

global.AsyncFunction = (async () => {}).constructor;

let initiated;
let pyjs_initiated;

module.exports = (async () => {
  await wait_exist(() => global.mp_js_init);
  const methods = {}
  const init = global.mp_js_init;
  methods.init = (stack) => !initiated && (initiated = !init(stack));
  const do_str = global.mp_js_do_str;
  global._mp_js_do_str = do_str;
  methods.do_str = async (code, module, initiated) => {
    const codes = code.split('\n');
    let spaces = '';
    for (let line of codes) {
      if (!line || !line.match(/[a-z]/i)) continue;
      let index = 0;
      for (let word of line) {
        if (index === 0 && word.match(/[a-z]/i)) break;
        if (word === ' ') spaces += ' ';
        index += 1;
      }
      break;
    }
    if (module) {
      if (!spaces) {
        code = code.replace(/^/gm, ' ');
        spaces = ' ';
      }
      code = 'def mpjs_module():\n' + code;
      code += '\n' + spaces + 'import sys';
      code += '\n' + spaces + `sys.modules['${module}'] = type('${module}', (), globals())()`;
      code += '\nmpjs_module()';
      if (!initiated) return code;
      spaces = '';
    }
    if (spaces) {
      let index_split = 0;
      const new_code = [];
      for (let line of codes) {
        line = line.slice(spaces.length - 1);
        new_code.push(line);
      }
      code = new_code.join('\n');
    }
    stdout_text = '';
    stdout_ready = false;
    code += "\nprint('mpjsendline')";
    if (global.promiseWaitInterval) await wait_exist(() => !global.promiseWaitInterval);
    do_str(code);
    await wait_exist(() => stdout_ready);
    return stdout_text;
  }
  methods.init_python = async (stack) => {
    if (pyjs_initiated) return;
    methods.init(stack);
    if (!pyjs_initiated) {
      await methods.do_str(`
        import json
        isbrowser = json.loads('${browser}')
      `);
      pyjs_initiated = true;
    }
    return await methods.do_str(pyjs);
  }
  methods.register_module = async (module, code) => {
    if (!pyjs_initiated) return pyjs += '\n' + await methods.do_str(code, module, false);
    return await methods.do_str(code, module, true);
  }
  global.mp_js_do_str = methods.do_str;
  methods.init_repl = global.mp_js_init_repl;
  methods.process_char = global.mp_js_process_char;
  return methods;
})().then((methods) => {
module.exports.init = methods.init;
module.exports.do_str = methods.do_str;
module.exports.init_python = methods.init_python;
module.exports.init_repl = methods.init_repl;
module.exports.process_char = methods.process_char;
return methods;
});

module.exports.init = mp._mp_js_init;
module.exports.do_str = mp._mp_js_do_str;
module.exports.init_repl = mp._mp_js_init_repl;
module.exports.process_char = mp._mp_js_process_char;
