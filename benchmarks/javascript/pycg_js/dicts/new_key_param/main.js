function func2() {}

function func(key = "a") {
  d[key] = func2;
}

const d = {};

func();
d["a"]();
