// staticinit/NonConstantFieldRefDemo.java
package staticinit;

public interface NonConstantFieldRefDemo {

    static String nonConstantField = initializeField();

    static String initializeField() {
        invokeCallback();
        return "Demo";
    }

    static void invokeCallback() {}
}

class Main {
    public static void main(String[] args) {
        NonConstantFieldRefDemo.nonConstantField.toString();
    }
}