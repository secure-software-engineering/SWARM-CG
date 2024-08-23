function returnFunc() {
}
  
function func() {
    let a = returnFunc;
    return a;
}

let a = func;
a()(); // Double call to invoke the function returned by func
