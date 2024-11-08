function func1(key = 'a') {
    d[key]();
}

function func2() {
}

function func3() {
}

let d = {
"a": func2,
"b": func3
};

func1();
func1('b');