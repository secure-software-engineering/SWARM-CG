[//]: # (MAIN: id.Class)
Tests the invocation of a lamdba that results in an invokedynamic with an *INVOKESTATIC* method handle
which points to an synthetic method. Please not that all primitive integers are autoboxed to
```java.lang.Integer``` which then fits the lambdas (cf. ```isEven```) type.
