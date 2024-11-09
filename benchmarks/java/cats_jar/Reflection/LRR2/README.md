[//]: # (MAIN: lrr.Demo)
This test cases concerns the reflection API as well as a class' static initializer. Within the main
method of ```lrr.Demo``` ```Class.forName``` is called trying to retrieve an object of
```java.lang.Class``` which is either parameterized over ```lrr.IsEven``` or ```lrr.IsOdd``` where 
both strings are constructed over a StringBuilder. This lookup can then trigger the static initializers
of ```lrr.IsEven``` or ```lrr.IsOdd``` which must thus be contained in program's call graph.
