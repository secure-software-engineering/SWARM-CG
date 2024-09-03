class A extends Error {
  constructor() {
    super();
  }
}
const a = A;
throw new a();
