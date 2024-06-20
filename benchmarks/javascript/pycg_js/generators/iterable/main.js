class func {
  constructor(n) {
    this.n = n;
    this.num = 0;
  }
  [Symbol.iterator]() {
    return {
      next: () => {
        if (this.num < this.n) {
          let cur = this.num;
          this.num++;
          return { value: cur, done: false };
        } else {
          return { done: true };
        }
      },
    };
  }
}
for (let i of new func(100)) {
}
