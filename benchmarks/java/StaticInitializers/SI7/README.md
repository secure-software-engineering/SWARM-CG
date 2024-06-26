[//]: # (MAIN: si.Main)
Assigning a *non-final static field* (e.g. ```si.Demo.assignMe```) triggers the JVM to execute
```si.Demo``` static initializer. ```si.Demo.assignMe``` is assigned in ```si.Main```'s main method
and thus its static initializer must be contained in the call graph.
