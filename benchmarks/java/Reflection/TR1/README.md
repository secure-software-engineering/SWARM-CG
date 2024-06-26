[//]: # (MAIN: tr.Demo)
Tests the reflective call resolution when an object of type ```java.lang.Class``` is used to find a
declared method (```Class.getDeclaredMethod```) of this class. Afterwards, the found method is invoked.
Since the target method ```Demo.target``` is static and has no arguments, neither a receiver nor a
method argument is passed over the ```invoke``` method.
