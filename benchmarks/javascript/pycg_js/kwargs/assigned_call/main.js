function func2() {}
function func(a) {
  a();
}
let a = func;
let b = func2;
a({ a: b });
