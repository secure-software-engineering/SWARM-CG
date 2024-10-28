// unsafe/UnsafeDemo.java
package unsafe;

import sun.misc.Unsafe;
import java.lang.reflect.Constructor;
import java.lang.reflect.Field;

public class UnsafeDemo {
    private TargetInterface targetField = null;

    public static void main(String[] args) throws Exception {
        Constructor<Unsafe> unsafeConstructor = Unsafe.class.getDeclaredConstructor();
        unsafeConstructor.setAccessible(true);
        Unsafe unsafe = unsafeConstructor.newInstance();

        UnsafeDemo demoInstance = new UnsafeDemo();
        Field targetFieldRef = UnsafeDemo.class.getDeclaredField("targetField");
        long targetFieldOffset = unsafe.objectFieldOffset(targetFieldRef);

        unsafe.compareAndSwapObject(demoInstance, targetFieldOffset, null, new UnsafeTargetClass());
        demoInstance.targetField.targetMethod();
    }
}

interface TargetInterface {
    String targetMethod();
}

class UnsafeTargetClass implements TargetInterface {
    public String targetMethod() {
        return "UnsafeTargetClass";
    }
}

class SafeTargetClass implements TargetInterface {
    public String targetMethod() {
        return "SafeTargetClass";
    }
}