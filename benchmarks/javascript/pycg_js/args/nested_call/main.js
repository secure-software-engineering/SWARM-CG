function nestedFunc() {
}

function paramFunc(a) {
    a();
}

function func(a) {
    a(nestedFunc);
}
  
const b = paramFunc;
const c = func;
c(b);
  