// j8dim/SuperClass.java
package j8dim;


class SuperClass {

    public static void main(String[] args){
        SubClass subClass = new SubClass();
        subClass.method();
    }
}

interface Interface {
    default void method() {
        // do something
    }
}

class SubClass extends SuperClass implements Interface {

}
