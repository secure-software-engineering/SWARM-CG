class A {
  constructor() {}
  func() {}
}
class B extends A {}
class C extends A {
  func() {}
}
class D extends C {}
let d = new D();
d.func();
