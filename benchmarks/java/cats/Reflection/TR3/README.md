[//]: # (MAIN: tr.Demo)
Tests the reflective call resolution when an object of type ```java.lang.Class``` is used to find a
method (```Class.getMethod```) of this class. Afterwards, the found method is invoked.
Since the target method ```Demo.target``` is an instance method, the receiver (```this```) is passed
```invoke``` such that the method can be called on the actual receiver.
