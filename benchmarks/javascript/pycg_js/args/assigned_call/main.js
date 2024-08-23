function paramFunc() {
}
  
function func(a) {
    a();
}

const b = paramFunc;
func(b);