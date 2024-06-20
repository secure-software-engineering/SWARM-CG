class A extends Error {
  constructor() {
    super();
  }
}
let a = A;
throw new a();
