
# ContextSensitiveReflection
The concrete strings require information about the context.

[//]: # (MAIN: csr.Demo)
This test cases concerns the reflection API as well as a class' static initializer. Within the main
method of ```csr.Demo``` a static method is called that receives the string constant
which is transitively passed to ```Class.forName``` and then tries to retrieve an object of
```java.lang.Class``` which is parameterized over ```csr.TargetClass```. To infer the parameter that
flows into ```Class.forName``` inter-procedural string tracking is required. This lookup can trigger
the static initializer of ```csr.TargetClass```.
