function dec1(f) {
  return function inner() {
    return f();
  };
}
function dec2(f) {
  return function inner() {
    return f();
  };
}
function func() {}
const funcDecorated = dec1(dec2(func));
funcDecorated();
