[//]: # (LIBRARY)
Tests library interface invocation for CBS edges under the following circumstances:
1) a ```public class PotentialSuperclass``` that can be inherited,
1) a ```public class DismissedSuperclass``` that cannot be inherited and, therefore, can't be target,
1) a ```public interface``` that can be inherited,
1) all of the previous mentioned classes/interfaces declare the method ```public void method()```.
