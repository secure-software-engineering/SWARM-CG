function dec(f) {
  f();
  return f;
}
const func = dec(function () {});
func();