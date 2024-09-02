function simpleDec(func) {
    return func;
}

function simpleFunc() {
}

simpleFunc = simpleDec(simpleFunc);

simpleFunc();
