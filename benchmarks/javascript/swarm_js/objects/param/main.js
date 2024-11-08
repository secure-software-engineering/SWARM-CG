function func2() {
}
  
function func1(d) {
    d["a"]();
}

let d = { "a": func2 };

func1(d);