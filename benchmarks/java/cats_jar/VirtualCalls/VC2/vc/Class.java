// vc/Class.java
package vc;

class Class {

    public void method(){ }

    public static void callMethod(Class cls) {
        cls.method();
    }

    public static void main(String[] args){
        callMethod(new SubClass());
    }
}

class SubClass extends Class {

    public void method() { }
}