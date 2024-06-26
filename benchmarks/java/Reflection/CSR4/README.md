[//]: # (MAIN: csr.Demo)
This test cases concerns the reflection API as well as a class' static initializer. Within the main
method the methods ```java.lang.System.getProperties``` and ```java.lang.System.setProperties``` are
used to add a ```className``` property with the value ```csr.TargetClass``` to the global system
properties and thus make it globally available throughout the program. Afterwards,
```csr.Demo.callForName``` is called that then uses ```java.lang.System.getProperty("className")```
to access the stored string which is passed to the ```Class.forName``` call. Modelling system
properties would help to resolve this case soundly and better precision.
