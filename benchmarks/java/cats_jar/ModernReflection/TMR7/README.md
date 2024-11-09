[//]: # (MAIN: tmr.Demo)
Tests modern reflection by performing a ```findStatic``` method handle lookup where the
declaring class type, the static method's name, and the method's signature is given within the
the main method of ```tmr.Demo```. Afterwards, ```invoke``` is called on the looked up method
handle which results in a call to ```target```. Due to the invocation of ```MethodHandle.invoke```
it is possible that the return- or parameter types are adapted by the JVM, i.e. types might be
(un)boxed.
