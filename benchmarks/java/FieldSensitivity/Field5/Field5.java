// field/Class.java
package field;

import lib.annotations.callgraph.DirectCall;

class Class {

    @DirectCall(name = "method", line = 15, resolvedTargets = "Lfield/A;", prohibitedTargets = {"Lfield/B;", "Lfield/Superclass;"})
    public static void main(String[] args){
        Test x  = new Test();
        Test y = new Test();
        x.a = new Superclass();
        y.a = new B();
        x = y;
        y.a = new A();
        x.a.method();
    }
}

class Superclass {
    void method() {
        //do something
    }
}
class A extends Superclass {
    void method() {
        //do something
    }
}
class B extends Superclass {
    void method() {
        //do something
    }
}
class Test {
    Superclass a;
}
