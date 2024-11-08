class MyClass {
  func2() {
  }

  func1() {
    return this.func2;
  }
}

const a = new MyClass();
const b = a.func1();
b();