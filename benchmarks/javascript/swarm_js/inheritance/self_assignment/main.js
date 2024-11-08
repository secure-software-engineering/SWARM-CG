class Beta {
    methodB() {
        this.someFunc = this.method;
    }

    method() {
    }
}

class Alpha extends Beta {
    methodA() {
        this.someFunc = this.method;
    }

    method() {
    }
}

let instance = new Alpha();
instance.methodB();
instance.someFunc();

instance.methodA();
instance.someFunc();