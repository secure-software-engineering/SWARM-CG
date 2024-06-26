[//]: # (MAIN: ser.Demo)
This test pertains to the ```writeReplace``` callback method that can be implemented when a class
implements ```java.io.Serializable``` as ```ser.Demo``` does. Overriding ```writeReplace``` forces
the JVM to call ```writeReplace``` instead of the normally used ```defaultwriteObject``` method. In
```ser.Demo```'s main method, an ```ObjectOutputStream``` is used to serialize an instance of
```ser.Demo```. The call to ```ObjectInputStream.writeObject``` then causes the JVM to trigger the
serialization mechanism which in turn calls ```ser.Demo.writeReplace```.
