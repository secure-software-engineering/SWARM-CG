function func() {
  return 1 + 1;
}
func();
function func2() {
  return 1;
}
function func3() {
  return func2;
}
function func4(a) {
  return func3();
}
func4()();
function func5() {
  return func2() + 1;
}
func5();