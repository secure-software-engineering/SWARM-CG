class A {
    func() {
        if (this.child) {
            this.child();
        }
    }
}
  
class B extends A {
    constructor() {
        super();
        this.child = this.func2;
    }

    func2() {
    }
}
  
class C extends A {
    constructor() {
      super();
      this.child = this.func2;
    }
  
    func2() {
    }
}
  
const b = new B();
b.func();

const c = new C();
c.func();
  