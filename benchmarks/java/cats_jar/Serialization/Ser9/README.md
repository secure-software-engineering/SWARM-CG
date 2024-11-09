# SerializableClasses
These category comprises test cases that model callbacks that must be handled when dealing with 
```java.io.Serializable``` classes. As soon as object (de-)serialization is found within a program
those mechanism can be used and all related methods must therefore be considered as on-the-fly
entry points.

[//]: # (MAIN: ser.Demo)
This scenario tests whether the constructor calls w.r.t. serializable classes are handled soundly.
During deserialization, the JVM calls the first constructor that neither has any formal parameter nor
belongs to ```Serializable``` class of the class which is deserialized. In the scenario below, an
instance of ```ser.Demo``` is going to be deserialized and during this process ```Superclass.<init>```
is called.
