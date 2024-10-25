// tr/Demo.java
package tr;

import java.lang.reflect.Field;


public class Demo {
    private Target field;

    public static void main(String[] args) throws Exception {
        Demo demo = new Demo();
        demo.field = new CallTarget();

        Field field = Demo.class.getDeclaredField("field");
        Target target = (Target) field.get(demo);
        target.target();
    }
}

interface Target {
    void target();
}

class CallTarget implements Target {
    public void target(){ /* do something */ }
}

class NeverInstantiated implements Target {
    public void target(){ /* do something */ }
}
