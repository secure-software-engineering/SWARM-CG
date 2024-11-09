# SerializableClasses
These category comprises test cases that model callbacks that must be handled when dealing with 
```java.io.Serializable``` classes. As soon as object (de-)serialization is found within a program
those mechanism can be used and all related methods must therefore be considered as on-the-fly
entry points.

[//]: # (MAIN: ser.Demo)
This test pertains to the ```writeObject``` callback method that can be implemented when a class
implements ```java.io.Serializable``` as ```ser.Demo``` does. Overriding ```writeObject``` forces
the JVM to call ```writeObject``` instead of the normally used ```defaultWriteObject``` method. In
```ser.Demo```'s main method, an instance of ```ser.Demo``` as well as an ```java.io.ObjectOutputStream```
is created. The latter is then used to serialize the instance of ```ser.Demo``` that has been created
previously. Serializing this object triggers the JVM which then calls the overridden 
```ser.Demo.writeObject``` method.
