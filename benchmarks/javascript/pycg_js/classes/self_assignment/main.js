class A {
  constructor() {
    this.smth = this.func2;
  }
  func() {
    this.smth();
  }
  func2() {}
}
const a = new A();
a.func();
