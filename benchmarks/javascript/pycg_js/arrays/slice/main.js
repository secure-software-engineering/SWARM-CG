function func1() {}
function func2() {}
function func3() {}
const ls = [func1, func2, func3];
const ls2 = ls.slice(1, 3);
ls2[0]();
