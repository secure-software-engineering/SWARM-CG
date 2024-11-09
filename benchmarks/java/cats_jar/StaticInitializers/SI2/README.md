[//]: # (MAIN: si.Demo)
A static initializer should be triggered when a *static interface method* is invoked. The scenario below
shows an interface ```si.Interface``` which declares a static method (```callback```) which is called in the
```si.Demo```'s main method. The invocation of ```callback``` causes the JVM to call ```si.Interface```'s
 static initializer (```<clinit>```). 
 >Please not that this is not directly annotatable and we thus use a static initialized field that
 is also initialized within the static initializer and triggers a method invocation that can be tested.
