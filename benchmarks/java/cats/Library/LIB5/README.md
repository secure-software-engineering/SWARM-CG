[//]: # (LIBRARY)
Tests library interface invocation for CBS edges under the following circumstances:
1) a ```public class PotentialSuperclass``` in package ```lib5.internal``` that can be
inherited from and, therefore, provides the method ```public void method()``` from its superclass,
2) a ```package visible class InternalClass``` in package ```lib5.internal``` that can be inherited 
(analogously to 1) ),
3) a ```package visible interface``` in package ```lib5.collude``` that can be inherited from classes in the same package,
4) all of the previous mentioned classes/interfaces declare the method ```public void method()```.
