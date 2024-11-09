# SerializableClasses
These category comprises test cases that model callbacks that must be handled when dealing with 
```java.io.Serializable``` classes. As soon as object (de-)serialization is found within a program
those mechanism can be used and all related methods must therefore be considered as on-the-fly
entry points.

[//]: # (MAIN: ser.Demo)
This test pertains to the ```readObject``` callback method that can be implemented when a class
implements ```java.io.Serializable``` as ```ser.Demo``` does. Overriding ```readObject``` forces
the JVM to call ```readObject``` instead of the normally used ```defaultReadObject``` method. In
```ser.Demo```'s main method, an ```ObjectInputStream``` is used to deserialize a previously
serialized object from the ```test.ser``` file. The call to ```ObjectInputStream.readObject``` then
causes the JVM to trigger the deserialization mechanism which in turn calls ```ser.Demo.readObject```.
The returned result is then casted to ```ser.Demo``` which either results in a class cast exception or
implies that the deserialized object was from type ```ser.Demo```.
Without any information about the file's content it is impossible to resolve the call precisely.
