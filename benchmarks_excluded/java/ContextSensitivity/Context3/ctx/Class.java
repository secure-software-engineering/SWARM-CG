// ctx/Class.java
package ctx;

import lib.annotations.callgraph.DirectCall;

class Class {

    @DirectCall(name = "method", line = 11, resolvedTargets = "Lctx/A;", rtParameterTypes = { int.class },
            prohibitedTargets = "Lctx/A;", ptParameterTypes = { String.class })
    public static void main(String[] args) {
        A a = new A();
        a.method(2);
    }
}
class A {
    void method(String a) {
        //do something
    }
    void method(int a) {
        //do something
    }
}
