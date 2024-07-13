[//]: # (MAIN: tmr.Demo)
Tests modern reflection by performing a ```findGetter``` method handle lookup where the
declaring class type, the field's name, and the field's type is given within the
the main method of ```tmr.Demo```. Afterwards, ```invoke``` is called with a new instance of
```tmr.Demo``` on the looked up method handle which results in a call to ```Demo.target``` on
```tmr.Demo.field```.
