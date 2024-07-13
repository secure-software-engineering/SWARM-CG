[//]: # (MAIN: spm1.Class)
This tests checks whether a static method call to a method with polymorphic signature is correctly performed.
The ```MethodHandle``` is first retrieved via ```MethodHandles.lookup().findStatic(..)``` and then
invoked via the MethodHandle's ```invoke``` method. The passed parameter must be casted to
match the called method's signature.
