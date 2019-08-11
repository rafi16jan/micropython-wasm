MicroPython.js
==============

MicroPython transmuted into Javascript (WASM) by Emscripten.

Official Repo https://github.com/micropython/micropython/tree/master/ports/javascript

Testing and Contribution Needed, feel free to make an issue or even better, a PR


What's New on 1.1
--------------------

- New Async/Await or Promise API
- New Python classes to expose JS API and Objects like DOM API, XHR, Node.JS require, and etc
- New Python promise class to wait promises with emscripten_sleep, using Emterpreter


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
  await mp_js.do_str("variable1.get('data1')"); //Access variables from the previous event loop
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
  const stdout = await mp_js.do_str("print('hello world')\n");
  console.log(stdout);
})();
```


Python API
---

The following functions and classes is used to interact with Javascript. Load this API with ```mp_js.init_python(stack_size)```

```python
JS(variable_name)
```
Check for variable on Javascript's global and return the corresponding types, functions and Javascript objects instantiate JSFunction and JSObject class. Promise instantiate JSPromise class.

```python
wait(promise)
```
Wait for a promise to be resolved on Javascript, and then returns the value. Uses emscripten_sleep. Also available as JSPromise class function:

```python
fetch = JS('require')('node-fetch')
response = fetch('https://github.com').wait() #Returns response object
html = response.text().wait() #Returns HTML string
```

Javascript API
---

The following functions have been exposed to Kavascript.

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

This function execute js.py to expose JS Objects to Python, Example:

```javascript
mp_js = require('micropython');

(async () => {
  await mp_js;
  await mp_js.init_python(64 * 1024);
  await mp_js.do_str(`

  import js

  fetch = False
  if isbrowser:
     fetch = JS('fetch')
  else:
     require = JS('require')
     fetch = require('node-fetch')
  response = fetch('https://github.com').wait()
  result = response.text().wait()
  print(result)
  
  `);
})();
```
