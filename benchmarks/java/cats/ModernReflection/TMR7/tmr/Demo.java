// tmr/Demo.java
package tmr;

import java.lang.invoke.MethodHandle;
import java.lang.invoke.MethodHandles;
import java.lang.invoke.MethodType;

class Demo {
    public static Object target(String param) { return param; }

    public static void main(String[] args) throws Throwable {
        MethodType methodType = MethodType.methodType(Object.class, String.class);
        MethodHandle handle = MethodHandles.lookup().findStatic(Demo.class, "target", methodType);
        String s = (String) handle.invoke((Object)"Demo");
    }
}
