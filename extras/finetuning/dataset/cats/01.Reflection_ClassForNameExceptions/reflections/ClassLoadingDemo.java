// reflections/ClassLoadingDemo.java
package reflections;


public class ClassLoadingDemo {

	public static void triggerException() { /* do something */ }

    public static void main(String[] args) {
        try {
            Class cls = Class.forName("reflections.DynamicClass");
            ExpectedClass expectedCls = (ExpectedClass) cls.newInstance();
        } catch (ClassCastException cce) {
            triggerException();
        } catch (ClassNotFoundException cnfe) {
            // DEAD CODE
        } catch (Exception rest) {
            // DEAD CODE
        }
    }
}

class DynamicClass {

}

class ExpectedClass {

}