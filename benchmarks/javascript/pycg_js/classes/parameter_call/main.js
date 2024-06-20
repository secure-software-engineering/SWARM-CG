class MyClass {
  func3() {}
  func2(a) {
    a();
  }
  func1(a, b) {
    a.call(this, b);
  }
}
const a = new MyClass();
a.func1(a.func2, a.func3);
