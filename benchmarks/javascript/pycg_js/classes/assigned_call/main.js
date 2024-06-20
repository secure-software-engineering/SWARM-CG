class MyClass {
  func() {}
}
const a = new MyClass();
const b = a.func.bind(a);
b();
