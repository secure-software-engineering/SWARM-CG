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

const c = a.func1.bind(a);
const [d, e] = [a.func2.bind(a), a.func3.bind(a)];

c();
d();
e();
