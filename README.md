MicroPython.js
==============

MicroPython transmuted into Javascript (WASM) by Emscripten.

Official Repo https://github.com/micropython/micropython/tree/master/ports/javascript

Running with Node.js
--------------------

```javascript
var mp_js = require('micropython');

mp_js.init(64 * 1024);
mp_js.do_str("print('hello world')\n");
```

Running with Webpack
-----------------
TODO

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

Execute the input code. `code` must be a `string`.

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
