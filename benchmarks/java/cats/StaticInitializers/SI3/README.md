[//]: # (MAIN: si.Demo)
Static initializer of an interface with a default method. An interface's static initializer is also
triggered when 1) *a subtype is initialized* and 2) *the interface has a default method*. Where as 1)
is given when a new instance of ```si.Demo``` - it implements the interface ```si.Interface```- is
created  in ```si.Demo```'s main method, 2) is given because ```si.Interface``` declares the
default method ```Interface.defaultMethod```. Since both criteria are fulfilled, the JVM will also
initialize ```si.Interface```.
