// ctx/Class.java
package ctx;

import lib.annotations.callgraph.DirectCall;

class Class {

    @DirectCall(name = "method", line = 11, resolvedTargets = "Lctx/A;", rtParameterTypes = { String.class },
            prohibitedTargets = "Lctx/A;", ptParameterTypes = { String.class, String.class })
    public static void main(String[] args) {
        A a = new A();
        a.method("Hi!!");
    }
}
class A {
    void method(String a, String b) {
        //do something
    }
    void method(String a) {
        //do something
    }
}
