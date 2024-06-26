[//]: # (MAIN: lrr.Demo)
This test cases concerns the reflection API as well as a class' static initializer. Within the main
method of ```lrr.Demo``` ```Class.forName``` is called trying to retrieve an object of
```java.lang.Class``` which is either parameterized over ```lrr.Left``` or ```lrr.Right```. This
lookup can trigger the static initializer of ```lrr.Left``` or ```lrr.Right``` which must thus be
contained in program's call graph.
