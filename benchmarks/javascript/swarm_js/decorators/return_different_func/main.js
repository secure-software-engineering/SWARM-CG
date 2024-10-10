function dec(f) {
  return function inner() {
    f();
  };
}
const func = dec(function () {});
function func2() {
  func();
}
func2();
