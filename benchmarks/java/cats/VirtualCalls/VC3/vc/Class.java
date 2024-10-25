// vc/Class.java
package vc;

interface Interface {
    void method();
}

class Class {

    public void method(){ }

    public static void callOnInterface(Interface i){
        i.method();
    }

    public static void main(String[] args){
        callOnInterface(new ClassImpl());
    }
}

class ClassImpl implements Interface {
    public void method(){ }
}
