[//]: # (MAIN: j8dim.SuperClass)
Tests the resolution of a polymorphic call when a class (cf. ```j8dim.SubClass```) implements an
interface with default method (cf. ```j8dim.Interface```) and extends a class (cf. ```j8dim.SuperClass```)
which doesn't provide a method with the same signature as the interface's default method, namely ```method```.
The subclass, inheriting from both, doesn't define a method with that signature, hence, the method
call on that class must be dispatched to the interface's method when called on ```j8dim.SubClass```.
