class C {
    func() {
    }
}
  
class B {
    constructor(c) {
      this.c = c;
    }
  
    func() {
      this.c.func();
    }
}
  
class A {
    constructor() {
      this.c = new C();
    }
  
    func() {
      const b = new B(this.c);
      b.func();
    }
}
  
const a = new A();
a.func();
  