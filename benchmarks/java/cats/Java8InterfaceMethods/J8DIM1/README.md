[//]: # (MAIN: j8dim.Class)
Tests the resolution of a polymorphic call when a class (cf.```j8dim.Class``` ) implements an
interface (cf. ```j8dim.Interface```) which declares a default method (cf. ```j8dim.Interface.method()```)and
inherits this default method from the inherited interface. A call on ```j8dim.Class.method()``` must
then be resolved to ```j8dim.Interface.method()```.
