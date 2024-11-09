// j8dim/SuperClass.java
package j8dim;


abstract class SuperClass {

    public void compute(){ /* do something*/ }

    public static void main(String[] args){
        Class cls = new Class();
        cls.method();
        cls.compute();
    }
}
class Class extends SuperClass implements DirectInterface, Interface1, Interface2 {

}

interface Interface1 {

    void compute();

    default void method() {
        // do something
    }
}

interface Interface2 {

    void compute();

    default void method() {
            // do something
        }
}

interface DirectInterface extends Interface1, Interface2 {
    default void method() {
        // do something
    }
}
