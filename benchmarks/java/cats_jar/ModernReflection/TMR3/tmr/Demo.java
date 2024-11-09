// tmr/Demo.java
package tmr;

import java.lang.invoke.MethodHandle;
import java.lang.invoke.MethodHandles;
import java.lang.invoke.MethodType;

class Demo {

    public static void main(String[] args) throws Throwable {
        MethodType methodType = MethodType.methodType(void.class);
        MethodHandle handle = MethodHandles.lookup().findConstructor(Demo.class, methodType);
        Demo f = (Demo) handle.invokeExact();
    }

    public Demo() {
        Demo.verifyCall();
    }

    public static void verifyCall(){ /* do something */ }
}
