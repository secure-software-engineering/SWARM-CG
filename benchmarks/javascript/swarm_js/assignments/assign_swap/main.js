function funcA() {
}

function funcB() {
}

let var1 = funcA;
let var2 = funcB;
[var1, var2] = [var2, var1];
var1();