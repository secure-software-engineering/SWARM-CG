# Signature Polymorphic Methods

Tests relating to this category are special cases of the ```java.lang.invoke.MethodHandle```, or 
```java.lang.invoke.VarHandle``` respectively, API.
A method is signature polymorphic if all of the following criteria are true:
- The method is declared in the ```java.lang.invoke.MethodHandle```/```java.lang.invoke.VarHandle```
class.
- It has a single formal parameter of type ```Object[]```.
- It has the ```ACC_VARARGS``` and ```ACC_NATIVE``` flags set.

Method calls of this category are special because the signature of the invoked method can differ from
the actually invoked method, when the method handle is invoked over MethodHandle's ```invoke``` method.
Therefore, special semantic applies to those method calls. For instance, passed parameters are (un)boxed,
casted, or widened automatically. Please note, those automated operations are not performed when
```invokeExcact``` is called. 

> Further information pertaining signature polymorhpic methods can be found withing the JVM spec §2.9.3