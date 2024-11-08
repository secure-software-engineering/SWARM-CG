function func4() {}
function func2() {}
function func3() {}
function func(a, b, c) {
  a();
  b();
  c();
}
func(func2, func3, func4);