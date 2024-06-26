In this test case, to different versions of a class are loaded using an `URLClassLoader`.
On both versions a call to `<Comparator<Integer>>.compare` is performed.
After those different versioned classes are loaded, methods are called on the classes which must
be resolved to different targets.
