function function1() {
}

function function2() {
}

class MyClass {
    constructor(func = function1) {
        this.fn = func;
    }
}

const instance = new MyClass(function2);
instance.fn();