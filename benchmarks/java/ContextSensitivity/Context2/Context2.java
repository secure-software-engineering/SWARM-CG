// ctx/Class.java
package ctx;

import lib.annotations.callgraph.DirectCall;

class Class {

    @DirectCall(name = "method", line = 11, resolvedTargets = "Lctx/Subclass1;" , prohibitedTargets = {"Lctx/Superclass;"})
    public static void main(String[] args) {
        Superclass clz1 = assignObj(new Subclass1());
        Superclass clz2 = assignObj(new Superclass());
        clz1.method();
    }

    private static Superclass assignObj(Superclass c) {
        return m1(c);
    }
    private static Superclass m1(Superclass c) {
        return m2(c);
    }private static Superclass m2(Superclass c) {
        return m3(c);
    }private static Superclass m3(Superclass c) {
        return m4(c);
    }private static Superclass m4(Superclass c) {
        return m5(c);
    }private static Superclass m5(Superclass c) {
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
