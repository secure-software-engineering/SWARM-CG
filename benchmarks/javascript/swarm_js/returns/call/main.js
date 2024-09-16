function return_func() {}
function func() {
  return return_func;
}
const a = func();
a();
