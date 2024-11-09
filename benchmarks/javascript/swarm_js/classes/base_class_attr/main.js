class B {
    bfunc() {}
}
class A {}
A.B = B;
class C extends A.B {
    cfunc() {}
}
const c = new C();
c.cfunc();
c.bfunc();