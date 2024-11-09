[//]: # (MAIN: tr.Demo)
Tests the reflective invocation of a constructor by retrieving ```Demo```'s constructor with a 
String argument via ```java.lang.Class```'s ```getConstructor``` method and then calling ```newInstance```
of the returned ```java.lang.reflect.Constructor``` object. This call must be resolved to Demo's 
```<init>(String)``` method.
