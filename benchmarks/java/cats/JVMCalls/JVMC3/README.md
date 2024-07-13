[//]: # (MAIN: jvmc.Demo)
This cases tests the implicitly introduced call edge from ```Thread.start``` to ```Thread.run```.
Please note that this test tests this feature indirectly by validating that the run method of
```TargetRunnable``` is transitively reachable.
