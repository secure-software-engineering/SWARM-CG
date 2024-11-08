function func3() {}
function func2(a = func3) {
  a();
}
function func1(a, b = func2) {
  a(b);
}
func1(func2, func3);