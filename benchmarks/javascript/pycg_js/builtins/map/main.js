function func(x) {
}

const array1 = [1, 2, 3];
array1.map(func);

function func2(x) {
    return func(x);
}

const array2 = [1, 2, 3];
array2.map(func2);

function func3(x) {
    function innerFunc() {
        return x;
    }
    return innerFunc;
}

const array3 = [1, 2, 3].map(func3);

array3.forEach(r => {
    r();
});
  