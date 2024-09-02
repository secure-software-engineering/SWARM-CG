function performTask() {
}

function* generatorFunc(maxIterations) {
    let count = 0;
    while (count < maxIterations) {
        yield performTask;
        count++;
    }
}

for (const task of generatorFunc(100)) {
    task();
}
