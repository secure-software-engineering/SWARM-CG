// unsafe/Demo.java
package unsafe;

import sun.misc.Unsafe;
import java.lang.reflect.Constructor;
import java.lang.reflect.Field;


public class Demo {
    private Object objectVar = null;

    public static void main(String[] args) throws Exception {
        Constructor<Unsafe> unsafeConstructor = Unsafe.class.getDeclaredConstructor();
        unsafeConstructor.setAccessible(true);
        Unsafe unsafe = unsafeConstructor.newInstance();

        Demo o = new Demo();
        Field objectField = Demo.class.getDeclaredField("objectVar");
        long objectOffset = unsafe.objectFieldOffset(objectField);

        o.objectVar = new UnsafeTarget();
        TargetInterface f = (TargetInterface) unsafe.getObject(o, objectOffset);
        f.targetMethod();
    }
}

interface TargetInterface {
    String targetMethod();
}

class UnsafeTarget implements TargetInterface{
	public String targetMethod() {
		return "UnsafeTarget";
	}
}

class SafeTarget implements TargetInterface {
    public String targetMethod() {
        return "SafeTarget";
    }
}
