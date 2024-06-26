// flow/Class.java
package flow;

import lib.annotations.callgraph.DirectCall;

class Class {
    @DirectCall(name = "method", line = 12, resolvedTargets = "Lflow/Subclass1;" ,
            prohibitedTargets = {"Lflow/Superclass;"})
    public static void main(String[] args){
        Superclass clz = new Superclass();
        Superclass clz1 = new Subclass1();
        clz = clz1;
        clz.method();
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
