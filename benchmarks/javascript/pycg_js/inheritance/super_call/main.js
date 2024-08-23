class Alpha {
    constructor() {
    }
}

class Beta extends Alpha {
    constructor() {
        super();
    }
}

class Gamma extends Beta {
    constructor() {
        super();
    }
}

let instance = new Gamma();