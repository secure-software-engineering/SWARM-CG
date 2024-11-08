class MyClass {
    constructor() {
    }

    func1() {
    }

    func2() {
    }

    func3() {
    }
}

class MyClass2 {
    constructor() {
    }
}

const a = new MyClass();
const b = new MyClass2();

const c = a.func1;
const [d, e] = [a.func2, a.func3];

c();
d();
e();