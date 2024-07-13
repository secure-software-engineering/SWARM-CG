[//]: # (MAIN: nvc.Class)
Tests the call resolution of default constructors which is caused by using Java's ```NEW``` keyword. The resulting 
bytecode contains a *INVOKESPECIAL* instruction which must be resolved to ```nvc.Class```'s ```<init>``` method, i.e.,
the default name for a constructor.
