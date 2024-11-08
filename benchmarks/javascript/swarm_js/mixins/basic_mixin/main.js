class Alpha {
    constructor() {
    }

    method() {
        console.log("Alpha method");
    }
}

class Beta extends Alpha {
}

const GammaMixin = {
    method() {
        console.log("Gamma method");
    }
};

class Delta extends Beta {
}

Object.assign(Delta.prototype, GammaMixin);

let instance = new Delta();
instance.method();