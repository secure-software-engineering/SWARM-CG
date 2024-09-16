function func(a) {
  a(1);
}
const y = (x) => x + 1;
func(y);
