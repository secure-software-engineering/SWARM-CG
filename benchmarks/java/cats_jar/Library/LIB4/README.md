[//]: # (LIBRARY)
Tests library interface invocation for CBS edges under the following circumstances:
1) a ```package visible class PotentialSuperclass``` in package ```lib4.collude``` that can be
inherited from a class within the same package, i.e. when a new class is added to the same package,
2) a ```package visible class InternalClass``` in package ```lib4.internal``` that can be inherited 
(analogously to 1) ),
3) a ```package visible interface``` in package ```lib4.collude``` that can be inherited from classes in the same package,
4) all of the previous mentioned classes/interfaces declare the method ```public void method()```.
