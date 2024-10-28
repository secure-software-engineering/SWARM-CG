// signaturepolymorphism/PolymorphicDemo.java
package signaturepolymorphism;

import java.lang.invoke.MethodHandle;
import java.lang.invoke.MethodHandles;
import java.lang.invoke.MethodType;

class PolymorphicDemo {

    public static void performAction(int i) {
        /* do something */
    }

    public static void performAction(byte i) {
        /* do something */
    }

    public static void main(String[] args) throws Throwable {
        MethodType methodTypeDescriptor = MethodType.methodType(void.class, int.class);
        MethodHandle methodHandle = MethodHandles.lookup().findStatic(PolymorphicDemo.class, "performAction", methodTypeDescriptor);
        byte valueToCast = 42;
        methodHandle.invoke(valueToCast);
    }
}