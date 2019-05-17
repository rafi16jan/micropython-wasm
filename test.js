(async () => {

const jspy = require('fs').readFileSync('js.py').toString()
const micropython = await require('./index.js')
console.log(micropython)
micropython.init(64 * 100000)
micropython.do_str(jspy)

//Testing JS event loop, works
/*await micropython.do_str('c = False')
global.interval = setInterval(() => {
  micropython.do_str(`
import js
if not c:
 js.exec("console.log('wait')")
else:
 js.exec("clearInterval(interval)")
  `)
}, 500)
setTimeout(() => {
  micropython.do_str(`
import js
c = True
js.exec("console.log('done')")
  `)
}, 5000)*/

//Testing tick skipping, works, but only on higher level (not possible on functions, or class)
/*await micropython.do_str("require = JS('require')")
await micropython.do_str("fetch = require('node-fetch')")
await micropython.do_str("result = fetch('https://google.com')")
await micropython.do_str("result = wait(result)")
await micropython.do_str("result = result._value")
await micropython.do_str("result = result.text()")
await micropython.do_str("result = wait(result)")
await micropython.do_str("result = result._value")
await micropython.do_str("print(result)")*/

})()
