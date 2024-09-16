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
        const result = 2 ** this.n;
        this.n += 1;
        return { value: result, done: false };
      },
    };
  }
}
const c = new Cls();
