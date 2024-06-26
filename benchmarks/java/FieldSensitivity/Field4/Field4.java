// field/Class.java
package field;

import lib.annotations.callgraph.DirectCall;

class Class {

    @DirectCall(name = "method", line = 12, resolvedTargets = "Lfield/A;", prohibitedTargets = {"Lfield/B;", "Lfield/Superclass;"})
    public static void main(String[] args){
        Test x  = new Test();
        Test y = x;
        x.a = new A();
        y.a.method();
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

class Test {
    Superclass a;
}
