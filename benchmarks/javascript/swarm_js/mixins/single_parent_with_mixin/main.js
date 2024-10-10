class Alpha {
    method() {
        console.log("Alpha method");
    }
}

class Beta {
    constructor() {
    }

    method() {
        console.log("Beta method");
    }
}

class Gamma extends Alpha {
}

Object.assign(Gamma.prototype, Beta.prototype);

let instance = new Gamma();
instance.method(); // Should call Beta method as it is assigned last
