MicroPython.js
==============

MicroPython transmuted into Javascript (WASM) by Emscripten.

Official Repo https://github.com/micropython/micropython/tree/master/ports/javascript

Testing and Contribution Needed, feel free to make an issue or even better, a PR


What's New on 1.1
--------------------

- New Async/Await or Promise API
- New Python classes to expose JS API and Objects like DOM API, XHR, Node.JS require, and etc


Running with Node.js
--------------------

On Node.JS console

```javascript
const mp_js = require('micropython');

mp_js.init(64 * 1024);
mp_js.do_str("print('hello world')\n");
```

On production/actual code use AsyncFunction or Promise to get the guaranteed result

```javascript
(async () => { //AsyncFunction
  const mp_js = await require('micropython');

  mp_js.init(64 * 1024);
  await mp_js.do_str("variable1 = {'data1': 1}");
  await mp_js.do_str("variable1.get('data1')"); //Access variables for previous event loop
})();
```

Running with Webpack
-----------------
Running MicroPython on Webpack is a little bit tricky. It expects the firmware.wasm file at /static/js/firmware.wasm. So a simple solution is to make static and js folder on webpack's public directory and put firmware.wasm on it. (PR is accepted for a better solution)

```
mkdir -p public/static/js
cp node_modules/micropython/lib/firmware.wasm public/static/js
```

And import it on your Javascript file

```javascript
import mp_js from 'micropython';

(async () => {
  await mp_js;
  mp_js.init(64 * 1024);
  mp_js.do_str("print('hello world')\n");
})();
```

API
---

The following functions have been exposed to javascript.

```
init(stack_size)
```

Initialize MicroPython with the given stack size in bytes. This must be
called before attempting to interact with MicroPython.

```
do_str(code)
```

Execute the input code. `code` must be a `string`. Returns a promise resulting an stdout.

```
init_repl()
```

Initialize MicroPython repl. Must be called before entering characters into
the repl.

```
process_char(char)
```

Input character into MicroPython repl. `char` must be of type `number`. This 
will execute MicroPython code when necessary.

```
init_python(stack_size)
```

NEW!! This function execute js.py to expose JS API to Python, even some helper function and experimental asynchronous queue/stack logic. Example:

```javascript
import mp_js from 'micropython';

(async () => {
  await mp_js;
  await mp_js.init_python(64 * 1024);
  await mp_js.do_str(`
  #This function executes every line one by one and await promise if it returns a promise
  exec("""
  
  require = JS('require')
  fetch = require('node-fetch') #Or do JS('window.fetch') on browser
  response = fetch('https://github.com')
  response = wait(response) #This is the 'await' equivalent
  result = response.text()
  result = wait(result)
  print(result) #Print the resulting HTML
  
  """)
  `);
})();
```
