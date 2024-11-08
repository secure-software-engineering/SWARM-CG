function func2() {
}

function func1() {
    return func2;
}

let d = { "a": func1() };

d["a"]();