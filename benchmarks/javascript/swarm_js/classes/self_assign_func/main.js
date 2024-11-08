class A {
  func() {
  }
}
  
class B {
  constructor(a) {
    this.a = a;
  }

  func() {
    this.a.func();
  }
}

const a = new A();
const b = new B(a);
b.func();