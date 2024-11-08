function function1() {
}

function function2() {
}

class MyClass {
    constructor(fn) {
        this.fn = fn;
    }
}

const instance1 = new MyClass(function1);
const instance2 = new MyClass(function2);
instance2.fn();