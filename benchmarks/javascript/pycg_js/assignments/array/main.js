function func1() {
}

function func2() {
}

function func3() {
}

let [a, b] = [func1, func2];
a();
b();

let [c, d, e] = [func1, func2, func3];
c();
d();
e();