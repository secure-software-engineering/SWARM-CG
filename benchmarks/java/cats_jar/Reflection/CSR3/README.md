
# ContextSensitiveReflection
The concrete strings require information about the context.

[//]: # (MAIN: csr.Demo)
This test cases concerns the reflection API as well as a class' static initializer. Within the main
method of ```csr.Demo``` a static method is called reads the value from a static field which is
first written write before the method call to ```Demo.callForName``` and then passed to ```Class.forName```.
```Class.forName``` then tries to retrieve an object of ```java.lang.Class``` which is parameterized
over ```csr.CallTarget```. In this test it is impossible to get any information about the retrieved
typed and, therefore, all possible types must be considered for a sound method resolution.
