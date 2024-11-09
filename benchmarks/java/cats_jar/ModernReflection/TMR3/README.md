[//]: # (MAIN: tmr.Demo)
Tests modern reflection by performing a ```findConstructor``` method handle lookup where the
declaring class type and the method's method type object is given within the
the main method of ```tmr.Demo```. Afterwards, ```invokeExact``` is called on the looked up method
handle which results in a call to ```tmr.Demo```'s constructor.

Whether the constructor is called or not is verified by a static method call within the constructor.
