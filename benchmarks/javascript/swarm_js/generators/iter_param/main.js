function func(c) {
    for (let i of c) {
    }
}

class Cls {
    constructor(max = 0) {
        this.max = max;
        this.n = 0;
    }

    *[Symbol.iterator]() {
        while (this.n <= this.max) {
            yield 2 ** this.n;
            this.n += 1;
        }
    }
}

func(new Cls());