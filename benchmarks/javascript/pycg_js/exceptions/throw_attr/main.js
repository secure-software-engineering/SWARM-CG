class A {
  static B = class extends Error {
    constructor() {
      super();
    }
  };
}
throw new A.B();
