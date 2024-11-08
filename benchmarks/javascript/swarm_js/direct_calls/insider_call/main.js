function func1() {}

function func2() {}

class cls {
    constructor(fn) {
        this.fn = fn;
    }
}

const c = new cls(func1);

function change() {
    c.fn = func2;
}

change();
c.fn();