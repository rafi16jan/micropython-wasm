global.mpjscache = {};
let pyjs;
let browser = true;
let stdout_text = '';
let stdout_ready = false;
let stdout_print = (stdout) => {
  if (browser) stdout = stdout.data;
  if (!browser) stdout = stdout.toString();
  stdout_text += stdout;
  if (stdout_text.indexOf('mpjsendline') > -1) {
    stdout_text = stdout_text.replace('mpjsendline', '');
    stdout_ready = true;
    console.log(stdout_text);
  }  
}
global.mpjsPrintStdout = stdout_print;

const mp = require('./lib/micropython.js');
if (typeof window === 'undefined' && typeof importScripts === 'undefined') {
  browser = false;
  pyjs = require('fs').readFileSync('./js.py');
} else {
  pyjs = require('!raw-loader!./js.py');
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
  const stdout = document.createElement('div');
  stdout.id = 'mp_js_stdout';
  stdout.style.display = 'none';
  stdout.addEventListener('print', stdout_print, false);
  document.body.append(stdout);
}

global.AsyncFunction = (async () => {}).constructor;

module.exports = (async () => {
  await wait_exist(() => global.mp_js_init);
  const methods = {}
  methods.init = global.mp_js_init;
  const do_str = global.mp_js_do_str;
  methods.do_str = async (code, concurrent) => {
    const codes = code.split('\n');
    let spaces = '';
    for (let line of codes) {
      if (!line) continue;
      let index = 0;
      for (let word of line) {
        if (index === 0 && word !== ' ') break;
        if (word === ' ') spaces += ' ';
        index += 1;
      }
      break;
    }
    if (spaces || concurrent) {
      if (concurrent) spaces = ' ';
      let index_split = 0;
      const new_code = [];
      for (let line of codes) {
        line = line.slice(spaces.length - 1);
        new_code.push(line);
      }
      if (concurrent) {
        const result = [];
        for (var each of new_code) {
          let await_code;
          if (each.indexOf(' = wait(') > -1) {
            const [variable, wait] = each.split(' = ')
            const promise = wait.slice(5, -1);
            await_code = variable + ' = ' + promise + '._value';
          }
          result.push(await global.mp_js_do_str(each, false));
          if (await_code) await global.mp_js_do_str(await_code, false);
        }
        return result.join('\n');
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
    methods.init(stack);
    return await methods.do_str(pyjs);
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
