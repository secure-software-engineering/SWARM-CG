import { Cls } from "./ext.js";
function fn(a) {
  a();
}
const a = new Cls();
fn(a.fun);
