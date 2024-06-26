[//]: # (MAIN: ser.Demo)
This test pertains to the ```readResolve``` callback method that can be implemented when a class
implements ```java.io.Serializable``` as ```ser.Demo``` does. Overriding ```readResolve``` forces
the JVM to call ```readResolve``` instead of the normally used ```defaultReadObject``` method when 
```readObject``` is not overridden. In ```ser.Demo```'s main method, an ```ObjectOutputStream``` is
used to serialize an instance of ```ser.Demo```. The call to ```ObjectInputStream.readObject``` then
causes the JVM to trigger the serialization mechanism which in turn calls ```ser.Demo.readResolve```.
