[//]: # (MAIN: spm5.VirtualSPMCall)
This tests checks whether a virutal method call to a method with polymorphic signature is correctly performed.
The ```MethodHandle``` is first retrieved via ```MethodHandles.lookup().findVirtual(..)``` and then
invoked via the MethodHandle's ```invoke``` method. The method is defined in the class and available
within the super class.
