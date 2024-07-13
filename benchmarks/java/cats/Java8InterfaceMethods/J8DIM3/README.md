[//]: # (MAIN: j8dim.SuperClass)
Tests the resolution of a polymorphic call when a class (cf. ```j8dim.SubClass```) implements an
interface with default method (cf. ```j8dim.Interface```) and extends a class (cf. ```j8dim.SuperClass```)
where the interface and the class define a method with the same signature, namely ```method```.
The subclass, inheriting from both, doesn't define a method with that signature, hence, the method
call on that class must be dispatched to the superclass's method when called on ```j8dim.SuperClass```.
