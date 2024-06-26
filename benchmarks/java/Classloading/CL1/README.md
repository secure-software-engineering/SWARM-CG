This test case uses an `URLClassLoader` in order to load classes from an external *.jar* file.
That class will be instantiated using `Class<?>.newInstance`.
Afterwards, it calls the `compare` on the `Comparator` interface, which will resolve to the `IntComparator` 
from the given *.jar* at runtime.
