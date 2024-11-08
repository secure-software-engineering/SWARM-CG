function func1(a) {
  return a + 1;
}
function func2(a) {
  return a + 1;
}
[...Array(10).keys()].map((b) => func2(b)).map((a) => func1(a));