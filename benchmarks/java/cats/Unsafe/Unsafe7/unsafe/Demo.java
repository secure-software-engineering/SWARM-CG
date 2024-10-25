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

        Demo demo = new Demo();
        Field objectField = Demo.class.getDeclaredField("objectVar");
        long objectOffset = unsafe.objectFieldOffset(objectField);

        demo.objectVar = new SafeTarget();
        UnsafeTarget unsafeTarget = new UnsafeTarget();
        unsafe.putObjectVolatile(demo, objectOffset, unsafeTarget);
        
        ((TargetInterface)demo.objectVar).targetMethod();
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
