function func2() {
}

function func1() {
    let d = { "a": func2 };
    return d;
}
  
let b = func1();
b["a"]();