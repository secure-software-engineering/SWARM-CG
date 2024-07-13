[//]: # (MAIN: tmr.Demo)
Tests modern reflection by performing a ```findSpecial``` method handle lookup where the
declaring class type, the method's name and signature, and the special caller are passed to method.
Afterwards, ```invoke``` is called with a new instance of ```tmr.Demo``` on the looked
up method handle which results in a call to ```Superclass.target``` on an instance of```tmr.Demo```.
