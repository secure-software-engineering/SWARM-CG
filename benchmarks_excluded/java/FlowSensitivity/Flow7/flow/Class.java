// flow/Class.java
package flow;

import lib.annotations.callgraph.DirectCall;

class Class {
    private static boolean isEven(int n) {
        return n%2 == 0;
    }
    @DirectCall(name = "method", line = 14, resolvedTargets = "Lflow/Subclass1;" ,
            prohibitedTargets = {"Lflow/Superclass;", "Lflow/Subclass2;"})
    public static void main(String[] args){
        Superclass clz = new Subclass2();
        if(isEven(3)){
            clz = new Superclass();
        }
        else{
            clz = new Subclass1();
        }
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

class Subclass2 extends Superclass {
    void method() {
        //do something
    }
}
