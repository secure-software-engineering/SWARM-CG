class A {
  func() {}
}
class B {
  constructor() {}
  func() {}
}
class C extends A {
  constructor() {
    super();
    B.prototype.constructor.call(this);
  }
}
let c = new C();
c.func();
