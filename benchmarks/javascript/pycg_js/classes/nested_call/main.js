class MyClass {
  func() {
    const nested = () => {};
    nested();
  }
}
const a = new MyClass();
a.func();
