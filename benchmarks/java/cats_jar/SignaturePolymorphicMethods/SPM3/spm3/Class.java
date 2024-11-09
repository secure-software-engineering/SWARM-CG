// spm3/Class.java
package spm3;


import java.lang.invoke.MethodHandle;
import java.lang.invoke.MethodHandles;
import java.lang.invoke.MethodType;

class Class {
    
       public static void method(MyObject mo){
           /* do Something */
       }
   
       public static void method(MyString ms){
           /* do Something */
       }

       public static void main(String[] args) throws Throwable {
           MethodType descriptor = MethodType.methodType(void.class, MyObject.class);
           MethodHandle mh = MethodHandles.lookup().findStatic(Class.class, "method", descriptor);
           MyString widenMe = new MyString();
           mh.invoke(widenMe);
       }
}

class MyObject {}
final class MyString extends MyObject {}
