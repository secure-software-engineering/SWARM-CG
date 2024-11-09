[//]: # (MAIN: tr.Demo)
Tests the reflective call resolution when an object of type ```java.lang.Class``` is used to find a
declared method (```Class.getDeclaredMethod```) of this class. Afterwards, the found method is invoked.
Since the target method ```Demo.target``` is static and has one parameter, a ```null``` receiver as
well as a ```String``` matching the method's parameters are passed over the ```invoke``` method.
