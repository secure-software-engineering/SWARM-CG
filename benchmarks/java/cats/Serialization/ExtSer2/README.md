[//]: # (MAIN: extser.Demo)
This test pertains to the ```readExternal``` callback method that can be implemented when a class
implements ```java.io.Externalizable``` as ```ser.Demo``` does. Overriding ```readExternal``` forces
the JVM to call ```readExternal``` during an object's deserialization via ```Externalizable```. In
```ser.Demo```'s main method, an instance of ```ser.Demo``` as well as an ```java.io.ObjectInputStream```
is created. The latter is then used to deserialize the instance of ```ser.Demo``` that was written to
```test.ser```previously. Deserializing this object triggers the JVM's deserialization mechanism 
which then calls the overridden ```ser.Demo.readExternal``` method.
