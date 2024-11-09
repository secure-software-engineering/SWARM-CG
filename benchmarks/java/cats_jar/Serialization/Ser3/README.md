# SerializableClasses
These category comprises test cases that model callbacks that must be handled when dealing with 
```java.io.Serializable``` classes. As soon as object (de-)serialization is found within a program
those mechanism can be used and all related methods must therefore be considered as on-the-fly
entry points.

[//]: # (MAIN: ser.Demo)
This test pertains to the ```writeObject``` callback method that can be implemented when a class
implements ```java.io.Serializable``` as ```ser.Demo``` does. Overriding ```writeObject``` forces
the JVM to call ```writeObject``` instead of the normally used ```defaultWriteObject``` method. In
```ser.Demo```'s main method, an instance of ```ser.Demo``` is created and passed to static method.
This method, ```ser.Demo.serialize```, creates an output stream and serializes the object given by the method's parameter.
Without considering inter-procedural information, the test case can only be modeled imprecisely by
taking all ```writeObject``` methods into account.
