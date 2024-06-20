function func1() {}

function func2() {}

let d = {
  a: {
    b: func1,
  },
};

d["a"]["b"] = func2;

d["a"]["b"]();
