// ctx/Class.java
package ctx;

import lib.annotations.callgraph.DirectCall;
import lib.annotations.callgraph.DirectCalls;

class Class {
    @DirectCalls({
            @DirectCall(name = "method", line = 13, resolvedTargets = "Lctx/Subclass1;", prohibitedTargets = {"Lctx/Superclass;"}),
            @DirectCall(name = "method", line = 15, resolvedTargets = "Lctx/Superclass;", prohibitedTargets = {"Lctx/Subclass1;"})})
    public static void main(String[] args) {
        Superclass clz, clz1;
        clz = assignObj(new Subclass1());
        clz.method();
        clz1 = assignObj(new Superclass());
        clz1.method();
    }

    private static Superclass assignObj(Superclass c) {
        return c;
    }
}

class Superclass {
    void method() {
        //do something
    }
}

class Subclass1 extends Superclass {
    void method() {
        //do something
    }
}
