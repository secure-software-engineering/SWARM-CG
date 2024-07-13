# SerializableClasses
These category comprises test cases that model callbacks that must be handled when dealing with 
```java.io.Serializable``` classes. As soon as object (de-)serialization is found within a program
those mechanism can be used and all related methods must therefore be considered as on-the-fly
entry points.

[//]: # (MAIN: ser.Demo)
This test pertains to the ```writeReplace``` callback method that can be implemented when a class
implements ```java.io.Serializable``` as ```ser.Demo``` does. Overriding ```writeReplace``` forces
the JVM to call ```writeReplace``` instead of the normally used ```defaultwriteObject``` method. In
```ser.Demo```'s main method, an ```ObjectOutputStream``` is used to serialize an instance of
```ser.Demo```. The call to ```ObjectInputStream.writeObject``` then causes the JVM to trigger the
serialization mechanism which in turn calls ```ser.Demo.writeReplace```.
