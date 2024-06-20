function func(x) {}
[1, 2, 3].map(func);
function func2(x) {
  return func(x);
}
[1, 2, 3].map(func2);
function func3(x) {
  return function () {
    return x;
  };
}
const res = [1, 2, 3].map(func3);
res.forEach((r) => {
  r();
});
