function return_func() {}
function func() {
  let a = return_func;
  return a;
}
let a = func;
a()();
