function param_func() {}
function func(a) {
  a();
}
let b = param_func;
func(b);
