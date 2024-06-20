class A {
  constructor() {}
}
class B {
  func() {}
}
class C extends A {
  constructor() {
    super();
  }
  func() {}
}
const c = new C();
c.func();
