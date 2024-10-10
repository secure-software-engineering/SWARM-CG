function func(a) {
    a();
}

function func2() {
    return func3;
}

function func3() {
}

func(func2());