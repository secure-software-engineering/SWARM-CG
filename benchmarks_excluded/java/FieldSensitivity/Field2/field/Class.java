// field/Class.java
package field;

import lib.annotations.callgraph.DirectCall;

class Class {

    @DirectCall(name = "method", line = 10, resolvedTargets = "Lfield/A;" , prohibitedTargets = {"Lfield/B;", "Lfield/C;"})
    public static void main(String[] args){
        C c = new C();
        c.b.a.method();
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
class C {
    B b = new B();
    void method() {
        //do something
    }
}
