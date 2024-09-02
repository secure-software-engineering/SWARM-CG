function outer() {
    x = 1;

    function inner() {
        y = "Hello";
        return y;
    }

    return inner();
}

result1 = outer();
