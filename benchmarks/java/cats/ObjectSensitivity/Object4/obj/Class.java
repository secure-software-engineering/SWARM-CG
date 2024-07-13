// obj/Class.java
package obj;

import lib.annotations.callgraph.DirectCall;

class Class {

    @DirectCall(name = "method", line = 12, resolvedTargets = "Lobj/Subclass1;" , prohibitedTargets = {"Lobj/Superclass;"})
    public static void main(String[] args) {
        Test clz = new Test(new Subclass1());
        Test clz1 = clz;
        Test clz2 = clz1.getThis();
        clz2.a.method();
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
    
    Superclass getA() {
        return this.a;
    }
    
    Test getThis() {
        return this;
    }
}
