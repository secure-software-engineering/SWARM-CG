class MyClass {
  func1() {}
  func2() {
    const a = this;
    a.func1();
  }
}
const a = new MyClass();
a.func2();
