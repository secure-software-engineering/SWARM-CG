function returnFunc() {
}
  
function func() {
    let a = returnFunc;
    return a;
}

let a = func;
a()();