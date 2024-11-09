[//]: # (MAIN: spm6.VirtualSPMCall)
This tests checks whether a virutal method call to a method with polymorphic signature is correctly performed.
The ```MethodHandle``` is first retrieved via ```MethodHandles.lookup().findVirtual(..)``` and then
invoked via the MethodHandle's ```invoke``` method. The called method is defined within an interface
(as default method).
