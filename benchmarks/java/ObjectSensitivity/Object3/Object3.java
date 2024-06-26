// obj/Class.java
package obj;

import lib.annotations.callgraph.DirectCall;

class Class {

    @DirectCall(name = "method", line = 11, resolvedTargets = "Lobj/Subclass1;" , prohibitedTargets = {"Lobj/Superclass;"})
    public static void main(String[] args) {
        Superclass clz = new Subclass1();
        Superclass clz1 = clz;
        clz1.method();
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
