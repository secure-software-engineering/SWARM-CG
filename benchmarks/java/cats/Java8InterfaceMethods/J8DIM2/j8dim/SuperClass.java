// j8dim/SuperClass.java
package j8dim;


class SuperClass {

    public void method(){
        // do something
    }

    public static void main(String[] args){
        Interface i = new SubClass();
        i.method();
    }
}

interface Interface {
    default void method() {
        // do something
    }
}

class SubClass extends SuperClass implements Interface {

}