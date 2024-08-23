class MyClass {
    func2() {
    }
  
    func1() {
      return this.func2;
    }
}
  
const a = new MyClass();
a.func1()();
