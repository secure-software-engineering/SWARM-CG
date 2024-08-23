function function1() {
}

function function2() {
}

function func(arg1, arg2 = function1) {
    arg1();
    arg2();
}

func(function2, function2);
