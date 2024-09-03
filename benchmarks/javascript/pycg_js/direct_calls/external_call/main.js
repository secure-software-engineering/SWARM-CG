import { change } from './from_module.js';


function local_func() {}

class cls {
    constructor(fn) {
        this.fn = fn;
    }
}

const c = new cls(local_func);
change(c);
c.fn();