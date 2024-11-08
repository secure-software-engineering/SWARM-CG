function func1() {
}

function func2() {
}

function func3() {
}

function func4() {
}

const functions = [func1, func2, func3, func4];
const [a, ...rest] = functions;
const [b, c] = rest.slice(0, -1);
const d = rest[rest.length - 1];

a();
b();
c();
d();