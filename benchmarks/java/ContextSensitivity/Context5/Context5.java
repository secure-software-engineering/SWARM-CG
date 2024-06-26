// ctx/Class.java
package ctx;

import lib.annotations.callgraph.DirectCall;

class Class {

    public static void main(String[] args) {
        assignObj(new Subclass1());
    }

    @DirectCall(name = "method", line = 13, resolvedTargets = "Lctx/Subclass1;" , prohibitedTargets = {"Lctx/Superclass;"})
    private static void assignObj(Superclass c) {
        c.method();
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
