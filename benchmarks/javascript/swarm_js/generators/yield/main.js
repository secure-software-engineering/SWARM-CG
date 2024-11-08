function* func1(n) {
  let num = 0;
  while (num < n) {
    yield func2;
    num += 1;
  }
}
function func2() {}
for (let i of func1(100)) {
  i();
}