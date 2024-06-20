function func2() {}
function func1() {
  return func2;
}
const d = { a: func1() };
d["a"]();
