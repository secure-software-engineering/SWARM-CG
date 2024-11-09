// spm7/VirtualSPMCall.java
package spm7;


import java.lang.invoke.MethodHandle;
import java.lang.invoke.MethodHandles;
import java.lang.invoke.MethodType;

class VirtualSPMCall {

    public static void main(String[] args) throws Throwable {   
        MethodType descriptor = MethodType.methodType(void.class, Object.class);
        MethodHandle mh = MethodHandles.lookup().findVirtual(Interface.class,"method", descriptor);
        Class callOnMe = new Class();
        mh.invoke(callOnMe, new Class());
   }
}

class Class extends Superclass implements Interface {
    /* empty class */
}

class Superclass {
   public void method(Object b){
       /* do something */
   }
}

interface Interface {
   default void method(Object b){
       /* do something */
   }
}
