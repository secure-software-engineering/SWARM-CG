# TrivialReflection
This tests pertain to the Java's reflection API and comprise method call to
```java.lang.Class.getDeclaredMethod```, ```java.lang.Class.getMethod```,
```java.lang.Class.getField```, ```java.lang.reflect.Method.invoke```, and others. Cases that belong
to this category are rather trivially resolvable as all API inputs are directly known and neither
data-flow nor control-flow analyses are required. 

[//]: # (MAIN: tr.Demo)
Tests the reflective call resolution when an object of type ```java.lang.Class``` is used to find a
declared method (```Class.getDeclaredMethod```) of this class. Afterwards, the found method is invoked.
Since the target method ```Demo.target``` is static and has no arguments, neither a receiver nor a
method argument is passed over the ```invoke``` method.
