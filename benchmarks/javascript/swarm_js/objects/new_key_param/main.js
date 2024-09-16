function func2() {
}
  
function func(key = 'a') {
    d[key] = func2;
}

let d = {};

func();
d['a']();
