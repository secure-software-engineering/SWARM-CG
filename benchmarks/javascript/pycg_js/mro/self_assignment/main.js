class B {
  funcb() {
    this.smth = this.func;
  }
  func() {}
}
class A extends B {
  funca() {
    this.smth = this.func;
  }
  func() {}
}
const a = new A();
a.funcb();
a.smth();
a.funca();
a.smth();
