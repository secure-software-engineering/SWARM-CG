import { ext_change } from './from_module.js';

function func1() {}

function func2() {}

class cls {
    constructor(fn) {
        this.fn = fn;
    }
}

const c = new cls(func1);

function local_change() {
    ext_change(c, func2);
}

local_change();
c.fn();