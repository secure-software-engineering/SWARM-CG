# ExternalizableClasses
Callback methods related to ```java.io.Externalizable``` classes.

[//]: # (MAIN: extser.Demo)
This test pertains to the ```writeExternal``` callback method that can be implemented when a class
implements ```java.io.Externalizable``` as ```ser.Demo``` does. Overriding ```writeExternal``` forces
the JVM to call ```writeExternal``` during an object's serialization via ```Externalizable```. In
```ser.Demo```'s main method, an instance of ```ser.Demo``` as well as an ```java.io.ObjectOutputStream```
is created. The latter is then used to serialize the instance of ```ser.Demo``` that has been created
previously. Serializing this object triggers the JVM's serialization mechanism  which then calls the
overridden ```ser.Demo.writeExternal``` method.
