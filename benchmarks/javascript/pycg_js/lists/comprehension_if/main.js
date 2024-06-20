function func() {
  return true;
}
let a = [...Array(10).keys()].filter((a) => func());
