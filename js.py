import json
import js
dircache = {}
objcache = {}
funcache = {}
procache = {}

#Javascript's JSON Types for eliminating json.loads
true = True
false = False
null = None
undefined = None

def js_exec(code, *args):
    code = format(code, *args)
    return js.exec('(async () => {\n' + code + '\n})();')

def py_exec(code, *args):
    code = format(code, *args)
    return js.exec('(async () => {\nreturn await global.mp_js_do_str(`\n' + code + '\n`, true);\n})();')
exec = py_exec

def format(string, *args):
    for index, arg in enumerate(args):
        string = string.replace('{%s}' % (index), str(arg))
    return string

#def print(value):
#    js.exec("""console.log(`%s`)""" % (str(value)))

def wait(promise):
    procache[promise._name] = promise
    js_exec("""
      global.promiseWaitInterval = setInterval(() => {
        const object = global.mpjscache['{0}'];
        //console.log(object)
        if (object && object.constructor !== Promise) {
          clearInterval(global.promiseWaitInterval);
          global.promiseWaitInterval = undefined;
          global.mp_js_do_str(`
            import js
            procache['{0}']._resolved = True
            procache['{0}']._value = JS('global.mpjscache["{0}"]')
            procache['{0}'] = procache['{0}']._value
          `);
        }
      }, 500);
    """, promise._name)
    exit

def resolve(cache, name, value):
    object = cache.get(name)
    if type(object) == JSPromise:
       cache[name] = object.resolve(value)
    else:
       cache[name] = value

async_id = 0

def async_py(function):
    def wrap(**kwargs):
        code_string = function(**kwargs)
        for key in kwargs:
            if key not in code_string: continue
            async_id += 1
            asycache[async_id] = kwargs[key]
            code_string = code_string.replace(key, 'asycache[%s]' % (async_id))
        exec(code_string)
        exit
    return wrap

class JSPromise():

    def __init__(self, name):
        self._name = name
        self._resolved = False
        self._value = False

    def resolve(self, value):
        self._resolved = True
        self._value = value
        return value

class JSObject():

    def __init__(self, name):
        self._name = name

    def __len__(self):
        if self._name:
           return 1
        else:
           return 0

    def __dir__(self):
        if not self._name: return []
        js_exec("""
          let keys = JSON.stringify(Object.keys({0}));
          global.mp_js_do_str(`
            import js
            dircache['{0}'] = ${keys}
          `);
        """, self._name)
        return dircache.get(self._name, [])

    def __getattr__(self, key):
        name = self._name + '.' + key if self._name else key
        js_exec("""
          let object = {0};
          if (object && object.constructor === Promise) {
            await global.mp_js_do_str(`
              import js
              objcache['{0}'] = JSPromise('{0}')
            `)
            object = await object;
          }
          try {
            if (object && [Array, Object, Number, String, Boolean, Function, AsyncFunction].indexOf(object.constructor) < 0) throw Error('Not JSON Serializable');
            if (object && object.constructor === Object) for (let key in Object.keys(object)) {
              if (object.indexOf(key) < 0) throw Error('Not a JSON');
            }
            else if (object && (object.constructor === Function || object.constructor === AsyncFunction)) {
              delete global.mpjscache['{0}'];
              return global.mp_js_do_str(`
                import js
                resolve(objcache, '{0}', JSFunction('{0}'))
              `);
            }
            object = object !== undefined ? JSON.stringify(object) : 'null';
            return global.mp_js_do_str(`
              import js
              import json
              resolve(objcache, '{0}', ${object})
            `);
          }
          catch(error) {
            return global.mp_js_do_str(`
              import js
              resolve(objcache, '{0}', JSObject('{0}'))
            `);
          }
        """, name)
        return objcache.get(name)

    def __setattr__(self, key, value):
        if not self._name: return
        value = json.dumps(value)
        object_name = self._name + '.' + key
        js_exec("""
          {0} = {1};
        """.format(object_name, value))

def JSFunction(name):
    short_name = name.split('.')[-1]
    def function(*args):
        args = json.dumps(list(args))
        js_exec("""
          let object;
          if (global.mpjscache['{0}']) {
            object = global.mpjscache['{0}'](...{1});
          }
          else if ({0}) {
            object = {0}(...{1});
          }
          //object = object(...{1});
          global.mpjscache['{0}'] = object;
          if (object && object.constructor === Promise) {
            await global.mp_js_do_str(`
              import js
              funcache['{0}'] = JSPromise('{0}')
            `)
            object = await object;
          }
          global.mpjscache['{0}'] = object;
          try {
            if (object && [Array, Object, Number, String, Boolean, Function, AsyncFunction].indexOf(object.constructor) < 0) throw Error('Not JSON Serializable');
            if (object && object.constructor === Object) for (let key in Object.keys(object)) {
              if (object.indexOf(key) < 0) throw Error('Not a JSON');
            }
            else if (object && (object.constructor === Function || object.constructor === AsyncFunction)) {
              return global.mp_js_do_str(`
                import js
                resolve(funcache, '{0}', JSFunction('{0}'))
              `);
            }
            object = object !== undefined ? JSON.stringify(object) : 'null';
            return global.mp_js_do_str(`
              import js
              import json
              resolve(funcache, '{0}', ${object})
            `);
          }
          catch(error) {
            return global.mp_js_do_str(`
              import js
              resolve(funcache, '{0}', JSObject('global.mpjscache{2}'))
            `);
          }
        """, name, args, '.' + name if '.' not in name else '["%s"]' % (name))
        return funcache.get(name)
    return function

def JS(variable):
    empty = JSObject('')
    return getattr(empty, variable)

#require = JS('require')
#result = require('fs').readFileSync('./test.js').toString()
#print(result)

#This code block is adaptable to Javascript's event loop
async {

require = JS('require')
response = require('node-fetch')('https://github.com/')
response = await response
print(response)
result = response.text()
result = await result
print(result)

} async ()
