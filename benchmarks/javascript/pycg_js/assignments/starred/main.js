function func1() {}

function func2() {}

function func3() {}

function func4() {}

let a = func1;
let b = [func2, func3];
let c = func4;

a();
b[0]();
b[1]();
c();
