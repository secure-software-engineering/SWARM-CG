function func2() {}

function func1(d) {
  d["a"]();
}

const d = { a: func2 };

func1(d);
