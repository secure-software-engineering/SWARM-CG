function func1() {}
function func2() {}
function func3() {}
const a = [func1, func2, func3];
a[0]();
a[1]();
a[2]();
function func4() {}
const b = [null];
b[0] = func4;
b[0]();