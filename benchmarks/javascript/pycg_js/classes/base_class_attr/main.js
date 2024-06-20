class A {
  static B = class {
    bfunc() {}
  };
}
class C extends A.B {
  cfunc() {}
}
const c = new C();
c.cfunc();
c.bfunc();
