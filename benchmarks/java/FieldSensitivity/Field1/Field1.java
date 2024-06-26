// field/Class.java
package field;

import lib.annotations.callgraph.DirectCall;

class Class {

    @DirectCall(name = "method", line = 10, resolvedTargets = "Lfield/A;" , prohibitedTargets = {"Lfield/B;"})
    public static void main(String[] args){
        B b = new B();
        b.a.method();
    }
}
class A {
    void method() {
        //do something
    }
}
class B {
    A a = new A();
    void method() {
        //do something
    }
}
