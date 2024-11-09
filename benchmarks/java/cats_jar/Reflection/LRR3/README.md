[//]: # (MAIN: lrr.Demo)
This test cases concerns the reflection API as well as a class' static initializer. Within the main
method of ```lrr.Demo``` ```Class.forName``` is called trying to retrieve an object of
```java.lang.Class``` which is parameterized over ```lrr.TargetClass```. The target String which is
passed to the respective ```Class.forName``` call is first assigned to Demo's field and then the
field's value is read and finally passed as parameter.
This lookup can then trigger the static initializer of ```lrr.TargetClass``` which must thus be
contained in program's call graph.
