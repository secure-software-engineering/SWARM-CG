function func2() {}

function func1(key) {
  ls[key]();
}

const ls = [func1, func2];

func1(1);
