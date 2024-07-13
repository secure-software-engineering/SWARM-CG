[//]: # (MAIN: jvmc.Demo)
This cases tests the implicitly introduced call edge from ```Thread.start``` to the transitively
reachable ```Thread.exit``` method that is also called by the JVM on a thread's exit.
