function nested_func() {}
function param_func(a) {
  a();
}
function func(a) {
  a(nested_func);
}
let b = param_func;
let c = func;
c(b);
