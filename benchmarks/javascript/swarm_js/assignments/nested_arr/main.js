function func1() {
}

function func2() {
}

function func3() {
}

function func4() {
}

function func5() {
}

function func6() {
}

let a, b, c, d;
[a, [b, c]] = [func1, [func2, func3]];
a();
b();
c();

[a, [b, [c, d]]] = [func1, [func2, [func3, func4]]];

d();

let f, e;
[f, b] = [c, e] = [func5, func6];

e();
f();