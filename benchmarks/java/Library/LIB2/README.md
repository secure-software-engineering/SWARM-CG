[//]: # (LIBRARY)
Tests virtual call resolution in the context of libraries where the calling context is unknown. 
The circumstances of the virtual call are as follows:
1) We have a method ```public void libraryEntryPoint(Type type)``` which calls a method on the passed
parameter,
2) A type ```public class Type``` which declares a method ```public void method()```,
3) Another type ```public class Subtype extends Type``` which also declares a method ```public void method()```,
4) An additional type ```public class SomeType``` which also delcares a method ```public void method()```.
Since the calling context of ```Type.method()``` in ```Demo.callOnField()``` is unknown, i.e.,
the field is public and non-final and, therefore, can be re-assigned by library users. The call-graph 
construction must assume that all possible subtypes of ```Type``` can be assigned to the field.
