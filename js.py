import json
import js

def js_exec(code, *args):
    code = format(code, *args)
    result = js.exec('formatString((() => {\n' + code + '\n})());')
    return json.loads(result)

def js_print(value):
    js.exec('console.log(%s)' % (json.dumps(str(value))))

py_print = print
print = js_print

def format(string, *args):
    for index, arg in enumerate(args):
        string = string.replace('{%s}' % (index), str(arg))
    return string

def wait(promise):
    while not promise._resolved:
        js.sleep(250)
        result = js_exec('''
          const object = {0};
          if (object && object.constructor !== Promise) return true;
        ''', promise._name)
        if result: promise.resolve(JS(promise._name))
    return promise._value

class JSPromise():

    def __init__(self, name):
        self._name = name
        self._resolved = False
        self._value = False

    def resolve(self, value):
        self._resolved = True
        self._value = value
        return value

    def wait(self):
        return wait(self)

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
        return js_exec('''
          return Object.keys({0}));
        ''', self._name)

    def __getattr__(self, key):
        name = self._name + '.' + key if self._name else key
        result = js_exec('''
          let object = {0};
          if (object && object.constructor === Promise) {
            object.then((object) => global.mpjscache['{0}'] = object);
            return 'mpjspromiseobject:{0}';
          }
          try {
            if (object && [Array, Object, Number, String, Boolean, Function, AsyncFunction].indexOf(object.constructor) < 0) throw Error('Not JSON Serializable');
            if (object && object.constructor === Object) for (let key in Object.keys(object)) {
              if (object.indexOf(key) < 0) throw Error('Not a JSON');
            }
            else if (object && (object.constructor === Function || object.constructor === AsyncFunction)) {
              delete global.mpjscache['{0}'];
              return 'mpjsfunctionobject:{0}';
            }
            return object;
          }
          catch(error) {
            return 'mpjsjavascriptobject:{0}';
          }
        ''', name)
        if type(result) != str: return result
        types = {'promise': JSPromise, 'function': JSFunction, 'javascript': JSObject}
        for object_type in types:
            if 'mpjs' + object_type + 'object' in result:
               result = types[object_type](result.split(':')[1])
               break
        return result

    def __setattr__(self, key, value):
        if not self._name: return
        value = json.dumps(value)
        object_name = self._name + '.' + key
        js_exec('''
          {0} = {1};
        ''', object_name, value)

def JSFunction(name):
    short_name = name.split('.')[-1]
    def function(*args):
        args = json.dumps(list(args))
        cache_name = 'global.mpjscache' + ('.' + name if '.' not in name else json.dumps([name]))
        result = js_exec('''
          let object;
          if (global.mpjscache['{0}']) {
            object = global.mpjscache['{0}'](...{1});
          }
          else if ({0}) {
            object = {0}(...{1});
          }
          global.mpjscache['{0}'] = object;
          if (object && object.constructor === Promise) {
            object.then((object) => global.mpjscache['{0}'] = object);
            return 'mpjspromiseobject';
          }
          try {
            if (object && [Array, Object, Number, String, Boolean, Function, AsyncFunction].indexOf(object.constructor) < 0) throw Error('Not JSON Serializable');
            if (object && object.constructor === Object) for (let key in Object.keys(object)) {
              if (object.indexOf(key) < 0) throw Error('Not a JSON');
            }
            else if (object && (object.constructor === Function || object.constructor === AsyncFunction)) {
              return 'mpjsfunctionobject';
            }
            return object;
          }
          catch(error) {
            return 'mpjsjavascriptobject';
          }
        ''', name, args)
        if type(result) != str: return result
        types = {'promise': JSPromise, 'function': JSFunction, 'javascript': JSObject}
        for object_type in types:
            if 'mpjs' + object_type + 'object' in result:
               result = types[object_type](cache_name)
               break
        return result
    return function

def JS(variable):
    empty = JSObject('')
    return getattr(empty, variable)

#require = JS('require')
#result = require('fs').readFileSync('./test.js').toString()
#print(result)

#New API promise.wait(), now works without skipping event loop using emscripten_sleep, requires emterpreter

#require = JS('require')
#response = require('node-fetch')('https://github.com/').wait()
#print(response)
#result = response.text().wait()
#print(result)
