// invokedynamic/MethodReferenceDemo.java
package invokedynamic;

class MethodReferenceDemo extends BaseClass {

    public void invokeViaMethodReference() {
        java.util.function.Supplier<String> typeSupplier = super::fetchTypeName;
        typeSupplier.get();
    }

    public static void main(String[] args) {
        MethodReferenceDemo demo = new MethodReferenceDemo();
        demo.invokeViaMethodReference();
    }
}

class BaseClass {
    protected String fetchTypeName() {
        return "Linvokedynamic/BaseClass;";
    }
}