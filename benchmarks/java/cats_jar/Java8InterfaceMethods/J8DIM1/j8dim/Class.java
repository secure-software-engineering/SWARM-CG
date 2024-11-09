// j8dim/Class.java
package j8dim;


class Class implements Interface {

    public static void main(String[] args){
        Interface i = new Class();
        i.method();
    }
}

interface Interface {
    default void method() {
        // do something
    }
}
