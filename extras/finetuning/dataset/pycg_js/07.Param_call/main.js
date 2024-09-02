function first_func(func) {
    func();
}

function param_func2() {
    return final_func3;
}

function final_func3() {}

first_func(param_func2());
