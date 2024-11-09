[//]: # (MAIN: tr.Demo)
Tests a reflective method invocation that is performed on a class' private field that is retrieved via the
reflection API. In ```tr.Demo```'s main method a new ```tr.Demo``` object is created and an object
of type ```tr.CallTarget``` is assigned to its field. This field is then retrieved via the reflection
using ```java.lang.Class.getDeclaredField(<fieldName>)``` and the field's name, namely ```"field"```.
```java.lang.reflect.Field.get``` is then used to get the object stored within the field of the Demo
instance that has been created previously. Afterwards, the returned instance is used to call
the ```target``` method.
