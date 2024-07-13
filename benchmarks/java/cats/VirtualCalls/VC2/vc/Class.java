// vc/Class.java
package vc;

import lib.annotations.callgraph.DirectCall;

class Class {

    public void method(boolean b){ 
        a();
    }

    public void method(int e){
        b();
     }
    
    @DirectCall(name = "method", line = 11, resolvedTargets = "Lvc/SubClass;")
    public static void callMethod(Class cls) {
        cls.method(false);
        cls.method(1)
    } 

    public static void main(String[] args){
        callMethod(new SubClass());
    }

    public void a(){ }
    public void b(){ }

}

class SubClass extends Class {

    public void method() { }
}
