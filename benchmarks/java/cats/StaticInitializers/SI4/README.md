[//]: # (MAIN: si.Demo)
An interface static initializer should be triggered when a *final static field* with a *non-primitive type*
and *non-String type* is referenced. The scenario below shows an interface ```si.Interface``` which
declares a static final field of type ```si.Demo``` that is referenced once in the ```si.Demo```'s
main method. When the field is referenced, the field must be initialized and in order to do so,
the JVM calls ```si.Interface```'s static initializer (```<clinit>```).
