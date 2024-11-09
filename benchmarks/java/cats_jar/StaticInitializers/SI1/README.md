[//]: # (MAIN: si.Main)
A static initializer should be triggered when a *non-constant static field* is referenced. The scenario below
shows an interface ```si.NonConstantFieldRef``` which declares a static non-constant field that is referenced
once in the ```si.Main```'s main method. When the field is references, the field must be initialized
and in order to do so, the JVM calls ```si.NonConstantFieldRef```'s static initializer (```<clinit>```).
