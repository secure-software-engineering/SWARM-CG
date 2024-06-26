[//]: # (MAIN: extser.Demo)
This scenario tests whether the constructor calls w.r.t. externalizable classes are handled soundly.
During deserialization, the JVM calls the no-argument constructor of the ```Externalizable``` class.
