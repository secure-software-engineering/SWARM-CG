function func(a) {
  return a + 1;
}
let ls = Array.from({ length: 10 }, (_, a) => func(a));
