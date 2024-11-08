function dec(f) {
  return f;
}
function func() {
  function dec(f) {
    return f;
  }
  function inner() {}
  dec(inner);
}
func();