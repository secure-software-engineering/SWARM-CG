function func3(a) {
  a();
}
function func2(a, b) {
  a();
  func3(b);
}
function func1(a, b, c) {
  a();
  func2(b, c);
}
func1(
  (x) => x + 1,
  (x) => x + 2,
  (x) => x + 3
);
