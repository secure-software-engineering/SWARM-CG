function func() {
}

function func2(a) {
    return a;
}
  
function func3() {
    return func2;
}

func3()(func)();
