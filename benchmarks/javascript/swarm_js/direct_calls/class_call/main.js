function func1() {}

function func2() {}

class cls {
    constructor(fn) {
        this.fn = fn;
    }

    change(fn) {
        this.fn = fn;
    }
}

const c = new cls(func1);
c.change(func2);
c.fn();