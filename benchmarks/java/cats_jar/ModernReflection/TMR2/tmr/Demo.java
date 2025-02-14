// tmr/Demo.java
package tmr;

import java.lang.invoke.MethodHandle;
import java.lang.invoke.MethodHandles;
import java.lang.invoke.MethodType;

class Demo {
    public String target() { return "Demo"; }

    public static void main(String[] args) throws Throwable {
        MethodType methodType = MethodType.methodType(String.class);
        MethodHandle handle = MethodHandles.lookup().findVirtual(Demo.class, "target", methodType);
        String s = (String) handle.invokeExact(new Demo());
    }
}
