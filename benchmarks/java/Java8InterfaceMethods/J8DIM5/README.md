[//]: # (MAIN: j8dim.SuperClass)
Tests the resolution of a polymorphic call when a class (cf. ```j8dim.Class```) extends an abstract
class (cf. ```j8dim.SuperClass```) that declares a method ```compute()``` and implements
several interfaces that are again in an inheritance relationship where all interfaces define a 
default method called ```method```. Respective calls on the ```compute``` and ```method``` methods
on ```j8dim.Class``` must then be dispatched to the correct methods. Since multiple interface define
the same method, the maximally specific methods must be computed (see JVM spec.).
