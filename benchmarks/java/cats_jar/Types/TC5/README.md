[//]: # (MAIN: instanceofclassapi.Demo)
Type narrowing due to Java's ```java.lang.Class.isInstance``` API call that checks whether a given
object (i.e. ```o```) is of the same type the class instance is parameterized over, i.e.,
```Target.class``` is a shorthand notation for ```java.lang.Class<Target>```. Within the ```this```
branch of ```Demo.callIfInstanceOfTarget``` it is thus known that the passed object ```o``` must be
of type ```Target```. Hence, ```o.toString``` must only be resolved to ```Target.toString```.
