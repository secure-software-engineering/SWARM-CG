// tmr/Demo.java
package tmr;

import java.lang.invoke.MethodHandle;
import java.lang.invoke.MethodHandles;


class Demo {
    public String toString() { return "42"; }

    public static Demo field = new Demo();

    public static void main(String[] args) throws Throwable {
        MethodHandle handle = MethodHandles.lookup().findStaticGetter(Demo.class, "field", Demo.class);
        handle.invoke().toString();
    }
}
