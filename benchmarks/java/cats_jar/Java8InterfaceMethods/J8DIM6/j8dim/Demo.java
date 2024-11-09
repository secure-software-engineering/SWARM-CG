// j8dim/Demo.java
package j8dim;


class Demo {

    public static void main(String[] args){
        new CombinedInterface(){}.method();
    }
}

interface SomeInterface {
    default void method() {
        // do something
    }
}

interface AnotherInterface {
    default void method() {
        // do something
    }
}

interface CombinedInterface extends SomeInterface, AnotherInterface {
    
    default void method() {
        SomeInterface.super.method();
        AnotherInterface.super.method();
    }
}
