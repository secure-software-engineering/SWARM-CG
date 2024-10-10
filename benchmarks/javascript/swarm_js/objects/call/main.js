function func1() {
}
  
function func2() {
}

let d = {
"a": func1,
1: func2,
2: 3
};

d["a"]();
d[1]();
