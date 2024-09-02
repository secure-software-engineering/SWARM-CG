function finalFunc() {
}

function firstFunc() {
    const returnVal = finalFunc;
    return returnVal;
}

const funcVal = firstFunc;
funcVal()();
