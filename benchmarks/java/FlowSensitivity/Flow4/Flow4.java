// flow/Class.java
package flow;

import lib.annotations.callgraph.DirectCall;

class Class {
    @DirectCall(name = "method", line = 11, resolvedTargets = "Lflow/Subclass1;" ,
            prohibitedTargets = {"Lflow/Superclass;"})
    public static void main(String[] args){
        Superclass clz = new Subclass1();
        Superclass clz1 = new Superclass();
        clz.method();
        clz = clz1;
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
