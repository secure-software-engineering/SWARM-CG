class Cls {
    constructor(max = 0) {
        this.max = max;
        this.n = 0;
    }

    *[Symbol.iterator]() {
        while (this.n <= this.max) {
            yield this.n;
            this.n += 1;
        }
    }
}

const c = new Cls();

for (let i of c) {
}
