function func1() {
  function dec(f) {
    return f;
  }
  return dec;
}
const func2 = func1()(function () {});
func2();
