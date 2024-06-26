[//]: # (MAIN: ser.Demo)
This test pertains to the ```validateObject``` callback method that can be implemented when a class
implements ```java.io.Serializable``` as ```ser.Demo``` does. Overriding ```validateObject``` implies
that it can be called by the JVM after an object is deserialized when a validation procedure has been
registered (see ```registerValidation``` in ```readObject```).
