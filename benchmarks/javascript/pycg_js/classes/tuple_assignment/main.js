class MyClass {
  constructor() {}
  func1() {}
  func2() {}
  func3() {}
}
class MyClass2 {
  constructor() {}
}
let a = new MyClass(),
  b = new MyClass2();
let c = a.func1,
  d = a.func2,
  e = a.func3;
c.call(a);
d.call(a);
e.call(a);
