[//]: # (MAIN: ser.Demo)
This test pertains to the ```writeObject``` callback method that can be implemented when a class
implements ```java.io.Serializable``` as ```ser.Demo``` does. Overriding ```writeObject``` forces
the JVM to call ```writeObject``` instead of the normally used ```defaultWriteObject``` method. In
```ser.Demo```'s main method, an instance of ```ser.Demo``` is created and passed to static method.
This method, ```ser.Demo.serialize```, creates an output stream and serializes the object given by the method's parameter.
Without considering inter-procedural information, the test case can only be modeled imprecisely by
taking all ```writeObject``` methods into account.
