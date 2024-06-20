function return_func() {
  function nested_return_func() {}
  return nested_return_func;
}
function func() {
  return return_func;
}
func()();
func()()();
