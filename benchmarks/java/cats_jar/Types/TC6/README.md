[//]: # (MAIN: tc.Demo)
Type narrowing due to Java's ```java.lang.Class.isAssignableFrom``` API call that checks whether a given
object (i.e. ```o```) can be assign to variable of the type the class instance is parameterized over, i.e.,
```Target.class``` is a shorthand notation for ```java.lang.Class<Target>```. Within the ```this```
branch of ```Demo.callIfInstanceOfTarget``` it is thus known that the passed object ```o``` must be
a subtype of ```Target```. Hence, ```o.toString``` must only be resolved to ```Target.toString```.
