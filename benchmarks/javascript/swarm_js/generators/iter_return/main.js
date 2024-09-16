function func() {}

class Cls {
  constructor(max = 0) {
    this.max = max;
  }

  [Symbol.iterator]() {
    this.n = 0;
    return {
      next: () => {
        if (this.n > this.max) {
          return { done: true };
        }

        let result = 2 ** this.n;
        this.n++;
        return { value: func, done: false };
      },
    };
  }
}

for (let i of new Cls()) {
  i();
}
