class C {
  func() {}
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
    let b = new B(this.c);
    b.func();
  }
}

let a = new A();
a.func();
