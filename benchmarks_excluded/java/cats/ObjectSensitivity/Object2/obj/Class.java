// obj/Class.java
package obj;

import lib.annotations.callgraph.DirectCall;

class Class {

    @DirectCall(name = "method", line = 11, resolvedTargets = "Lobj/Subclass1;" , prohibitedTargets = {"Lobj/Superclass;"})
    public static void main(String[] args) {
        Test clz = new Test(new Superclass());
        Test clz1 = new Test(new Subclass1());
        clz1.a.method();
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
class Test {
    Superclass a;
    
    public Test(Superclass a) {
        this.a = a;
    }
}
