[//]: # (MAIN: tr.Demo)
This test cases concerns the reflection API as well as a class' static initializer. Within the main
method of ```tr.Demo``` ```Class.forName``` is called trying to retrieve an object of
```java.lang.Class``` which is parameterized over ```tr.InitializedClass```. This lookup can trigger
the static initializer of ```tr.InitializedClass``` which must thus be contained in program's call graph.
