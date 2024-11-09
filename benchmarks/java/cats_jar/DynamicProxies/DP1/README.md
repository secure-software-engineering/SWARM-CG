[//]: # (MAIN: dp.Main)
Tests the dynamic proxy API by implementing the ```dp.DebugProxy``` class that implements ```java.lang.reflect.Invocationhandler```
and provides a ```newInstance``` method that can than be used to instantiate a dynamic proxy object.
```dp.DebugProxy``` is then used in ```dp.Main```'s main method to instantiate a proxy object of the
```dp.FooImpl``` class and then calls a method on it.
