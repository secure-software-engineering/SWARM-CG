// field/Class.java
package field;

import lib.annotations.callgraph.DirectCall;

class Class {

    @DirectCall(name = "method", line = 11, resolvedTargets = "Lfield/A;", prohibitedTargets = {"Lfield/B;"})
    public static void main(String[] args) {
        B b = new B();
        setField(b);
        b.a.method();
    }
    private static void setField(B b) {
        b.a = new A();
    }
}

class A {
    void method() {
        //do something
    }
}
class B {
    A a;
    void method() {
        //do something
    }
}
