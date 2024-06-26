[//]: # (MAIN: tmr.Demo)
Tests modern reflection by performing a ```findVirtual``` method handle lookup where the
declaring class type, the instance method's name, and the method's method type object is given within the
the main method of ```tmr.Demo```. Afterwards, ```invokeExact``` is called on the looked up method
handle which results in a call to ```tmr.Demo.target```.
