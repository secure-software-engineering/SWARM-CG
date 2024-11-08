function dec1(f) {
  return f;
}
function dec2(f) {
  return f;
}
let a = dec1;
a = dec2;
function func() {}
a(func)();