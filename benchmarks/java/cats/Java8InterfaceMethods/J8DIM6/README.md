[//]: # (MAIN: j8dim.Demo)
An interface which extends two other interfaces that declare the same default method, as
```CombinedInterface``` does by extending ```SomeInterface``` and ```AnotherInterface```,
and also declares a default method (i.e. ```CombinedInterface.method```) it is possible to use
qualified super calls of the form ```SomeInterface.super.method()``` that must be resolved to the
respective super class' method implementation. The super calls must be qualified by the targeted
super interface since it is not unique otherwise.
