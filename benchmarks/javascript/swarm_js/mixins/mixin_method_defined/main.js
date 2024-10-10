class Alpha {
    constructor() {
        console.log("Alpha constructor");
    }
}

class Beta {
    method() {
        console.log("Beta method");
    }
}

class Gamma extends Alpha {
    constructor() {
        super();
    }

    method() {
        console.log("Gamma method");
    }
}

Object.assign(Gamma.prototype, Beta.prototype);

let instance = new Gamma();
instance.method(); // Calls Gamma method
