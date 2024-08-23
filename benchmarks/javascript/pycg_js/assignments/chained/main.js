function func1() {
}

function func2() {
}

let a = b = func1;
b();
a = b = func2;
a(); 