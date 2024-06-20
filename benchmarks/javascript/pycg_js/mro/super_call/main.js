class A {
  constructor() {}
}
class B extends A {
  constructor() {
    super();
  }
}
class C extends B {
  constructor() {
    super();
  }
}
let c = new C();
