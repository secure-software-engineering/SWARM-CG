[//]: # (MAIN: si.Main)
When initialization of a class occurs during execution, all its super classes must be initialized
beforehand. In ```si.Main```'s main method an instance of ```si.Subclass``` is created. Hence, all
super classes of ```si.Subclass``` must be initialized too. Those are ```si.Superclass``` as direct
super class and ```si.RootClass``` as transitive super class. Since all three classes provide static
initialization routines, calls to all must be included in the call graph.
